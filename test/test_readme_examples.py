#!/usr/bin/env python3

# standards
from doctest import DocTestParser, DocTestRunner
from pathlib import Path
import re

# poisk
import poisk


NAMESPACE = {
    'find_many': poisk.find_many,
    'find_one': poisk.find_one,
    're': re,
}


def test_readme_examples():
    readme_file = Path(__file__).parent / '..' / 'README.md'
    all_blocks = re.findall(
        r'```python\s+(.+?)```',
        readme_file.read_text('UTF-8'),
        flags=re.S,
    )
    for block in all_blocks:
        parser = DocTestParser()
        test = parser.get_doctest(block, NAMESPACE, readme_file.name, readme_file.name, 0)
        runner = DocTestRunner()
        runner.run(test)
        assert not runner.failures
