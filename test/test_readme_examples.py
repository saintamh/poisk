#!/usr/bin/env python3

# standards
from doctest import DocTestParser, DocTestRunner
from pathlib import Path
import re

# 3rd parties
import lxml.etree as ET
import pytest

# poisk
import poisk


README_FILE = Path(__file__).parent / '..' / 'README.md'


NAMESPACE = {
    'ET': ET,
    'find_all': poisk.find_all,
    'find_one': poisk.find_one,
    're': re,
}


def _iter_readme_examples():
    return re.findall(
        r'```python\s+(.+?)```',
        README_FILE.read_text('UTF-8'),
        flags=re.S,
    )


@pytest.mark.parametrize('block', _iter_readme_examples())
def test_readme_examples(block):
    parser = DocTestParser()
    test = parser.get_doctest(block, NAMESPACE, README_FILE.name, README_FILE.name, 0)
    runner = DocTestRunner()
    runner.run(test)
    assert not runner.failures
