"""ma_list_refs

Prepare a HTML file with all reference information in chronological
order; write output to a file named 'ma_list1.htm'
"""
# pylint: disable=R0912
# pylint: disable=R0914
# pylint: disable=R0915

import locale
import datetime
import sqlite3

from os.path import basename, splitext
from html import escape

from lib import ConfigParams as CP
from lib import ErrorReports as ER
from lib import report_log
from lib import s_fix_url_for_html


def main(s_config_filename: str) -> None:
    """
    main program
    """

    # initialize

    report_log("\n*** list1 executing ***\n")

    o_error = ER()
    o_params = CP(o_error, s_config_filename)

    locale.setlocale(locale.LC_TIME, 'de_DE')

    s_backup_path = o_params.s_get_config_path('ref_files')
    di_items = o_params.di_get_all_config_items(CP.METADATA_COLS)
    s_base_filename = splitext(basename(__file__))[0]
    o_output_file = open('ma_list1.htm', 'w')

    # copy part1 from template

    o_input_file = open('htm/' + s_base_filename + '.htm', 'r')
    for s_line in o_input_file:
        s_line = s_line.rstrip()
        if s_line == '<>':
            break
        o_output_file.write(s_line + '\n')

    # insert base

    o_output_file.write(
        '    <base href="{0}" target="_blank" />'
        .format(s_backup_path)
        )

    # copy part2 from template

    for s_line in o_input_file:
        s_line = s_line.rstrip()
        if s_line == '<>':
            break
        o_output_file.write(s_line + '\n')

    # create heading

    d_today = datetime.date.today()

    o_output_file.write(
        '<h1>Medienbeiträge (chronologisch sortiert)</h1>\n'
        '<p>erstellt am {0}</p>\n'
        .format(d_today.strftime('%d. %B %Y'))
    )
    o_output_file.write(
        '<table border="1" width="580pt">\n'
        '<colgroup>\n'
        '<col width="40pt" />\n'
        '<col width="540pt" />\n'
        '</colgroup>\n'
    )
    # prepare database

    o_dbconn = sqlite3.connect(o_params.s_get_config_filename('db_name'))
    o_dbcursor = o_dbconn.cursor()

    # loop over all files and check if record exists

    n_count = 0
    i_index = 0
    s_request = "SELECT m.ID"
    di_result = dict()
    di_result['m.ID'] = i_index

    def add_item(s_item: str):
        nonlocal s_request, i_index, di_result
        s_request += ', ' + s_item
        i_index += 1
        di_result[s_item] = i_index

    for s_item in di_items:
        add_item('m.' + s_item)

    add_item('m.url_ok')
    add_item('m.ref_ok')

    add_item('r.region_code')
    add_item('r.region_name')
    add_item('r.country_name')

    s_request += (
        " FROM " + CP.METADATA_TABLE + " m "
        "LEFT OUTER JOIN " + CP.REGIONS_TABLE + " r "
        "ON m.region = r.region_code "
        "ORDER BY m.date;")

    # ready to loop over each entry

    for ts_row in o_dbcursor.execute(s_request):

        n_count += 1

        # start new row, column 1 with ID

        o_output_file.write(
            '<tr class="vtop">\n'
            '<td class="hcenter">\n'
            '{0}\n'
            '</td>\n'
            '<td class="hleft">\n'
            .format(ts_row[0])
        )

        # author, title, subtitle, rating

        s_item = ts_row[di_result['m.author']]
        if s_item is not None:
            o_output_file.write(
                '{0}: '
                .format(escape(s_item))
            )

        s_title = ts_row[di_result['m.title']]
        s_subt = ts_row[di_result['m.subtitle']]
        if s_title is None:
            s_title = '<???>'
        if s_subt is not None:
            s_title += ' - ' + s_subt

        # url for title

        s_item = ts_row[di_result['m.url']]
        if s_item is None:
            s_prefix = ''
            s_suffix = ''
        else:
            s_item = s_fix_url_for_html(s_item)
            s_prefix = '<a href="{0}" target="_blank">'.format(s_item)
            s_suffix = '</a>'

        # rating - transform integers to (*****) best, (-) worst

        s_item = ts_row[di_result['m.rating']]
        if s_item is None:
            s_item = '?'
        elif s_item == '6':
            s_item = '-'
        elif s_item.isnumeric():
            s_item = '*' * (6 - int(s_item))
        else:
            pass  # leave string as it is

        o_output_file.write(
            '{0}<i>{1}</i>{2} ({3})<br />\n'
            .format(s_prefix, escape(s_title), s_suffix, s_item)
        )

        # media, type, date

        s_item = ts_row[di_result['m.media']]
        if s_item is None:
            s_item = '&lt;???&gt;'
        o_output_file.write(
            'In: <i>{0}</i>'
            .format(s_item)
        )

        s_item = ts_row[di_result['m.type']]
        if s_item is not None:
            o_output_file.write(' ({0})'.format(s_item))

        s_item = ts_row[di_result['m.date']]
        if s_item is None:
            s_item = ''
        else:
            ls_item = s_item.split('-')
            if len(ls_item) == 1:
                s_item = datetime.date(
                    int(ls_item[0]), 1, 1).strftime('%Y')
            elif len(ls_item) == 2:
                s_item = datetime.date(
                    int(ls_item[0]),
                    int(ls_item[1]),
                    1).strftime('%B %Y')
            elif len(ls_item) == 3:
                s_item = datetime.date(
                    int(ls_item[0]),
                    int(ls_item[1]),
                    int(ls_item[2])).strftime('%d. %B %Y')
            else:
                s_item = ''
        if len(s_item) > 0:
            o_output_file.write(', {0}'.format(s_item))
        o_output_file.write('.<br />\n')

        # place, contact
        #
        # place - DE
        # place (region) - DE-rr
        # place (country) - xx
        # place (region, country) - xx-rr
        #
        # region - DE
        # (country) - xx
        # region (country) - xx-rr

        s_place = ts_row[di_result['m.place']]
        s_code = ts_row[di_result['m.region']]
        s_region = ts_row[di_result['r.region_name']]
        s_country = ts_row[di_result['r.country_name']]

        if s_code is None:
            assert s_place is None, "place requires code"
        elif s_code[0:2] == 'DE':
            s_country = None

        if s_place is None:
            if s_region is None and s_country is None:
                s_item = None  # nothing to output
            elif s_region is None:
                s_item = '({0})'.format(s_country)
            elif s_country is None:
                s_item = '{0}'.format(s_region)
            else:
                s_item = '{0} ({1})'.format(s_region, s_country)
        else:
            s_item = escape(s_place)
            if s_region is None and s_country is None:
                pass  # that's it, output place only
            elif s_region is None:
                s_item += ' ({0})'.format(s_country)
            elif s_country is None:
                s_item += ' ({0})'.format(s_region)
            else:
                s_item += ' ({0}, {1})'.format(s_region, s_country)

        if s_item is not None:
            o_output_file.write(escape(s_item))

        # contact

        s_contact = ts_row[di_result['m.contact']]
        if s_item is None and s_contact is None:
            pass  # do not output this line
        elif s_item is None:
            o_output_file.write(
                'Kontakt: {0}<br />\n'
                .format(escape(s_contact))
            )
        elif s_contact is None:
            o_output_file.write(
                '<br />\n'
            )
        else:
            o_output_file.write(
                ', Kontakt: {0}<br />\n'
                .format(s_contact))
        # notes

        s_item = ts_row[di_result['m.notes']]
        if s_item is not None:
            o_output_file.write(
                'Anmerkungen: {0}<br />\n'
                .format(escape(s_item))
            )

        # local copy

        if ts_row[di_result['m.ref_ok']]:
            s_item = ts_row[di_result['m.ref_copy']]
            o_output_file.write(
                '<a href="{0}">Kopie</a>'
                .format(s_item))
        else:
            s_item = None

        if ts_row[di_result['m.url_ok']]:
            if s_item is None:
                pass  # nothing to do
            else:
                o_output_file.write('<br />\n')
        else:
            s_item = '' if s_item is None else ' '
            s_item += '(Original nicht mehr online verfügbar)<br />\n'
            o_output_file.write(s_item)

        # that's it for this item

        o_output_file.write('</td></tr>\n')

    o_dbconn.close()

    o_output_file.write('</table>\n')

    # copy remaining part of template

    for s_line in o_input_file:
        s_line = s_line.rstrip()
        o_output_file.write(s_line + '\n')

    o_output_file.close()

    # output some statistics

    report_log(
        "\n*** list1 completed ***\n"
        "{0} records created.\n"
        .format(n_count)
    )
