#!/usr/bin/env python3
from collections import defaultdict
from os.path import exists
from sys import exit
from itertools import combinations
from csv import writer

from clusterTree import TreeBuilder
from flag import *

class MultiTreeBuilder:
    def __init__(self, input_file_name: str, cluster_sizes: list):
        """ input_file_name is the name of the file (without the extension) that contains the corpus given to Brown's algorithm
            cluster_sizes is the list of -c arguments provided to each execution of the algorithm"""
        self.cluster_sizes = cluster_sizes

        # file locations of the paths files
        self.file_names = [f"{input_file_name}-c{size}-p1.out/paths" for size in cluster_sizes]
        for f_name in self.file_names:
            if not exists(f_name):
                raise ValueError(f'File at {f_name} could not be found')

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

    def pairwise_score(self):
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
                max_path = 2 * max_tree_depths[i]
                key = make_bitstring_key(i, a_bitstr, b_bitstr)
                value = ((max_path + 1) / (ab_path + 1)) * self.cluster_sizes[i]
                tree_bitstring_pair_values[key] = value

        print('built memoized bistring dict!')

        for (a, a_bitstrs), (b, b_bitstrs) in combinations(self.word_paths.items(), 2):
            edge_weight = 0
            for i in range(len(self.trees)):
                a_str, b_str = a_bitstrs[i], b_bitstrs[i]
                if a_str != b_str:
                    key = make_bitstring_key(i, a_str, b_str)
                    edge_weight += tree_bitstring_pair_values[key]
                else:
                    max_path = 2 * max_tree_depths[i]
                    edge_weight += max_path * self.cluster_sizes[i]
            yield a, b, edge_weight


if __name__ == "__main__":
    cluster_flag = LiteralFlag('c', 'clusters', 'List of cluster sizes to compare')
    delimiter_flag = LiteralFlag('d', 'delimiter', 'The delimiter string to use\nfor the output file', default_value='\t')
    help_flag = Flag('h', 'help', 'Shows this prompt')

    def print_help():
        print('--- Help ---------------------------------------------')
        print('\tThis tool must be provided with cluster sizes \n\tand the name of the file that was used as\n\tinput to the algorithm (without its extension)')
        print(cluster_flag.format_description(4, 18))
        print(delimiter_flag.format_description(4, 18))
        print(help_flag.format_description(4, 18))
        print('------------------------------------------------------')

    args = Flag.get_terminal_args()

    if help_flag.remove_from_args(args):
        print_help()
        exit()
    
    if not cluster_flag.remove_from_args(args):
        print_help()
        raise ValueError('MultiTree requires a list of cluster sizes (w/o spaces)')

    if not delimiter_flag.remove_from_args(args):
        print(f'Using default delimter: {delimiter_flag.value}')
    
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

    multi_builder = MultiTreeBuilder(input_name, cluster_flag.value)
    multi_builder.build_all()

    # do algorithm now
    with open('./test-output.csv', 'w+') as f:
        csv_writer = writer(f, delimiter=delimiter_flag.value)
        csv_writer.writerow('source target weight'.split())
        for result in multi_builder.pairwise_score():
            csv_writer.writerow(result)

    print('done')
