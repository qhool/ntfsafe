#!/usr/bin/env python

import argparse
import os
import stat
import pwd
import grp
import shutil
import sys
import zlib

MAX_LEN=255 #NTFS file names are a maximum of 255 *characters*
LONGFILE_EXT = '.LONG'
VERBOSE = False

def truncate(s, max_len=MAX_LEN):
    if len(s) > max_len:
        return (s[:max_len], True)
    else:
        return (s, False)

def perm_str(path):
    stat = os.stat(path)
    owner = pwd.getpwuid(stat.st_uid).pw_name
    group = grp.getgrgid(stat.st_gid).gr_name
    return f'{stat.st_mode}.{owner}.{group}'

def safe_filename(dest,dir,filename):
    base, ext = os.path.splitext(filename)
    pattern = f'{zlib.crc32(bytes(filename,'utf-8')):08x}'
    tail = f'--{pattern}.{perm_str(os.path.join(dir,filename))}{ext}'
    len_lim = MAX_LEN - len(tail)
    longfile = None
    if len(base) > len_lim:
        max = len_lim - len(LONGFILE_EXT)
        base = base[:max]
        longfile = os.path.join(dest,f'{base}{tail}{LONGFILE_EXT}')
    return os.path.join(dest,f'{base}{tail}'), longfile
        
def make_safe_file(dest,root,name):
    path = os.path.join(root,name)
    safe, long = safe_filename(dest,root,name)
    if not os.path.lexists(safe):
        if os.path.isdir(path):
            if VERBOSE:
                print(f"DIR: {safe}",file=sys.stderr)
            os.mkdir(safe)
        else:
            if VERBOSE:
                print(f"LINK: {safe}",file=sys.stderr)
            os.symlink(path, safe)
        if long is not None:
            if VERBOSE:
                print(f"LONG: {long}",file=sys.stderr)
            with open(long, 'w') as lf: lf.write(name)
    return safe, long

def build_symtree(source, dest):
    created = set()
    for name in os.listdir(source):
        safe, long = make_safe_file(dest, source, name)
        created.add(safe)
        created.add(long)
        if os.path.isdir(safe):
            build_symtree(os.path.join(source,name),safe)
    for name in os.listdir(dest):
        path = os.path.join(dest,name)
        if path not in created:
            if os.path.isdir(path):
                if VERBOSE:
                    print(f"RMDIR: {path}",file=sys.stderr)
                shutil.rmtree(path)
            else:
                if VERBOSE:
                    print(f"RM: {path}",file=sys.stderr)
                os.remove(path)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some directories.')
    parser.add_argument('-v', '--verbose', action='store_true', help='increase output verbosity')
    parser.add_argument('source', type=str, help='the source directory')
    parser.add_argument('dest', type=str, help='destination for symlink tree')

    args = parser.parse_args()

    if args.verbose:
        VERBOSE = True

    if not os.path.isdir(args.source):
        print(f"Error: '{args.source}' is not a directory or does not exist.")
        sys.exit(1)
    if not os.path.isdir(args.dest):
        print(f"Error: '{args.dest}' is not a directory or does not exist.")
        sys.exit(1)
 
    build_symtree(os.path.abspath(args.source),os.path.abspath(args.dest))