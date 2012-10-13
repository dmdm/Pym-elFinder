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
        cls.fixt = lib.CMD_FIXT['cmd_rm.txt']
        cls.file_1 = os.path.join(lfs.DIR, 'file_1.txt')
        cls.file_2 = os.path.join(lfs.DIR, 'file_2.txt')
        cls.dir_1 = os.path.join(lfs.DIR, 'dir_1')
        cls.file_1_1 = os.path.join(lfs.DIR, 'dir_1', 'file_1_1.txt')

    def test_rm_files(self):
        """
        Test removal of file_1 and file_2.
        """
        lfs.mkfile(self.file_1)
        lfs.mkfile(self.file_2)
        
        req = self.fixt[0]['request']
        r0 = self.fixt[0]['response'] # expected response
       
        cmd, args = lib.prepare_request(req)
        assert cmd == 'rm'
        
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

    def test_rm_non_empty_dir(self):
        """
        Test removal of dir_1
        """
        os.mkdir(self.dir_1)
        lfs.mkfile(self.file_1_1)
        
        req = self.fixt[1]['request']
       
        cmd, args = lib.prepare_request(req)
        assert cmd == 'rm'
        
        with self.assertRaisesRegexp(exc.FinderError, exc.ERROR_RM):
            self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        self.assertTrue('error' in r)
        self.assertEqual(r['error'][0], exc.ERROR_RM)
        
        os.remove(self.file_1_1)
        os.rmdir(self.dir_1)

