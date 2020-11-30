"""ma_list2

Prepare a HTML file reference information in region and chronological
order; output is written to a file with the same name as this file and
having the extension .htm

Format is to suit radelnohnealter.de/presse format
"""
# pylint: disable=R0912
# pylint: disable=R0914
# pylint: disable=R0915

import locale
import datetime
import sqlite3

from os.path import basename, splitext
#from html import escape

from lib import ConfigParams as CP
from lib import ErrorReports as ER
from lib import report_log
from lib import s_format_heading
from lib import s_format_entry


def main(s_config_filename: str) -> None:
    """
    main program
    """

    # initialize

    report_log("\n*** list2 executing ***\n")

    o_error = ER()
    o_params = CP(o_error, s_config_filename)

    locale.setlocale(locale.LC_TIME, 'de_DE')

    s_base_filename = splitext(basename(__file__))[0]
    o_output_file = open('ma_list2.htm', 'w')

    # copy part1 from template

    o_input_file = open('htm/' + s_base_filename + '.htm', 'r')
    for s_line in o_input_file:
        s_line = s_line.rstrip()
        if s_line == '<>':
            break
        o_output_file.write(s_line + '\n')

    # create heading

    d_today = datetime.date.today()

    o_output_file.write(
        '<h1>Medienbeiträge (nach Regionen und Zeit sortiert)</h1>\n'
        '<p>erstellt am {0}</p>\n'
        .format(d_today.strftime('%d. %B %Y'))
    )

    # prepare database

    o_dbconn = sqlite3.connect(o_params.s_get_config_filename('db_name'))
    o_dbcursor = o_dbconn.cursor()

    # loop over all files and check if record exists

    s_request = (
        '''
        SELECT m.title, m.subtitle, m.url, m.media, m.url_ok,
        m.date, m.region,
        CASE WHEN m.region=="DE" THEN "Deutschland" ELSE
        CASE WHEN m.region=="DE-BE" THEN "Berlin"  ELSE
        CASE WHEN m.region=="DE-HH" THEN "Hamburg" ELSE m.place END END END
        AS "xplace",
        CASE WHEN m.region=="DE" THEN 1 ELSE 2 END AS "xorder"
        FROM {0} AS m
        WHERE (m.title IS NOT NULL) AND
        (SUBSTR(m.region, 1, 2)=="DE")
        AND (m.url_ok) AND (m.rating IN ("1","2","3"))
        ORDER BY xorder ASC, xplace ASC, m.date DESC;
        '''
        .format(CP.METADATA_TABLE)
        )

    # ready to loop over each entry

    s_last_place = str()
    n_count = 0

    for ts_row in o_dbcursor.execute(s_request):

        n_count += 1

        # new group?

        if s_last_place != ts_row[7]:
            if n_count > 1:
                o_output_file.write('</p>')
            s_last_place = ts_row[7]
            o_output_file.write(
                "<p>" + s_format_heading(ts_row[7]) + "<br />\n")

        o_output_file.write(
            s_format_entry(
                ts_row[0], # title
                ts_row[1], # subtitle
                ts_row[2], # url
                ts_row[3], # media
                ts_row[5]  # date
                ))

        o_output_file.write('<br />\n')

        # that's it for this item

    # end of loop, output closing tag

    if n_count > 1:
        o_output_file.write('</p>')

    o_dbconn.close()

    # copy remaining part of template

    for s_line in o_input_file:
        s_line = s_line.rstrip()
        o_output_file.write(s_line + '\n')

    o_output_file.close()

    # output some statistics

    report_log(
        "\n*** list2 completed ***\n"
        "{0} records created.\n"
        .format(n_count)
    )
