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
                    (-c, --config)

            list2p  create a list2 snippet from a single record (row)
                    provided in the clipboard; return entry in clipboard
                    ready to insert into HTML file

            makefn  helper to create local backup filenames from
                    date and title + optionally subtitle entries

            files   utility to check if files in database match
                    files in archive folder
                    (-c, --config)

            help    outputs this text

    options:

    -c, --config        path and filename of configuration file
                        (defaults to ma_tools.ini)
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


LS_SUBCMD = ['check', 'load', 'ping',
             'list1', 'list2', 'list2p',
             'makefn', 'files', 'help']

# versioning:   major.minor.intermediate
#
# where         intermediate increments for each release
#               minor increments with documentation update
#               major increments with new documentation

MA_VERSION = "1.1.0"


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
        usage='%(prog)s [tool] [options]',
        prog='ma_tools',
        description='Media Archive toolset'
    )
    parser.add_argument(
        'tool', choices=LS_SUBCMD, nargs='?',
        default='help'
        )
    parser.add_argument(
        '-v', '--version', action='version',
        version=f"{parser.prog} " + MA_VERSION
    )
    parser.add_argument(
        '-c', '--config', action='store',
        type=argparse.FileType('r'),
        default='ma_tools.ini'
    )
    parser.add_argument(
        '-p', '--ping', action='store_true',
        default=False
    )
    parser.add_argument(
        '-x', '--exist', action='store_true',
        default=False
    )
    return parser


def main():
    """
    parse command line parameters and call respective function
    """
    parser = init_argparse()
    args = parser.parse_args()

    if args.tool == 'makefn':
        import lib.main_make
        lib.main_make.main()
        sys.exit(0)

    if args.tool == 'check':
        import lib.main_check
        sys.exit(lib.main_check.main(args.config.name, args.ping, args.exist))

    if args.tool == 'ping':
        import lib.main_ping
        lib.main_ping.main(args.config.name)
        sys.exit(0)

    if args.tool == 'load':
        import lib.main_load
        lib.main_load.main(args.config.name)
        sys.exit(0)

    if args.tool == 'files':
        import lib.main_files
        lib.main_files.main(args.config.name)
        sys.exit(0)

    if args.tool == 'list1':
        import lib.main_list1
        lib.main_list1.main(args.config.name)
        sys.exit(0)

    if args.tool == 'list2':
        import lib.main_list2
        lib.main_list2.main(args.config.name)
        sys.exit(0)

    if args.tool == 'list2p':
        import lib.main_list2p
        lib.main_list2p.main()
        sys.exit(0)

    if args.tool == 'help':
        parser.print_help()
        sys.exit(0)

    print('>>> NOT IMPLEMENTED: {0} <<<'.format(args.tool))


if __name__ == "__main__":
    main()
