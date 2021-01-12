#!/usr/bin/env python3

# standards
import re

# 3rd parties
import lxml.etree as ET
import pytest

# forban
from forban import MoreThanOne, NotFound, one


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


XML_DOC = ET.XML(
    '''
    <doc
      xmlns:a="http://xml.com/ns1"
      xmlns:b="http://xml.com/ns2"
    >
      <a:foo>
         <b:bar>Text</b:bar>
      </a:foo>
    </doc>
    '''
)


@pytest.mark.parametrize(
    'collection, test, options, expected',
    [

        # regex matching
        ('abracadabra', r'br.c', {}, 'brac'),
        ('abracadabra', r'br(.)c', {}, 'a'),
        ('abracadabra', r'a(.+)a(.+)a(.+)a(.+)a', {}, ('br', 'c', 'd', 'br')),
        ('abracadabra', r'b.a', {}, MoreThanOne),
        ('abracadabra', r'b.a', {'allow_many': True}, 'bra'),
        ('abracadabra', r'brr', {}, NotFound),
        ('abracadabra', r'brr', {'allow_mismatch': True}, None),
        ('abracadabra', r'BR.C', {}, NotFound),

        # regex flags
        ('abracadabra', r'BR.C', {'flags': re.I}, 'brac'),

        # xpath matching
        (HTML_DOC, 'body/p/b/text()', {}, 'forban'),
        (HTML_DOC, './body/p/b/text()', {}, 'forban'),
        (HTML_DOC, '/body/p/b/text()', {}, 'forban'),
        (HTML_DOC, '//body/p/b/text()', {}, 'forban'),
        (HTML_DOC, 'b/text()', {}, 'forban'),
        (HTML_DOC, '//b/text()', {}, 'forban'),
        (HTML_DOC, 'i/text()', {}, NotFound),
        (HTML_DOC, 'i/text()', {'allow_mismatch': True}, None),
        (HTML_DOC, 'p/text()', {}, MoreThanOne),
        (HTML_DOC, 'p/text()', {'allow_many': True}, 'Au large, '),

        # Element.xpath() kwargs, used for namespaces, or passing arbitrary variables, see https://lxml.de/xpathxslt.html
        (HTML_DOC, '//p[@id = $my_var]/b', {'my_var': 'first'}, '<b>forban</b>!'),
        (XML_DOC, 'foo/bar/text()', {}, NotFound),
        (XML_DOC, 'x:foo/y:bar/text()', {'namespaces': {'x': 'http://wrong.com/blah', 'y': 'http://other.com/boo'}}, NotFound),
        (XML_DOC, 'x:foo/y:bar/text()', {'namespaces': {'x': 'http://xml.com/ns1', 'y': 'http://xml.com/ns2'}}, 'Text'),

        # css matching
        (HTML_DOC, 'p b', {}, '<b>forban</b>!'),
        (HTML_DOC, 'p > b', {}, '<b>forban</b>!'),
        (HTML_DOC, 'body b', {}, '<b>forban</b>!'),
        (HTML_DOC, 'body > b', {}, NotFound),
        (HTML_DOC, 'body > b', {'allow_mismatch': True}, None),
        (HTML_DOC, 'p', {}, MoreThanOne),
        (HTML_DOC, 'p', {'allow_many': True}, '<p id="first">Au large, <b>forban</b>!</p>'),
        (HTML_DOC, 'p#first b', {}, '<b>forban</b>!'),
        (HTML_DOC, 'p.second', {}, '<p class="second">Au large, flibustier!</p>'),

        # arbitrary list filtering
        (['', None, False, 'boo'], bool, {}, 'boo'),
        (['', None, False, 'boo'], lambda v: v == 'boom', {}, NotFound),
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
