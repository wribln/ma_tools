"""ma_list2p

Prepare a HTML snippet for a single reference from the clipboard. This
is for situations when a new reference should be processed quickly for
simple insertion into an existing list2.htm listing.

Format is to suit radelnohnealter.de/presse format
"""
import pyperclip
import sys
import locale

from lib import s_format_heading
from lib import s_format_entry


def main() -> None:
    """
    process one record from the clipboard
    """

    locale.setlocale(locale.LC_ALL, "de_DE.utf-8")

    # expect a complete record on the clipboard,
    # or at least as many columns as needed for this functionality

    s_record = pyperclip.paste()
    l_record = list(s_record.split('\t'))

    if len(l_record) < 10:
        print(
            '>>> insufficient data: clipboard contains only {0} columm(s)'
            .format(len(l_record)+1)
            )
        sys.exit(1)

    print(s_format_heading(l_record[3]))

    s_entry = s_format_entry(
        l_record[6],
        l_record[7],
        l_record[9],
        l_record[1],
        l_record[2])

    print(s_entry)
    pyperclip.copy(s_entry)
