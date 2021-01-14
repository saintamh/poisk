Poisk implements a thin veneer of convenience over familiar search functions.
It can be used for regular expression searches, `jq`-style data structure
searches, and XPath queries.


The `find_one` function performs a search, checks that there is exactly one
match, and returns it.

So this:

```python
>>> find_one(r'\d+', 'Vostok 1 was the first spaceflight')
'1'
```

is just a cleaner version of this:

```python
>>> number, = re.findall(r'\d+', 'Vostok 1 was the first spaceflight')
>>> number
'1'
```

with nicer syntax and clearer error handling.


The `find_many` function works similarly, but returns a list. It also raises an
exception if no matches are found.

So this:

```python
>>> payload = {"records": [{"id": 1, "v": 78}, {"id": 2}, {"id": 3, "v": 91}]}
>>> find_many(r'records[].v', payload)
[78, 91]
```

is just a cleaner version of this:

```python
>>> payload = {"records": [{"id": 1, "v": 78}, {"id": 2}, {"id": 3, "v": 91}]}
>>> values = [r["v"] for r in payload["records"] if "v" in r]
>>> if not values:
...     raise ValueError("No matches")
>>> values
[78, 91]
```
