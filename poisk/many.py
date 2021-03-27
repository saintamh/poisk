#!/usr/bin/env python3

# standards
import re as _re
from typing import Callable, Iterable, List, Type, TypeVar, overload

# 3rd parties
from cssselect import HTMLTranslator

# poisk
from .exceptions import NotFound
from .pods import SearchablePods, pods_search
from .types import XPathType


_css_to_xpath = HTMLTranslator().css_to_xpath

_filter = filter


# type annotations used below

T = TypeVar('T')  # pylint: disable=invalid-name

TPrime = TypeVar('TPrime')



@overload
def re(
    needle: str,
    haystack: str,
    parse: None = None,
    *,
    allow_mismatch: bool = False,
    flags: int = 0,
) -> List[str]:
    """
    Find and return all matches of `needle` in `haystack`. If `parse` is None, then we return a list of str's.
    """

@overload
def re(
    needle: _re.Pattern,
    haystack: str,
    parse: None = None,
    *,
    allow_mismatch: bool = False,
) -> List[str]:
    """
    Regex needles can also be expressed as `re.Pattern` objects. Note that in that case the `flags` kwarg can't be used.
    """

@overload
def re(
    needle: str,
    haystack: str,
    parse: Callable[[str], T],
    *,
    allow_mismatch: bool = False,
    flags: int = 0,
) -> List[T]:
    """
    When `parse` is not None, then we return a list of whatever type `parse` returns.
    """

@overload
def re(
    needle: _re.Pattern,
    haystack: str,
    parse: Callable[[str], T],
    *,
    allow_mismatch: bool = False,
) -> List[T]:
    """
    In this case too, `needle` can be a `re.Pattern` object. Again in this case the `flags` kwarg can't be used.
    """

def re(needle, haystack, parse=None, *, allow_mismatch=False, flags=0):
    results = _re.findall(needle, haystack, flags=flags)
    return _many(
        needle,
        haystack,
        results,
        parse,
        allow_mismatch=allow_mismatch,
    )


@overload
def etree(
    needle: str,
    haystack: XPathType,
    parse: None = None,
    *,
    allow_mismatch: bool = False,
    **kwargs
) -> List[XPathType]:
    """
    When `needle` is an XPath/CSS query. If `parse` is None, we return a list of Elements. Note that this means that if the xpath
    selects a string (e.g. "./a/@href"), then you need to specify `parse=str` to please the type checker.

    Note that the type annotation here is slightly off. It says we accept any type that has an `xpath` method, and then return a
    list of the same type, which isn't 100% correct: the output should be a list of ET._Element objects, but the input could be an
    ET._ElementTree object. Hopefully it'll work out, since the two classes have very similar interfaces.
    """

@overload
def etree(
    needle: str,
    haystack: XPathType,
    parse: Callable[[XPathType], T],
    *,
    allow_mismatch: bool = False,
    **kwargs
) -> List[T]:
    """
    When `parse` is not None, we return a list of whatever type `parse` returns. Use this with `parse=str` if the xpath selector
    selects text.
    """

@overload
def etree(
    needle: str,
    haystack: XPathType,
    parse: Callable[[str], T],
    *,
    allow_mismatch: bool = False,
    **kwargs
) -> List[T]:
    """
    When `parse` is a callable that accepts a `str`, we return a list of whatever type `parse` returns. Use this with e.g.
    `parse=int` to convert text selected by the xpath to an int. Note that it can still fail at runtime if the xpath selector
    doesn't return a string.
    """

def etree(needle, haystack, parse=None, *, allow_mismatch=False, **kwargs):
    if _re.search(r'[@/]', needle):
        # XPath is able to search outside of a given node's subtree. We don't want that, we only want to change the subtree. If the
        # path doesn't already start with "./", prepend a dot, and slashes if there weren't already some.
        xpath = _re.sub(r'^(?!\./)/{,2}', lambda m: '.' + (m.group() or '//'), needle)
    else:
        xpath = _css_to_xpath(needle)
    results = haystack.xpath(xpath, **kwargs)
    return _many(
        needle,
        haystack,
        results,
        parse,
        allow_mismatch=allow_mismatch,
    )


@overload
def pods(
    needle: str,
    haystack: SearchablePods,
    parse: None = None,
    *,
    type: None = None,
    allow_mismatch: bool = False,
) -> List[object]:
    """
    PODS search
    """

@overload
def pods(
    needle: str,
    haystack: SearchablePods,
    parse: None = None,
    *,
    type: Type[T],
    allow_mismatch: bool = False,
) -> List[T]:
    """
    If you add type=T, then we return a list of T
    """

@overload
def pods(
    needle: str,
    haystack: SearchablePods,
    parse: Callable[[object], T],
    *,
    type: None = None,
    allow_mismatch: bool = False,
) -> List[T]:
    """
    If `parse` is not None, we return a list of whatever type `parse` returns.
    """

@overload
def pods(
    needle: str,
    haystack: SearchablePods,
    parse: Callable[[T], TPrime],
    *,
    type: Type[T],
    allow_mismatch: bool = False,
) -> List[TPrime]:
    """
    You can again check for a specific type using the `type` kwargs. If `parse` is set, then it must accept an instance of `type`.
    """

def pods(needle, haystack, parse=None, *, type=None, allow_mismatch=False):
    results = pods_search(needle, haystack, type=type)
    return _many(
        needle,
        haystack,
        results,
        parse,
        allow_mismatch=allow_mismatch,
    )


@overload
def filter(
    needle: Callable[[T], object],
    haystack: Iterable[T],
    parse: None = None,
    *,
    allow_mismatch: bool = False,
) -> List[T]:
    """
    `haystack` is a sequence of T elements, and `needle` must accept `T` values. If `parse` is None, we return T's.
    """

@overload
def filter(
    needle: Callable[[T], object],
    haystack: Iterable[T],
    parse: Callable[[T], TPrime],
    *,
    allow_mismatch: bool = False,
) -> List[TPrime]:
    """
    If `needle` is callable, and `parse` is not None, then we return a list of whatever type `parse` returns.
    """

def filter(needle, haystack, parse=None, allow_mismatch=False):
    results = list(_filter(needle, haystack))
    return _many(
        needle,
        haystack,
        results,
        parse,
        allow_mismatch=allow_mismatch,
    )


def _many(needle, haystack, results, parse=None, allow_mismatch=False):
    """
    Finds and returns all matches of `needle` within `haystack`. If no match is found and `allow_mismatch` is `False` (the
    default), a `NotFound` exception is raised. In other words an empty list is never returned, unless `allow_mismatch` is set to
    `True`.

    Behaviour and remaining `**kwargs` depend on the type of `haystack`:

    If `haystack` is a string, `needle` is a regular expression, either as a string or as a compiled regex object. The returned
    list will be the same as returned by `re.findall`: if the regex has capturing groups, we'll return a list of tuples containing
    the captured groups of all matches, and if the regex has no groups, we'll return a list of the matching strings. The `**kwargs`
    are passed to `re.findall`, and so the only allowed key is `flags`.

    If `haystack` is an ElementTree object, `needle` is an XPath or CSS selector, and the returned list will contain the
    subelements matched by the selector.

    If `needle` is a function, it will be called in turn with each element of `haystack`, and the returned list will contain only
    those elements for which the function returned a truthy value. This is done by calling `filter`, which accepts no kwargs, and
    so in this case no `**kwargs` may be provided.

    `parse`, if specified, is a callable that will be applied to every return, map-style.
    """
    if not results and not allow_mismatch:
        raise NotFound(needle, haystack)
    if parse is not None:
        results = list(map(parse, results))
    return results
