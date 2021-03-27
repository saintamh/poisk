#!/usr/bin/env python3

"""
Implements a function for searching in Plain Old Data Structures.


Initially this was going to use JMESPath, but that library has a few limitations that made it tricky to use here:

<> We can't easily tell these two apart:

       >>> jmespath.search("list", {"list": [1, 2]})
       [1, 2]
       >>> jmespath.search("list[]", {"list": [1, 2]})
       [1, 2]

   But the difference matters to us here, because a `one.pods` of the list should work (you're finding the one list at that path),
   whereas a `one.pods` of the second should raise `ManyFound` (since the list has more than one element).

<> We can't tell these apart either:

       >>> jmespath.search("myvalue", {"myvalue": None})
       None
       >>> jmespath.search("myvalue", {})
       None

   But again the difference matters to us. `one.pods` should return `None` in the first case, but raise `NotFound` in the second.

So we hack our own, and it does the job.


Note that this is therefore a lot simpler and much less featured than JMESPath. For instance we don't do filters like
"locations[?state == 'WA'].name", we don't have the pipe operator, functions like `sort` etc. But these aren't really necessary
when working in Python, as you can just as easily write those as list expressions or function calls.
"""


# standards
from collections.abc import Mapping, Sequence
import re
from typing import Iterable, List, Mapping as MappingType, Type, TypeVar, Union, overload


CHILDREN = object()


T = TypeVar('T')  # pylint: disable=invalid-name

SearchablePods = Union[MappingType, list, tuple]  # NB not using `Sequence` as we don't want to include `str`


@overload
def pods_search(
    needle: str,
    haystack: SearchablePods,
) -> List[object]:
    ...

@overload
def pods_search(
    needle: str,
    haystack: SearchablePods,
    type: Type[T],
) -> List[T]:
    ...


def pods_search(
    needle: str,
    haystack: SearchablePods,
    type = None,
):
    results = []
    stack = [(haystack, list(_parse_steps(needle)))]
    while stack:
        node, steps = stack.pop()
        if not steps:
            if type is not None and not isinstance(node, type):
                raise TypeError(f'Expected {type.__name__}, found {node.__class__.__name__}')
            results.append(node)
        else:
            head, *tail = steps
            if head is CHILDREN:
                if isinstance(node, Sequence) and not isinstance(node, str):
                    for element in reversed(node):
                        stack.append((element, tail))
            elif (isinstance(node, Mapping) and head in node) or (isinstance(node, Sequence) and isinstance(head, int)):
                stack.append((node[head], tail))  # type: ignore  # mypy gets confused but I think it's fine
    return results


def _parse_steps(needle: str) -> Iterable[Union[object]]:
    """
    Splits the user-specified `needle` into its components. See examples of the supported format in `test_poisk.py`.

    >>> list(_parse_steps("a.b.c"))
    ["a", "b", "c"]
    >>> list(_parse_steps("a[].b[0].c"))
    ["a", CHILDREN, "b", 0, "c"]
    """
    pos = 0
    re_step = re.compile(
        r'''
          \s*
          (?:
              "  (?P<double> (?:[^\\"]|\\.)+ ) "
            | '  (?P<single> (?:[^\\']|\\.)+ ) '
            |    (?P<word> \w+ )
            | \[ (?P<index> \d+ ) \]
            |    (?P<brackets> \[\] )
          )
          (?: \s*\.\s* | (?=\s*\[) | $ )
        ''',
        flags=re.X,
    )
    while pos < len(needle):
        match = re_step.match(needle, pos)
        if not match:
            raise ValueError(f"Can't parse needle at '{needle[pos:]}'")
        groups = match.groupdict()
        if groups.get('double') or groups.get('single'):
            string: str = groups.get('double') or groups.get('single')  # type: ignore[assignment]
            yield re.sub(r'\\(.)', r'\1', string)
        elif groups.get('index'):
            yield int(groups['index'])
        elif groups.get('brackets'):
            yield CHILDREN
        else:
            yield groups.get('word')
        pos = match.end()
