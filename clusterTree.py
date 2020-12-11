#!/usr/bin/env python3
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
        """ Get right child if right is true, or left child otherwise """
        return self.right_child if right else self.left_child

    def force_child(self, right: bool):
        """ Get a child, or create it if it doesn't exist yet. Gets right child
            if right is true, left child otherwise """
        if right:
            if not self.right_child:
                self.right_child = TreeNode(self.label + '1')
        else:
            if not self.left_child:
                self.left_child = TreeNode(self.label + '0')
        return self.get_child(right)

    def __getitem__(self, right):
        """ Overloads the tree[___] syntax.
            right must be a bool, 0, 1 or a bitstring."""
        if isinstance(right, bool):
            return self.force_child(right)
        if isinstance(right, int):
            return self.force_child(right != 0)
        if isinstance(right, str):
            return self.walk_with_bitstring(right)
        raise ValueError('must be indexed by bool, int, or str')

    def walk_with_bitstring(self, path: str):
        """Takes a bitstring path, and forces a walk along that string,
        creating nodes as necessary to complete the walk. Returns the node that the
        path terminates at. Equivalent to:

        >>> current = tree_root
        >>> for c in path:
        >>>     right = TreeNode.str_to_right(c)
        >>>     current = current[right]
        >>> return current"""
        if not path:
            return self

        first, rest = path[0], path[1:]
        right = TreeNode.str_to_right(first)

        return self.force_child(right).walk_str(rest)

    def add_word(self, word, count):
        """Adds (word, count) to self.words"""
        self.words.append((word, count))

    def compute_weight(self):
        """ Counts how many leaf nodes have this as an ancestor, and saves that
        as self.value. (Runs recursively, so all descendants will also have self.value set.)"""
        value = sum(c for _, c in self.words)
        if self.right_child:
            value += self.right_child.compute_weight()
        if self.left_child:
            value += self.left_child.compute_weight()
        self.value = value
        return value

    def __str__(self):
        s = "TreeNode " + self.label
        if self.value:
            s += " self.value"
        if self.words:
            s += " self.words"
        if self.left_child or self.right_child:
            s += " [l: " + self.left_child + ", r: " + self.right_child + "]"
        return s

    # sets the console representation to be identical to str(self)
    __repr__ = __str__

    @staticmethod
    def str_to_right(s):
        """Returns False if s == '0', True if s == '1', otherwise raises an error."""
        if s == '0':
            return False
        if s == '1':
            return True
        raise ValueError('s must be a 0 or 1 (bitstring char)')

    def pretty_format(self, digitsLen=None, joinLines=True):
        """ Recursively computes the pretty formatting for this node and all descendants.

        digitsLen is the number digits to show in the value slot.

        When joinLines is true, this returns a string, otherwise it returns a list of lines."""
        if digitsLen is None:
            digitsLen = len(str(self.value))
        padding = (digitsLen - len(str(self.value))) * ' '
        lines = ["Node " + self.label + padding + self.value + "--"]

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
    def __init__(self, path, line_iter=None):
        """Sets up to parse the tree at path using the file_line_iter if line_iter is None"""
        self.path = path
        self.file_line_iter = TreeBuilder.file_line_iter(path) if line_iter is None else line_iter
        self.tree = TreeNode('')
        self.leaf_paths = set()

    @staticmethod
    def file_line_iter(path):
        """Iterates over the lines of path, returning a 2-tuple of
        line-number, line-text."""
        with open(path, 'r') as f:
            i = 0
            while line := f.readline():
                yield i, line
                i += 1

    def tokenize_next_line(self):
        """Consumes the next line of the file and returns a tokenized form, if present.
        None otherwise.

        Tokenized form is: [path: str, word: str, count: int]"""
        line_tuple = next(self.file_line_iter, None)
        if line_tuple is None:
            return None
        line_no, line = line_tuple

        # if empty line, then skip it.
        if not line:
            return self.tokenize_next_line()

        return TreeBuilder.tokenize_line(line_no, line)

    @staticmethod
    def tokenize_line(line_number, line):
        """Splits the line according to the format of the output/paths file:

        path-bitstring word word-count

        Expected format: three strings of characters separated by two characters.
        The word count must be an int literal."""
        segments = line.split()

        if len(segments) != 3:
            raise AttributeError(f'Unexpected formatting at: \n line {line_number} | {line}Expected three words.')

        path, word, count = segments
        return path, word, int(count)

    def parse_next_line(self):
        """Consumes and parses the next unread line of the file. Returns True
        if there are still lines in the file, False otherwise."""
        tokens = self.tokenize_next_line()
        if tokens is None:
            return False

        path, word, count = tokens
        self.leaf_paths.add(path)
        self.tree[path].add_word(word, count)
        return True

    def build_tree(self):
        """Parses all of the lines at the provided path, then computes the weights of each node"""
        while self.parse_next_line():
            pass

        # compute the weights
        self.tree.compute_weight()

        return self.tree

    @staticmethod
    def distance(label0: str, label1: str):
        """ Returns the smallest number of nodes required to travel from node0 to node1
            -----

            Consider the following example lables

                   label0: 11010101
                   label1: 110110

            common prefix: 1101 (lowest common ancestor)
            They share the prefix 1101 which is the path of
            the lowest common ancestor. Therefore the distance
            between them is the sum of the lengths of the unique
            suffixes '0101' and '10', ie 6 nodes apart.

            This can be computed as the sum of lengths of each label
            minus twice the size of the shared prefix. """
        return len(label0) + len(label1) - 2 * TreeBuilder.lca_depth(label0, label1)

    @staticmethod
    def min_dist_to_lca(label0: str, label1: str):
        """ Out of the two distances: label0 to lca, and label1 to lca, returns
            the minimum of those two values """
        min_label_length = min(len(label0), len(label1))
        return min_label_length - TreeBuilder.lca_depth(label0, label1)

    @staticmethod
    def max_dist_to_lca(label0: str, label1: str):
        """ Out of the two distances: label0 to lca, and label1 to lca, returns
            the maximum of those two values """
        max_label_length = max(len(label0), len(label1))
        return max_label_length - TreeBuilder.lca_depth(label0, label1)

    @staticmethod
    def lca_depth(label0: str, label1: str):
        """Returns the level that the lowest common ancestor of label0 and label1 are on.

        lca_depth('110111', '1101000') -> 4 (lca is '1101')

        lca_depth('1101', '0110') -> 0 (lca is root node)
        """
        for i, (l0, l1) in enumerate(zip(label0, label1)):
            if l0 != l1:
                return i + 1
        return min(len(label0), len(label1))

    @staticmethod
    def lca_label(label0: str, label1: str):
        """Returns the label (eg, '110111') of the lowest common ancestor of
        label0 and label1 (biggest common prefix of the labels)."""
        return label0[:TreeBuilder.lca_depth(label0, label1)]


if __name__ == "__main__":
    builder = TreeBuilder('./lolcat-c50-p1.out/paths')
    tree = builder.build_tree()
    print(tree.pretty_format())
    print('leaf pathes:', len(builder.leaf_paths))
