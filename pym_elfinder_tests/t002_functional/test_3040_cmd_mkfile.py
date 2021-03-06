import unittest
import os

from pprint import pprint

from .. import lib


# We create and test new items in this dir
DIR = os.path.join(lib.FIXTURES_DIR, 'files', 'some_dir')


class TestCmdMkFile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.finder = lib.create_finder()
        cls.fixt = lib.CMD_FIXT['cmd_mkfile.txt'][0]

    def test_mkfile(self):
        req = self.fixt['request']
        r0 = self.fixt['response'] # expected response
        new_path = os.path.join(DIR, req['name'])
       
        # Make sure, the to be created file does not exist
        try:
            os.remove(new_path)
        except OSError:
            pass # assume exception was raised because new_path does not exist

        cmd, args = lib.prepare_request(req)
        assert cmd == 'mkfile'
        
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

        # Cleanup: remove the new file
        # If remove() fails, our mkfile() returned the correct response but
        # did not create the file correctly.
        os.remove(new_path)
