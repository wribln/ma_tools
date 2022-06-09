"""ma_list3

Prepare a publications listing for the given month in regional order
and reverse chronological order; output is written to a file with the
same name as this file and having the extension .htm

Format is for use in mailings
"""
# pylint: disable=R0912
# pylint: disable=R0914
# pylint: disable=R0915

import locale
import datetime
import sqlite3
import re

from os.path import basename, splitext
from dateutil.relativedelta import relativedelta
from dateutil.parser import isoparse

from lib import ConfigParams as CP
from lib import ErrorReports as ER
from lib import report_log
from lib import s_format_heading
from lib import s_format_entry
from lib import s_sups
from lib import TagString


def main(
    s_config_filename: str,
    s_month: str
    ) -> int:
    """
    main program
    """

    # check s_month for correct syntax YYYY-MM or create default

    o_error = ER()

    o_date = None
    if s_month is None:
        o_date = datetime.date.today() + relativedelta(day=1, months=-1)
        s_month = o_date.strftime('%Y-%m')
    else:
        o_match = re.search('^([0-9]{4})-([0-9]{2})$', s_month)
        try:
            if o_match is None:
                raise ValueError()
            o_date = datetime.date(
                int(o_match.group(1)),
                int(o_match.group(2)),
                1
                )
        except ValueError:
            o_error.report_error('Invalid month: >{0}<'.format(s_month))
            return 1

    # initialize

    report_log("\n*** list3 executing ***\n")

    o_params = CP(o_error, s_config_filename)

    locale.setlocale(locale.LC_TIME, 'de_DE.utf-8')

    s_base_filename = splitext(basename(__file__))[0]
    o_output_file = open('ma_list3.htm', 'w')

    # copy part1 from template

    o_input_file = open('htm/' + s_base_filename + '.htm', 'r')
    for s_line in o_input_file:
        s_line = s_line.rstrip()
        if s_line == '<>':
            break
        o_output_file.write(s_line + '\n')

    # create heading

    o_output_file.write(
        '<h2>Radeln ohne Alter in den Medien ({0})</h2>\n'
        .format(o_date.strftime('%B %Y'))
    )

    # prepare database

    o_dbconn = sqlite3.connect(o_params.s_get_config_filename('db_name'))
    o_dbcursor = o_dbconn.cursor()

    # loop over all files and check if record exists

    s_request = (
        '''
        SELECT m.title, m.subtitle, m.url, m.media, m.url_ok,
        m.date, m.region, m.notes,
        CASE WHEN m.region=="DE" THEN "Deutschland" ELSE
        CASE WHEN m.region=="DE-BE" THEN "Berlin"  ELSE
        CASE WHEN m.region=="DE-HH" THEN "Hamburg" ELSE m.place END END END
        AS "xplace",
        CASE WHEN m.region=="DE" THEN 1 ELSE 2 END AS "xorder"
        FROM {0} AS m
        WHERE (m.title IS NOT NULL) AND
        (SUBSTR(m.region, 1, 2)=="DE")
        AND (m.url_ok) AND (m.rating IN ("1","2","3","4"))
        AND (m.date LIKE "{1}%")
        ORDER BY xorder ASC, xplace ASC, m.date;
        '''
        .format(CP.METADATA_TABLE, s_month)
        )

    # ready to loop over each entry

    s_last_place = str()
    n_count = 0

    for ts_row in o_dbcursor.execute(s_request):

        n_count += 1

        # new group?

        if s_last_place != ts_row[8]:
            if n_count > 1:
                o_output_file.write('\n</p>\n')
            s_last_place = ts_row[8]
            o_output_file.write(
                s_format_heading(ts_row[8]) + '\n<p>\n')
        else:
            o_output_file.write('<br />\n')

        # determine flags

        o_tags = TagString(ts_row[7])
        o_tags.with_simple('#paywall')
        o_tags.with_excls('#media_type', ['#video', '#audio'])
        sl_tags = []
        if o_tags.b_has_simple_tag('#paywall'):
            sl_tags.append('#paywall')
        sl_tags.append(o_tags.s_get_excls_tag('#media_type', '#other'))
        s_sups_list = s_sups(sl_tags)

        o_output_file.write(
            s_format_entry(
                ts_row[0],  # title
                ts_row[1],  # subtitle
                ts_row[2],  # url
                ts_row[3],  # media
                ts_row[5],  # date
                '',
                s_sups_list
                ))

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
        "\n*** list3 completed ***\n"
        "{0} records created.\n"
        .format(n_count)
    )

    return 0
