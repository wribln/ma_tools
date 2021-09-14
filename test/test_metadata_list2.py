"""
test class ErrorReports in metadata_check_reports
"""

import unittest
import lib

def s_output(s_icons: str) -> str:
    return '<span style="font-family:FontAwesome;">' + s_icons + '</span>'

class TestMetadataList2(unittest.TestCase):
    """
    test class
    """

    def test_ok_case(self):
        """
        standard, ok case
        """
        r = lib.s_icons('', False)
        self.assertEqual(r, '')

        r = lib.s_icons('other', False)
        self.assertEqual(r, '')

        r = lib.s_icons('video', False)
        self.assertEqual(r, s_output('&#xf03d;&nbsp;'))

        r = lib.s_icons('audio', False)
        self.assertEqual(r, s_output('&#xf130;&nbsp;'))

        r = lib.s_icons('', True)
        self.assertEqual(r, s_output('&#xf023;&nbsp;'))

        r = lib.s_icons('other', True)
        self.assertEqual(r, s_output('&#xf023;&nbsp;'))

        r = lib.s_icons('video', True)
        self.assertEqual(r, s_output('&#xf023;&nbsp;&#xf03d;&nbsp;'))

        r = lib.s_icons('audio', True)
        self.assertEqual(r, s_output('&#xf023;&nbsp;&#xf130;&nbsp;'))


if __name__ == '__main__':
    unittest.main()
