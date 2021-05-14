"""md_check

The metadata check application checks the metadata file for syntactical
and semantical correctness reporting any inconsistencies against the
specifications.
"""
# pylint: disable=C0321
# pylint: disable=W0401
# pylint: disable=R0912
# pylint: disable=R0914
# pylint: disable=R0915

import csv
import re
from os.path import basename, splitext

from lib import ErrorReports, ConfigParams
from lib import report_log, s_check_for_valid_file, \
    s_url_is_alive, s_trim, ls_import_valid_string_values, b_is_valid_path, \
    s_check_url, s_make_backup_filename, s_check_date


def fix_labels(n_max_col: int, sl_labels: list):
    """
    Helper function which replaces/adds missing headings with <empty>
    """
    for i_column in range(0, n_max_col):
        if i_column < len(sl_labels):
            if len(sl_labels[i_column]) > 0:
                sl_labels[i_column] = 'column {0} ({1})'.format(
                    sl_labels[i_column], i_column + 1)
                continue
        else:
            sl_labels.append(None)

        sl_labels[i_column] = 'column <empty> ({0})'.format(i_column + 1)


def main(
        s_config_file: str,
        b_check_ext_links: bool,
        b_check_int_links: bool
        ) -> int:
    """
    main program - exits (1) on error, exits (0) if all checks passed
    """

    # initialize

    report_log("\n*** check executing ***\n")

    o_error = ErrorReports()
    o_params = ConfigParams(o_error, s_config_file)
    b_errors = False

    # validate files

    s_filename = o_params.s_get_config_filename('vv_types')
    s_filepath = s_check_for_valid_file(s_filename, o_error)
    if s_filepath is None:
        b_errors = True
    else:
        key_col = o_params.i_get_config_item(
            'vv_type_cols', 'type_code')
        sl_vv_types = ls_import_valid_string_values(
            s_filepath, key_col, o_error)

    s_filename = o_params.s_get_config_filename('vv_ratings')
    s_filepath = s_check_for_valid_file(s_filename, o_error)
    if s_filepath is None:
        b_errors = True
    else:
        key_col = o_params.i_get_config_item(
            'vv_rating_cols', 'rating_code')
        sl_vv_ratings = ls_import_valid_string_values(
            s_filepath, key_col, o_error)

    s_filename_r = o_params.s_get_config_filename('vv_regions')
    s_filepath_r = s_check_for_valid_file(s_filename_r, o_error)
    if s_filepath_r is None:
        b_errors = True
    else:
        key_col = o_params.i_get_config_item('vv_region_cols', 'region_code')
        sl_vv_regions = ls_import_valid_string_values(
            s_filepath_r, key_col, o_error
        )

    s_filename_m = o_params.s_get_config_filename('metadata')
    s_filepath_m = s_check_for_valid_file(s_filename_m, o_error)
    if s_filepath_m is None:
        b_errors = True

    s_backup_path = o_params.s_get_config_path('ref_files')
    if not b_is_valid_path(s_backup_path):
        o_error.report_error(
            "Path to backup files could not be found:\n{0}"
            .format(s_backup_path))
        b_errors = True

    if b_errors:
        report_log(
            "\n*** check reports {0} errors.\n"
            .format(o_error.n_error_count()))
        return 1

    # validate vv_regions as they will be read into the metadata database

    report_log("\n*** check processing {0} ***\n".format(s_filename_r))

    try:
        with open(s_filepath_r, 'r') as o_file:

            # prepare to loop over each record:
            # di_params - dictionary of column names and indices
            # n_max_col - last column  needed to access
            # s_error - standard start of error text

            di_params = o_params.di_get_all_config_items('vv_region_cols')
            n_max_col = o_params.i_get_max_column('vv_region_cols')

            o_reader = csv.reader(o_file)
            sl_labels = next(o_reader)
            if sl_labels is None:
                raise StopIteration()
            fix_labels(n_max_col, sl_labels)

            # start loop over each record

            for sl_row in o_reader:

                b_errors = False

                # check if all required columns can be read

                if n_max_col > len(sl_row):
                    o_error.report_error(
                        "Record ending in row {0} "
                        "does not have at least {1} columns."
                        .format(o_reader.line_num, n_max_col))
                    continue

                # can I process this column?

                i_column_rc = di_params['region_code']
                s_item_rc = sl_row[i_column_rc].strip()
                if len(s_item_rc) == 0:
                    o_error.report_missing_field(
                        o_reader.line_num,
                        sl_labels[i_column_rc]
                    )
                    continue

                # check for duplicate

                if sl_vv_regions.count(s_item_rc) > 1:
                    o_error.report_with_std_msg(
                        o_reader.line_num,
                        sl_labels[i_column_rc],
                        ("'{0}' is not unique in file.")
                        .format(s_item_rc)
                        )

                # country is always required

                i_column_cn = di_params['country_name']
                s_item_cn = sl_row[i_column_cn].strip()

                if len(s_item_cn) == 0:
                    o_error.report_missing_field(
                        o_reader.line_num,
                        sl_labels[i_column_cn]
                    )

                i_column_rn = di_params['region_name']
                s_item_rn = sl_row[i_column_rn].strip()

                if len(s_item_rc) > 2:  # have a region code
                    if len(s_item_rn) == 0:
                        o_error.report_missing_field(
                            o_reader.line_num,
                            sl_labels[i_column_rn]
                        )
                else:  # no region code
                    if len(s_item_rn) > 0:
                        o_error.report_with_std_msg(
                            o_reader.line_num,
                            sl_labels[i_column_rn],
                            'Redundant label ignored.'
                        )

    except IOError as o_this_error:
        o_error.report_bad_file(s_filename_m, o_this_error)

    except StopIteration:
        o_error.report_empty_file(s_filename_m)

    # open metadata and start processing

    report_log("\n*** check processing {0} ***\n".format(s_filename_m))

    try:
        with open(s_filepath_m, 'r') as o_file:

            # prepare to loop over each record:
            # di_params - dictionary of column names and indices
            # n_max_col - last column  needed to access
            # s_error - standard start of error text

            di_params = o_params.di_get_all_config_items('metadata_cols')
            n_max_col = o_params.i_get_max_column('metadata_cols')

            o_reader = csv.reader(o_file)
            sl_labels = next(o_reader)
            if sl_labels is None:
                raise StopIteration()
            fix_labels(n_max_col, sl_labels)

            # start loop over each record

            n_rows = 1  # include header row

            for sl_row in o_reader:

                n_rows += 1

                # check if all required columns can be read

                if n_max_col > len(sl_row):
                    o_error.report_error(
                        "Record ending in row {0} "
                        "does not have at least {1} columns."
                        .format(o_reader.line_num, n_max_col))
                    b_errors = True

                i_column = 0
                s_check_item = ''

                # basic checks to be done for each column

                def b_pass_basic_checks(s_param, sl_row, b_required=False):
                    """
                    return False if error found or empty input
                    preventing any further checks
                    """
                    nonlocal i_column, di_params
                    nonlocal s_check_item
                    nonlocal o_error, o_reader

                    # can I process this column?

                    i_column = di_params[s_param]
                    if i_column >= len(sl_row):
                        return False

                    # empty items are permitted when not required

                    s_check_item = sl_row[i_column].strip()
                    if len(s_check_item) == 0:
                        if b_required:
                            o_error.report_with_std_msg(
                                o_reader.line_num,
                                sl_labels[i_column],
                                "This field must not be empty."
                            )
                        return False

                    # must not permit newlines within strings as they
                    # are counted by o_reader.line_num

                    if len(re.findall('\n', sl_row[i_column])) > 0:
                        o_error.report_with_std_msg(
                            o_reader.line_num,
                            sl_labels[i_column],
                            "This item must not contain new line characters.")
                        return False

                    return True

                # check valid values (type, region)

                for s_param, sd_vv in zip(
                    ('type', 'region', 'rating'),
                    (sl_vv_types, sl_vv_regions, sl_vv_ratings)
                ):

                    if not b_pass_basic_checks(s_param, sl_row):
                        continue

                    # test against permitted values

                    if s_check_item not in sd_vv:
                        o_error.report_with_std_msg(
                            o_reader.line_num,
                            sl_labels[i_column],
                            "Value '{0}' is not a valid value."
                            .format(s_check_item)
                        )

                # if a place is given, region must also be given

                if b_pass_basic_checks('place', sl_row):
                    if len(s_check_item) > 0:
                        if b_pass_basic_checks('region', sl_row, True):
                            pass
                        else:
                            o_error.report_with_std_msg(
                                o_reader.line_num,
                                sl_labels[i_column],
                                "If {0} is given, {1} must be "
                                "specified as well."
                                .format(
                                    sl_labels[di_params['place']],
                                    sl_labels[i_column])
                            )

                # check date format: YYYY, YYYY-MM, YYYY-MM-DD

                if b_pass_basic_checks('date', sl_row):
                    s_date = s_check_date(s_check_item)
                else:
                    s_date = 'invalid'

                if s_date == 'invalid':
                    o_error.report_with_std_msg(
                        o_reader.line_num, sl_labels[i_column],
                        "'{0}' is not a valid date.".format(s_check_item))
                elif s_date == 'too early':
                    o_error.report_with_std_msg(
                        o_reader.line_num, sl_labels[i_column],
                        "'{0}' is before start of 'CWA'.".format(s_check_item))

                # check title

                if b_pass_basic_checks('title', sl_row, b_required=True):
                    # create filename for backup url
                    s_title = s_check_item
                else:
                    s_title = ''

                # check subtitle

                if b_pass_basic_checks('subtitle', sl_row):
                    s_backup_filename =\
                        s_make_backup_filename(s_date, s_title, s_check_item)
                else:
                    s_backup_filename = ''

                # check reference copy

                if b_pass_basic_checks('ref_copy', sl_row):
                    s_check_item = s_backup_path + s_check_item
                    s_basename = basename(s_check_item)
                    s_file_no_ext = splitext(s_basename)[0]
                    if len(s_backup_filename) > 0 and \
                            s_file_no_ext != s_backup_filename:
                        o_error.report_with_std_msg(
                            o_reader.line_num,
                            sl_labels[i_column],
                            ('Suggested filename S: '
                                'does not match actual filename A:\n'
                                'S: {0}\nA: {1}')
                            .format(s_backup_filename, s_file_no_ext)
                        )

                    # check if reference copy is available

                    if b_check_int_links:
                        s_result = s_check_for_valid_file(s_check_item)
                        if s_result is not None:
                            o_error.report_with_std_msg(
                                o_reader.line_num,
                                sl_labels[i_column],
                                ('\n{0}\n{1}\n')
                                .format(s_check_item, s_result)
                            )

                # check if link can be reached

                if b_pass_basic_checks('url', sl_row):
                    s_result = s_check_url(s_check_item)
                    if s_result is not None:
                        o_error.report_with_std_msg(
                            o_reader.line_num,
                            sl_labels[i_column],
                            (s_result + "\n{0}")
                            .format(s_trim(s_check_item, 80))
                        )

                    elif b_check_ext_links:
                        s_result = s_url_is_alive(s_check_item)
                        if s_result is not None:
                            o_error.report_with_std_msg(
                                o_reader.line_num,
                                sl_labels[i_column],
                                (s_result + "\n{0}")
                                .format(s_trim(s_check_item, 80))
                            )

    except IOError as o_this_error:
        o_error.report_bad_file(s_filename_m, o_this_error)

    except StopIteration:
        o_error.report_empty_file(s_filename_m)

    # output final, completion message

    report_log(
        "\n*** check completed ***\n"
        "{0} issues were found in {1} rows.\n"
        .format(o_error.n_error_count(), n_rows))

    if o_error.n_error_count() == 0:
        return 0
    return 1
