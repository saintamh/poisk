#!/usr/bin/env python3

# standards
from doctest import DocTestParser, DocTestRunner
from pathlib import Path
import re

# poisk
import poisk


def test_readme_examples():
    readme_file = Path(__file__).parent / '..' / 'README.md'
    doctest_str = '\n\n'.join(
        re.sub(
            # We auto-insert doctest <BLANKLINE> markers into the examples. Don't want to put them in the README itself, it would
            # make the examples a bit confusing.
            r'\n\n(?!>>>)',
            '\n<BLANKLINE>\n',
            block_str
        )
        for block_str in re.findall(
            r'```python\s+(.+?)```',
            readme_file.read_text('UTF-8'),
            flags=re.S,
        )
    )
    assert doctest_str
    print(doctest_str)
    parser = DocTestParser()
    runner = DocTestRunner()
    runner.run(
        parser.get_doctest(
            doctest_str,
            dict(globals(), poisk=poisk, __file__=readme_file),
            'README.md',
            'README.md',
            0,
        ),
    )
    assert runner.failures == 0
