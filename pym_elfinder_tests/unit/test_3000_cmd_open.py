import unittest

from . import lib

class TestCmdOpen(unittest.TestCase):

    def setUp(self):
        self.finder = lib.create_finder()

    # Received on client initialization
    def test_open_init(self):
        fixt = lib.CMD_FIXT['cmd_open-init.txt'][0]
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

    
    # Received if client has a hash for root
    def TODO_test_open_init_target(self):
        pass
    
    # Received when client opens dir "some_dir"
    def TODO_test_open_some_dir(self):
        pass
