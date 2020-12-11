#!/usr/bin/env python3
from collections import defaultdict
from os.path import exists

from clusterTree import TreeBuilder
from flag import *

class MultiTreeBuilder:
    def __init__(self, paths):
        """paths are the relative file locations that self should build path_trees from."""
        self.word_paths = defaultdict(list)
        self.paths = paths
        self.tree_builders = { path: self.make_new_tree(path) for path in paths }
        self.trees = list()

    def make_new_tree(self, path):
        """Returns a new tree builder that uses this line_iter"""
        return TreeBuilder(path, self.multi_file_line_iter(path))

    def multi_file_line_iter(self, path):
        """Creates a line_iter usable for a TreeBuilder (takes a path and returns an iter that 
        generates (line-number, line-text)), but also saves each path for each word that
        this generator yields."""
        for i, line in TreeBuilder.file_line_iter(path):
            path, word, _ = TreeBuilder.tokenize_line(i, line)
            self.word_paths[word].append(path)
            yield i, line
    
    def build_all(self):
        """Calls build_tree on each builder in self.tree_builder, then stores a list of results
        in self.trees"""
        self.trees = [builder.build_tree() for builder in self.tree_builders.values()]
    
    def get_tree(self, path: str):
        return self.tree_builders[path].tree
        

if __name__ == "__main__":
    cluster_flag = LiteralFlag('c', 'clusters', 'List of cluster sizes to compare')

    args = Flag.get_terminal_args()
    if not args:
        raise ValueError('MultiTree requires a list of cluster sizes (w/o spaces)')

    cluster_flag.remove_from_args(args)
    input_name = args[0]

    del args[0]

    if args:
        raise ValueError('Unkown args: ', *args)

    # now the args are parsed
    # cluster_flag should have a list of cluster sizes as cluster_flag.value 
    # input_name should be a string with the name of the input file for the original brown's algorithm

    file_names = [f"{input_name}-c{size}-p1.out/paths" for size in cluster_flag.value]
    
    for f_name in file_names:
        if not exists(f_name):
            raise ValueError(f'File at {f_name} could not be found')
    
    print('All files found:', ', '.join(file_names))

    # now we have all valid file_paths

    multi_builder = MultiTreeBuilder(file_names)
    multi_builder.build_all()

    # do algorithm now

    # test code
    print('hai paths:', multi_builder.word_paths['hai'])


