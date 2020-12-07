#!/usr/bin/env python3
import itertools as it

class TreeNode:
    def __init__(self, label):
        self.label = label

        # index 0, '0', or False
        self.right_child = None
        # index 1, '1', or True
        self.left_child = None

        # list of (word, count) pairs
        self.words = []
        self.value = 0

    def get_child(self, right: bool):
        return self.right_child if right else self.left_child

    def force_child(self, right: bool):
        if right:
            if not self.right_child:
                self.right_child = TreeNode(self.label + '1')
        else:
            if not self.left_child:
                self.left_child = TreeNode(self.label + '0')
        return self.get_child(right)

    def __getitem__(self, right):
        if isinstance(right, bool):
            return self.force_child(right)
        if isinstance(right, int):
            return self.force_child(right != 0)
        if isinstance(right, str):
            return self.walk_str(right)
        raise ValueError('must be indexed by bool, int, or str')

    def walk_str(self, walk_string: str):
        if not walk_string:
            return self

        first, rest = walk_string[0], walk_string[1:]
        right = TreeNode.str_to_right(first)

        if right is None:
            raise ValueError('walk_string must be a binary string of 0s and 1s, not ' + first)

        return self.force_child(right).walk_str(rest)
    
    def add_word(self, word, count):
        self.words.append((word, count))

    def compute_weight(self):
        value = sum(c for _, c in self.words)
        if self.right_child:
            value += self.right_child.compute_weight()
        if self.left_child:
            value += self.left_child.compute_weight()
        self.value = value
        return value

    def __str__(self):
        s = f'TreeNode "{self.label}"'
        if self.value:
            s += f' ({self.value})'
        if self.words:
            s += f' {self.words}'
        if self.left_child or self.right_child:
            s += f' [l: {self.left_child}, r: {self.right_child}]'
        return s
    
    __repr__ = __str__

    @staticmethod
    def str_to_right(s):
        if s == '0':
            return False
        if s == '1':
            return True
        return None

    def pretty_format(self, digitsLen=None, joinLines=True):
        if digitsLen is None:
            digitsLen = len(str(self.value))
        padding = (digitsLen - len(str(self.value))) * ' '
        lines = [f'Node {self.label} {padding}{self.value} --']

        if not self.left_child and not self.right_child:
            return '\n'.join(lines) if joinLines else lines

        indent_width = max(map(len, lines)) + 1
        child_lines = self.left_child.pretty_format(digitsLen, False) if self.left_child else []
        if self.right_child:
            child_lines.extend(self.right_child.pretty_format(digitsLen, False))

        for i, line in enumerate(child_lines):
            if len(lines) == i:
                lines.append(' ' * indent_width + '| ' + line)
            else:
                lines[i] += ' ' * (indent_width - len(lines[i])) + '| ' + line

        return '\n'.join(lines) if joinLines else lines


class TreeBuilder:
    def __init__(self, path):
        self.path = path
        self.file_line_iter = TreeBuilder.file_line_iter(path)
        self.tree = TreeNode('')
        self.leaf_paths = set()

    @staticmethod
    def file_line_iter(path):
        with open(path, 'r') as f:
            i = 0
            while line := f.readline():
                yield i, line
                i += 1

    def tokenize_next_line(self):
        line_tuple = next(self.file_line_iter, None)
        if line_tuple is None:
            return None
        line_no, line = line_tuple
        
        # if empty line, then skip it.
        if not line:
            return self.tokenize_next_line()
        
        segments = line.split()
        
        if len(segments) != 3:
            raise AttributeError(f'Unexpected formatting at: \n line {line_no} | {line}Expected three words.')

        path, word, count = segments
        return path, word, int(count)

    def parse_next_line(self):
        tokens = self.tokenize_next_line()
        if tokens is None:
            return False
        
        path, word, count = tokens
        self.leaf_paths.add(path)
        self.tree[path].add_word(word, count)
        return True
    
    def build_tree(self):
        while self.parse_next_line():
            pass

        # compute the weights
        self.tree.compute_weight()

        return self.tree

    @staticmethod
    def distance(label0: str, label1: str):
        """Returns the number of nodes required to travel from node0 to node1"""
        # Consider the following example lables
        #        label0: 11010101
        #        label1: 110110
        # common prefix: 1101 (lowest common ancestor)
        # They share the prefix 1101 which is the path of
        # the lowest common ancestor. Therefore the distance 
        # between them is the sum of the lengths of the unique
        # suffixes '0101' and '10', ie 6 nodes apart.
        # 
        # This can be computed as the sum of lengths of each label
        # minus twice the size of the shared prefix.
        #
        # Note that if and only if the labels are the same, the dist is 0.
        # (if the lengths are different, zip will stop before dist is 0)
        # (if the contents are different, for will break before dist is 0)
        dist = len(label0) + len(label1)
        
        for l0, l1 in zip(label0, label1):
            if l0 == l1:
                dist -= 2
            else:
                break
        
        return dist

    @staticmethod
    def min_dist_to_lca(label0: str, label1: str):
        min_label_length = min(len(label0), len(label1))
        return min_label_length - TreeBuilder.lca_depth(label0, label1)

    @staticmethod
    def max_dist_to_lca(label0: str, label1: str):
        max_label_length = max(len(label0), len(label1))
        return max_label_length - TreeBuilder.lca_depth(label0, label1)

    @staticmethod
    def lca_depth(label0: str, label1: str):
        for i, (l0, l1) in enumerate(zip(label0, label1)):
            if l0 != l1:
                return i + 1
        return min(len(label0), len(label1))
    
    @staticmethod
    def lca_label(label0: str, label1: str):
        return label0[:TreeBuilder.lca_depth(label0, label1)]
        


if __name__ == "__main__":
    builder = TreeBuilder('./lolcat-c50-p1.out/paths')
    tree = builder.build_tree()
    print(tree.pretty_format())
    print(len(builder.leaf_paths))
