import unittest

import os

from .. import lib


class TestCmdDuplicate(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.finder = lib.create_finder()
        cls.fixt = lib.CMD_FIXT['cmd_duplicate.txt']
        cls.dir_ = os.path.join(lib.FIXTURES_DIR, 'files', 'some_dir')

    @classmethod
    def tearDownClass(cls):
        # from dup 1
        fn = os.path.join(cls.dir_, "deeper2 (copy 1).txt")
        os.remove(fn)
        fn = os.path.join(cls.dir_, "image (copy 1).jpg")
        os.remove(fn)
        # from dup 2
        # "deeper2 (copy 2).txt" is removed within test method
        fn = os.path.join(cls.dir_, "image (copy 2).jpg")
        os.remove(fn)
        # from dup 3
        fn = os.path.join(cls.dir_, "deeper2 (copy 2).txt")
        os.remove(fn)
        fn = os.path.join(cls.dir_, "image (copy 3).jpg")
        os.remove(fn)

    def test_duplicate_1(self):
        n = 0

        r0 = self.fixt[n]['response'] # expected response
        
        cmd, args = lib.prepare_request(self.fixt[n]['request'])
        assert cmd == 'duplicate'
        
        # 1st duplication
        self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        #pprint(r); raise Exception("DIE")
        #pprint(r0); raise Exception("DIE")
        lib.prepare_response(r0, r)

        self.assertEqual(r0.keys(), r.keys())
        self.maxDiff = None
        self.assertEqual(r0['added'], r['added'])
        self.assertEqual(len(r0['added']), 2)

        fn1 = os.path.join(self.dir_, "deeper2 (copy 1).txt")
        fn2 = os.path.join(self.dir_, "image (copy 1).jpg")
        self.assertTrue(os.path.exists(fn1))
        self.assertTrue(os.path.exists(fn2))

    def test_duplicate_2(self):
        n = 1

        r0 = self.fixt[n]['response'] # expected response
        
        cmd, args = lib.prepare_request(self.fixt[n]['request'])
        assert cmd == 'duplicate'
        
        # 2nd duplication
        self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        #pprint(r); raise Exception("DIE")
        #pprint(r0); raise Exception("DIE")
        lib.prepare_response(r0, r)

        self.assertEqual(r0.keys(), r.keys())
        self.maxDiff = None
        self.assertEqual(r0['added'], r['added'])
        self.assertEqual(len(r0['added']), 2)

        fn1 = os.path.join(self.dir_, "deeper2 (copy 2).txt")
        fn2 = os.path.join(self.dir_, "image (copy 2).jpg")
        self.assertTrue(os.path.exists(fn1))
        self.assertTrue(os.path.exists(fn2))

        # Remove one copy
        os.remove(fn1)

    def test_duplicate_3(self):
        n = 2

        r0 = self.fixt[n]['response'] # expected response
        
        cmd, args = lib.prepare_request(self.fixt[n]['request'])
        assert cmd == 'duplicate'
        
        # 2nd duplication
        self.finder.run(cmd, args, debug=True)
        
        r = self.finder.response
        #pprint(r); raise Exception("DIE")
        #pprint(r0); raise Exception("DIE")
        lib.prepare_response(r0, r)

        self.assertEqual(r0.keys(), r.keys())
        self.maxDiff = None
        self.assertEqual(r0['added'], r['added'])
        self.assertEqual(len(r0['added']), 2)

        fn1 = os.path.join(self.dir_, "deeper2 (copy 2).txt")
        fn2 = os.path.join(self.dir_, "image (copy 3).jpg")
        self.assertTrue(os.path.exists(fn1))
        self.assertTrue(os.path.exists(fn2))
