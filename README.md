Poisk implements a thin veneer of convenience over familiar search functions.
It can be used for:

* regular expression searches;
* `jq`- or JMESPath-style data structure searches;
* XPath queries over `ElementTree`s;
* `filter`-style iterable filtering.

It offers just two functions, `find_one` and `find_all`.


#### `find_one`

The `find_one` function performs a search, checks that there is exactly one
match (no more, no less), and returns it.

So this:

```python
>>> find_one(r'\d+', 'Vostok 1 was the first spaceflight')
'1'
```

is roughly equivalent to this:

```python
>>> number, = re.findall(r'\d+', 'Vostok 1 was the first spaceflight')
>>> number
'1'
```

but with nicer syntax and clearer error handling.

If no matches are found, `NotFound` is raised, unless `allow_mismatch=True` is
passed to the function, and if multiple matches are found, `ManyFound` is
raised, unless `allow_many=True` is passed, in which case only the first match
is returned.

```python
>>> find_one(r'\w+', '')
Traceback (most recent call last):
  ....
poisk.exceptions.NotFound: '\\w+'

>>> print(find_one(r'\w+', '', allow_mismatch=True))
None

>>> find_one(r'\w+', 'The quick brown fox')
Traceback (most recent call last):
  ....
poisk.exceptions.ManyFound: '\\w+'

>>> find_one(r'\w+', 'The quick brown fox', allow_many=True)
'The'
```


#### `find_all`

The `find_all` function works similarly, but returns a list of all matches.
Unlike `find_one` it allows more than one match, but it does raise an exception
if no matches are found.

So this:

```python
>>> find_all(r'\w+', 'over the lazy dog')
['over', 'the', 'lazy', 'dog']
```

is roughly equivalent to this:

```python
>>> values = re.findall(r'\w+', 'over the lazy dog')
>>> if not values:
...     raise ValueError("No matches")
>>> values
['over', 'the', 'lazy', 'dog']
```

If no matches are found `NotFound` is raised, unless `allow_mismatch=True` is
passed to the function:

```python
>>> find_all(r'\w+', '')
Traceback (most recent call last):
 ...
poisk.exceptions.NotFound: '\\w+'

>>> find_all(r'\w+', '', allow_mismatch=True)
[]
```


#### Regex search

If `needle` is a regular expression and `haystack` is a string, Poisk performs
a regular expression search. Like `re.findall`, if the regular expression
pattern contains capturing groups, the returned values are tuples of those
groups, and if not, the whole match is returned.

```python
>>> find_one(r'\d+', '10 to the dozen')
'10'

>>> find_one(r'(\d+)', '10 to the dozen')
'10'

>>> find_one(r'(\w+) to the (\w+)', '10 to the dozen')
('10', 'dozen')

>>> find_all(r'(\w+)-(\w+)', 'Deep-fried Greek-style pork-chops')
[('Deep', 'fried'), ('Greek', 'style'), ('pork', 'chops')]
```


#### XPath/CSS search

If the `haystack` parameter is an ElementTree, the search functions perform
XPath or CSS selection (using the
[cssselect](https://cssselect.readthedocs.io/) package):

```python
>>> document = ET.fromstring('<ul><li id="one">One</li><li>Two</li><li>Three</li></ul>')

>>> find_all('li/text()', document)
['One', 'Two', 'Three']

>>> one = find_one('li#one', document)
>>> ET.tostring(one, encoding=str)
'<li id="one">One</li>'
```


#### PODS (Plain Old Data Structure) search

If the `haystack` parameter is a `list` or a `dict`, the search is done using a
query language similar to that of [jq](https://stedolan.github.io/jq/) or
[JMESPath](https://jmespath.org/):

```python
>>> payload = {
...  "records": [
...    {"id": 1, "v": 78},
...    {"id": 2},
...    {"id": 3, "v": 91, "z": "zed"},
...  ],
... }

>>> find_all('records[].v', payload)
[78, 91]

>>> find_one('records[].z', payload)
'zed'
```


#### filtering

If the `needle` is a callable, then the standard `filter` function is used to
sift through the `haystack`, which must be iterable. This is useful to ensure
that the result has either only a single match, or is not empty.

```python
>>> find_one(lambda s: s == ''.join(reversed(s)), ['abracadabra', 'kayak', 'canal'])
'kayak'

>>> find_all(str.isupper, ['a', 'b', 'c'])
Traceback (most recent call last):
 ...
poisk.exceptions.NotFound: <method 'isupper' of 'str' objects>
```


#### the `parse` function

Both `find_one` and `find_all` accept an optional `parse` parameter, which, if
specified, should be a callable will be applied to returns when results are
found. If no results are found (and if `allow_mismatch=True`), it is not
called.

```python
>>> find_one(r'\d+', '3 little piggies')
'3'

>>> find_one(r'\d+', '3 little piggies', parse=int)
3

>>> print(find_one(r'\d+', 'Three little piggies', parse=int, allow_mismatch=True))
None
```
