import unittest

from pym_elfinder.exceptions import FinderError

class TestExceptions(unittest.TestCase):

    def test_001(self):
        e = FinderError("Some elFinder Error", "FOO", bar="BAR")
        s = str(e)
        self.assertEqual("FinderError('Some elFinder Error', 'FOO', 'bar': 'BAR')", s)
        self.assertEqual("BAR", e.bar)
