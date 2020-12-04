#!/usr/bin/env python3
from os.path import exists, abspath

class TreeBuilder:
    class TreeNode:
        # index 0, '0', or False
        right_child = None
        # index 1, '1', or True
        left_child = None

        def __init__(self, right: bool):
            self.is_right = right

        def get_child(self, right: bool):
            return self.right_child if right else self.left_child

        def force_child(self, right: bool):
            if right:
                if not self.right_child:
                    self.right_child = TreeNode(True)
            else:
                if not self.left_child:
                    self.left_child = TreeNode(False)
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

            right = TreeBuilder.TreeNode.str_to_right(first)

            if right is None:
                raise ValueError('walk_string must be a binary string of 0s and 1s, not ' + first)

            child = self.force_child(right)
            return child.walk_string(rest)

        @staticmethod
        def str_to_right(s):
            if s == '0':
                return False
            if s == '1':
                return True
            return None

    def __init__(self, path):
        self.path = path
        self.file = None

    def __enter__(self):
        self.file = open(self.path, 'r')
        return self

    def __exit__(self):
        if self.file and not self.file.closed():
            self.file.close()
