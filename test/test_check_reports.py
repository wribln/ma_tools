"""
test class ErrorReports in metadata_check_reports
"""

import unittest
from unittest.mock import patch

import lib


class TestCheckReports(unittest.TestCase):
    """
    test class
    """

    @patch('builtins.print')
    def test_error_count(self, mock_print):
        """
        test procedure
        """
        o_er = lib.ErrorReports()
        self.assertTrue(o_er.b_is_valid())
        self.assertEqual(o_er.n_error_count(), 0)
        o_er.report_error('Test 1')
        mock_print.assert_called_with('Test 1', '\n')
        self.assertTrue(o_er.b_is_valid())
        self.assertEqual(o_er.n_error_count(), 1)
        o_er.report_error('Test 2')
        mock_print.assert_called_with('Test 2', '\n')
        self.assertTrue(o_er.b_is_valid())
        self.assertEqual(o_er.n_error_count(), 2)


if __name__ == '__main__':
    unittest.main()
