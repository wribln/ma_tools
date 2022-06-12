"""load

The metadata loaddb support app loads the metadata into a local database
for further processing. While loading, it will create some new fields,
filling them for later use:
- c_region: computed region, i.e. the label from the region field, or
  a label calculated from the region_code and the related texts in the
  regions table
The following fields are true by default (to ease other processing) but
can be set using respective tests by the ping utility:
- url_ok: true if the URL can be reached
- ref_ok: true if the reference copy was found

"""
# pylint: disable=C0321
# pylint: disable=W0401
# pylint: disable=R0912
# pylint: disable=R0914
# pylint: disable=R0915

import csv
import sqlite3

from lib import ErrorReports as ER
from lib import ConfigParams as CP
from lib import report_log, s_check_for_valid_file


def ls_replace_empty_string_by_none(sl_list: list) -> list:
    """
    Replaces in the given list all empty strings by None such
    that storing the list in the database will cause all empty
    strings to be stored as NULL
    """
    return [(item or None) for item in sl_list]

def t_determine_place_label(
    s_place: str,
    s_region: str,
    db_cursor) -> tuple():
    """
    determine a label for the place from the region table
    if none was given
    """
    if s_place is None:
        sl_place_labels = db_cursor.execute(
            'SELECT country_name, region_name FROM {0} '
            'WHERE region_code = "{1}"'
            .format(CP.REGIONS_TABLE, s_region)).fetchone()
        if sl_place_labels is None:
            t_place_label = (None, 0)
        elif sl_place_labels[1] is None:
            t_place_label = (sl_place_labels[0], 1)
        else:
            t_place_label = (sl_place_labels[1], 2)
    else:
        t_place_label = (s_place, 3)
    return t_place_label


def main(s_config_filename: str) -> None:
    """
    main program
    """

    # initialize

    report_log("\n*** load executing ***\n")

    o_error = ER()
    o_params = CP(o_error, s_config_filename)

    # prepare to access metadata file

    s_filename = o_params.s_get_config_filename('vv_regions')
    s_filepath = s_check_for_valid_file(s_filename, o_error)

    # prepare database

    o_dbconn = sqlite3.connect(o_params.s_get_config_filename('db_name'))
    o_dbcursor = o_dbconn.cursor()
    s_db_cmd = 'DROP TABLE IF EXISTS {0};'
    o_dbcursor.execute(s_db_cmd.format(CP.REGIONS_TABLE))
    o_dbcursor.execute(s_db_cmd.format(CP.METADATA_TABLE))

    # load region data

    n_max_col = o_params.i_get_max_column(CP.REGIONS_COLS)
    id_items = o_params.di_get_all_config_items(CP.REGIONS_COLS)
    sl_items = [None] * n_max_col

    s_db_cmd = 'CREATE TABLE ' + CP.REGIONS_TABLE + ' ('
    for s_item, i_col in id_items.items():
        if s_item == 'region_code':
            s_db_cmd += 'region_code TEXT PRIMARY KEY NOT NULL, '
        else:
            s_db_cmd += s_item + ' TEXT, '
        sl_items[i_col] = s_item
    s_db_cmd = s_db_cmd[:-2] + ');'
    o_dbcursor.execute(s_db_cmd)

    s_ic_cmd = 'INSERT INTO ' + CP.REGIONS_TABLE + ' ('
    s_ic_cmd += ','.join(sl_items)
    s_ic_cmd += ') VALUES (' + '?,' * (n_max_col - 1) + '?);'

    try:
        with open(s_filepath, 'r') as o_file:
            o_reader = csv.reader(o_file)
            sl_labels = next(o_reader)
            if sl_labels is None:
                raise StopIteration()
            for sl_row in o_reader:
                sl_row = ls_replace_empty_string_by_none(sl_row[:n_max_col])
                o_dbcursor.execute(s_ic_cmd, sl_row)
                o_dbconn.commit()

    except IOError as o_this_error:
        o_error.report_bad_file(s_filename, o_this_error)

    except StopIteration:
        o_error.report_empty_file(s_filename)

    sl_row = o_dbcursor.execute(
        'SELECT COUNT(*) FROM ' + CP.REGIONS_TABLE + ';')
    for row in sl_row:
        print("regions records read: {0}".format(row[0]))

    # prepare to access metadata file

    s_filename = o_params.s_get_config_filename('metadata')
    s_filepath = s_check_for_valid_file(s_filename, o_error)

    # load metadata

    n_max_col = o_params.i_get_max_column(CP.METADATA_COLS)
    id_items = o_params.di_get_all_config_items(CP.METADATA_COLS)
    sl_items = [None] * n_max_col

    s_db_cmd = (
        'CREATE TABLE ' + CP.METADATA_TABLE
        + ' (ID INT PRIMARY KEY NOT NULL, '
    )

    for s_item, i_col in id_items.items():
        s_db_cmd += s_item + ' TEXT, '
        sl_items[i_col] = s_item

    s_db_cmd += (
        'region_label TEXT, '
        'region_level INT, '
        'url_ok BOOLEAN DEFAULT 0 NOT NULL, '
        'ref_ok BOOLEAN DEFAULT 0 NOT NULL);'
    )
    o_dbcursor.execute(s_db_cmd)

    i_col_place = id_items['place']
    i_col_region = id_items['region']

    s_ic_cmd = 'INSERT INTO ' + CP.METADATA_TABLE + ' (ID,'
    s_ic_cmd += ','.join(sl_items)
    s_ic_cmd += ') VALUES (' + '?,' * n_max_col + '?);'

    s_up_cmd = 'UPDATE ' + CP.METADATA_TABLE
    s_up_cmd += ' SET region_label = ?, region_level = ?,'
    s_up_cmd += ' url_ok = ?, ref_ok = ? WHERE ID = ?;'

    try:
        with open(s_filepath, 'r') as o_file:
            o_reader = csv.reader(o_file)
            sl_labels = next(o_reader)
            if sl_labels is None:
                raise StopIteration()
            for sl_row in o_reader:
                sl_row = ls_replace_empty_string_by_none(sl_row[:n_max_col])
                a_place_label = t_determine_place_label(
                    sl_row[i_col_place],
                    sl_row[i_col_region],
                    o_dbcursor)
                o_dbcursor.execute(s_ic_cmd, [o_reader.line_num] + sl_row)
                o_dbcursor.execute(s_up_cmd, list(a_place_label) +
                    [True, True, o_reader.line_num])
                o_dbconn.commit()

    except IOError as o_this_error:
        o_error.report_bad_file(s_filename, o_this_error)

    except StopIteration:
        o_error.report_empty_file(s_filename)

    sl_row = o_dbcursor.execute(
        'SELECT COUNT(*) FROM ' + CP.METADATA_TABLE + ';').fetchone()
    print("metadata records added: {0}".format(sl_row[0]))

    o_dbconn.close()

    report_log("\n*** load completed ***\n")
