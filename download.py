#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, division
import argparse
import json
import sys
import os
from os.path import join

import subprocess
import zipfile
try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen

__author__ = 'Fisher Yu'
__email__ = 'fy@cs.princeton.edu'
__license__ = 'MIT'

OBJECT_LIST_PATH = 'objects_category_indices.txt'
SCENE_LIST_PATH  = 'scenes_category_indices.txt'

with open(OBJECT_LIST_PATH) as f:
    o_list = [i.split(' ')[0] for i in f.read().splitlines()]
with open(SCENE_LIST_PATH) as f:
    s_list = [i.split(' ')[0] for i in f.read().splitlines()]

#--------------------------------------------------------------------------------------------------------------------------------
def s_list_categories(tag):
    url = 'http://lsun.cs.princeton.edu/htbin/list.cgi?tag=' + tag
    f = urlopen(url)
    return json.loads(f.read())


def s_download(out_dir, category, set_name, tag):
    url = 'http://lsun.cs.princeton.edu/htbin/download.cgi?tag={tag}' \
          '&category={category}&set={set_name}'.format(**locals())
    if set_name == 'test':
        out_name = 'test_lmdb.zip'
    else:
        out_name = '{category}_{set_name}_lmdb.zip'.format(**locals())
    out_path = join(out_dir, out_name)
    cmd = ['curl', url, '-o', out_path]
    print('Downloading', category, set_name, 'set')
    subprocess.call(cmd)

def o_download(out_dir, category):
    url = 'http://tigress-web.princeton.edu/~fy/lsun/public/release/{}.zip'.format(category)
    out_name = str(category) + '.zip'
    out_path = join(out_dir, out_name)
    cmd = ['curl', url, '-o', out_path]
    print('Downloading', category)
    subprocess.call(cmd)
    with zipfile.ZipFile(out_path,"r") as zip_ref:
        zip_ref.extractall(out_path.replace('.zip',''))
    os.remove(out_path)

#--------------------------------------------------------------------------------------------------------------------------------
def make_parser(argv):
    prog = argv[0]
    parser = argparse.ArgumentParser(
        prog        = prog,
        description = 'Tool for downloading 10 scenes / 20 objects of LSUN dataset. All links refer to http://www.yf.io/p/lsun',
        epilog      = 'Type "%(prog)s <command> -h" for more information.')

    subparsers = parser.add_subparsers(dest='command')
    subparsers.required = True
    def add_command(cmd, help, example=None):
        epilog = 'Example: %s %s' % (prog, example) if example is not None else None
        return subparsers.add_parser(cmd, description=help, help=help, epilog=epilog)

    command_parser = add_command('object',  'Download objects data of LSUN dataset. (NOTICE: object downloading usually spends a huge time)',
                                            'object -o 20_objects -c airplane')

    command_parser.add_argument('--out_dir',        default='20_objects',
                                                    help='output directory [%(default)s]')
    command_parser.add_argument('--category',       default=None, choices=o_list,
                                                    help='categories [%(default)s]')

    command_parser = add_command('scene',   'Download scenes data of LSUN dataset.',
                                            'scene -o 10_scenes -c bedroom')

    command_parser.add_argument('--tag',            type=str,  default='latest',
                                                    help='url tag [%(default)s]')
    command_parser.add_argument('--out_dir',        default='10_scenes',
                                                    help='output directory [%(default)s]')
    command_parser.add_argument('--category',       default=None, choices=s_list,
                                                    help='categories [%(default)s]')
    args = parser.parse_args()
    return args

#--------------------------------------------------------------------------------------------------------------------------------
def main(argv):
    args = make_parser(argv)

    if args.command == 'scene':
        categories = s_list_categories(args.tag)
        if args.category is None:
            print('Downloading', len(categories), 'categories')
            for category in categories:
                s_download(args.out_dir, category, 'train', args.tag)
                s_download(args.out_dir, category, 'val', args.tag)
            s_download(args.out_dir, '', 'test', args.tag)
        else:
            if args.category == 'test':
                s_download(args.out_dir, '', 'test', args.tag)
            elif args.category not in categories:
                print('Error:', args.category, "doesn't exist in",
                      args.tag, 'LSUN release')
            else:
                s_download(args.out_dir, args.category, 'train', args.tag)
                s_download(args.out_dir, args.category, 'val', args.tag)
    elif args.command == 'object':
        if args.category is None:
            input('Category name is empty. It\'s coming to download all data about LSUN objects.\nPress any key to continue...')
            print('Downloading', len(o_list), 'categories')
            for category in o_list:
                o_download(args.out_dir, category)
        else:
            o_download(args.out_dir, args.category)
    else:
        raise NameError("Unrecognized command '%s'" % args.command)



if __name__ == '__main__':
    main(sys.argv)
