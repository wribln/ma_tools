"""ma_tools - main driver

This is the main driver program for all media-archive tools: It basically
interprets the tool parameter and runs the respective program using the
given options.

Syntax:

    ma_tools <tool> <options>

    tool:   check   perform basic checks on the given csv file(s)
                    (-c, --config, -p, --ping, -x, --exist)

            load    load data into database
                    (-c, --config)

            ping    update url and file status in database
                    (-c, --config)

            list<n> create a listing of the metadata
                    (-c, --config, [-m, --month])
                    -m, --month used only for list3

            files   utility to check if files in database match
                    files in archive folder
                    (-c, --config)

            row     processes a single row from the media archive:
                    perform some checks, output a generated backup filename,
                    and create an HTML snippet suitable for inclusion in the
                    radelnohnealter.de/presse webpage.

            help    outputs this text

            makefn  helper to create local backup filenames from
                    date and title + optionally subtitle entries

    options:

    -c, --config        path and filename of configuration file
                        (defaults to ma_tools.ini)
    -m, --month         value format: YYYY-MM
                        month to be reported (list3 only),
                        defaults to previous month
    -p, --ping          check if urls exist (check only)
    -x, --exist         check if files exist (check only)
    -h, --help          outputs this text or specific information about
                        the selected tool
    -v, --version       reports the version of program
"""
# The above is the help text output for -h/--help !!
# pylint: disable=C0415

import argparse
import sys


LS_SUBCMD = [r'check', r'load', r'ping', r'list1',
             r'list2', r'list3', r'files', r'help',
             r'row', r'makefn']

# versioning:   major.minor.intermediate
#
# where         intermediate increments for each release
#               minor increments with documentation update
#               major increments with new documentation

MA_VERSION = "1.7.2"


class ArgumentParser(argparse.ArgumentParser):
    """
    derived class permits me to add my own help output
    """

    def print_help(self, file=None):
        print(__doc__)


def init_argparse() -> ArgumentParser():
    """
    Initialize argparse and return handle.
    """
    parser = ArgumentParser(
        usage=r'%(prog)s [tool] [options]',
        prog=r'ma_tools',
        description=r'Media Archive toolset'
    )
    parser.add_argument(
        r'tool', choices=LS_SUBCMD, nargs='?',
        default=r'help'
    )
    parser.add_argument(
        r'-v', r'--version', action=r'version',
        version=f"{parser.prog} " + MA_VERSION
    )
    parser.add_argument(
        r'-c', r'--config', action=r'store',
        type=argparse.FileType(r'r'),
        default=r'ma_tools.ini'
    )
    parser.add_argument(
        r'-p', r'--ping', action=r'store_true',
        default=False
    )
    parser.add_argument(
        r'-x', r'--exist', action=r'store_true',
        default=False
    )
    parser.add_argument(
        r'-m', r'--month',
        default=None
    )
    return parser


def main():
    """
    parse command line parameters and call respective function
    """
    parser = init_argparse()
    args = parser.parse_args()

    if args.tool == r'makefn':
        import lib.main_make
        lib.main_make.main()
        sys.exit(0)

    if args.tool == r'check':
        import lib.main_check
        sys.exit(lib.main_check.main(args.config.name, args.ping, args.exist))

    if args.tool == r'ping':
        import lib.main_ping
        lib.main_ping.main(args.config.name)
        sys.exit(0)

    if args.tool == r'load':
        import lib.main_load
        lib.main_load.main(args.config.name)
        sys.exit(0)

    if args.tool == r'files':
        import lib.main_files
        lib.main_files.main(args.config.name)
        sys.exit(0)

    if args.tool == r'list1':
        import lib.main_list1
        lib.main_list1.main(args.config.name)
        sys.exit(0)

    if args.tool == r'list2':
        import lib.main_list2
        lib.main_list2.main(args.config.name)
        sys.exit(0)

    if args.tool == r'list3':
        import lib.main_list3
        sys.exit(lib.main_list3.main(args.config.name, args.month))

    if args.tool == r'row':
        import lib.main_row
        lib.main_row.main()
        sys.exit(0)

    if args.tool == r'help':
        parser.print_help()
        sys.exit(0)

    print(r'>>> NOT IMPLEMENTED: {0} <<<'.format(args.tool))


if __name__ == r'__main__':
    main()
