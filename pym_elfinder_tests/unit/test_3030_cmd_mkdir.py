import unittest

from . import lib


class TestCmdMkDir(unittest.TestCase):

    def setUp(self):
        self.finder = lib.create_finder()

    # Received on client initialization
    def test_mkdir(self):
        fixt = lib.CMD_FIXT['cmd_mkdir.txt'][0]
        r0 = fixt['response'] # expected response
        
        cmd, args = lib.prepare_request(fixt['request'])
        assert cmd == 'mkdir'
        
        # This throws exception on error
        self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        #pprint(r); raise Exception("DIE")
        #pprint(r0); raise Exception("DIE")
        lib.prepare_response(r0, r)

        self.assertEqual(r0.keys(), r.keys())
        self.maxDiff = None
        self.assertEqual(r0, r)
