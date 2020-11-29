"""main_make

Suggests a filename based on date and title given
"""

import pyperclip

from lib import s_make_filename


def main() -> None:
    """
    main loop
    """

    while True:

        print("\nInput date and title: ")
        try:
            s_input = input()
        except (EOFError, KeyboardInterrupt):
            print('\nGood bye.')
            return
        except ValueError:
            print('Input bad - try again.')
            continue

        ls_input = s_input.split("\t")
        if len(ls_input) < 2 or len(ls_input) > 3:
            print('input bad - try again')
            continue
        ls_input = [x.strip() for x in ls_input]

        s_date = ls_input[0]
        s_date = (s_date.replace('-', '') + '00000000')[:8]

        s_file = ls_input[1]
        if s_file == "Radeln ohne Alter":
            if len(ls_input) > 2:
                s_file = (s_file + "_-_" + ls_input[2])
        s_file = s_date + '_' + s_make_filename(s_file)

        print('\n', s_file)
        pyperclip.copy(s_file)
