"""metadata_check_tools

Metadata validation support functions

This module contains various support functions for the
metadata_check_app.
"""
from pathlib import Path
import csv
import os.path
import re
import glob
import datetime
from urllib.parse import urlparse, quote
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# Check https://regex101.com/r/A326u1/5 for reference

_DOMAIN_FORMAT = re.compile(
    r"(?:^(\w{1,255}):(.{1,255})@|^)"  # http basic authentication [optional]
    r"(?:(?:(?=\S{0,253}(?:$|:))"  # check full domain length to be less than
    # or equal to 253 (starting after http basic auth, stopping before port)
    r"((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"  # check for at least
    # one subdomain (maximum length per subdomain: 63 characters), dashes
    # in between allowed
    r"(?:[a-z0-9]{1,63})))"  # check for top level domain, no dashes allowed
    r"|localhost)"  # accept also "localhost" only
    r"(:\d{1,5})?",  # port [optional]
    re.IGNORECASE
)
_SCHEME_FORMAT = re.compile(
    r"^(http|hxxp|ftp|fxp)s?$",  # scheme: http(s) or ftp(s)
    re.IGNORECASE
)

# translation tables for s_make_filename

_CD_XLAT = {
    ord('Ä'): 'Ae',
    ord('Ö'): 'Oe',
    ord('Ü'): 'Ue',
    ord('ä'): 'ae',
    ord('ö'): 'oe',
    ord('ü'): 'ue',
    ord('ß'): 'ss',
    ord('*'): '_',
    ord(' '): '_'}

_CL_XLAT = (
    'abcdefghijklmnopqrstuvwxyz'
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    '0123456789'
    '-,_()').encode('latin-1')


def s_fix_url_for_html(s_url: str) -> str:
    """
    Need to replace ampersands in urls by &amp; when used in HTML

    >>> s_fix_url_for_html('file://a_file_with_ampersand_&')
    'file://a_file_with_ampersand_&amp;'

    """
    assert s_url is not None, 'None is not a valid string'
    s_new_url = quote(s_url, r"\./_-:&,=?")
    return s_new_url.replace('&', '&amp;')


def ls_import_valid_string_values(
        s_csv_file: str,
        i_column: int,
        o_error) -> list:
    """
    Reads strings from the specified column of the given file with the
    name s_csv_file, returning a list of these strings.

        Parameters:
            s_csv_file (string):    the filename to read from
            i_column (string):      index into the column to read
            o_error (class object): error handling

        Returns:
            ls_valid_values[]:      a list of string values

    """
    assert Path(s_csv_file).is_file, 'expect existing file'
    assert i_column > 0, 'i_column must be a non-zero, positive integer'
    assert o_error.b_is_valid(), 'error handling object must be ok'

    # initialize return value

    ls_valid_values = list()

    # attempt to open file for reading
    try:
        with open(s_csv_file, 'r') as o_file:
            # use first line with heading to determine column
            o_reader = csv.reader(o_file)
            s_row = next(o_reader)
            if s_row is None:
                raise StopIteration()
            # given column must exist in header line
            if i_column < 1 or i_column > len(s_row):
                o_error.report_error(
                    "Problem in file >{0}<\n"
                    "No column >{1}< in record ending in row >{2}<."
                    .format(s_csv_file, i_column, o_reader.line_num)
                )
                return list()
            # now loop over all remaining rows of the input file
            for s_row in o_reader:
                if i_column > len(s_row):
                    o_error.report_error(
                        "Problem in file >{0}<\n"
                        "No column >{1}< in record ending in row >{2}<."
                        .format(s_csv_file, i_column, o_reader.line_num)
                    )
                else:
                    ls_valid_values.append(s_row[i_column - 1])

    except IOError as o_this_error:
        o_error.report_error(
            "Could not read file >{0}<\n"
            "Reason: >{1}<".
            format(s_csv_file, o_this_error.strerror))

    except StopIteration:
        o_error.report_error(
            "File is empty >{0}<".format(s_csv_file))

    return ls_valid_values


def b_is_valid_path(s_path: str) -> bool:
    """
    Validates given path
    """
    assert s_path is not None, 's_path must be a string'
    assert s_path, 's_path must not be empty'

    return os.path.isdir(s_path)


def s_check_date(s_text: str) -> str:
    """
    Check if date is correctly formatted, i.e. permitted formats are:
    * YYYY          year only
    * YYYY-MM       year + month
    * YYYY-MM-DD    year, month, date

        Returns:
            00000000    for an empty or illformatted string
            invalid     for invalid date, e.g. 2020-02-30
            too early   if date is before start of CWA
            YYYYMMDD    with zeros for missing information (day, day and month)

    >>> s_check_date('')
    '00000000'

    >>> s_check_date('2020-02-30')
    'invalid'

    >>> s_check_date('2002-02-02')
    'too early'

    >>> s_check_date('2020-02-02')
    '20200202'

    """
    o_match = re.search('^([0-9]{4})(-([0-9]{2})(-([0-9]{2}))*)*$', s_text)
    if o_match is not None:
        s_date = o_match.group(0).replace('-', '')
        try:
            o_date = datetime.date(int(o_match.group(1)), 1, 1)
            if o_match.group(3) is None:
                s_date += '0000'
            else:
                o_date = o_date.replace(month=int(o_match.group(3)))
                if o_match.group(5) is None:
                    s_date += '00'
                else:
                    o_date = o_date.replace(day=int(o_match.group(5)))

        except ValueError:
            s_date = 'invalid'

        if o_date < datetime.date(2013, 1, 1):
            s_date = 'too early'

    else:
        s_date = '00000000'

    return s_date


def s_check_for_valid_file(s_file: str, o_error=None) -> str:
    """
    Makes sure the given file exists, is accessible and not empty

        Parameters
            s_file          a file specification
            o_error         the error reporting object

        Returns
            if o_error is None, return problem specifics or None
                            if file is OK
            else return the full path for the given file or output
                            error message and return None if file
                            cannot be used
    """
    assert s_file is not None, 's_file must be a string'
    assert s_file, 's_file must not be empty'
    assert o_error is None or o_error.b_is_valid(), \
        'error handling object must be None or ok'

    s_error_detail = None
    s_full_path = os.path.abspath(s_file)

    if s_full_path is None:
        s_error_detail = 'Cannot determine full path.'
    elif not os.path.exists(s_full_path):
        s_error_detail = 'File does not exist.'
    elif not os.access(s_full_path, os.R_OK):
        s_error_detail = 'File cannot be read.'
    elif os.stat(s_full_path).st_size == 0:
        s_error_detail = 'File is empty.'

    if o_error is None:
        return s_error_detail

    if s_error_detail is None:
        return s_full_path

    o_error.report_error(
        "Problem with file >{0}<\n{1}"
        .format(s_file, s_error_detail)
    )
    return None


def s_trim(s_text: str, i_max_len: int) -> str:
    """
    Trims the given string s_text to a maximum of i_max_len characters.
    If the string is longer than i_max_len, the string is trimmed to
    i_max_len - 3 characters and '...' is added to the string to indicate
    that the string is longer.

    >>> s_trim('123', 5)
    '123'

    >>> s_trim('12345', 5)
    '12345'

    >>> s_trim('123456', 5)
    '12...'

    >>> s_trim('1234567890', 5)
    '12...'

    """
    assert i_max_len > 4, 'i_max_len <= 4 does not make sense'

    if len(s_text) <= i_max_len:
        return s_text
    return s_text[:(i_max_len - 3)] + '...'


def s_check_url(url: str) -> str:
    """
    Checks if a given URL has a valid syntax.
    Returns error details or None.
    """
    assert url.strip(), 'non-empty url required'

    if len(url) > 2048:
        return (
            "Maximum length of 2048 characters exceeded (given length={})"
            .format(len(url))
        )

    result = urlparse(url)
    scheme = result.scheme
    domain = result.netloc

    if not scheme:
        return "No scheme (http(s), ftp(s), etc.) specified."

    if not re.fullmatch(_SCHEME_FORMAT, scheme):
        return (
            "Scheme must either be http(s) or ftp(s) (given scheme={})"
            .format(scheme)
        )

    if not domain:
        return "No domain specified."

    if not re.fullmatch(_DOMAIN_FORMAT, domain):
        return "Invalid domain given (domain={})".format(domain)

    return None


def s_url_is_alive(url: str) -> str:
    """
    Test whether given url can be reached, return error string
    if not, else None
    """
    try:
        url_req = Request(url, None, {
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64; rv:78.0) '
            'Gecko/20100101 Firefox/78.0'
            })
        urlopen(url_req)
    except HTTPError as u_error:
        return (
            "Server couldn't fulfill the request.\n"
            "HTTP status code: {0}.".format(u_error.code)
            )
    except URLError as u_error:
        return (
            "Could not reach server, reason:\n"
            "{0}.".format(u_error.reason)
            )
    except ValueError as u_error:
        return (
            "Unable to check status of server, reason:\n"
            "{0}.".format(u_error)
            )
    return None


def s_make_filename(s_text: str) -> str:
    """
    Convert the given string to a suitable filename;
    filename is longer than 56 characters will be trimmed

    >>> s_make_filename('test')
    'test'

    >>> s_make_filename('Ümläüte_and more:\\ ÄöÖ')
    'Uemlaeuete_and_more_AeoeOe'

    >>> s_make_filename('123456789 123456789 123456789 123456789 123456789' + \
        ' 123456789')
    '123456789_123456789_123456789_123456789_123456789_123456'

    """
    s_old = s_text.encode('latin-1', 'ignore')
    s_new = str()
    for i_char in s_old:
        if i_char in _CL_XLAT:
            s_new += chr(i_char)
        elif i_char in _CD_XLAT:
            s_new += _CD_XLAT[i_char]
    return s_new[:56]


def s_make_backup_filename(s_date: str, s_title: str, s_subtitle: str) -> str:
    """
    If s_title too general, add subtitle.
    Prepend date. Return empty string on error.

    >>> s_make_backup_filename('20200202', '', '')
    ''

    >>> s_make_backup_filename('20200202', 'test', 'test')
    '20200202_test'

    >>> s_make_backup_filename('20200202', 'test', '')
    '20200202_test'

    >>> s_make_backup_filename('20200202', 'Radeln ohne Alter', 'test')
    '20200202_Radeln_ohne_Alter_-_test'

    """
    assert len(s_date) == 8, 's_date must be exactly 8 characters long'
    s_filename = s_title
    if not s_title:
        return ''
    if s_title == 'Radeln ohne Alter' and s_subtitle:
        s_filename = s_title + '_-_' + s_subtitle
    return s_date + '_' + s_make_filename(s_filename)


def b_files_exist(s_file: str) -> bool:
    """
    Given a filename or a search pattern (path ending with *),
    check if the file exists or if there are files at the
    given location
    """
    return len(glob.glob(s_file)) > 0


if __name__ == "__main__":
    import doctest
    doctest.testmod()
