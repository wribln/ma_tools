"""metadata_list2_htm

provides several HTML formatting functions to be used by list2, list2p
to ensure consistent formatting
"""
from html import escape
import datetime

from lib import s_fix_url_for_html

_MEDIA_ICON = {
    'video': '<span style="font-family:FontAwesome;">&#xf03d;&nbsp;</span>',
    'sound': '<span style="font-family:FontAwesome;">&#xf130;&nbsp;</span>'
}


def s_format_heading(s_text: str) -> str:
    """
    format text as intermediate heading (place)
    """
    return "<strong>{0}</strong>".format(s_text)


def s_format_entry(
        s_maintitle: str,
        s_subtitle: str,
        s_url: str,
        s_media: str,
        s_date: str,
        s_media_type,
        ) -> str:
    """
    format complete record
    """

    # title + subtitle

    if s_maintitle is None or len(s_maintitle) == 0:
        s_title = '<???>'
    else:
        s_title = s_maintitle
    s_title = escape(s_title)

    if s_subtitle is not None and len(s_subtitle) > 0:
        s_title += '&nbsp;-&nbsp;' + escape(s_subtitle)

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
        .format(s_prefix, _MEDIA_ICON.get(s_media_type, ''), s_title, s_suffix)
        )

    # media, date

    if s_date is not None:
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

        s_item = ', '.join(filter(None, (s_media, s_date)))

        if len(s_item) > 0:
            s_result += ' ({0})'.format(s_item)

    return s_result
