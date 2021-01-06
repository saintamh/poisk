#!/usr/bin/env python3

# 3rd parties
import lxml.etree as ET
import pytest

# forban
from forban import Mismatch, MoreThanOne, one


HTML_DOC = ET.HTML(
    '''
    <html>
      <body>
        <p>Au large, <b>forban</b>!</p>
        <p>Au large, flibustier!</p>
      </body>
    </html>
    '''
)


@pytest.mark.parametrize(
    'test, collection, expected',
    [
        (r'br.c', 'abracadabra', 'brac'),
        (r'b.a', 'abracadabra', MoreThanOne),
        (r'brr', 'abracadabra', Mismatch),

        ('body/p/b/text()', HTML_DOC, 'forban'),
        ('./body/p/b/text()', HTML_DOC, 'forban'),
        ('/body/p/b/text()', HTML_DOC, 'forban'),
        ('//body/p/b/text()', HTML_DOC, 'forban'),
        ('b/text()', HTML_DOC, 'forban'),
        ('//b/text()', HTML_DOC, 'forban'),
        ('i/text()', HTML_DOC, Mismatch),
        ('p/text()', HTML_DOC, MoreThanOne),

        ('p b', HTML_DOC, '<b>forban</b>!'),
        ('p > b', HTML_DOC, '<b>forban</b>!'),
        ('body b', HTML_DOC, '<b>forban</b>!'),
        ('body > b', HTML_DOC, Mismatch),
        ('p', HTML_DOC, MoreThanOne),

        (bool, ['', None, False, 'boo'], 'boo'),
        (bool, ['', None, False], Mismatch),
        (bool, ['', None, False, 'boo', 'ah!'], MoreThanOne),
    ]
)
def test_one(test, collection, expected):
    try:
        result = one(test, collection)
    except Exception as ex:  # anything at all, pylint: disable=broad-except
        if isinstance(expected, type) and issubclass(expected, Exception):
            assert isinstance(ex, expected)
        else:
            raise
    else:
        if isinstance(result, ET._Element):  # pylint: disable=protected-access
            result = ET.tostring(result, encoding=str)
        assert result == expected
