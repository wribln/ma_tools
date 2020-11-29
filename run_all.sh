#!/bin/sh
#
_do_syntax()
{
# perform syntax tests on file in $_FILE
echo ">>> checking >$1<"
pylint $1 || exit 1
pycodestyle $1 || exit 2
}
_do_syntax lib/metadata_check_reports.py
_do_syntax lib/metadata_check_tools.py
_do_syntax lib/metadata_params.py
_do_syntax lib/main_check.py
_do_syntax lib/main_load.py
_do_syntax lib/main_make.py
_do_syntax lib/main_ping.py
_do_syntax lib/main_files.py
_do_syntax lib/main_list1.py
_do_syntax lib/main_list2.py
_do_syntax ma_tools.py
_do_syntax test/test_check_reports.py
_do_syntax test/test_check_tools.py
_do_syntax test/test_params.py
python3 -m unittest -v
