import unittest

from .. import lib

from pprint import pprint

class TestCmdOpen(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.finder = lib.create_finder()
        cls.fixt = lib.CMD_FIXT['cmd_open.txt']

    def setUp(self):
        # We create some items in dir "some_dir" here, so make sure the
        # response fixtures for "some_dir" has "dirs":1.
        #lfs.create_src_items(lfs.SOURCE_ITEMS, lfs.DIR)
        pass

    def tearDown(self):
        #lfs.unlink_src_items(lfs.SOURCE_ITEMS, lfs.DIR)
        pass

    # Received on client initialization
    def test_open_init(self):
        fixt = self.fixt[0]
        r0 = fixt['response'] # expected response
        
        cmd, args = lib.prepare_request(fixt['request'])
        assert cmd == 'open'
        
        # This throws exception on error
        self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        #pprint(r); raise Exception("DIE")
        #pprint(r0); raise Exception("DIE")

        lib.prepare_response(r0, r, take_these=['ts', 'mime'])

        assert len(r['debug']['mountErrors']) == 0
        
        for i, it in enumerate(r['files']):
            a0 = r0['files'][i]
            a  = r['files'][i]
            self.assertEqual(a0, a,
                msg="\n[{i}] {msg}\nCOMMAND: {cmd} {args}".format(
                i=i, msg=lib.diff_dicts(a0, a), cmd=cmd, args=args))

    
    def test_open_init_target(self):
        fixt = self.fixt[1]
        r0 = fixt['response'] # expected response
        
        cmd, args = lib.prepare_request(fixt['request'])
        assert cmd == 'open'
        
        # This throws exception on error
        self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        #pprint(r); raise Exception("DIE")
        #pprint(r0); raise Exception("DIE")

        lib.prepare_response(r0, r, take_these=['ts', 'mime'])

        assert len(r['debug']['mountErrors']) == 0
        
        for i, it in enumerate(r['files']):
            a0 = r0['files'][i]
            a  = r['files'][i]
            self.assertEqual(a0, a,
                msg="\n[{i}] {msg}\nCOMMAND: {cmd} {args}".format(
                i=i, msg=lib.diff_dicts(a0, a), cmd=cmd, args=args))
    
    
    def test_open_some_dir(self):
        fixt = self.fixt[2]
        r0 = fixt['response'] # expected response
        
        cmd, args = lib.prepare_request(fixt['request'])
        assert cmd == 'open'
        
        # This throws exception on error
        self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        #pprint(r); raise Exception("DIE")
        #pprint(r0); raise Exception("DIE")

        lib.prepare_response(r0, r, take_these=['ts', 'mime'])

        assert len(r['debug']['mountErrors']) == 0
        
        for i, it in enumerate(r['files']):
            a0 = r0['files'][i]
            a  = r['files'][i]
            self.assertEqual(a0, a,
                msg="\n[{i}] {msg}\nCOMMAND: {cmd} {args}".format(
                i=i, msg=lib.diff_dicts(a0, a), cmd=cmd, args=args))
    
    
    def test_open_some_dir_on_reload(self):
        fixt = self.fixt[3]
        r0 = fixt['response'] # expected response
        
        cmd, args = lib.prepare_request(fixt['request'])
        assert cmd == 'open'
        
        # This throws exception on error
        self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        #pprint(r); raise Exception("DIE")
        #pprint(r0); raise Exception("DIE")

        lib.prepare_response(r0, r, take_these=['ts', 'mime'])

        assert len(r['debug']['mountErrors']) == 0
        
        for i, it in enumerate(r['files']):
            a0 = r0['files'][i]
            a  = r['files'][i]
            self.assertEqual(a0, a,
                msg="\n[{i}] {msg}\nCOMMAND: {cmd} {args}".format(
                i=i, msg=lib.diff_dicts(a0, a), cmd=cmd, args=args))

