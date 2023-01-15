# https://github.com/anir/dos2unix-python/blob/master/dos2unix.py
# https://stackoverflow.com/questions/36422107/how-to-convert-crlf-to-lf-on-a-windows-machine-in-python
# https://stackoverflow.com/questions/11427138/python-wildcard-search-in-string
#
'''
usage: dos2unix.py <dos2unix|unix2dos> path
'''
import fnmatch
import glob
import mmap
import os
import re
import sys

if len(sys.argv[1:]) != 2:
    sys.exit(__doc__)

param_file = sys.argv[2]
op_direction = sys.argv[1]

op_mode = -1                # UNKnown command
op_wild_ext = '*'           # if mode wildcard extension, then here's and extension
op_root = ''                # root dir

# @todo: /dir/, /dir/*, /dir/*.ext

MODE_UNK = -1
MODE_FILE = 1       # dir/file
MODE_WILD_EXT = 2   # dir/*.py
MODE_WILD_ANY = 3   # dir/*

EXCLUSIONS = ('.*', '*.pdf')

LF = b'\n'
CRLF = b'\r\n'


def is_file_binary(filename) -> bool:
    '''
    https://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
    '''
    with open(filename, 'rb') as f:
        data_str: bytes = f.read(1024)
    textchars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7f})
    is_binary_string = bool(data_str.translate(None, textchars))
    return is_binary_string


def is_file_excluded(filename) -> bool:
    for ex in (('.', '..') + EXCLUSIONS):
        if fnmatch.fnmatch(os.path.basename(filename), ex):
            return True
    return False


def our_mode(filename: str) -> int:
    global op_mode, op_wild_ext, op_root
    if match := re.match(r'(.*(\\|/)?)\*$', filename):              # dir\*
        op_mode = MODE_WILD_ANY
        op_wild_ext = ''
        op_root = match[1] or '.'
    elif match := re.match(r'(.*(\\|/)?)\*\.([a-zA-Z]+)$', filename):      # dir\*.py check and get extension
        op_mode = MODE_WILD_EXT
        op_wild_ext = match[3] or ''
        op_root = match[1] or '.'
    elif os.path.exists(filename) and os.path.isfile(filename):
        op_mode = MODE_FILE
        op_wild_ext = ''
        op_root = filename
    else:
        op_mode = MODE_UNK
    return op_mode


def process_files(path):
    if op_mode == MODE_FILE and not is_file_excluded(path):
        change_eol(path)
    else:
        for ff in glob.glob(os.path.join(path, '*')):
            print(f'\n{ff}', sep=' ', end='\t')

            if is_file_excluded(os.path.basename(ff)):
                print('[..skipped: excluded..]', sep=' ', end='')
                continue
            elif os.path.isfile(ff):
                if op_mode == MODE_WILD_EXT and not ff.endswith(f'.{op_wild_ext}'):
                    print(f'[..skipped: not *.{op_wild_ext}..]', end='')
                    continue
                change_eol(ff)
            elif os.path.isdir(ff):
                process_files(os.path.join(path, os.path.basename(ff)))


def is_dos_file_eol(filename):
    file_lines = 0
    dos_eols = 0
    last_filepos = 0
    try:
        f = open(filename, 'r', encoding='utf-8')
        for file_lines, _ in enumerate(f):
            pass
        f.close()
    except UnicodeDecodeError:
        f = open(filename, 'r')
        for file_lines, _ in enumerate(f):
            pass
        f.close()

    file_lines += 1

    with open(filename, 'r+b') as f:
        ff = mmap.mmap(f.fileno(), 0)
        while (last_filepos := ff.find(CRLF, last_filepos + 1)) != -1:
            dos_eols += 1
        ff.close()

    if (dos_eols == file_lines) or (dos_eols == file_lines - 1):
        return 1                # definetely yes (even if the last line without EOL)
    elif dos_eols == 0:
        return 0                # definetely no
    else:
        return -1               # mixed file


def change_eol(path):
    if is_file_binary(path):
        print('[..skipped: binary..]', end='')
    elif op_direction == 'unix2dos' and is_dos_file_eol(path) == 1:
        print('[..skipped: already DOS EOLs..]', end='')
    elif op_direction == 'dos2unix' and is_dos_file_eol(path) == 0:
        print('[..skipped: already non-DOS EOLs..]', end='')
    elif is_dos_file_eol(path) == -1:
        print('[..skipped: mixed file..]', end='')
    else:
        print('[..touched..]', end='')
        if op_direction == 'dos2unix':
            with open(path, 'rb') as f:
                text = f.read().replace(CRLF, LF)
            with open(path, 'wb') as f:
                f.write(text)
        elif op_direction == 'unix2dos':
            with open(path, 'rb') as f:
                text = f.read().replace(LF, CRLF)
            with open(path, 'wb') as f:
                f.write(text)
        else:
            sys.exit('Possible args can be dos2unix or unix2dos')


if our_mode(param_file) == MODE_UNK:
    sys.exit('File not found or you should set either wildcard or wildcard.extension')

print(f'DIRECTION: {op_direction}')

process_files(op_root)
