"""ma_files

This utility validates the files in the archive folder and reports all
files not found in the metadata database.
"""

import sqlite3
import os

from lib import ConfigParams as CP
from lib import ErrorReports as ER
from lib import report_log


def main(s_config_filename: str) -> None:
    """
    main program
    """

    # initialize

    report_log("\n*** files executing ***\n")

    o_error = ER()
    o_params = CP(o_error, s_config_filename)

    s_backup_path = o_params.s_get_config_path('ref_files')

    # prepare database

    o_dbconn = sqlite3.connect(o_params.s_get_config_filename('db_name'))
    o_dbcursor = o_dbconn.cursor()
    s_request = (
        "SELECT EXISTS (SELECT 1 FROM " + CP.METADATA_TABLE +
        " WHERE ref_copy = '{0}' LIMIT 1);"
        )

    # loop over all files and check if record exists

    n_count_good = 0
    n_count_bad = 0

    for s_file in os.scandir(s_backup_path):
        t_result = o_dbcursor.execute(s_request.format(s_file.name))
        if t_result.fetchone()[0]:
            n_count_good += 1
        else:
            n_count_bad += 1
            o_error.report_error(
                "File in reference folder but not in metadata database:\n"
                "{0}".format(s_file.name))

    o_dbconn.close()

    # output some statistics

    report_log(
        "\n*** files completed: ***\n"
        "{0} files tested ok,\n"
        "{1} files not used in database.\n"
        .format(n_count_good, n_count_bad)
    )
