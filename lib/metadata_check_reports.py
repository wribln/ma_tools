"""metadata_check_reports

Implements a class for error reporting including keeping
counts of errors.
"""

_STD_ITEM_ERROR_MSG = "Record ending in row {0}, {1}:\n{2}"


class ErrorReports:
    """
    Error counting and reporting
    _n_error_count          holds the total number of errors reported so far
    """

    def __init__(self):
        self._n_error_count = 0

    def b_is_valid(self) -> bool:
        """
        returns true if object is in a valid state - useful only for
        assertions
        """
        return \
            (self._n_error_count is not None) and \
            (self._n_error_count >= 0)

    def n_error_count(self) -> int:
        """
        return number of error messages written so far
        """
        return self._n_error_count

    def report_error(self, s_text: str):
        """
        formats and outputs the given message string;
        increases the global error count; terminates
        program if requested

            Parameter:
                s_text:                 the text to output
        """
        assert self.b_is_valid()
        assert s_text, 'non-empty string expected'

        self._n_error_count += 1
        print(s_text, '\n')

    # output standard error messages

    def report_bad_file(self, s_filename: str, o_error):
        """
        used to report any error with the given file
        (more assertions are done in the called function)
        """
        assert isinstance(o_error, Exception), 'o_error must be Exception'

        self.report_error(
            "Could not read file >{0}<\n"
            "Reason: >{1}<".
            format(s_filename, o_error.strerror))

    def report_empty_file(self, s_filename: str):
        """
        used to produce an error message when the file is empty
        (assertions are done in the called function)
        """
        self.report_error(
            "File is empty >{0}<".format(s_filename))

    def report_missing_field(
            self, i_line: int, s_label: str):
        """
        reports a missing item in a record
        """
        self.report_with_std_msg(
            i_line, s_label,
            "Required field must not be empty."
            )

    def report_with_std_msg(
            self, i_line: int, s_label: str, s_text: str):
        """
        reports an error on an item using a standard message
        """
        self.report_error(
            _STD_ITEM_ERROR_MSG.format(
                i_line, s_label, s_text)
            )


def report_log(s_text: str):
    """
    formats and outputs the given message string without increasing
    the global error count (useful to output subtitles)
    """
    print(s_text)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
