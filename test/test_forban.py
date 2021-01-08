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
        <p id="first">Au large, <b>forban</b>!</p>
        <p class="second">Au large, flibustier!</p>
      </body>
    </html>
    '''
)


@pytest.mark.parametrize(
    'collection, test, options, expected',
    [
        ('abracadabra', r'br.c', {}, 'brac'),
        ('abracadabra', r'b.a', {}, MoreThanOne),
        ('abracadabra', r'b.a', {'allow_many': True}, 'bra'),
        ('abracadabra', r'brr', {}, Mismatch),
        ('abracadabra', r'brr', {'allow_mismatch': True}, None),

        (HTML_DOC, 'body/p/b/text()', {}, 'forban'),
        (HTML_DOC, './body/p/b/text()', {}, 'forban'),
        (HTML_DOC, '/body/p/b/text()', {}, 'forban'),
        (HTML_DOC, '//body/p/b/text()', {}, 'forban'),
        (HTML_DOC, 'b/text()', {}, 'forban'),
        (HTML_DOC, '//b/text()', {}, 'forban'),
        (HTML_DOC, 'i/text()', {}, Mismatch),
        (HTML_DOC, 'i/text()', {'allow_mismatch': True}, None),
        (HTML_DOC, 'p/text()', {}, MoreThanOne),
        (HTML_DOC, 'p/text()', {'allow_many': True}, 'Au large, '),

        (HTML_DOC, 'p b', {}, '<b>forban</b>!'),
        (HTML_DOC, 'p > b', {}, '<b>forban</b>!'),
        (HTML_DOC, 'body b', {}, '<b>forban</b>!'),
        (HTML_DOC, 'body > b', {}, Mismatch),
        (HTML_DOC, 'body > b', {'allow_mismatch': True}, None),
        (HTML_DOC, 'p', {}, MoreThanOne),
        (HTML_DOC, 'p', {'allow_many': True}, '<p id="first">Au large, <b>forban</b>!</p>'),
        (HTML_DOC, 'p#first b', {}, '<b>forban</b>!'),
        (HTML_DOC, 'p.second', {}, '<p class="second">Au large, flibustier!</p>'),

        (['', None, False, 'boo'], bool, {}, 'boo'),
        (['', None, False, 'boo'], lambda v: v == 'boom', {}, Mismatch),
        (['', None, False, 'boo'], lambda v: v == 'boom', {'allow_mismatch': True}, None),
        (['', None, False, 'boo'], lambda v: not v, {}, MoreThanOne),
        (['', None, False, 'boo'], lambda v: not v, {'allow_many': True}, ''),
    ]
)
def test_one(collection, test, options, expected):
    try:
        result = one(test, collection, **options)
    except Exception as ex:  # anything at all, pylint: disable=broad-except
        if isinstance(expected, type) and issubclass(expected, Exception):
            assert isinstance(ex, expected)
        else:
            raise
    else:
        if isinstance(result, ET._Element):  # pylint: disable=protected-access
            result = ET.tostring(result, encoding=str).strip()
        assert result == expected
