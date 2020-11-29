"""ping

This short utility checks whether the sites given in the url are
accessible and whether the file given in ref_copy file specification
actually exists. It then updates the respective status variables in the
database such that this status can be used for successive queries.

ping may be called more than once on the same database: this will cause
an update of the respective status variables.
"""

import sqlite3

from lib import ErrorReports as ER
from lib import ConfigParams as CP
from lib import report_log, s_url_is_alive, b_files_exist


def main(s_config_filename: str) -> int:
    """
    main program
    """

    # initialize

    report_log("\n*** ping executing ***\n")

    o_error = ER()
    o_params = CP(o_error, s_config_filename)

    s_backup_path = o_params.s_get_config_path('ref_files')

    # prepare database

    o_dbconn = sqlite3.connect(o_params.s_get_config_filename('db_name'))
    o_dbcursor = o_dbconn.cursor()

    # loop over all records and check accessibility

    n_count_recs = 0
    n_count_good = [0, 0]
    n_count_bad = [0, 0]

    for ts_row in o_dbcursor.execute(
            'SELECT id, title, url, ref_copy FROM ' + CP.METADATA_TABLE +
            ' WHERE url NOT NULL;'
            ):

        n_count_recs += 1

        if ts_row[2] is None:
            i_result_1 = 0
        else:
            s_result = s_url_is_alive(ts_row[2])
            i_result_1 = int(s_result is None)
            if i_result_1 == 1:
                n_count_good[0] += 1
            else:
                n_count_bad[0] += 1
                o_error.report_error(
                    "Link for row {0} cannot be reached: {1}\n"
                    "{2}\n"
                    "{3}"
                    .format(ts_row[0], ts_row[1], ts_row[2], s_result)
                )

        if ts_row[3] is None:
            i_result_2 = 0
        else:
            i_result_2 = int(b_files_exist(s_backup_path + ts_row[3]))
            if i_result_2 == 1:
                n_count_good[1] += 1
            else:
                n_count_bad[1] += 1
                o_error.report_error(
                    "Reference file for row {0} cannot be reached: {1}\n"
                    "{2}"
                    .format(ts_row[0], ts_row[1], ts_row[3])
                )

        o_dbconn.execute(
            'UPDATE ' + CP.METADATA_TABLE +
            ' SET url_ok = ?, ref_ok = ? WHERE ID = ?;',
            [i_result_1, i_result_2, ts_row[0]])
        o_dbconn.commit()

    o_dbconn.close()

    # output some statistics

    report_log(
        "\n*** ping completed ***\n"
        "{0} records processed,\n"
        "{1} links tested ok,\n"
        "{2} failed link tests,\n"
        "{3} references verified,\n"
        "{4} references not found.\n"
        .format(
            n_count_recs,
            n_count_good[0],
            n_count_bad[0],
            n_count_good[1],
            n_count_bad[1],
        )
    )
