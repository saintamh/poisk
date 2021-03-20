#!/usr/bin/env python3

# standards
from collections.abc import Mapping, Sequence
import re

# 3rd parties
import lxml.etree as ET
import pytest

# poisk
from poisk import ManyFound, NotFound, find_all, find_one


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


FIRST_P = find_one(
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
    'haystack, needle, options, expected',
    [

        # regex matching
        ('abracadabra', r'br.c', {}, 'brac'),
        ('abracadabra', r'br(.)c', {}, 'a'),
        ('abracadabra', r'a(.+)a(.+)a(.+)a(.+)a', {}, ('br', 'c', 'd', 'br')),
        ('abracadabra', r'b.a', {}, ManyFound),
        ('abracadabra', r'b.a', {'allow_many': True}, 'bra'),
        ('abracadabra', r'brr', {}, NotFound),
        ('abracadabra', r'brr', {'allow_mismatch': True}, None),
        ('abracadabra', r'BR.C', {}, NotFound),

        # regex matching kwags
        ('abracadabra', r'B R . C', {}, NotFound),
        ('abracadabra', r'B R . C', {'flags': re.I|re.X}, 'brac'),
        ('abracadabra', 'a', {'made_up_kwarg': True}, TypeError),

        # pods matching
        ({'number': 1926}, 'number', {}, 1926),
        ({'string': 's'}, 'string', {}, 's'),
        ({'dict': {'k': 'v'}}, 'dict', {}, {'k': 'v'}),
        ({'null': None}, 'null', {}, None),
        ({}, 'anything', {}, NotFound),
        ({}, 'anything', {'allow_mismatch': True}, None),
        # if the needle resolves to a single list, we return the list. Empty lists are fine
        ({'list': []}, 'list', {}, []),
        ({'list': [1, 2, 3]}, 'list', {}, [1, 2, 3]),
        # if the needle ends in `[]`, however, meaning that we intent to select the list's elements, then the list must have a
        # single element
        ({'list': []}, 'list[]', {}, NotFound),
        ({'list': []}, 'list[]', {'allow_mismatch': True}, None),
        ({'list': [1]}, 'list[]', {}, 1),
        ({'list': [1, 2]}, 'list[]', {}, ManyFound),
        ({'list': [1, 2]}, 'list[]', {'allow_many': True}, 1),
        ({'list': [[1, 2]]}, 'list[]', {}, [1, 2]),
        ({'list_of_obj': [{'v': 1}, {'v': 2}]}, 'list_of_obj', {}, [{'v': 1}, {'v': 2}]),
        ({'list_of_obj': [{'v': 1}, {'v': 2}]}, 'list_of_obj[]', {}, ManyFound),
        ({'list_of_obj': [{'v': 1}, {'v': 2}]}, 'list_of_obj[].v', {}, ManyFound),
        ({'list_of_obj': [{'v': 1}, {'other': 2}]}, 'list_of_obj[].v', {}, 1),
        ({'list_of_obj': [{'v': 1}, {'other': 2}]}, 'list_of_obj[].k', {}, NotFound),
        ({'one two': 12}, 'one two', {}, ValueError),  # can't parse the needle
        ({'one two': 12}, '"one two"', {}, 12),
        ({'one two': 12}, "'one two'", {}, 12),
        ({'"hello"': 12}, '\'"hello"\'', {}, 12),
        # any sequence can be traversed the same as a list
        ({'tuple': ({'v': 1},)}, 'tuple[].v', {}, 1),
        ({'seq': MySequence({'v': 1})}, 'seq[].v', {}, 1),
        (MyMapping(x=MySequence(12)), 'x[]', {}, 12),
        # '[]' needs to be quoted
        ({'list[]': [1, 2, 3]}, 'list[]', {}, NotFound),
        ({'list[]': [1, 2, 3]}, '"list[]"', {}, [1, 2, 3]),
        # list index
        ({'n': [0, 1, 2]}, 'n[0]', {}, 0),

        # xpath matching
        (HTML_DOC, 'body/p/b/text()', {}, 'forban'),
        (HTML_DOC, './body/p/b/text()', {}, 'forban'),
        (HTML_DOC, '/body/p/b/text()', {}, 'forban'),
        (HTML_DOC, '//body/p/b/text()', {}, 'forban'),
        (HTML_DOC, 'b/text()', {}, 'forban'),
        (HTML_DOC, '//b/text()', {}, 'forban'),
        (HTML_DOC, 'i/text()', {}, NotFound),
        (HTML_DOC, 'i/text()', {'allow_mismatch': True}, None),
        (HTML_DOC, 'p/text()', {}, ManyFound),
        (HTML_DOC, 'p/text()', {'allow_many': True}, 'Au large, '),

        # Element.xpath() kwargs, used for namespaces, or passing arbitrary variables, see https://lxml.de/xpathxslt.html
        (HTML_DOC, '//p[@id = $my_var]/b', {'my_var': 'first'}, '<b>forban</b>!'),
        (XML_DOC, 'foo/bar/text()', {}, NotFound),
        (XML_DOC, 'x:foo/y:bar/text()', {'namespaces': {'x': 'http://wrong.com/blah', 'y': 'http://other.com/boo'}}, NotFound),
        (XML_DOC, 'x:foo/y:bar/text()', {'namespaces': {'x': 'http://xml.com/ns1', 'y': 'http://xml.com/ns2'}}, 'Text'),

        # xpath matching is limited to the given node's subtree
        (FIRST_P.getparent(), 'b', {}, ManyFound),
        (FIRST_P, 'b', {}, ManyFound),
        (FIRST_P, '/b', {}, '<b>one has <b>nests</b></b>'),
        (FIRST_P, './b', {}, '<b>one has <b>nests</b></b>'),
        (FIRST_P, '//b', {}, ManyFound),
        (FIRST_P, './/b', {}, ManyFound),

        # css matching
        (HTML_DOC, 'p b', {}, '<b>forban</b>!'),
        (HTML_DOC, 'p > b', {}, '<b>forban</b>!'),
        (HTML_DOC, 'body b', {}, '<b>forban</b>!'),
        (HTML_DOC, 'body > b', {}, NotFound),
        (HTML_DOC, 'body > b', {'allow_mismatch': True}, None),
        (HTML_DOC, 'p', {}, ManyFound),
        (HTML_DOC, 'p', {'allow_many': True}, '<p id="first">Au large, <b>forban</b>!</p>'),
        (HTML_DOC, 'p#first b', {}, '<b>forban</b>!'),
        (HTML_DOC, 'p.second', {}, '<p class="second">Au large, flibustier!</p>'),

        # accessing attributes using xpath
        (FIRST_P, '@id', {}, 'one'),
        (FIRST_P, './@id', {}, 'one'),
        (FIRST_P, '/@id', {}, 'one'),

        # arbitrary list filtering
        (['', None, False, 'boo'], bool, {}, 'boo'),
        (['', None, False, 'boo'], lambda v: v == 'boom', {}, NotFound),
        (['', None, False, 'boo'], lambda v: v == 'boom', {'allow_mismatch': True}, None),
        (['', None, False, 'boo'], lambda v: not v, {}, ManyFound),
        (['', None, False, 'boo'], lambda v: not v, {'allow_many': True}, ''),

        # list filtering takes no kwargs
        ([1, 2, 3], lambda v: v, {'anything_at_all': True}, TypeError),

        # unsupported types
        (MyClass(), 'needle', {}, TypeError),
        (MyClass(), 'needle', {'allow_mismatch': True}, TypeError),

        # subclassing a string works
        (MyString('hello'), r'.+(?=.)', {}, 'hell'),

        # anything with an 'xpath' method works
        (MyTree(HTML_DOC), 'body/p/b/text()', {}, 'forban'),
        (MyTree(HTML_DOC), 'p b', {}, '<b>forban</b>!'),

        # `parse` is applied iff a match was found
        ('I have 10 brothers', r'\d+', {'parse': int}, 10),
        ('I have no brothers', r'\d+', {'parse': int, 'allow_mismatch': True}, None),
    ]
)
def test_find_one(haystack, needle, options, expected):
    try:
        result = find_one(needle, haystack, **options)
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
    'haystack, needle, options, expected',
    [

        # regex matching
        ('abracadabra', r'.a.', {}, ['rac', 'dab']),
        ('abracadabra', r'(.a).', {}, ['ra', 'da']),
        ('abracadabra', r'(.)a(.)', {}, [('r', 'c'), ('d', 'b')]),
        ('abracadabra', r'z', {}, NotFound),
        ('abracadabra', r'z', {'allow_mismatch': True}, []),

        # regex flags
        ('abracadabra', r'. A .', {}, NotFound),
        ('abracadabra', r'. A .', {'flags': re.I|re.X}, ['rac', 'dab']),
        ('abracadabra', 'a', {'made_up_kwarg': True}, TypeError),

        # regex objects are also accepted
        ('abracadabra', re.compile(r'.a.'), {}, ['rac', 'dab']),

        # pods matching
        ({'number': 1926}, 'number', {}, [1926]),
        ({'string': 's'}, 'string', {}, ['s']),
        ({'dict': {'k': 'v'}}, 'dict', {}, [{'k': 'v'}]),
        ({'null': None}, 'null', {}, [None]),
        ({}, 'anything', {}, NotFound),
        ({}, 'anything', {'allow_mismatch': True}, []),
        # if the needle resolves to a single list, we return the one list. Empty lists are fine
        ({'list': []}, 'list', {}, [[]]),
        ({'list': [1, 2, 3]}, 'list', {}, [[1, 2, 3]]),
        # if the needle ends in `[]`, however, meaning that we intent to select the list's elements, then the list must have
        # elements
        ({'list': []}, 'list[]', {}, NotFound),
        ({'list': []}, 'list[]', {'allow_mismatch': True}, []),
        ({'list': [1]}, 'list[]', {}, [1]),
        ({'list': [1, 2]}, 'list[]', {}, [1, 2]),
        ({'list': [[1, 2]]}, 'list[]', {}, [[1, 2]]),
        ([1, 2], '[]', {}, [1, 2]),
        ([], '[]', {}, NotFound),
        ({'list_of_obj': [{'v': 1}, {'v': 2}]}, 'list_of_obj', {}, [[{'v': 1}, {'v': 2}]]),
        ({'list_of_obj': [{'v': 1}, {'v': 2}]}, 'list_of_obj[]', {}, [{'v': 1}, {'v': 2}]),
        ({'list_of_obj': [{'v': 1}, {'v': 2}]}, 'list_of_obj[].v', {}, [1, 2]),
        ({'list_of_obj': [{'v': 1}, {'other': 2}]}, 'list_of_obj[].v', {}, [1]),
        ({'list_of_obj': [{'v': 1}, {'other': 2}]}, 'list_of_obj[].k', {}, NotFound),
        ({'v': [[0,1], [2,3], [4,5]]}, 'v[][0]', {}, [0, 2, 4]),

        # xpath matching
        (HTML_DOC, 'body/p/text()', {}, ['Au large, ', '!', 'Au large, flibustier!']),
        (HTML_DOC, 'body/div/text()', {}, NotFound),
        (HTML_DOC, 'body/div/text()', {'allow_mismatch': True}, []),

        # xpath matching is limited to the given node's subtree
        (FIRST_P.getparent(), 'b', {}, ['<b>one has <b>nests</b></b>', '<b>nests</b>', '<b>two</b>']),
        (FIRST_P, 'b', {}, ['<b>one has <b>nests</b></b>', '<b>nests</b>']),
        (FIRST_P, '/b', {}, ['<b>one has <b>nests</b></b>']),
        (FIRST_P, './b', {}, ['<b>one has <b>nests</b></b>']),
        (FIRST_P, '//b', {}, ['<b>one has <b>nests</b></b>', '<b>nests</b>']),
        (FIRST_P, './/b', {}, ['<b>one has <b>nests</b></b>', '<b>nests</b>']),

        # css matching
        (HTML_DOC, 'p', {}, ['<p id="first">Au large, <b>forban</b>!</p>', '<p class="second">Au large, flibustier!</p>']),
        (HTML_DOC, 'div', {}, NotFound),
        (HTML_DOC, 'div', {'allow_mismatch': True}, []),

        # arbitrary list filtering
        (list(range(10)), lambda i: i % 3 == 0, {}, [0, 3, 6, 9]),
        (list(range(10)), lambda i: i > 12, {}, NotFound),
        (list(range(10)), lambda i: i > 12, {'allow_mismatch': True}, []),

        # list filtering takes no kwargs
        ([1, 2, 3], lambda v: v, {'anything_at_all': True}, TypeError),

        # unsupported types
        (MyClass(), 'needle', {}, TypeError),
        (MyClass(), 'needle', {'allow_many': True}, TypeError),

        # subclassing a string works
        (MyString('hello'), r'[aeiou]', {}, ['e', 'o']),

        # anything with an 'xpath' method works
        (MyTree(HTML_DOC), 'body/p/b/text()', {}, ['forban']),
        (MyTree(HTML_DOC), 'p b', {}, ['<b>forban</b>!']),

        # `parse` is applied to every match
        ('in my honest opinion', r'\b\w', {'parse': str.upper}, ['I', 'M', 'H', 'O']),
    ]
)
def test_find_all(haystack, needle, options, expected):
    try:
        results = find_all(needle, haystack, **options)
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
