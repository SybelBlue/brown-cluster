from os.path import abspath, exists, split, join
import sys

class ArgFlag:
    def __init__(self, flag, longForm=None, description=''):
        self.flag = flag
        self.longForm = longForm
        self.description = description

        self.proper_flag = f'-{flag}'
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
    
    def format_description(self, starting_indent_width=8, flag_indent_width=12):
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

        
        

flags = {
    'help': ArgFlag('h', 'help', 'Displays the help prompt'),
    'write': ArgFlag('w', 'write', 'If present, overwrites the input file'),
    'force': ArgFlag('f', 'force', 'Runs without further input, \nusing defaults where necessary')
}


def first(_iter: iter, pred=lambda item: True):
    return next(filter(pred, _iter), None)

def print_help():
    flag_text = '\n\n'.join(flag.format_description() for flag in flags.values())
    print(f"""
---  input cleaner help --------------------------------------
    This program expects the relative path to
    an input corpus.

    It will insert spacing around valid non-alphanumeric words
    and delete the rest.

    Optional flags are listed below.

    Flags:\n{flag_text}
--------------------------------------------------------------
    """.strip())

def print_need_args():
    print_error('This tool requires a file path.\nRun with --help for more information.')

def print_error(text: str):
    """Prints the text, indenting each line and wrapping in the body in the error box."""
    print(
        "---  input cleaner error -------------------------------------\n\t" + 
        '\n\t'.join(text.splitlines()) + 
        "\n--------------------------------------------------------------")

def get_file_line_iter(path):
    with open(path, 'r') as f:
        while line := f.readline():
            yield line

def get_file_name(old_path):
    head, name = split(old_path)
    return join(head, 'cleaned-' + name)

def parse_commandline_args():
    args = sys.argv[1:]
    if not args:
        print_need_args()
        return
    
    flag_dict = { name: flag.remove_from_args(args) for name, flag in flags.items() }

    if flag_dict['help']:
        print_help()
        return
    
    if not args:
        print_need_args()
        return

    potential_path = first(args, lambda item: not item.startswith('-'))
    
    if not potential_path:
        print_need_args()
        return

    args.remove(potential_path)

    potential_path = abspath(potential_path)
    
    if exists(potential_path):
        file_lines = get_file_line_iter(potential_path)
    else:
        print_error(f'Unkown file! \n\t{potential_path}')
        return

    if args:
        plural = 's' if len(args) > 1 else ''
        error_text = ', '.join(args)
        print_error(f'Unknown flag{plural}! \n\t{error_text}')
        

    overwrite_old = flag_dict['write']

    if overwrite_old and not flag_dict['force']:
        confirm = input('Are you sure you want to overwrite the input file? (y or n): ')
        overwrite_old = confirm in 'y yes Yes YES'.split()
    
    new_file_path = potential_path if overwrite_old else get_file_name(potential_path)

    return file_lines, new_file_path

def write_file(path, lineIter: iter):
    with open(new_file_path, 'w+') as write_file:
        write_file.writelines(lineIter)

def clean_line(line):
    return line


if __name__ == "__main__":
    if parse_result := parse_commandline_args():
        file_lines, new_file_path = parse_result
        write_file(new_file_path, map(clean_line, file_lines))
        



        
