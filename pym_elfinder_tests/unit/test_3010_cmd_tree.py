import unittest

from . import lib


class TestCmdTree(unittest.TestCase):

    def setUp(self):
        self.finder = lib.create_finder()

    # Received on client initialization
    def test_tree(self):
        fixt = lib.CMD_FIXT['cmd_tree.txt'][0]
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
