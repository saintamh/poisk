#!/usr/bin/env python3

# pylint: disable=line-too-long

# standards
from collections.abc import Mapping, Sequence
import re

# 3rd parties
import lxml.etree as ET
import pytest

# poisk
from poisk import ManyFound, NotFound, many, one


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


FIRST_P = one.etree(
    '#one',
    ET.fromstring(
        '''
        <div>
          <p id="one">This is <b>one has <b>nests</b></b></p>
          <p id="two">This is <b>two</b></p>
        ''',
        parser=ET.HTMLParser(),
    )
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


class MyClass:
    # pylint: disable=too-few-public-methods
    pass


class MyString(str):
    # pylint: disable=too-few-public-methods
    pass


class MySequence(Sequence):

    def __init__(self, *values):
        self.values = values

    def __getitem__(self, item):
        return self.values[item]

    def __len__(self):
        return len(self.values)


class MyMapping(Mapping):

    def __init__(self, **items):
        self.items = items

    def __getitem__(self, item):
        return self.items[item]

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)


class MyTree:
    # pylint: disable=too-few-public-methods

    def __init__(self, element):
        self.element = element

    def xpath(self, *args, **kwargs):
        return self.element.xpath(*args, **kwargs)


@pytest.mark.parametrize(
    'find, haystack, needle, options, expected',
    [

        # regex matching
        (one.re, 'abracadabra', r'br.c', {}, 'brac'),
        (one.re, 'abracadabra', r'br(.)c', {}, 'a'),
        (one.re, 'abracadabra', r'a(.+)a(.+)a(.+)a(.+)a', {}, ('br', 'c', 'd', 'br')),
        (one.re, 'abracadabra', r'b.a', {}, ManyFound),
        (one.re, 'abracadabra', r'b.a', {'allow_many': True}, 'bra'),
        (one.re, 'abracadabra', r'brr', {}, NotFound),
        (one.re, 'abracadabra', r'brr', {'allow_mismatch': True}, None),
        (one.re, 'abracadabra', r'BR.C', {}, NotFound),

        # regex matching kwags
        (one.re, 'abracadabra', r'B R . C', {}, NotFound),
        (one.re, 'abracadabra', r'B R . C', {'flags': re.I|re.X}, 'brac'),
        (one.re, 'abracadabra', 'a', {'made_up_kwarg': True}, TypeError),

        # subclassing a string works
        (one.re, MyString('hello'), r'.+(?=.)', {}, 'hell'),

        # `parse` is applied iff a match was found
        (one.re, 'I have 10 brothers', r'\d+', {'parse': int}, 10),
        (one.re, 'I have no brothers', r'\d+', {'parse': int, 'allow_mismatch': True}, None),

        # pods matching
        (one.pods, {'number': 1926}, 'number', {}, 1926),
        (one.pods, {'string': 's'}, 'string', {}, 's'),
        (one.pods, {'dict': {'k': 'v'}}, 'dict', {}, {'k': 'v'}),
        (one.pods, {'null': None}, 'null', {}, None),
        (one.pods, {}, 'anything', {}, NotFound),
        (one.pods, {}, 'anything', {'allow_mismatch': True}, None),
        (one.pods, [{'number': 1926}], '[].number', {}, 1926),
        # if the needle resolves to a single list, we return the list. Empty lists are fine
        (one.pods, {'list': []}, 'list', {}, []),
        (one.pods, {'list': [1, 2, 3]}, 'list', {}, [1, 2, 3]),
        # if the needle ends in `[]`, however, meaning that we intent to select the list's elements, then the list must have a
        # single element
        (one.pods, {'list': []}, 'list[]', {}, NotFound),
        (one.pods, {'list': []}, 'list[]', {'allow_mismatch': True}, None),
        (one.pods, {'list': [1]}, 'list[]', {}, 1),
        (one.pods, {'list': [1, 2]}, 'list[]', {}, ManyFound),
        (one.pods, {'list': [1, 2]}, 'list[]', {'allow_many': True}, 1),
        (one.pods, {'list': [[1, 2]]}, 'list[]', {}, [1, 2]),
        (one.pods, {'list_of_obj': [{'v': 1}, {'v': 2}]}, 'list_of_obj', {}, [{'v': 1}, {'v': 2}]),
        (one.pods, {'list_of_obj': [{'v': 1}, {'v': 2}]}, 'list_of_obj[]', {}, ManyFound),
        (one.pods, {'list_of_obj': [{'v': 1}, {'v': 2}]}, 'list_of_obj[].v', {}, ManyFound),
        (one.pods, {'list_of_obj': [{'v': 1}, {'other': 2}]}, 'list_of_obj[].v', {}, 1),
        (one.pods, {'list_of_obj': [{'v': 1}, {'other': 2}]}, 'list_of_obj[].k', {}, NotFound),
        (one.pods, {'one two': 12}, 'one two', {}, ValueError),  # can't parse the needle
        (one.pods, {'one two': 12}, '"one two"', {}, 12),
        (one.pods, {'one two': 12}, "'one two'", {}, 12),
        (one.pods, {'"hello"': 12}, '\'"hello"\'', {}, 12),
        # any sequence can be traversed the same as a list
        (one.pods, {'tuple': ({'v': 1},)}, 'tuple[].v', {}, 1),
        (one.pods, {'seq': MySequence({'v': 1})}, 'seq[].v', {}, 1),
        (one.pods, MyMapping(x=MySequence(12)), 'x[]', {}, 12),
        # '[]' needs to be quoted
        (one.pods, {'list[]': [1, 2, 3]}, 'list[]', {}, NotFound),
        (one.pods, {'list[]': [1, 2, 3]}, '"list[]"', {}, [1, 2, 3]),
        # list index
        (one.pods, {'n': [0, 1, 2]}, 'n[0]', {}, 0),
        # type checking
        (one.pods, {'list': [1, 2, 3]}, 'list', {'type': list}, [1, 2, 3]),
        (one.pods, {'list': [1, 2, 3]}, 'list', {'type': int}, TypeError),
        (one.pods, {'list': []}, 'list', {'type': list}, []),
        (one.pods, {'list': []}, 'list[]', {'type': list}, NotFound),

        # xpath matching
        (one.etree, HTML_DOC, 'body/p/b/text()', {}, 'forban'),
        (one.etree, HTML_DOC, './body/p/b/text()', {}, 'forban'),
        (one.etree, HTML_DOC, '/body/p/b/text()', {}, 'forban'),
        (one.etree, HTML_DOC, '//body/p/b/text()', {}, 'forban'),
        (one.etree, HTML_DOC, 'b/text()', {}, 'forban'),
        (one.etree, HTML_DOC, '//b/text()', {}, 'forban'),
        (one.etree, HTML_DOC, 'i/text()', {}, NotFound),
        (one.etree, HTML_DOC, 'i/text()', {'allow_mismatch': True}, None),
        (one.etree, HTML_DOC, 'p/text()', {}, ManyFound),
        (one.etree, HTML_DOC, 'p/text()', {'allow_many': True}, 'Au large, '),

        # Element.xpath() kwargs, used for namespaces, or passing arbitrary variables, see https://lxml.de/xpathxslt.html
        (one.etree, HTML_DOC, '//p[@id = $my_var]/b', {'my_var': 'first'}, '<b>forban</b>!'),
        (one.etree, XML_DOC, 'foo/bar/text()', {}, NotFound),
        (one.etree, XML_DOC, 'x:foo/y:bar/text()', {'namespaces': {'x': 'http://wrong.com/blah', 'y': 'http://other.com/boo'}}, NotFound),
        (one.etree, XML_DOC, 'x:foo/y:bar/text()', {'namespaces': {'x': 'http://xml.com/ns1', 'y': 'http://xml.com/ns2'}}, 'Text'),

        # xpath matching is limited to the given node's subtree
        (one.etree, FIRST_P.getparent(), 'b', {}, ManyFound),
        (one.etree, FIRST_P, 'b', {}, ManyFound),
        (one.etree, FIRST_P, '/b', {}, '<b>one has <b>nests</b></b>'),
        (one.etree, FIRST_P, './b', {}, '<b>one has <b>nests</b></b>'),
        (one.etree, FIRST_P, '//b', {}, ManyFound),
        (one.etree, FIRST_P, './/b', {}, ManyFound),

        # css matching
        (one.etree, HTML_DOC, 'p b', {}, '<b>forban</b>!'),
        (one.etree, HTML_DOC, 'p > b', {}, '<b>forban</b>!'),
        (one.etree, HTML_DOC, 'body b', {}, '<b>forban</b>!'),
        (one.etree, HTML_DOC, 'body > b', {}, NotFound),
        (one.etree, HTML_DOC, 'body > b', {'allow_mismatch': True}, None),
        (one.etree, HTML_DOC, 'p', {}, ManyFound),
        (one.etree, HTML_DOC, 'p', {'allow_many': True}, '<p id="first">Au large, <b>forban</b>!</p>'),
        (one.etree, HTML_DOC, 'p#first b', {}, '<b>forban</b>!'),
        (one.etree, HTML_DOC, 'p.second', {}, '<p class="second">Au large, flibustier!</p>'),

        # accessing attributes using xpath
        (one.etree, FIRST_P, '@id', {}, 'one'),
        (one.etree, FIRST_P, './@id', {}, 'one'),
        (one.etree, FIRST_P, '/@id', {}, 'one'),

        # anything with an 'xpath' method works
        (one.etree, MyTree(HTML_DOC), 'body/p/b/text()', {}, 'forban'),
        (one.etree, MyTree(HTML_DOC), 'p b', {}, '<b>forban</b>!'),

        # arbitrary list filtering
        (one.filter, ['', None, False, 'boo'], bool, {}, 'boo'),
        (one.filter, ['', None, False, 'boo'], lambda v: v == 'boom', {}, NotFound),
        (one.filter, ['', None, False, 'boo'], lambda v: v == 'boom', {'allow_mismatch': True}, None),
        (one.filter, ['', None, False, 'boo'], lambda v: not v, {}, ManyFound),
        (one.filter, ['', None, False, 'boo'], lambda v: not v, {'allow_many': True}, ''),

        # list filtering takes no kwargs
        (one.filter, [1, 2, 3], lambda v: v, {'anything_at_all': True}, TypeError),
    ]
)
def test_find_one(find, haystack, needle, options, expected):
    try:
        result = find(needle, haystack, **options)
    except Exception as ex:  # anything at all, pylint: disable=broad-except
        if isinstance(expected, type) and issubclass(expected, Exception):
            assert isinstance(ex, expected)
        else:
            raise
    else:
        if isinstance(result, ET._Element):  # pylint: disable=protected-access
            result = ET.tostring(result, encoding=str).strip()
        assert result == expected


@pytest.mark.parametrize(
    'find, haystack, needle, options, expected',
    [

        # regex matching
        (many.re, 'abracadabra', r'.a.', {}, ['rac', 'dab']),
        (many.re, 'abracadabra', r'(.a).', {}, ['ra', 'da']),
        (many.re, 'abracadabra', r'(.)a(.)', {}, [('r', 'c'), ('d', 'b')]),
        (many.re, 'abracadabra', r'z', {}, NotFound),
        (many.re, 'abracadabra', r'z', {'allow_mismatch': True}, []),

        # regex flags
        (many.re, 'abracadabra', r'. A .', {}, NotFound),
        (many.re, 'abracadabra', r'. A .', {'flags': re.I|re.X}, ['rac', 'dab']),
        (many.re, 'abracadabra', 'a', {'made_up_kwarg': True}, TypeError),

        # regex objects are also accepted
        (many.re, 'abracadabra', re.compile(r'.a.'), {}, ['rac', 'dab']),

        # subclassing a string works
        (many.re, MyString('hello'), r'[aeiou]', {}, ['e', 'o']),

        # `parse` is applied to every match
        (many.re, 'in my honest opinion', r'\b\w', {'parse': str.upper}, ['I', 'M', 'H', 'O']),

        # xpath matching
        (many.etree, HTML_DOC, 'body/p/text()', {}, ['Au large, ', '!', 'Au large, flibustier!']),
        (many.etree, HTML_DOC, 'body/div/text()', {}, NotFound),
        (many.etree, HTML_DOC, 'body/div/text()', {'allow_mismatch': True}, []),

        # xpath matching is limited to the given node's subtree
        (many.etree, FIRST_P.getparent(), 'b', {}, ['<b>one has <b>nests</b></b>', '<b>nests</b>', '<b>two</b>']),
        (many.etree, FIRST_P, 'b', {}, ['<b>one has <b>nests</b></b>', '<b>nests</b>']),
        (many.etree, FIRST_P, '/b', {}, ['<b>one has <b>nests</b></b>']),
        (many.etree, FIRST_P, './b', {}, ['<b>one has <b>nests</b></b>']),
        (many.etree, FIRST_P, '//b', {}, ['<b>one has <b>nests</b></b>', '<b>nests</b>']),
        (many.etree, FIRST_P, './/b', {}, ['<b>one has <b>nests</b></b>', '<b>nests</b>']),

        # css matching
        (many.etree, HTML_DOC, 'p', {}, ['<p id="first">Au large, <b>forban</b>!</p>', '<p class="second">Au large, flibustier!</p>']),
        (many.etree, HTML_DOC, 'div', {}, NotFound),
        (many.etree, HTML_DOC, 'div', {'allow_mismatch': True}, []),

        # anything with an 'xpath' method works
        (many.etree, MyTree(HTML_DOC), 'body/p/b/text()', {}, ['forban']),
        (many.etree, MyTree(HTML_DOC), 'p b', {}, ['<b>forban</b>!']),

        # pods matching
        (many.pods, {'number': 1926}, 'number', {}, [1926]),
        (many.pods, {'string': 's'}, 'string', {}, ['s']),
        (many.pods, {'dict': {'k': 'v'}}, 'dict', {}, [{'k': 'v'}]),
        (many.pods, {'null': None}, 'null', {}, [None]),
        (many.pods, {}, 'anything', {}, NotFound),
        (many.pods, {}, 'anything', {'allow_mismatch': True}, []),
        # if the needle resolves to a single list, we return the one list. Empty lists are fine
        (many.pods, {'list': []}, 'list', {}, [[]]),
        (many.pods, {'list': [1, 2, 3]}, 'list', {}, [[1, 2, 3]]),
        # if the needle ends in `[]`, however, meaning that we intent to select the list's elements, then the list must have
        # elements
        (many.pods, {'list': []}, 'list[]', {}, NotFound),
        (many.pods, {'list': []}, 'list[]', {'allow_mismatch': True}, []),
        (many.pods, {'list': [1]}, 'list[]', {}, [1]),
        (many.pods, {'list': [1, 2]}, 'list[]', {}, [1, 2]),
        (many.pods, {'list': [[1, 2]]}, 'list[]', {}, [[1, 2]]),
        (many.pods, [1, 2], '[]', {}, [1, 2]),
        (many.pods, [], '[]', {}, NotFound),
        (many.pods, {'list_of_obj': [{'v': 1}, {'v': 2}]}, 'list_of_obj', {}, [[{'v': 1}, {'v': 2}]]),
        (many.pods, {'list_of_obj': [{'v': 1}, {'v': 2}]}, 'list_of_obj[]', {}, [{'v': 1}, {'v': 2}]),
        (many.pods, {'list_of_obj': [{'v': 1}, {'v': 2}]}, 'list_of_obj[].v', {}, [1, 2]),
        (many.pods, {'list_of_obj': [{'v': 1}, {'other': 2}]}, 'list_of_obj[].v', {}, [1]),
        (many.pods, {'list_of_obj': [{'v': 1}, {'other': 2}]}, 'list_of_obj[].k', {}, NotFound),
        (many.pods, {'v': [[0,1], [2,3], [4,5]]}, 'v[][0]', {}, [0, 2, 4]),

        # arbitrary list filtering
        (many.filter, list(range(10)), lambda i: i % 3 == 0, {}, [0, 3, 6, 9]),
        (many.filter, list(range(10)), lambda i: i > 12, {}, NotFound),
        (many.filter, list(range(10)), lambda i: i > 12, {'allow_mismatch': True}, []),

        # list filtering takes no kwargs
        (many.filter, [1, 2, 3], lambda v: v, {'anything_at_all': True}, TypeError),
    ]
)
def test_find_all(find, haystack, needle, options, expected):
    try:
        results = find(needle, haystack, **options)
    except Exception as ex:  # anything at all, pylint: disable=broad-except
        if isinstance(expected, type) and issubclass(expected, Exception):
            assert isinstance(ex, expected)
        else:
            raise
    else:
        assert isinstance(results, list), results
        results = [
            ET.tostring(element, encoding=str).strip()
            if isinstance(element, ET._Element)  # pylint: disable=protected-access
            else element
            for element in results
        ]
        assert results == expected
