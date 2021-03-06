#!/usr/bin/env python3

# standards
from collections.abc import Mapping, Sequence
import re
from typing import Any, Callable, Iterable, List, TypeVar, overload

# 3rd parties
from cssselect import HTMLTranslator
from typing_extensions import Protocol  # for pre-3.8 pythons

# poisk
from .exceptions import ManyFound, NotFound
from .pods import pods_search


_css_to_xpath = HTMLTranslator().css_to_xpath


# type annotations used below

T = TypeVar('T')  # pylint: disable=invalid-name

TPrime = TypeVar('TPrime')

class HasXPathMethod(Protocol):

    @property
    def xpath(self) -> Callable[..., Any]:
        # This declaration here is not actually for a property, it's for a method called `xpath`, whose signature we don't care
        # about (beyond its name). Apparently this is the way you can get mypy to recognize this. This hacky solution of using a
        # @property was coined (by the BDFL) here: https://github.com/python/mypy/issues/9560#issuecomment-705955103
        ...

XPathType = TypeVar('XPathType', bound=HasXPathMethod)



@overload
def find_all(
    needle: str,
    haystack: str,
    type: None = None,
    allow_mismatch: bool = False,
    **kwargs
) -> List[str]:
    """
    When `haystack` is a str, then `needle` is a regex for searching in it. If `type` is None, then we return a list of str's.
    """

@overload
def find_all(
    needle: str,
    haystack: str,
    type: Callable[[str], T],
    allow_mismatch: bool = False,
    **kwargs
) -> List[T]:
    """
    When `haystack` is a str and `type` is not None, then we return a list of whatever type `type` returns.
    """


@overload
def find_all(
    needle: str,
    haystack: XPathType,
    type: None = None,
    allow_mismatch: bool = False,
    **kwargs
) -> List[XPathType]:
    """
    When `haystack` is an lxml.ET._Element, needle is an XPath/CSS query. If `type` is None, we return a list of Elements. Note
    that this means that if the xpath selects a string (e.g. "./a/@href"), then you need to specify type=str to please the type
    checker.

    Note that the type annotation here is slightly off. It says we accept any type that has an `xpath` method, and then return a
    list of the same type, which isn't 100% correct: the output should be a list of ET._Element objects, but the input could be an
    ET._ElementTree object. Hopefully it'll work out, since the two classes have very similar interfaces.
    """

@overload
def find_all(
    needle: str,
    haystack: XPathType,
    type: Callable[[XPathType], T],
    allow_mismatch: bool = False,
    **kwargs
) -> List[T]:
    """
    When `haystack` is an lxml.ET._Element and `type` is not None, we return a list of whatever type `type` returns. Use this with
    `type=str` if the xpath selector selects text.
    """

@overload
def find_all(
    needle: str,
    haystack: XPathType,
    type: Callable[[str], T],
    allow_mismatch: bool = False,
    **kwargs
) -> List[T]:
    """
    When `haystack` is an lxml.ET._Element and `type` is a callable that accepts a `str`, we return a list of whatever type `type`
    returns. Use this with e.g. `type=int` to convert text selected by the xpath to an int. Note that it can still fail at runtime
    if the xpath selector doesn't return a string.
    """


@overload
def find_all(
    needle: Callable[[T], bool],
    haystack: Iterable[T],
    type = None,
    allow_mismatch: bool = False,
    **kwargs
) -> List[T]:
    """
    If `needle` is callable, then `haystack` is a sequence of T elements, and `needle` must accept `T` values. If `type` is None,
    we return T's.
    """

@overload
def find_all(
    needle: Callable[[T], bool],
    haystack: Iterable[T],
    type: Callable[[T], TPrime],
    allow_mismatch: bool = False,
    **kwargs
) -> List[TPrime]:
    """
    If `needle` is callable, and `type` is not None, then we return a list of whatever type `type` returns
    """


def find_all(needle, haystack, type=None, allow_mismatch=False, **kwargs):
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

    `type`, if specified, is a callable that will be applied to every return, map-style.
    """

    if isinstance(haystack, str):
        results = re.findall(needle, haystack, **kwargs)
    elif callable(getattr(haystack, 'xpath', None)):
        if re.search(r'[@/]', needle):
            # XPath is able to search outside of a given node's subtree. We don't want that, we only want to change the subtree.
            # If the path doesn't already start with "./", prepend a dot, and slashes if there weren't already some.
            xpath = re.sub(r'^(?!\./)/{,2}', lambda m: '.' + (m.group() or '//'), needle)
        else:
            xpath = _css_to_xpath(needle)
        results = haystack.xpath(xpath, **kwargs)
    elif callable(needle):
        results = list(filter(needle, haystack, **kwargs))
    elif isinstance(haystack, (Mapping, Sequence)):
        results = pods_search(needle, haystack)
    else:
        if haystack is None:
            raise TypeError('haystack is None') from None
        else:
            raise TypeError(f"Don't know how to select from {type(haystack)}")

    if not results and not allow_mismatch:
        raise NotFound(needle, haystack)
    if type is not None:
        results = list(map(type, results))
    return results


def find_one(needle, haystack, allow_mismatch=False, allow_many=False, type=None, **kwargs):
    """
    Finds and returns the only match of `needle` within `haystack`. If no match is found and `allow_mismatch` is `False` (the
    default), a `NotFound` exception is raised; if `allow_mismatch` is True, `None` is returned. If more than one match is found
    and `allow_many` is `False` (the default), a `ManyFound` exception is raised; if `allow_many` is True, the first match is
    returned.

    In other words this function ensures that exactly one value exists that matches the given selector, unless `allow_mismatch` or
    `allow_many` is set to `True`. It only ever returns one value.

    `type`, if specified, is a callable that will be applied to the return value. If will not be applied to the `None` value that
    is returned if no match is found and allow_mismatch is True.

    Behaviour and remaining `**kwargs` depend on the type of the haystack, see the docstring for `many` for details.
    """
    results = find_all(needle, haystack, allow_mismatch=allow_mismatch, type=type, **kwargs)
    if not results:
        assert allow_mismatch
        return None
    if len(results) > 1 and not allow_many:
        raise ManyFound(needle, haystack)
    return results[0]
