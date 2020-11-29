"""
test functions in metadata_check_tools
"""

import os
import unittest
from unittest.mock import patch

import lib


class TestImportValidStringValues(unittest.TestCase):
    """
    test class
    """

    def test_ok_case(self):
        """
        standard, ok case
        """
        o_error = lib.ErrorReports()

        s_list = lib.ls_import_valid_string_values(
            'test/test_check_tools_ok.csv', 1, o_error)
        self.assertEqual(s_list, [
            'Audio', 'Online', 'Print',
            'Radio', 'TV', 'Video', 'Dokument'])
        self.assertEqual(o_error.n_error_count(), 0)

    @patch('builtins.print')
    def test_file_problems(self, mock_print):
        """
        validate behaviour if file is not usable
        """
        o_error = lib.ErrorReports()

        # 1 - no does not exist

        s_list = lib.ls_import_valid_string_values(
            'test/test_check_tools_no.csv', 1, o_error)
        mock_print.assert_called_with(
            'Could not read file >test/test_check_tools_no.csv<\n'
            'Reason: >No such file or directory<', '\n')
        self.assertEqual(s_list, [])
        self.assertEqual(o_error.n_error_count(), 1)

        # 2 - empty has zero length

        s_list = lib.ls_import_valid_string_values(
            'test/test_check_tools_empty.csv', 1, o_error)
        mock_print.assert_called_with(
            'File is empty >test/test_check_tools_empty.csv<', '\n')
        self.assertEqual(s_list, [])
        self.assertEqual(o_error.n_error_count(), 2)

        # 3 - no_read is not accessible

        # cannot move to/from github with no access: hence change
        # access here.

        os.chmod('test/test_check_tools_no_read.csv', 0o044)
        s_list = lib.ls_import_valid_string_values(
            'test/test_check_tools_no_read.csv', 1, o_error)
        mock_print.assert_called_with(
            'Could not read file >test/test_check_tools_no_read.csv<\n'
            'Reason: >Permission denied<', '\n')
        self.assertEqual(s_list, [])
        self.assertEqual(o_error.n_error_count(), 3)

    @patch('builtins.print')
    def test_header_problems(self, mock_print):
        """
        validate header checks
        """
        o_error = lib.ErrorReports()

        # 1 - attempt to read past last column

        s_list = lib.ls_import_valid_string_values(
            'test/test_check_tools_ok.csv', 3, o_error)
        mock_print.assert_called_with(
            'Problem in file >test/test_check_tools_ok.csv<\n'
            'No column >3< in record ending in row >1<.', '\n')
        self.assertEqual(s_list, [])
        self.assertEqual(o_error.n_error_count(), 1)

        # 2 - bad_header contains 3 column in row 1, only 2 in others
        # note: function continues to loop over all 8 records!

        s_list = lib.ls_import_valid_string_values(
            'test/test_check_tools_bad_header.csv', 3, o_error)
        mock_print.assert_called_with(
            'Problem in file >test/test_check_tools_bad_header.csv<\n'
            'No column >3< in record ending in row >8<.', '\n')
        self.assertEqual(s_list, [])
        self.assertEqual(o_error.n_error_count(), 8)

    @patch('builtins.print')
    def test_check_file_valid(self, mock_print):
        """
        validate check_file_valid
        """
        o_error = lib.ErrorReports()

        # 1 - OK case

        s_result = lib.s_check_for_valid_file(
            'ma_tools.ini', o_error)
        self.assertIsNotNone(s_result)
        self.assertEqual(o_error.n_error_count(), 0)

        # 2 - try non-existing file

        s_result = lib.s_check_for_valid_file(
            'test/test_non_existing.csv', o_error)
        self.assertIsNone(s_result)
        self.assertEqual(o_error.n_error_count(), 1)
        mock_print.assert_called_with(
            'Problem with file >test/test_non_existing.csv<\n'
            'File does not exist.', '\n')

        # 3 - try file with no access

        # cannot move to/from github with no access: hence change
        # access here.

        os.chmod('test/test_check_tools_no_read.csv', 0o044)
        s_result = lib.s_check_for_valid_file(
            'test/test_check_tools_no_read.csv', o_error)
        self.assertIsNone(s_result)
        self.assertEqual(o_error.n_error_count(), 2)
        mock_print.assert_called_with(
            'Problem with file >test/test_check_tools_no_read.csv<\n'
            'File cannot be read.', '\n')

        # 4 - try empty file

        s_result = lib.s_check_for_valid_file(
            'test/test_check_tools_empty.csv', o_error)
        self.assertIsNone(s_result)
        self.assertEqual(o_error.n_error_count(), 3)
        mock_print.assert_called_with(
            'Problem with file >test/test_check_tools_empty.csv<\n'
            'File is empty.', '\n')

    def test_s_trim(self):
        """
        Test procedure
        """
        self.assertEqual(lib.s_trim('0123456789', 11), '0123456789')
        self.assertEqual(lib.s_trim('0123456789', 10), '0123456789')
        self.assertEqual(lib.s_trim('0123456789', 9), '0123456...')

    def test_s_make_filename(self):
        """
        Test procedure
        """
        self.assertEqual(
            lib.s_make_filename(
                'Ä Ö Ü ä ö ü ß '
            ),
            'Ae_Oe_Ue_ae_oe_ue_ss_'
        )
        self.assertEqual(
            lib.s_make_filename(
                '012345678901234567890123456789012345678901234567890123456789'
            ),
            '01234567890123456789012345678901234567890123456789012345'
        )
        self.assertEqual(
            lib.s_make_filename(
                'With a ' + u'\u2014' + u'\u2013'
                ' dash, and some (special) characters ' + u'\u212B'
                'ê'
            ),
            'With_a__dash,_and_some_(special)_characters_'
        )

    def test_b_files_exist(self):
        """
        Test procedure
        """
        self.assertTrue(lib.b_files_exist('test/config_bad*'))
        self.assertTrue(lib.b_files_exist('test/config_good.ini'))
        self.assertTrue(lib.b_files_exist('../../archive/*'))

    def test_b_is_valid_path(self):
        """
        Test procedures
        """
        self.assertTrue(lib.b_is_valid_path('test/'))
        self.assertTrue(lib.b_is_valid_path('lib/'))
        self.assertFalse(lib.b_is_valid_path('test/config_good.ini'))


if __name__ == '__main__':
    unittest.main()
