#!/usr/bin/env python3

# standards
from pathlib import Path
from textwrap import dedent

# 3rd parties
from mypy.build import build  # pylint: disable=no-name-in-module
from mypy.modulefinder import BuildSource  # pylint: disable=no-name-in-module
from mypy.options import Options  # pylint: disable=no-name-in-module
import pytest
import yaml


def load_fixtures():
    auto_imports = dedent('''\
        import re
        import lxml.etree
        from poisk import find_all, find_one
    ''')
    fixtures_file = Path(__file__).parent / 'test_type_checking.yaml'
    doc = yaml.safe_load(fixtures_file.read_text('UTF-8'))
    for test_case in doc['test_cases']:
        yield (
            test_case['name'],
            auto_imports + test_case['code'],
            test_case['expected_error'],
        )


@pytest.mark.parametrize(
    'code_str, expected_error',
    [
        pytest.param(code_str, expected_error, id=name)
        for name, code_str, expected_error in load_fixtures()
    ],
)
def test_type_checking(code_str, expected_error):
    """ Check that mypy can recognise correct invocations of poisk. """
    options = Options()
    options.show_error_codes = True
    options.ignore_missing_imports = True
    all_errors = []
    build(
        [BuildSource(None, None, code_str)],
        options,
        flush_errors=lambda errors, *rest, **kwargs: all_errors.extend(errors),
    )
    if expected_error is None:
        if all_errors:
            pytest.fail('\n'.join(all_errors))
    else:
        assert expected_error in '\n'.join(all_errors)
