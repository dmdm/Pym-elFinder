import unittest
import os

from . import lib
from pym_elfinder.finder import Finder


class TestEncodePath(unittest.TestCase):

    def test_001(self):
        finder = Finder(lib.DEF_OPTS, cache=lib.dummy_cache)
        finder.mount_volumes()
        vol_id = list(finder.volumes.keys())[0]
        vol = finder.volumes[vol_id]
        # Must use abs path
        path = os.path.join(lib.DEF_OPTS['roots'][0]['path'], 'abc', 'äöü', 'xyz')
        hash_ = vol.encode(path)
        assert path == vol.decode(hash_)
