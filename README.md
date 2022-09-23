Poisk implements a thin veneer of convenience over familiar search functions.
It can be used for:

* regular expression searches;
* jq- or JMESPath-style searches in lists and dicts;
* XPath queries over ElementTrees.


## `one` and `many`

At the core of Poisk is the idea that you'd rather raise an exception than
extract the wrong data. We want to check that our expectations hold. If we
expect our search to return matches, it should not return an empty list. If we
expect a single matching element, there shouldn't be two.

The search functions are grouped into two modules, called `one` and `many`. The
search functions under `one` expect to find a single matching value, which they
return. They raise `NotFound` if no results are found, and `ManyFound` if more
than one match is found.

Here is an example using `one.re`, which performs regular expression searches:

```python
>>> from poisk import one

>>> one.re(r'H\w+', 'Hello world!')
'Hello'

>>> one.re(r'H\w+', 'Greetings, world!')
Traceback (most recent call last):
    ...
poisk.exceptions.NotFound: 'H\\w+' in 'Greetings, world!'

>>> one.re(r'H\w+', 'Ho Ho Ho, world!')
Traceback (most recent call last):
    ...
poisk.exceptions.ManyFound: 'H\\w+' in 'Ho Ho Ho, world!'
```

The corresponding functions under `many` expect one or more results, which they
return as a list. They raise `NotFound` if no matches are found:

```python
>>> from poisk import many

>>> many.re(r'\w+', 'Hello!')
['Hello']

>>> many.re(r'\w+', 'Hello world!')
['Hello', 'world']

>>> many.re(r'\d+', 'Hello world!')
Traceback (most recent call last):
    ...
poisk.exceptions.NotFound: '\\d+' in 'Hello world!'
```


## Supported search functions

The previous two examples use `one.re` and `many.re` to perform regular
expression searches, using the standard
[re](https://docs.python.org/3/library/re.html) module.

Also available are functions for xpath search over ElementTrees using
[lxml.etree](https://lxml.de/api/):

```python
>>> import lxml.etree as ET
>>> from poisk import many, one

>>> document = ET.HTML('''
...     <div>
...         <p id="p1">First paragraph</p>
...         <p id="p2">Second paragraph</p>
...     </div>
... ''')

>>> one.etree('p[@id="p1"]/text()', document)
'First paragraph'

>>> many.etree('p/text()', document)
['First paragraph', 'Second paragraph']
```

The same `one.etree` and `many.etree` functions accept CSS selectors (via
[cssselect](https://github.com/scrapy/cssselect)):

```python
>>> one.etree('p#p1', document).text
'First paragraph'
```

The `one.pods` and `many.pods` functions allow searches using Plain Old Data
Structures (dicts and lists) using a jq- or JMESPath-style query language:

```python
>>> data = {
...     "payload": {
...         "total": 3,
...         "results": [
...             {"id": 1},
...             {"id": 2},
...             {"id": 3},
...         ],
...     },
... }

>>> one.pods('payload.total', data)
3

>>> many.pods('payload.results[].id', data)
[1, 2, 3]
```

The `test/` directory contains many more examples of the sort functionality that Poisk offers.