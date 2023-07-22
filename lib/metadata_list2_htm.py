"""metadata_list2_htm

provides several HTML formatting functions to be used by list2
row to ensure consistent formatting
"""
from html import escape
import datetime

from .metadata_check_tools import s_fix_url_for_html

_ICON_LIST = {
    '#paywall': '&#xf023;',
    '#video': '&#xf03d;',
    '#audio': '&#xf130;',
    '#pdf': '&#xf1c1;'
    }

_SUP_LIST = {
    '#paywall': 'Paywall',
    '#video': 'Video',
    '#audio': 'Audio',
    '#pdf': 'PDF'
    }


def s_icons(sl_tags: list) -> str:
    """
    return string to inject into HTML with icons according to params,
    ignore tags not in _ICON_LIST
    """
    ls_icon_list = filter(lambda x: x in _ICON_LIST.keys(), sl_tags)
    ls_icon_list = list(map(lambda x: _ICON_LIST[x], ls_icon_list))
    s_icon_list = '&nbsp;'.join(ls_icon_list)
    if len(s_icon_list) > 0:
        return '<span style="font-family:FontAwesome;">' + \
                s_icon_list + '&nbsp;</span>'
    return ''


def s_sups(sl_tags: list) -> str:
    """
    return string to inject into HTML with superscript tags
    """
    ls_sup_list = filter(lambda x: x in _SUP_LIST.keys(), sl_tags)
    ls_sup_list = list(map(lambda x: _SUP_LIST[x], ls_sup_list))
    s_sup_list = ',&nbsp;'.join(ls_sup_list)
    if len(s_sup_list) > 0:
        return '<sup>&nbsp;' + s_sup_list + '</sup>'
    return ''


def s_format_heading(s_text: str) -> str:
    """
    format text as intermediate heading (place)
    """
    return "<h3>{0}</h3>".format(s_text)


def s_format_date(s_date: str) -> str:
    """
    return a useful date string - none if date is not valid
    """
    try:
        ls_date = s_date.split('-')
        if len(ls_date) == 1:
            s_date = datetime.date(
                int(ls_date[0]), 1, 1).strftime('%Y')
        elif len(ls_date) == 2:
            s_date = datetime.date(
                int(ls_date[0]),
                int(ls_date[1]),
                1).strftime('%B %Y')
        elif len(ls_date) == 3:
            s_date = datetime.date(
                int(ls_date[0]),
                int(ls_date[1]),
                int(ls_date[2])).strftime('%d. %B %Y')
        else:
            s_date = None

    except ValueError:
        s_date = None

    return s_date


# pylint: disable=too-many-arguments

def s_format_entry(
        s_maintitle: str,
        s_subtitle: str,
        s_url: str,
        s_media: str,
        s_date: str,
        s_icon_list='',
        s_sups_list='') -> str:
    """
    format complete record
    s_icon_list will be placed before record,
    s_sups_list will be placed after record
    """

    # title + subtitle

    if s_maintitle is None or s_maintitle:
        s_title = '<???>'
    else:
        s_title = s_maintitle
    s_title = escape(s_title)

    if s_subtitle is not None and not s_subtitle:
        if s_subtitle[0] != '(':
            s_title += '&nbsp;&ndash;'
        s_title += ' ' + escape(s_subtitle)

    # url

    if s_url is None:
        s_prefix = ''
        s_suffix = ''
    else:
        s_prefix = (
            '<a href="{0}" target="_blank" rel="noopener noreferrer">'
            .format(s_fix_url_for_html(s_url))
            )
        s_suffix = '</a>'

    s_result = (
        '{0}{1}<i>{2}</i>{3}'
        .format(s_prefix, s_icon_list, s_title, s_suffix)
        )

    # media, date

    s_item = ', '.join(filter(None, (s_media, s_format_date(s_date))))

    if not s_item:
        s_result += ' ({0}){1}'.format(s_item, s_sups_list)

    return s_result


if __name__ == "__main__":
    import doctest
    doctest.testmod()
