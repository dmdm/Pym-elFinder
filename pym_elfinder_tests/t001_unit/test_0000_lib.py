import unittest

from .. import lib

# Make sure, our test lib is correct ;)

class TestLib(unittest.TestCase):

    def test_000_prepare_request(self):
        url_param = dict(cmd='doit', arg1='foo', arg2=12, arg3=True,
            _='341234', answer=42)
        args0 = dict(arg1='foo', arg2=12, arg3=True)
        cmd, args = lib.prepare_request(url_param)
        assert cmd == 'doit'
        self.assertEqual(args0, args, msg="\n"+lib.diff_dicts(args0, args))

    def test_001_prepare_response(self):
        r0 = dict(
            v0 = 12,
            ts = 'master_ts',
            v1 = dict(
                v10 = 33,
                ts = 'master_ts',
                v11 = [
                        dict(
                            v110 = 99,
                            v111 = 'foo',
                            ts = 'master_ts'
                        ),
                        dict(
                            v112 = 77,
                            v113 = 'bar'
                        )
                    ]
                )
            )
        r = dict(
            v0 = 12,
            ts = 'ts',
            v1 = dict(
                v10 = 33,
                ts = 'ts',
                v11 = [
                        dict(
                            v110 = 99,
                            v111 = 'foo',
                            ts = 'ts'
                        ),
                        dict(
                            v112 = 77,
                            v113 = 'bar'
                        )
                    ]
                )
            )
        lib.prepare_response(r, r0)
        self.assertEqual(r0, r, msg="\n"+lib.diff_dicts(r0, r))
