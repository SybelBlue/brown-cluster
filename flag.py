from sys import argv

class Flag:
    """A class that represents a flag that could be entered at the command line"""

    def __init__(self, shortForm, longForm=None, description=''):
        self.shortForm = shortForm
        self.longForm = longForm
        self.description = description

        self.proper_flag = f'-{shortForm}'
        self.proper_long_flag = f'--{longForm}'

    def args_have(self, args: list):
        return self.proper_flag in args or self.proper_long_flag in args
    
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
        return f'ArgFlag({self.flag}, {self.longForm})'
    
    __repr__ = __str__

    @staticmethod
    def get_terminal_args():
        """Gets the command line args, minus the name of the file executing"""
        return argv[1:]
