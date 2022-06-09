"""ma_row

Process a single row: Perform checks, create backup filename and prepare
a HTML snippet for a single reference from the clipboard. This is for
situations when a new reference should be processed quickly for simple
insertion into an existing list2.htm listing or unto the website (the
format is to suit radelnohnealter.de/presse)
"""
import sys
import locale
import re
import pyperclip

from lib import s_format_heading
from lib import s_format_entry
from lib import s_make_backup_filename
from lib import s_check_date
from lib import TagString

# the following are indeces into the row being processed:

_COL_MEDIA = 1
_COL_DATE = 2
_COL_PLACE = 3
_COL_REGION = 4
_COL_TITLE = 6
_COL_SUBTITLE = 7
_COL_URL = 9
_COL_COMMENT = 12
_COL_COUNT = 13  # total number of columns needed to process request


def s_format_backup_filename(
        s_date: str, s_title: str, s_subtitle: str) -> str:
    """
    create filename for backup file using date, title and
    - optionally - subtitle
    """

    s_date_new = (s_date.replace('-', '') + '00000000')[:8]
    return s_make_backup_filename(s_date_new, s_title, s_subtitle)


def main() -> None:
    """
    process one record from the clipboard
    """

    locale.setlocale(locale.LC_ALL, "de_DE.utf-8")

    # expect a complete record on the clipboard,
    # or at least as many columns as needed for this functionality

    s_record = pyperclip.paste()
    l_record = list(s_record.split('\t'))

    if len(l_record) < _COL_COUNT:
        print(
            '>>> insufficient data: clipboard contains only {0} columm(s)'
            .format(len(l_record)+1)
            )
        sys.exit(1)

    # perform basic Checks

    def b_pass_basic_checks(i_col: int, b_required=False) -> bool:
        nonlocal l_record

        # required fields must not be empty
        # empty fields must not have white spaces

        if len(l_record[i_col].strip()) == 0:

            if b_required:
                print(
                    '>>> Column {0} must not be empty.'
                    .format(i_col)
                )
                return False

            if len(l_record[i_col]) > 0:
                print(
                    '>>> Column {0} contains only white spaces.'
                    .format(i_col)
                )
                return False

            if len(re.findall('\n', l_record[i_col])) > 0:
                print(
                    '>>> Column {0} contains new line characters.'
                    .format(i_col)
                )
                return False

        return True

    b_ok = b_pass_basic_checks(_COL_URL) \
        and b_pass_basic_checks(_COL_DATE, True) \
        and b_pass_basic_checks(_COL_MEDIA, True) \
        and b_pass_basic_checks(_COL_PLACE) \
        and b_pass_basic_checks(_COL_REGION, True) \
        and b_pass_basic_checks(_COL_TITLE, True) \
        and b_pass_basic_checks(_COL_SUBTITLE)

    # fix place if only region given

    if len(l_record[_COL_PLACE]) > 0:
        s_region = l_record[_COL_PLACE]
    else:
        s_region = l_record[_COL_REGION]

    # check date

    s_date = s_check_date(l_record[_COL_DATE])
    b_ok = (b_ok and (s_date not in ('invalid', 'too early')))

    if not b_ok:
        sys.exit(1)

    # check remarks for tags

    o_tags = TagString(l_record[_COL_COMMENT])
    o_tags.with_simple('#paywall')
    o_tags.with_excls('#media_type', ['#video', '#audio', '#pdf'])
    i_check = o_tags.i_check_tags()
    if i_check > 0:
        print(
            '>>> Issue with tags in column {0}, code: {1}'
            .format(_COL_COMMENT, i_check)
            )
    ls_bad_tags = o_tags.l_unknown_tags()
    if len(ls_bad_tags) > 0:
        print(
            '>>> Unknown tags in column {0}: {1}.'
            .format(_COL_COMMENT, ls_bad_tags)
            )

    sl_tags = []
    if o_tags.b_has_simple_tag('#paywall'):
        sl_tags.append('#paywall')
    sl_tags.append(o_tags.s_get_excls_tag('#media_type', '#other'))
    s_icon_list = s_icons(sl_tags)

    # done checking and preparing, ready to start output

    s_filename = s_format_backup_filename(
        s_date,
        l_record[_COL_TITLE],
        l_record[_COL_SUBTITLE]
        )
    print("\n{0}\n".format(s_filename))

    print(s_format_heading(s_region))
    print(s_format_entry(
        l_record[_COL_TITLE],
        l_record[_COL_SUBTITLE],
        l_record[_COL_URL],
        l_record[_COL_MEDIA],
        l_record[_COL_DATE],
        s_icon_list))
    print()

    pyperclip.copy(s_filename)

    sys.exit(0)
