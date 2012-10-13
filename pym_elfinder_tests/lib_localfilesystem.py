# -*- coding: utf-8 -*-

"""
Helpers for the local filesystem test suite.
"""

import os
import errno
from . import lib

if not os.path.exists(lib.FIXTURES_DIR):
    raise Exception("FIXTURES_DIR does not exist: " + lib.FIXTURES_DIR)
DIR = os.path.join(lib.FIXTURES_DIR, 'files', 'some_dir')
"""
Create and test new items in this directory.
"""

SOURCE_ITEMS = {
    'file_1.txt' : 1,
    'file_2.txt' : 1,
    'dir_1'  : {
        'file_1_1.txt' : 1,
        'file_1_2.txt' : 1,
        'dir_1_1' : {
            'file_1_1_1.txt' : 1,
            'file_1_1_2.txt' : 1,
        }
    },
}
"""
These fixtures will be dynamically created. Used to test commands paste-copy
and paste-move.
"""

def mkfile(fn):
    if os.path.exists(fn):
        raise Exception("mkfile failed, file exists: '{0}'".format(fn))
    open(fn, "w").close()

def create_src_items(twig, dir_):
    """
    Creates fixtures from SOURCE_ITEMS.

    Call with SOURCE_ITEMS and start dir; calls itself recursively to
    create complete fixture tree.
    """
    for name, x in twig.items():
        fullname = os.path.join(dir_, name)
        if isinstance(x, dict):
            try:
                os.mkdir(fullname)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
            create_src_items(x, fullname)
        else:
            with open(fullname, "w") as fh:
                fh.write("File " + name)

def create_dst_dir():
    """
    Creates a directory as destination vor paste-copy and paste-move.
    """
    path = os.path.join(DIR, "tmpdstdir")
    try:
        os.mkdir(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    return path

def unlink_dst_items(twig, dir_):
    """
    Removes copied/moved items from destination directory.
    
    Call with SOURCE_ITEMS and start dir; calls itself recursively to
    remove complete fixture tree.
    """
    for name, x in twig.items():
        fullname = os.path.join(dir_, name)
        if isinstance(x, dict):
            unlink_dst_items(x, fullname)
            try:
                os.rmdir(fullname)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise
        else:
            try:
                os.remove(fullname)
            except OSError as e:
                if e.errno != errno.ENOENT:
                    raise

def unlink_src_items(twig, dir_):
    """
    Removes source items from source directory.
    
    Call with SOURCE_ITEMS and start dir; calls itself recursively to
    remove complete fixture tree.
    """
    # Yep, we can use the same mechanics as for removing dst items.
    # Only the start dir is different, but this lies in caller's
    # responsibility.
    unlink_dst_items(twig, dir_)

def unlink_dst_dir(dir_):
    """
    Removes destination directory; must be empty.
    """
    try:
        os.rmdir(dir_)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise

def check_src_gone(tc, twig, dir_):
    """
    Checks that the complete tree which is used as source for move is gone.

    Call with reference to test-case, SOURCE_ITEMS and start dir; calls
    itself recursively to check whole tree.
    """
    for name, x in twig.items():
        fullname = os.path.join(dir_, name)
        tc.assertFalse(os.path.exists(fullname),
            msg="Src still exists: '{0}'".format(fullname))
        if isinstance(x, dict):
            check_src_gone(tc, x, fullname)

def check_dst_exists(tc, twig, dir_):
    """
    Checks that the complete tree at destination of copy/move exists.

    Call with reference to test-case, SOURCE_ITEMS and start dir; calls
    itself recursively to check whole tree.
    """
    for name, x in twig.items():
        fullname = os.path.join(dir_, name)
        tc.assertTrue(os.path.exists(fullname), 
            msg="Dst does not exist: '{0}'".format(fullname))
        if isinstance(x, dict):
            check_dst_exists(tc, x, fullname)

def check_src_exists(tc, twig, dir_):
    """
    Checks that the complete tree at source of copy exists.

    Call with reference to test-case, SOURCE_ITEMS and start dir; calls
    itself recursively to check whole tree.
    """
    for name, x in twig.items():
        fullname = os.path.join(dir_, name)
        tc.assertTrue(os.path.exists(fullname), 
            msg="Src does not exist: '{0}'".format(fullname))
        if isinstance(x, dict):
            check_dst_exists(tc, x, fullname)
