import unittest
import os

from .. import lib
from pym_elfinder.finder import Finder


def touch(fn):
    if os.path.exists(fn):
        raise Exception("Failed to touch: file exists: " + fn)
    open(fn, "w").close()


class TestUniqueName(unittest.TestCase):

    def test_001(self):
        finder = Finder(lib.DEF_OPTS, cache=lib.dummy_cache)
        finder.mount_volumes()
        vol = finder.default_volume
        basename = "foo"
        ext = ".txt"
        path = os.path.join(lib.FIXTURES_DIR, 'files', 'some_dir')
        orig_fn = os.path.join(path, basename + ext)
        # create original file of which we want to create unique names 
        touch(orig_fn)

        for i in range(1, 3):
            unique = vol.unique_name(path, basename+ext)
            self.assertEqual(unique, "{0} (copy {1}){2}".format(
                basename, i, ext))
            touch(os.path.join(path, unique))

        # Cleanup: remove original file and copies
        os.remove(orig_fn)
        for i in range(1, 3):
            os.remove(os.path.join(path,"{0} (copy {1}){2}".format(
                basename, i, ext))) 
