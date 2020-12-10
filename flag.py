from sys import argv
from ast import literal_eval

class Flag:
    """A class that represents a flag that could be entered at the command line"""

    def __init__(self, shortForm, longForm=None, description=''):
        self.shortForm = shortForm
        self.longForm = longForm if longForm else shortForm
        self.description = description

        self.proper_flag = f'-{self.shortForm}'
        self.proper_long_flag = f'--{self.longForm}'
    
    def remove_from_args(self, args: list):
        """Returns true if this flag is present in the args list, false otherwise.
        Will also remove the flag from args if present."""
        if self.proper_flag in args:
            args.remove(self.proper_flag)
            return True
        
        if self.proper_long_flag in args:
            args.remove(self.proper_long_flag)
            return True
        
        return False
    
    def format_description(self, starting_indent_width, flag_indent_width):
        """Formats this object to print such that

        | <--- starting indent ---> | <---- flag indent ------> |
                                     -f, --flag                  Description starts...
                                                                 description continues...
                                                                 and continues.


        for starting and flag indent widths in character length        
        """
        def n_spaces(n):
            return ' ' * n
        
        flag_str = f'{self.proper_flag}, {self.proper_long_flag}'

        remaining_indent_width = flag_indent_width - len(flag_str)
        if len(flag_str) < flag_indent_width:
            flag_str += n_spaces(remaining_indent_width)
        
        description_lines = self.description.splitlines()

        lines = n_spaces(starting_indent_width) + flag_str + description_lines[0]
        for l in description_lines[1:]:
            lines += '\n'
            lines += n_spaces(starting_indent_width + flag_indent_width) + l
        
        return lines

    def __str__(self):
        return f'Flag({self.shortForm}, {self.longForm})'
    
    __repr__ = __str__

    @staticmethod
    def get_terminal_args():
        """Gets the command line args, minus the name of the file executing"""
        return argv[1:]


class LiteralFlag(Flag):
    def __init__(self, shortForm, longForm=None, description=''):
        Flag.__init__(self, shortForm, longForm, description)
        self.value = None

    def __str__(self):
        return f'LiteralFlag({self.shortForm}, {self.longForm}: {self.value})'
    
    __repr__ = __str__

    def remove_from_args(self, args: list):
        """Returns true if this flag is present in the args list, false otherwise.
        Will also remove the flag and its value from args if present."""
        if self.proper_flag in args:
            i = args.index(self.proper_flag)        
        elif self.proper_long_flag in args:
            i = args.index(self.proper_long_flag)
        else:        
            return False
        
        del args[i]

        if i == len(args):
            return True
        
        self.value = literal_eval(args[i])
        del args[i]
        
        return True


if __name__ == "__main__":
    f = LiteralFlag('t', 'test', 'description')
    print(f.format_description(2, 5))
    args = Flag.get_terminal_args()
    print('starting args:', args)
    f.remove_from_args(args)
    print(f)
    print('ending args:', args)
