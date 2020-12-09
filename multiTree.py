#!/usr/bin/env python3
from collections import defaultdict
from clusterTree import TreeBuilder

class MultiTreeBuilder:
    def __init__(self, *paths):
        self.word_paths = defaultdict(list)
        self.paths = paths
        self.path_trees = { path: self.make_new_tree(path) for path in paths }

    def make_new_tree(self, path):
        return TreeBuilder(path, self.multi_file_line_iter)

    def multi_file_line_iter(self, path):
        for i, line in TreeBuilder.file_line_iter(path):
            path, word, _ = TreeBuilder.tokenize_line(line)
            self.word_paths[word].append(path)
            yield i, line
    
    def build_all(self):
        for tree in self.path_trees.values():
            tree.build_tree()
        
