import unittest

from .. import lib

from pprint import pprint


class TestCmdTree(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.finder = lib.create_finder()
        cls.fixt = lib.CMD_FIXT['cmd_tree.txt']

    def test_tree_from_root(self):
        fixt = self.fixt[0]
        r0 = fixt['response'] # expected response
        
        cmd, args = lib.prepare_request(fixt['request'])
        assert cmd == 'tree'
        
        # This throws exception on error
        self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        #pprint(r); raise Exception("DIE")
        #pprint(r0); raise Exception("DIE")
        lib.prepare_response(r0, r)

        self.assertEqual(r0.keys(), r.keys())
        self.maxDiff = None
        self.assertEqual(r0['tree'], r['tree'])

    def test_tree_from_some_dir(self):
        fixt = self.fixt[1]
        r0 = fixt['response'] # expected response
        
        cmd, args = lib.prepare_request(fixt['request'])
        self.assertEqual(cmd, 'tree')
        
        # This throws exception on error
        self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        #pprint(r); raise Exception("DIE")
        #pprint(r0); raise Exception("DIE")
        lib.prepare_response(r0, r)

        self.assertEqual(r0.keys(), r.keys())
        self.maxDiff = None
        self.assertEqual(r0['tree'], r['tree'])
