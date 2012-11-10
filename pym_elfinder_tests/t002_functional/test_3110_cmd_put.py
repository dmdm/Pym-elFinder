import unittest
import os

from pprint import pprint

from .. import lib
from .. import lib_localfilesystem as lfs


class TestCmdPut(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.finder = lib.create_finder()
        cls.fixt = lib.CMD_FIXT['cmd_put-POST.txt']
        cls.src = os.path.join(lfs.DIR, 'sometextfile.txt')

    def setUp(self):
        lfs.mkfile(self.src, "Some contents.")

    def tearDown(self):
        os.remove(self.src)

    def test_put(self):
        """
        Test putting content in a text file
        """
        req = self.fixt[0]['request']
        r0 = self.fixt[0]['response'] # expected response
       
        cmd, args = lib.prepare_request(req)
        assert cmd == 'put'
        
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

