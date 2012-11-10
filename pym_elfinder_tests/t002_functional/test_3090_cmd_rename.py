import unittest
import os

from pprint import pprint

import pym_elfinder.exceptions as exc
from .. import lib
from .. import lib_localfilesystem as lfs


class TestCmdRm(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.finder = lib.create_finder()
        cls.fixt = lib.CMD_FIXT['cmd_rename.txt']
        cls.src   = os.path.join(lfs.DIR, 'deeper2-foo.txt')
        cls.dst_1 = os.path.join(lfs.DIR, 'deeper2-bar.txt')
        cls.dst_2 = os.path.join(lfs.DIR, 'deeper2.txt')

    def setUp(self):
        lfs.mkfile(self.src)

    def tearDown(self):
        try:
            os.remove(self.src)
        except OSError:
            pass
        try:
            os.remove(self.dst_1)
        except OSError:
            pass

    def test_rename(self):
        """
        Test renaming
        """
        req = self.fixt[0]['request']
        r0 = self.fixt[0]['response'] # expected response
       
        cmd, args = lib.prepare_request(req)
        assert cmd == 'rename'
        
        # This throws exception on error
        self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        #pprint(r); raise Exception("DIE")
        #pprint(r0); raise Exception("DIE")
        lib.prepare_response(r0, r)

        self.assertEqual(r0.keys(), r.keys())
        del r0['debug']
        del r['debug']
        self.maxDiff = None
        self.assertEqual(r0, r)

    def test_rename_to_existing(self):
        """
        Test renaming to existing
        """
        req = self.fixt[1]['request']
       
        cmd, args = lib.prepare_request(req)
        assert cmd == 'rename'
        
        with self.assertRaisesRegexp(exc.FinderError, exc.ERROR_EXISTS):
            self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        self.assertTrue('error' in r)
        self.assertEqual(r['error'][0], exc.ERROR_EXISTS)

