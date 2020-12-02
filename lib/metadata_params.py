"""metadata_params

Implements a class to make all parameters from the config.ini file
available to the utilities.
"""
from configparser import ConfigParser, Error
from sys import exit as sysexit

from .metadata_check_reports import ErrorReports, report_log
from .metadata_check_tools import s_check_for_valid_file

# The program parameters are read from the configuration file.
# Since defaults do not make much sense here, all parameters
# are required: __init__ will make sure that all parameters
# are specified and of the correct type. The sequence in
# _LS_CONFIG_SECTIONS and _LS_CONFIG_ITEMS must match!!!

_LS_CONFIG_SECTIONS = [         # sections
    'metadata_cols',
    'vv_region_cols',
    'vv_rating_cols',
    'files',
    'paths',
    'vv_type_cols']

_LS_CONFIG_ITEMS = ([
    [                           # items in first section
        'media',
        'author',
        'contact',
        'date',
        'place',
        'region',
        'ref_copy',
        'subtitle',
        'title',
        'type',
        'url',
        'rating',
        'notes'],
    [                           # items in second section
        'country_name',
        'region_code',
        'region_name'],
    [                           # items in third section
        'rating_code',
        'rating_label'],
    [                           # items in fourth section
        'metadata',
        'vv_regions',
        'vv_types',
        'vv_ratings',
        'db_name'],
    [                           # items in fifth section
        'ref_files',
        'ref_base'],
    [                           # items in sixth section
        'type_code',
        'type_description']
    ])


class ConfigParams:
    """
    Load from and save to config.ini file the software configuration
    parameters needed by the various utilities; make them available
    in the appropriate format; performs error checking on the input
    file as users may need to edit the file.

    Instance variables:
        _config_params      result of ConfigParser()
        _il_max_col         integer list of maximum column index
                            per section
        _o_error            copy of initial ErrorReports instance
    """

    # names of tables in database

    METADATA_TABLE = 'metadata'
    REGIONS_TABLE = 'regions'

    METADATA_COLS = _LS_CONFIG_SECTIONS[0]
    REGIONS_COLS = _LS_CONFIG_SECTIONS[1]
    RATING_COLS = _LS_CONFIG_SECTIONS[2]
    FILE_PARAMS = _LS_CONFIG_SECTIONS[3]
    PATH_PARAMS = _LS_CONFIG_SECTIONS[4]
    TYPE_COLS = _LS_CONFIG_SECTIONS[5]

    def __init__(self, o_error: ErrorReports, s_file: str) -> None:
        """
        Load config.ini, report any problems using ErrorReports.
        """
        assert isinstance(o_error, ErrorReports), \
            'o_error not an ErrorReports instance'
        assert o_error.b_is_valid(), 'o_error must be valid'
        assert s_file is not None, 's_file must not be none'
        assert len(s_file) > 0, 's_file must not be empty'

        b_config_ok = True
        self._o_error = o_error

        # do I have a valid filename?

        s_full_path = s_check_for_valid_file(s_file, self._o_error)
        b_config_ok = s_full_path is not None

        if b_config_ok:
            self._config_params = ConfigParser()
            try:
                self._config_params.read(s_full_path)
            except Error as o_current_error:
                self._o_error.report_error(
                    "Error while reading >{0}<\n"
                    "Details: {1}".
                    format(s_file, str(o_current_error)))
                b_config_ok = False

        # before checking each and every item,
        # initialize list of maximum column indeces per section

        self._max_col = [0] * len(_LS_CONFIG_SECTIONS)

        if b_config_ok:
            if not self._check_config():
                report_log(
                    "Error(s) in file >{0}<\n"
                    .format(s_file))
                b_config_ok = False

        # problems encountered with .ini file? - get out!

        if not b_config_ok:
            sysexit(
                 "Program aborted after reporting {0} errors."
                 .format(o_error.n_error_count()))

    def s_get_config_filename(self, s_item: str) -> str:
        """
        Return a file specification from the respective section.
        """
        assert s_item is not None, 'Parameter must not be None'
        assert s_item in _LS_CONFIG_ITEMS[3], \
            "'{0}'' must be an item in ['{1}'']".format(
                s_item, self.FILE_PARAMS)

        return self._config_params[self.FILE_PARAMS][s_item]

    def s_get_config_path(self, s_item: str) -> str:
        """
        Return a path specification from the respective section
        """
        assert s_item in _LS_CONFIG_ITEMS[4], \
            "'{0}' must be an item in [{1}]".format(s_item, self.PATH_PARAMS)

        return self._config_params[self.PATH_PARAMS][s_item]

    def i_get_config_item(self, s_section: str, s_item: str) -> int:
        """
        Load value of item in given section
        """
        assert s_section in _LS_CONFIG_SECTIONS
        assert s_item in _LS_CONFIG_ITEMS[_LS_CONFIG_SECTIONS.index(s_section)]

        return self._config_params.getint(s_section, s_item)

    def di_get_all_config_items(self, s_section: str) -> dict:
        """
        Load all values of items in given section
        and convert them to a dictionary (name: index)
        """
        assert s_section in _LS_CONFIG_SECTIONS

        sd_params = dict(self._config_params.items(s_section))
        for p_key, p_value in sd_params.items():
            sd_params[p_key] = int(p_value) - 1
        return sd_params

    def i_get_max_column(self, s_section: str) -> dict:
        """
        Returns maximum column index from all items in the given section
        """
        assert s_section in _LS_CONFIG_SECTIONS, \
            ">{0}< must be a section name from\n>{1}<"\
            .format(s_section, _LS_CONFIG_SECTIONS)

        i_section = _LS_CONFIG_SECTIONS.index(s_section)
        return self._max_col[i_section]

    def _check_config(self):
        """
        Do a complete validation of the config.ini file:
        make sure all parameters are set and of the necessary type.
        Returns False if any validation failed.
        """

        def _compare_lists(
                ls_actual: list,
                ls_expected: list,
                s_label: str,
                o_error) -> bool:
            """
            compares two lists and outputs any errors;
            returns True if lists have identical contents, else False.
            """

            # 1 - make sure we have same number of elements
            #     in both lists

            if len(ls_expected) != len(ls_actual):
                o_error.report_error(
                    "Number of {0} do not match:\n"
                    "Expected number: {1}\n"
                    "Actual numer: {2}"
                    .format(
                        s_label,
                        len(ls_expected),
                        len(ls_actual)))
                return False

            # 2 - compare lists: convert to sets and use set magic

            ss_actual = set(ls_actual)
            ss_expected = set(ls_expected)

            if ss_actual == ss_expected:
                return True

            for s_expected in ss_expected.difference(ss_actual):
                o_error.report_error(
                    "Expected item >{0}< not found."
                    .format(s_expected))

            return False

        # 1 - start to compare all lists

        b_result = _compare_lists(
            self._config_params.sections(),
            _LS_CONFIG_SECTIONS,
            'sections', self._o_error)
        if b_result:
            pass
        else:
            return False

        for i_item, s_section in enumerate(_LS_CONFIG_SECTIONS):
            b_result = b_result and _compare_lists(
                self._config_params[s_section],
                _LS_CONFIG_ITEMS[i_item],
                'items in section ' + s_section, self._o_error)

        # 2 - sections ..._col must have integer values > 0

        for i_item, s_section in enumerate(_LS_CONFIG_SECTIONS):
            if s_section[-5:] == '_cols':
                for s_item in self._config_params[s_section]:
                    s_value = self._config_params.get(s_section, s_item)
                    if s_value.isnumeric():
                        i_value = int(s_value)
                        if i_value > self._max_col[i_item]:
                            self._max_col[i_item] = i_value
                    else:
                        self._o_error.report_error(
                            "Section >{0}< Item >{1}<"
                            " is not numeric: >{2}<."
                            .format(s_section, s_item, s_value))
                        b_result = False
        return b_result
