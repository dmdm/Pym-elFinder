# -*- coding: utf-8 -*-

"""
Helpers for the test suite.
"""

import os
from glob import glob
import anyjson as json

from pym_elfinder import Finder
from pym_elfinder.cache import Cache


FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
"""
Directory where we store our filesystem fixtures.
"""


# Default options for connector as taken from elFinder's PHP demo.
# These options were active to generate the command fixtures.
DEF_OPTS = dict(
    locale = 'en_US.UTF-8',
#    bind = dict(
#        # '*' = 'logger',
#        'mkdir mkfile rename duplicate upload rm paste' = 'logger'
#    ),
    debug = True,
    roots = [
        dict(
            id = "1", # ALWAYS DEFINE ID, otherwise we get errors with concurrency
            driver     = 'pym_elfinder.volume.localfilesystem',
                            # path to files (REQUIRED)
            path       = os.path.abspath(os.path.join(
                            os.path.dirname(__file__),
                            'fixtures', 'files')),
            #startPath  = '../files/test/',
            #URL        = dirname($_SERVER['PHP_SELF']) . '/../files/',
            # treeDeep   = 3,
            # alias      = 'File system',
            mimeDetect = 'internal',
            #tmbPath    = '.tmb',
            utf8fix    = True,
            #tmbCrop    = False,
            #tmbBgColor = 'transparent',
            accessControl = 'access',
            acceptedName    = '/^[^\.].*$/',
            # tmbSize = 128,
            attributes = [
                dict(
                    pattern = '/\.js$/',
                    read = True,
                    write = False
                ),
                dict(
                    pattern = '/^\/icons$/',
                    read = True,
                    write = False
                ),
                dict(
                    pattern = '/^[^.].*$/',
                    read = True,
                    write = True
                )
            ]
            # uploadDeny = dict('application', 'text/xml')
        ),
###        dict(
###            driver     = 'LocalFileSystem',
###            path       = '../files2/',
###            # URL        = dirname($_SERVER['PHP_SELF']) . '/../files2/',
###            alias      = 'File system',
###            mimeDetect = 'internal',
###            tmbPath    = '.tmb',
###            utf8fix    = True,
###            tmbCrop    = False,
###            startPath  = '../files/test',
###            # separator = ':',
###            attributes = list(
###                dict(
###                    pattern = '~/\.~',
###                    # pattern = '/^\/\./',
###                    read = False,
###                    write = False,
###                    hidden = True,
###                    locked = False
###                ),
###                dict(
###                    pattern = '~/replace/.+png$~',
###                    # pattern = '/^\/\./',
###                    read = False,
###                    write = False,
###                    # hidden = True,
###                    locked = True
###                )
###            ),
###            # defaults = dict(read = False, write = True)
###        ),
        
        # dict(
        #     driver = 'FTP',
        #     host = '192.168.1.38',
        #     user = 'dio',
        #     pass = 'hane',
        #     path = '/Users/dio/Documents',
        #     tmpPath = '../files/ftp',
        #     utf8fix = True,
        #     attributes = list(
        #         dict(
        #             pattern = '~/\.~',
        #             read = False,
        #             write = False,
        #             hidden = True,
        #             locked = False
        #         ),
        #         
        #     )
        # ),
        # dict(
        #     driver = 'FTP',
        #     host = 'work.std42.ru',
        #     user = 'dio',
        #     pass = 'wallrus',
        #     path = '/',
        #     tmpPath = '../files/ftp',
        # ),
        # dict(
        #     driver = 'FTP',
        #     host = '10.0.1.3',
        #     user = 'frontrow',
        #     pass = 'frontrow',
        #     path = '/',
        #     tmpPath = '../files/ftp',
        # ),
        
        # dict(
        #     driver     = 'LocalFileSystem',
        #     path       = '../files2/',
        #     URL        = dirname($_SERVER['PHP_SELF']) . '/../files2/',
        #     alias      = 'Files',
        #     mimeDetect = 'internal',
        #     tmbPath    = '.tmb',
        #     # copyOverwrite = False,
        #     utf8fix    = True,
        #     attributes = list(
        #         dict(
        #             pattern = '~/\.~',
        #             # pattern = '/^\/\./',
        #             # read = False,
        #             # write = False,
        #             hidden = True,
        #             locked = False
        #         ),
        #     )
        # ),
        
###        dict(
###            driver = 'MySQL',
###            path = 1,
###            # treeDeep = 2,
###            # socket          = '/opt/local/var/run/mysql5/mysqld.sock',
###            user = 'root',
###            pass = 'hane',
###            db = 'elfinder',
###            user_id = 1,
###            # accessControl = 'access',
###            # separator = ':',
###            tmbCrop         = True,
###            # thumbnails background color (hex #rrggbb or 'transparent')
###            tmbBgColor      = '#000000',
###            files_table = 'elfinder_file',
###            # imgLib = 'imagick',
###            # uploadOverwrite = False,
###            # copyTo = False,
###            # URL    = 'http:#localhost/git/elfinder',
###            tmpPath = '../filesdb/tmp',
###            tmbPath = '../filesdb/tmb',
###            tmbURL = dirname($_SERVER['PHP_SELF']) . '/../filesdb/tmb/',
###            # attributes = [
###            #     dict(),
###            #     dict(
###            #         pattern = '/\.jpg$/',
###            #         read = False,
###            #         write = False,
###            #         locked = True,
###            #         hidden = True
###            #     )
###            # ]
###            
###        )
    ]
        
)
"""
Default options for connector as taken from elFinder's PHP demo.

These options were active to generate the command fixtures.
"""

DUMMY_CACHE_DATA = {}
dummy_cache = Cache(DUMMY_CACHE_DATA)


def create_finder(opts=None):
    """
    Creates finder instance for tests and mounts all volumes.
    """
    if not opts:
        opts = DEF_OPTS
    finder = Finder(opts, cache=dummy_cache)
    finder.debug = True
    finder.mount_volumes()
    return finder


def diff_dicts(a, b):
    """
    Returns a visually pleasant diff of two dicts.
    """
    fmt = "!! {ka:10} = {va:20} -> {kb:10} = {vb:20}"
    diffs = []

    ka = set(a.keys())
    kb = set(b.keys())

    for k in (ka - kb):
        diffs.append(fmt.format(ka=k, va=a[k], kb='?', vb='?'))
    for k in (kb - ka):
        diffs.append(fmt.format(kb=k, vb=b[k], ka='?', va='?'))

    for k in (ka & kb):
        if a[k] != b[k]:
            diffs.append(fmt.format(ka=k, va=a[k], kb=k, vb=b[k]))
    return "\n".join(diffs) if diffs else ''


def cmp_dicts(d1, d2, skip=None):
    """
    Returns 3 lists of 2-tuples with differences of 2 dicts.

    ``skip`` is an optional list of keys that shall not be compared.

    :returns: 3 lists of 2-tuples:
              
              1=items only in dict1, 2=items only in dict2,
              3=items in both, but different.
              
              Each 2-tuple is a key-value pair.
    """
    if skip is None:
        skip = []
    kk1 = set(d1.keys())
    kk2 = set(d2.keys())
    items1only = [ (k, d1[k]) for k in kk1 - kk2 if k not in skip ]
    items2only = [ (k, d2[k]) for k in kk2 - kk1 if k not in skip ]
    kk = kk1 & kk2
    itemsdiff = [ (k, d1[k], d2[k]) for k in kk if d1[k] != d2[k]
        if k not in skip ]
    return items1only, items2only, itemsdiff


def load_cmd_fixtures():
    """Loads fixtures for commands

    Fixtures for commands are the URL parameters of the request and the
    response body (JSON).

    A command may trigger several more requests/responses. The resulting data
    structure is:

        {
            command1 : [
                {
                    request : { }
                    response : { }
                }
                , {
                    request : { }
                    response : { }
                }
                , ...
            ]
            , command2 : [
                ...
            ]
            ...
        }

    """
    pat = os.path.join(FIXTURES_DIR, 'cmd_*.txt')
    files = glob(pat)
    fixt = {}
    for fn in files:
        item = {}
        req = {}
        resp = None
        in_content = False
        with open(fn, 'r', encoding='utf-8') as fh:
            for ln in fh:
                ln = ln.strip()
                # Ignore empty lines and comments
                if not in_content and (len(ln) == 0 or ln.startswith('#')):
                    continue
                # Line starting with "{" denotes the JSON of the response
                # (Make sure, parameter "content" does not contain such a line!)
                if ln.startswith('{'):
                    in_content = False
                    # Remove the last blank line from content. It was just the
                    # spacing between content and JSON
                    if "content" in req:
                        if len(req["content"][-1].strip()) == 0:
                            del req["content"][-1]
                        req['content'] = "\n".join(req['content'])
                    # Process JSON response and store request and response
                    resp = json.loads(ln)
                    item['request'] = req
                    item['response'] = resp
                    bn = os.path.basename(fn)
                    if bn not in fixt:
                        fixt[bn] = [item]
                    else:
                        fixt[bn].append(item)
                    # Start new command in case file has more than one
                    item = {}
                    req = {}
                    resp = None
                elif in_content:
                    req["content"].append(ln)
                else:
                    k, v = ln.split('=', 1)
                    # Parameter "content" may have multiple unquoted lines.
                    # "content" must be the last parameter in fixture. It is
                    # ended only by the JSON line!
                    if k == "content":
                        in_content = True
                        req[k] = [ v ]
                    else:
                        # Parameters that allow multiple values end with "[]"
                        # These become lists.
                        if k.endswith("[]"):
                            k = k.rstrip("[]")
                            try:
                                req[k].append(v)
                            except KeyError:
                                req[k] = [ v ]
                        # Scalar parameters
                        else:
                            req[k] = v

    return fixt


CMD_FIXT = load_cmd_fixtures()
"""
"Constant" of loaded command fixtures.

See :meth:`load_cmd_fixtures()` for details.
"""


def prepare_request(req):
    """Returns cmd and args

    Input URL parameters as dict, like you may fetch a live request from
    e.g. WebOb.params.

    We return a 2-tuple: 0 -> command, 1 -> dict with cmd's args.

    elFinder client allows to send arbitrary user-defined parameters.
    An application must remove them (e.g. in a view), as we do here.
    """
    args = req.copy()
    try:
        cmd = args['cmd']
        del args['cmd']
    except KeyError:
        cmd = ''
    
    try:
        del args['_']
        # This parameter is set by the PHP demo of elFinder
        del args['answer']
    except KeyError:
        pass

    return (cmd, args)


def prepare_response(resp0, resp, lvl=0, debug=False, remove_these=None, take_these=None):
    """Processes response for keys that are allowed to be different.

    E.g. ``ts`` is the item modification time. If current response and
    fixture differ here, it is ok.

    The response is modified in-place, so no return value.

    :param resp0: The reference response
    :param resp:  The response to be modified
    :param lvl: Internal
    :param debug: If True, prints out each processed key and depth
    :param remove_these: List of keys to be removed from response
    :param take_these: List of keys whose values are copied from reference resp0
                       to response resp.
    """
    if remove_these is None:
        remove_these = []
    if take_these is None:
        take_these = ['ts']
    ind = '..'*lvl

    def key(it):
        try:
            return it['hash']
        except KeyError:
            return str(it['ts'])

    for k in remove_these:
        if k in resp:
            if debug:
                print(ind, "++ Removing", k)
            del resp[k]

    for k in take_these:
        if k in resp:
            if debug:
                print(ind, "++ Taking", k)
            resp[k] = resp0[k]

    for k, v in resp.items():
        if debug:
            print(ind, "++ Processing", k, type(v))
        if isinstance(v, dict):
            if debug:
                print(ind, "  -- {0} is dict => recurse".format(k))
            try:
                prepare_response(v, resp0[k], lvl=lvl+1, debug=debug,
                    remove_these=remove_these, take_these=take_these)
            except IndexError:
                # If resp0 does not have this item, use current resp item
                # instead (i.e. its value and children stay as-is)
                prepare_response(v, v, lvl=lvl+1, debug=debug)
        elif isinstance(v, (list, set, tuple)):
            if debug:
                print(ind, "  -- {0} is list".format(k))
            for i, it in enumerate(v):
                if debug:
                    print(ind, "    -- [{0}] is dict => recurse".format(i))
                if isinstance(it, dict):
                    try:
                        prepare_response(it, resp0[k][i], lvl=lvl+2, debug=debug,
                            remove_these=remove_these, take_these=take_these)
                    except IndexError:
                        # If resp0 does not have this item, use current resp item
                        # instead (i.e. its value and children stay as-is)
                        prepare_response(it, it, lvl=lvl+2, debug=debug,
                            remove_these=remove_these, take_these=take_these)


def print_types(d, lvl=0):
    """
    Walks a nested data structure and for each key/level prints out the value's
    type.
    """
    ind = lvl * '..'
    if isinstance(d, (list, set, tuple)):
        print(ind, ': is list')
        for i, it in enumerate(d):
            print(ind, "[{0}]".format(i), type(it))
            if isinstance(it, dict):
                print_types(it, lvl+1)
    elif isinstance(d, dict):
        print(ind, ': is dict')
        for k, v in d.items():
            print(ind, k, type(v))
    else:
        print(ind, ': is scalar', type(v))


if __name__ == '__main__':
    
    from pprint import pprint
    
    pprint(CMD_FIXT)

