from sys import argv
from ast import literal_eval
from math import ceil, floor

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
    def __init__(self, shortForm, longForm=None, description='', default_value=None):
        Flag.__init__(self, shortForm, longForm, description)
        self.value = default_value

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
        
        try:
            self.value = literal_eval(args[i])
            del args[i]
        except:
            raise ValueError(f'Parsing of literal "{args[i]}" failed for flag {self.proper_long_flag}')
        
        return True


class ProgressMeter():
    """A class that creates a maintains a progress bar"""
    def __init__(self, pct_per_char=5):
        """pct_per_char is how many percent per '=' in the bar"""
        self.last = -1
        self.bar_size = ceil(100 / pct_per_char)
        self.pct_per_char = pct_per_char
    
    def update_meter(self, pct_complete, force=False):
        """Updates the meter each time a percent passes, or if force is true"""
        if force or pct_complete - self.last < 1:
            return
        pct_complete = min(100, pct_complete)
        self.last = pct_complete
        filled = floor(pct_complete / self.pct_per_char)
        if pct_complete >= 100 - self.pct_per_char / 2:
            bar = "[" + self.bar_size * "=" + ']'
        else:
            spaces = self.bar_size - 1 - filled
            bar = '[' + filled * '=' + '>' \
                        + spaces * ' ' + ']'
        print(f'\rcompletion: {ceil(pct_complete)/100:>4.0%} {bar}', end='')


def prompt_yn(prompt: str):
    return input(prompt + " (Y/n) ").strip() in ['Y', 'y', 'yes']

if __name__ == "__main__":
    f = LiteralFlag('t', 'test', 'description')
    print(f.format_description(2, 5))
    args = Flag.get_terminal_args()
    print('starting args:', args)
    f.remove_from_args(args)
    print(f)
    print('ending args:', args)
