#!/usr/bin/env python3
from collections import defaultdict
from os.path import exists
from sys import exit
from itertools import combinations
from csv import writer, reader
from math import ceil

from clusterTree import TreeBuilder
from terminalHelpers import *
from analysis import make_buckets

class MultiTreeBuilder:
    @staticmethod
    def create_file_locs(input_file_name, cluster_sizes):
        """ input_file_name is the name of the file (without the extension) that contains the corpus given to Brown's algorithm
            cluster_sizes is the list of -c arguments provided to each execution of the algorithm"""
        file_names = [f"{input_file_name}-c{size}-p1.out/paths" for size in cluster_sizes]

        for f_name in file_names:
            if not exists(f_name):
                raise ValueError(f'File at {f_name} could not be found')
        
        return file_names

    def __init__(self, file_names: list):
        """file_names are the tree output path locations ie 'input-c40-p1.out/paths'"""
        # file locations of the paths files
        self.file_names = file_names
        # TreeBuilder's buildTree method takes in a file location and creates a tree.
        self.tree_builders = { path: self.make_new_tree(path) for path in self.file_names }

        self.word_paths = defaultdict(list) # stores the bitstring paths for each word
        self.trees = list() # list of trees

    def make_new_tree(self, path):
        """Returns a new tree builder that uses this line_iter"""
        return TreeBuilder(path, self.multi_file_line_iter(path))

    def multi_file_line_iter(self, file_path):
        """Creates a line_iter usable for a TreeBuilder (takes a file_path and returns an iter that
        generates (line-number, line-text)), but also saves each path for each word that
        this generator yields."""
        for i, line in TreeBuilder.file_line_iter(file_path):
            path, word, _ = TreeBuilder.tokenize_line(i, line)
            self.word_paths[word].append(path)
            yield i, line

    def build_all(self):
        """Calls build_tree on each builder in self.tree_builder, then stores a list of results
        in self.trees"""
        self.trees = [builder.build_tree() for builder in self.tree_builders.values()]

    def get_tree(self, path: str):
        return self.tree_builders[path].tree

    def analyse(self):
        """ Yields (percent_completion, pairwise_score_value), or
            (pct_complete: float, (word0: str, word1: str, score: float))"""
        # this is the of number of yielded values for pairwise_score
        # == len(combinations(self.word_paths, 2))
        value_count = len(self.word_paths)
        value_count *= value_count - 1
        value_count /= 2
        for i, result in enumerate(self.pairwise_score()):
            yield i / value_count * 100, result

    def pairwise_score(self):
        """Yields 3-tuples containing unique pairs of words and their pairwise relation"""
        # Edge weight calculation:
        # For every set of words/nodes A and B:
        #     edgeWeight = 0
        #     For each tree with cluster size C:
        #         maxPath = longest distance between 2 nodes, longest walk in the tree
        #         abPath = length of path between a,b
        #         edgeWeight += ((maxPath + 1)/(abPath + 1))*C

        def make_bitstring_key(tree_num, str0, str1):
            """makes it so that each pair of nodes in a tree has a unique label regardless of ordering"""
            major = max(str0, str1)
            minor = min(str0, str1)
            return tree_num, major, minor

        max_tree_depths = [builder.max_depth() for builder in self.tree_builders.values()]

        # fill this dict
        tree_bitstring_pair_values = dict()
        for i, builder in enumerate(self.tree_builders.values()):
            for a_bitstr, b_bitstr in combinations(builder.leaf_paths, 2):
                ab_path = TreeBuilder.distance(a_bitstr, b_bitstr)
                key = make_bitstring_key(i, a_bitstr, b_bitstr)
                tree_bitstring_pair_values[key] = 2 * max_tree_depths[i] / (ab_path + 1)
            for bitstr in builder.leaf_paths:
                key = make_bitstring_key(i, bitstr, bitstr)
                tree_bitstring_pair_values[key] = 2 * max_tree_depths[i]

        print(f'built memoized bistring dict! (size: {len(tree_bitstring_pair_values)})')

        for (a, a_bitstrs), (b, b_bitstrs) in combinations(self.word_paths.items(), 2):
            edge_weight = 0.1
            for i in range(len(self.trees)):
                a_str, b_str = a_bitstrs[i], b_bitstrs[i]
                key = make_bitstring_key(i, a_str, b_str)
                edge_weight += tree_bitstring_pair_values[key]
            yield a, b, ceil(edge_weight)


if __name__ == "__main__":
    cluster_flag = LiteralFlag('c', 'clusters', 'List of cluster sizes to compare')
    delimiter_flag = LiteralFlag('d', 'delimiter', 'The delimiter string to use\nfor the output file', default_value='\t')
    help_flag = Flag('h', 'help', 'Shows this prompt')
    output_flag = LiteralFlag('o', 'output', 'Where to write csv output', default_value='./multi-tree-output.csv')

    def print_help():
        print('--- Help ---------------------------------------------')
        print('\tThis tool must be provided with cluster sizes \n\tand the name of the file that was used as\n\tinput to the algorithm (without its extension)')
        for flag in [cluster_flag, delimiter_flag, help_flag, output_flag]:
            print(flag.format_description(4, 18))
        print('------------------------------------------------------')

    args = Flag.get_terminal_args()

    if help_flag.remove_from_args(args):
        print_help()
        exit()

    if not cluster_flag.remove_from_args(args):
        print_help()
        raise ValueError('MultiTree requires a list of cluster sizes (w/o spaces)')
    if not isinstance(cluster_flag.value, list):
        print_help()
        raise ValueError('MultiTree cluster flag must be followed by a python list literal')

    if not delimiter_flag.remove_from_args(args):
        print('Using default delimter: "' + delimiter_flag.value + '"')
    if not isinstance(delimiter_flag.value, str):
        print_help()
        raise ValueError('MultiTree delimiter flag must be followed by a python str literal')

    if not output_flag.remove_from_args(args):
        print(f'Using default output location: {output_flag.value}')
    if not isinstance(output_flag.value, str):
        print_help()
        raise ValueError('MultiTree output flag must be a str-literal location of an output file')
    if not exists(output_flag.value):
        print(f'Creating new file for output: {output_flag.value}')

    if not args:
        raise ValueError('MultiTree requires the name of the input file (without extension)')

    input_name = args[0]

    del args[0]

    if args:
        print_help()
        raise ValueError('Unkown args: ', *args)

    # now the args are parsed
    # cluster_flag should have a list of cluster sizes as cluster_flag.value
    # input_name should be a string with the name of the input file for the original brown's algorithm

    files = MultiTreeBuilder.create_file_locs(input_name, cluster_flag.value)
    multi_builder = MultiTreeBuilder(files)
    multi_builder.build_all()

    # do algorithm now
    with open(output_flag.value, 'w+') as f:
        csv_writer = writer(f, delimiter=delimiter_flag.value)
        csv_writer.writerow('source target weight'.split())
        meter = ProgressMeter()
        written = 0
        max_value = 0
        for pct_completion, result in multi_builder.analyse():
            meter.update_meter(pct_completion)
            max_value = max(max_value, result[2])
            csv_writer.writerow(result)
            written += 1

    print()
    print(f'done! wrote {written:,} lines to {output_flag.value} (max {max_value})')

    inverted_output = output_flag.value.replace('.csv', "-inverted.csv")

    if inverse := prompt_yn("Do you wish to invert the score so low value is high correlation?"):
        with open(output_flag.value) as raw:
            with open(inverted_output, 'w+') as new:
                meter = ProgressMeter()
                r = reader(raw, delimiter=delimiter_flag.value)
                w = writer(new, delimiter=delimiter_flag.value)
                w.writerow(next(r)) # write header
                for i, (a, b, s) in enumerate(r):
                    meter.update_meter(100 * i / written)
                    w.writerow((a, b, max_value - int(s) + 1))
        print()
        print("done!")
    
    if prompt_yn("Do you wish to run buckets?"):
        make_buckets(inverted_output if inverse else output_flag.value)
        print('done!')
