"""
This module integrates SQLFluff with diff_cover's "diff-quality" tool.
"""
from diff_cover.hook import hookimpl as diff_cover_hookimpl
from diff_cover.violationsreporters.base import BaseViolationReporter, Violation

from sqlfluff.cli.commands import get_config, get_linter


class SQLFluffViolationReporter(BaseViolationReporter):
    """
    Class that implements diff-quality integration.
    """
    supported_extensions = ['sql']

    def __init__(self):
        """
        Calls the base class constructor to set the object's name.
        """
        super(SQLFluffViolationReporter, self).__init__('sqlfluff')

    def violations(self, src_path):
        """
        Given the path to a .sql file, analyze it and return a list of
        violations (i.e. formatting or style issues).

        :param src_path:
        :return: list of Violation
        """
        linter = get_linter(get_config())
        linter.output_func = None
        linted_path = linter.lint_path(src_path)
        result = []
        for violation in linted_path.files[0].violations:
            try:
                # Normal SQLFluff warnings
                message = violation.description
            except AttributeError:
                # Parse errors
                message = violation.message
            result.append(Violation(violation.line_no(), message))
        return result


@diff_cover_hookimpl
def diff_cover_report_quality():
    """
    This function is registered as a diff_cover entry point. diff-quality calls
    it in order to "discover" the SQLFluff plugin.

    :return: Object that implements the BaseViolationReporter ABC
    """
    return SQLFluffViolationReporter()
