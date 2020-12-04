from os.path import abspath, exists, split, join
from sys import argv, exit
import re


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


class CleanerPrinter:
    """A class for grouping together the console output behavior of the cleaning program"""

    @staticmethod
    def print_help(flags):
        flag_text = '\n\n'.join(flag.format_description(8, 12) for flag in flags)
        print(
f"""---  input cleaner help --------------------------------------
    This program expects the relative path to
    an input corpus.

    It will insert spacing around valid non-alphanumeric words
    and delete the rest.

    Optional flags are listed below.

    Flags:\n{flag_text}
--------------------------------------------------------------""")

    @staticmethod
    def raise_need_file_path():
        CleanerPrinter.raise_error('This tool requires a file path.\nRun with --help for more information.')

    @staticmethod
    def raise_error(text: str, do_raise=True):
        """Prints the text, indenting each line and wrapping in the body in the error box."""
        print(
            "---  input cleaner error -------------------------------------\n\t" + 
            '\n\t'.join(text.splitlines()) + 
            "\n--------------------------------------------------------------")
        if do_raise:
            exit(1)
    
    @staticmethod
    def print_success(target_path):
        print(
            "---  input cleaner success -----------------------------------\n\t" + 
            "File Written!\n\t" + target_path +
            "\n--------------------------------------------------------------")



def get_file_line_iter(path):
    """Creates an iterator over the lines of the file at path. Reads while lines exist."""
    with open(path, 'r') as f:
        while line := f.readline():
            yield line

def get_cleaned_file_name(old_path):
    """Creates a file name for the cleaned version over """
    head, name = split(old_path)
    return join(head, 'cleaned-' + name)

def first(_iter: iter, pred=lambda item: True):
    """Returns the first item in _iter that satisfies pred, or 
    None of no such item exists"""
    return next(filter(pred, _iter), None)

def parse_commandline_args():
    """Gets the command line args when called, and parses them. Returns an iterable of the 
    lines for the file to read, and the path of the file to write cleaned lines to.
    
    Will call sys.exit if there is a formatting error."""
    
    # flags for this program
    flags = [
        Flag('h', 'help', 'Displays this help prompt'),
        Flag('w', 'write', 'If set, overwrites the input file \ninstead of making a new one'),
        Flag('f', 'force', 'Runs without further input, \nusing defaults where necessary')
    ]

    args = argv  # get the system input
    if args[0].startswith('clean-input'):
        # if it's called like:
        #   python3 clean-input.py ... flags ...
        # then it includes clean-input.py as a flag which we discard
        args = args[1:]
    
    # read the flag data as { longForm: T/F }, removing identified flags from args
    # as it constructs set_flags
    set_flags = { flag.longForm: flag.remove_from_args(args) for flag in flags }

    # if request help, then print help and exit
    if set_flags['help']:
        CleanerPrinter.print_help(flags)
        exit()
    
    # if there is no file path, raise error
    if not args:
        CleanerPrinter.raise_need_file_path()

    # get the first arg that doesn't have the flag prefix "-"
    potential_path = first(args, lambda item: not item.startswith('-'))
    
    # if it doesn't exist, raise error
    if not potential_path:
        CleanerPrinter.raise_need_file_path()

    # remove it from the args
    args.remove(potential_path)

    # use os.abspath to resolve
    potential_path = abspath(potential_path)

    # if it exists, get the file line iterator, otherwise raise exception    
    if exists(potential_path):
        file_lines = get_file_line_iter(potential_path)
    else:
        CleanerPrinter.raise_error(f'Unkown file! \n\t{potential_path}')

    # raises error on unknown flags/options (which would be all remaining args)
    if args:
        plural = 's' if len(args) > 1 else ''
        error_text = ', '.join(args)
        CleanerPrinter.raise_error(f'Unknown flag{plural}! \n\t{error_text}', do_raise=not set_flags['force'])
        
    do_overwrite_old = set_flags['write']

    # if not forced, confirm overwriting corpus
    if do_overwrite_old and not set_flags['force']:
        confirm = input('Are you sure you want to overwrite the input file? (y or n): ')
        do_overwrite_old = confirm in 'y yes Yes YES'.split()
    
    destination_file_path = potential_path if do_overwrite_old else get_cleaned_file_name(potential_path)

    return file_lines, destination_file_path

def write_file(path, line_iter: iter):
    """Writes the lines in line_iter to the file at path, or creates a new
    one if it is not present. Closes the file on completion."""
    with open(path, 'w+') as target_file:
        target_file.writelines(line_iter)

# the regex for identifying bunches of punctuation.
# optionally followed by whitespace.
# provides the punctuation as group 1.
punctuation_cleaning_regex = re.compile(r'([^\w\s]+)\s*')
# the regex to substitute captured bunches of punctuation.
# simply surrounds it with spaces.
punctuation_sub_regex = r' \g<1> '
def clean_line(line):
    """Spaces out each bunch of symbols, and terminates with a single newline."""
    cleaned = re.sub(punctuation_cleaning_regex, punctuation_sub_regex, line).strip()
    return cleaned + '\n'

def clean_corpus(file_lines: iter, target_path):
    """Cleans each line in file_lines, and writes to the target_path. Creates
    a new file if no such file at target_path exists."""
    write_file(target_path, map(clean_line, file_lines))

if __name__ == "__main__":
    if parse_result := parse_commandline_args():
        file_lines, target_path = parse_result
        clean_corpus(file_lines, target_path)
        CleanerPrinter.print_success(target_path)