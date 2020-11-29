"""
test class ErrorReports in metadata_check_reports
"""

import unittest
from unittest.mock import patch

import lib


class TestCheckParams(unittest.TestCase):
    """
    test class
    """

    def test_init1(self):
        """
        test procedure
        """
        self.assertRaises(
            AssertionError, lib.ConfigParams,
            None, None)

        self.assertRaises(
            AssertionError, lib.ConfigParams,
            None, 'string')

        o_error = lib.ErrorReports()

        self.assertRaises(
            AssertionError, lib.ConfigParams,
            o_error, None)

        o_params = lib.ConfigParams(o_error, 'ma_tools.ini')

        self.assertIsNotNone(o_params)

    def test_assertions_s_get_config_filename(self):
        """
        test procedures
        """
        o_error = lib.ErrorReports()
        o_params = lib.ConfigParams(o_error, 'test/config_good.ini')

        self.assertRaises(
            AssertionError, o_params.s_get_config_filename, None)
        self.assertRaises(
            AssertionError, o_params.s_get_config_filename, 'bad_item')

        self.assertEqual(
            o_params.s_get_config_filename('metadata'), 'metadata.csv')
        self.assertEqual(
            o_params.s_get_config_filename('vv_regions'), 'country_codes.csv')
        self.assertEqual(
            o_params.s_get_config_filename('vv_types'), 'type_codes.csv')
        self.assertEqual(
            o_params.s_get_config_filename('vv_ratings'), 'ratings.csv')

    def test_assertions_s_get_config_path(self):
        """
        test if assertions are correctly implemented
        """

        o_error = lib.ErrorReports()
        o_params = lib.ConfigParams(o_error, 'test/config_good.ini')

        self.assertRaises(
            AssertionError, o_params.s_get_config_path, None)
        self.assertRaises(
            AssertionError, o_params.s_get_config_path, 'None')
        self.assertEqual(
            o_params.s_get_config_path('ref_files'),
            '~/Activities/RoA/Medienarchiv/archive/')

    def test_assertions_i_get_config_item(self):
        """
        Tests assertions of i_get_config_item( s_section, s_item)
        """
        o_error = lib.ErrorReports()
        o_params = lib.ConfigParams(o_error, 'test/config_good.ini')

        self.assertRaises(
            AssertionError, o_params.i_get_config_item, None, None)
        self.assertRaises(
            AssertionError, o_params.i_get_config_item, 'test', None)
        self.assertRaises(
            AssertionError, o_params.i_get_config_item, None, 'test')
        self.assertRaises(
            AssertionError, o_params.i_get_config_item, 'test', 'test')
        self.assertRaises(
            AssertionError, o_params.i_get_config_item, 'files', None)
        self.assertRaises(
            AssertionError, o_params.i_get_config_item, None, 'metadata')

    def test_assertions_i_get_max_column(self):
        """
        Tests assertions of i_get_max_columns(s_section)
        """
        o_error = lib.ErrorReports()
        o_params = lib.ConfigParams(o_error, 'test/config_good.ini')
        self.assertRaises(
            AssertionError, o_params.i_get_max_column, None)
        self.assertRaises(
            AssertionError, o_params.i_get_max_column, 'test')

    @patch('builtins.print')
    def test_init2(self, mock_print):
        """
        test procedure
        """

        o_error = lib.ErrorReports()

        # 1 - non-existing file

        self.assertRaises(
            SystemExit, lib.ConfigParams,
            o_error, 'test/config_no_exist.ini')
        mock_print.assert_called_with(
           'Problem with file >test/config_no_exist.ini<\n'
           'File does not exist.', '\n')

        self.assertEqual(o_error.n_error_count(), 1)

        # 2 - bad section

        self.assertRaises(
            SystemExit, lib.ConfigParams,
            o_error, 'test/config_bad_section.ini')
        mock_print.assert_called_with(
            'Error(s) in file >test/config_bad_section.ini<\n')
        self.assertEqual(o_error.n_error_count(), 2)

        # 3 - extra section

        self.assertRaises(
            SystemExit, lib.ConfigParams,
            o_error, 'test/config_extra_section.ini')
        mock_print.assert_called_with(
            'Error(s) in file >test/config_extra_section.ini<\n')
        self.assertEqual(o_error.n_error_count(), 3)

        # 4 - bad item

        self.assertRaises(
            SystemExit, lib.ConfigParams,
            o_error, 'test/config_bad_item.ini')
        mock_print.assert_called_with(
            'Error(s) in file >test/config_bad_item.ini<\n')
        self.assertEqual(o_error.n_error_count(), 4)

        # 5 - extra item

        self.assertRaises(
            SystemExit, lib.ConfigParams,
            o_error, 'test/config_extra_item.ini')
        mock_print.assert_called_with(
            'Error(s) in file >test/config_extra_item.ini<\n')
        self.assertEqual(o_error.n_error_count(), 5)

        # 6 - bad item value

        self.assertRaises(
            SystemExit, lib.ConfigParams,
            o_error, 'test/config_bad_value.ini')
        mock_print.assert_called_with(
            'Error(s) in file >test/config_bad_value.ini<\n')
        self.assertEqual(o_error.n_error_count(), 6)

        # 7 - extra item with bad value

        self.assertRaises(
            SystemExit, lib.ConfigParams,
            o_error, 'test/config_bad_bad_item.ini')
        mock_print.assert_called_with(
            'Error(s) in file >test/config_bad_bad_item.ini<\n')
        self.assertEqual(o_error.n_error_count(), 7)

        # finally - good file

        o_params = lib.ConfigParams(o_error, 'test/config_good.ini')
        self.assertEqual(o_error.n_error_count(), 7)
        self.assertIsInstance(o_params, lib.ConfigParams)
        self.assertEqual(o_params.i_get_max_column('files'), 0)
        self.assertEqual(o_params.i_get_max_column('metadata_cols'), 13)
        self.assertEqual(o_params.i_get_max_column('vv_region_cols'), 3)
        self.assertEqual(o_params.i_get_max_column('vv_type_cols'), 2)
        self.assertEqual(o_params.i_get_max_column('vv_rating_cols'), 2)

    def test_di_get_all_config_items(self):
        """
        tests for sd_get_all_config_items
        """
        o_error = lib.ErrorReports()
        o_params = lib.ConfigParams(o_error, 'test/config_good.ini')

        self.assertRaises(
            ValueError, o_params.di_get_all_config_items, 'paths')

        idict = o_params.di_get_all_config_items('vv_rating_cols')
        self.assertEqual(idict['rating_code'], 0)
        self.assertEqual(idict['rating_label'], 1)

        idict = o_params.di_get_all_config_items('vv_type_cols')
        self.assertEqual(idict['type_code'], 0)
        self.assertEqual(idict['type_description'], 1)

        idict = o_params.di_get_all_config_items('vv_region_cols')
        self.assertEqual(idict['country_name'], 0)
        self.assertEqual(idict['region_name'], 1)
        self.assertEqual(idict['region_code'], 2)

        idict = o_params.di_get_all_config_items('metadata_cols')
        self.assertEqual(idict['type'], 0)
        self.assertEqual(idict['media'], 1)
        self.assertEqual(idict['date'], 2)
        self.assertEqual(idict['place'], 3)
        self.assertEqual(idict['region'], 4)
        self.assertEqual(idict['contact'], 5)
        self.assertEqual(idict['title'], 6)
        self.assertEqual(idict['subtitle'], 7)
        self.assertEqual(idict['author'], 8)
        self.assertEqual(idict['ref_copy'], 10)
        self.assertEqual(idict['url'], 9)
        self.assertEqual(idict['rating'], 11)
        self.assertEqual(idict['notes'], 12)


if __name__ == '__main__':
    unittest.main()
