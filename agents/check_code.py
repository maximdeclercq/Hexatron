import re
import sys

class WrongFileException(Exception):
	pass

def code_check(code):
    forbidden_strings = [r'eval[^A-z0-9_]', r'exec[^A-z0-9_]', r'open[^A-z0-9_]', 
                         'file', 'import os', 'import sys', 'from os', 'from sys', 
                         'subprocess', 'dircache', '__', r'dir[^A-z0-9_]', 
                         'globals', 'getattr']
    allowed_starts = (' ', '\t', '\n', 'import', 'from', 'def', '#', '@', '\r')
    legal_imports = ['functools', 'itertools', 'collections', 'operator', 'heapq',
                     'math', 'random', 'numpy', 'time', 'queue']

    for forbidden_string in forbidden_strings:
        if re.search(forbidden_string, code):
            msg = 'Code contains an illegal clause: {}'
            raise WrongFileException(msg.format(forbidden_string))

    if not re.search('def generate_move', code):
        raise WrongFileException('Code does not contain a generate_move function!')

    for line in code.split('\n'):
        if len(line) > 0 and not line.startswith(allowed_starts):
            raise WrongFileException('File contains execution code!')
        if line.startswith('import'):
            lib = line.split()[1]
            if lib not in legal_imports:
                raise WrongFileException('{} is not an allowed library! You can send a request to include this library through the feedback form.'.format(lib))

    return True

def main(argv):
    """Script starting point.

    Args:
        argv (list): List of command-line arguments. The first element is
            always "simulator.py", the name of this script. The second element
            should be the name of the first agent's file. The final element
            should be the name of the opponent's file. Not that this can be
            the same name as the previous file.
    """

    if len(argv) != 2:
        print('Usage: python[3] check_code.py [file]')
        exit(1)

    file = argv[1]
    with open(file, 'r', encoding='utf-8') as ifp:
        print(code_check(ifp.read()))

if __name__ == '__main__':
    main(sys.argv)