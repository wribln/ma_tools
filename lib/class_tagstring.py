""" class_tagstring

    implements a class to handle tags in a string, i.e.
    substrings with a specific prefix and pattern.

    A tag must be a word, i.e. a string consisting of characters,
    digits and underlines.

    The following types of tags can be used:

    #xxx    simple, no parameters

    #xxx    exclusive, i.e. #xxx, #yyy, #zzz are a group with a name
            'aaa', with #xxx, #yyy, #zzz as permitted values

    #yyyy-mm-dd a date (must be valid)
"""

import re
import sys
import json
from datetime import datetime


_TAG_CHARSET = '[a-zA-Z0-9-_]+'  # tags must consist of these characters
_TAG_TYPES = set(('simple', 'excls', 'date'))


def _s_tag_pattern(s_tag: str) -> str:
    return '\\' + s_tag + '\\b'


class TagString:
    """ This class handles a string containing certains tags, i.e.
        substrings often prefixed with a specified character.

        _s_tagged_string    holds a copy of the original string with
                            tags

        _s_tag_prefix       holds the leadin character of the tags
                            (default '#')

        _l_tag_list         holds all tags found in _s_tagged_string

        _d_tag_dict         a dictionary for each tag, holds type of
                            tag and tag-type specific information, i.e.

            simple:         ['simple', bool]
                            where bool is true when tag was found

            excls:          ['excls', dict]
                            where dict contains for each tag in that
                            group a bool which is true when that tag
                            was found

            date            ['date', bool]
                            where bool is true if the date in the tag
                            is a valid date
        """

    def __init__(self, s_tagged_string: str, s_tag_prefix='#'):
        """ initialize instance by setting string and prefix """
        assert (len(s_tag_prefix) == 1), \
            "s_tag_prefix must be a single character"
        assert (re.search(s_tag_prefix, _TAG_CHARSET) is None), \
            "s_tag_prefix must not be a character which can be " \
            "used in a tag itself"
        self._s_tagged_string = s_tagged_string
        self._s_tag_prefix = s_tag_prefix
        self._l_tag_list = re.findall(
            '\\' + self._s_tag_prefix + _TAG_CHARSET + '\\b',
            self._s_tagged_string, re.I)
        self._d_tag_dict = dict()

    def s_get_tag_prefix(self) -> str:
        """
        returns tag prefix
        """
        return self._s_tag_prefix

    def i_check_tags(self, n_tags=None) -> int:
        """
        utility to determine (internal) consistency using asserts
        and return error code for run-time problems:
        (0) no problem encountered
        (1) duplicate exclusive tags found in tagged string
        (2) duplicate tags found in tagged string
        (3) at least one date tag is not a valid date
        """
        if n_tags is not None and len(self._l_tag_list) != n_tags:
            return 2
        for tag in self._d_tag_dict.values():
            assert tag[0] in _TAG_TYPES
            if tag[0] == 'simple':
                assert isinstance(tag[1], bool)
            elif tag[0] == 'excls':
                i_trues = 0
                for tags in tag[1].values():
                    assert isinstance(tags, bool)
                    if tags:
                        i_trues += 1
                if i_trues > 1:
                    return 1
            elif tag[0] == 'date':
                assert isinstance(tag[1], bool)
                if not tag[1]:
                    return 3
            else:
                assert(False), 'unknown tag type'
        return 0

    def _b_is_tag(self, s_tag: str) -> bool:
        return s_tag[0] == self._s_tag_prefix

    def b_has_unique_tags(self) -> bool:
        """ returns true if all tags are unique """
        return len(self._l_tag_list) == len(set(self._l_tag_list))

    def l_duplicate_tags(self) -> list:
        """ returns a list of all non-unique tags """
        sl_unique = list()
        sl_duplicates = list()
        for s_tag in self._l_tag_list:
            if s_tag in sl_unique:
                sl_duplicates.append(s_tag)
            else:
                sl_unique.append(s_tag)
        return sl_duplicates

    def dump(self):
        """ dumps class data """
        sys.stderr.write((
            '\nDump of TagString' +
            '\n_s_tag_prefix:    >{0}<' +
            '\n_s_tagged_string: >{1}<' +
            '\n_l_tag_list:' +
            '\n{2}' +
            '\n_d_tag_dict:' +
            '\n{3}' +
            '\n').format(
                self._s_tag_prefix,
                self._s_tagged_string,
                json.dumps(self._l_tag_list),
                json.dumps(self._d_tag_dict)))

    def b_has_simple_tag(self, s_tag: str) -> bool:
        """ true if string contains specified tag """
        assert self._b_is_tag(s_tag)
        result = s_tag in self._d_tag_dict
        result = result and self._d_tag_dict[s_tag][0] == 'simple'
        return result and self._d_tag_dict[s_tag][1]

    def with_simple(self, s_tag: str):
        """ define simple tag """
        assert self._b_is_tag(s_tag)
        result = re.search(
            _s_tag_pattern(s_tag),
            self._s_tagged_string, re.I)
        self._d_tag_dict[s_tag] = ["simple", (result is not None)]

    def with_excls(self, s_group: str, ls_items: list):
        """ the given s_items can be specified alternatively """
        assert self._b_is_tag(s_group)
        for s_item in ls_items:
            assert self._b_is_tag(s_item)
        self._d_tag_dict[s_group] = ['excls', dict()]
        for s_item in ls_items:
            result = re.search(
                _s_tag_pattern(s_item),
                self._s_tagged_string, re.I)
            self._d_tag_dict[s_group][1][s_item] = (result is not None)

    def b_has_excls_tag(self, s_group, s_tag) -> bool:
        """ true when tag s_tag in group s_group is specified """
        assert self._b_is_tag(s_group)
        assert self._b_is_tag(s_tag)
        result = s_group in self._d_tag_dict
        result = result and self._d_tag_dict[s_group][0] == 'excls'
        result = result and s_tag in self._d_tag_dict[s_group][1]
        return result and self._d_tag_dict[s_group][1][s_tag]

    def s_get_excls_tag(self, s_group, s_default=None) -> str:
        """ return tag set in given group, None if none set """
        assert self._b_is_tag(s_group)
        assert self._d_tag_dict[s_group][0] == 'excls'
        for s_item, b_set in self._d_tag_dict[s_group][1].items():
            if b_set:
                return s_item
        return s_default

    def with_dates(self):
        """ finds all tags formatted as dates YYYY-MM-DD """
        l_result = re.findall(
            _s_tag_pattern(
                self._s_tag_prefix + r'\d\d\d\d-\d\d-\d\d'),
            self._s_tagged_string)
        for s_date in l_result:
            try:
                datetime.strptime(s_date, '#%Y-%m-%d')
                self._d_tag_dict[s_date] = ['date', True]
            except ValueError:
                self._d_tag_dict[s_date] = ['date', False]

    def b_has_date_tag(self, s_date):
        """ returns true if the given date is used as tag """
        s_tag = self._s_tag_prefix + s_date
        result = s_tag in self._d_tag_dict
        return result and self._d_tag_dict[s_tag][0] == 'date'

    def l_unknown_tags(self) -> list:
        """ returns list with unrecognized tags (so far) """
        l_unknown = self._l_tag_list.copy()
        for tag, value in self._d_tag_dict.items():
            if (value[0] == 'simple') and value[1]:
                l_unknown.remove(tag)
            elif value[0] == 'excls':
                for item in value[1]:
                    if value[1][item]:
                        l_unknown.remove(item)
            elif value[0] == 'date':
                l_unknown.remove(tag)
        return l_unknown


if __name__ == "__main__":
    import doctest
    doctest.testmod()
