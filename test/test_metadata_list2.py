"""
test class ErrorReports in metadata_check_reports
"""

import unittest
import lib


def s_output(s_icons: str) -> str:
    """ create result for comparison """
    return '<span style="font-family:FontAwesome;">' + s_icons + '</span>'


class TestMetadataList2(unittest.TestCase):
    """
    test class
    """

    def test_ok_case(self):
        """
        standard, ok case
        """
        result = lib.s_icons([])
        self.assertEqual(result, '')

        result = lib.s_icons(['#other'])
        self.assertEqual(result, '')

        result = lib.s_icons(['#video'])
        self.assertEqual(result, s_output('&#xf03d;&nbsp;'))

        result = lib.s_icons(['#audio'])
        self.assertEqual(result, s_output('&#xf130;&nbsp;'))

        result = lib.s_icons(['#paywall'])
        self.assertEqual(result, s_output('&#xf023;&nbsp;'))

        result = lib.s_icons(['#other', '#paywall'])
        self.assertEqual(result, s_output('&#xf023;&nbsp;'))

        result = lib.s_icons(['#video', '#paywall'])
        self.assertEqual(result, s_output('&#xf03d;&nbsp;&#xf023;&nbsp;'))

        result = lib.s_icons(['#audio', '#paywall'])
        self.assertEqual(result, s_output('&#xf130;&nbsp;&#xf023;&nbsp;'))


if __name__ == '__main__':
    unittest.main()
