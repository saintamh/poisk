#!/usr/bin/env python3

# standards
from collections.abc import Mapping, Sequence
import re

# 3rd parties
from cssselect import HTMLTranslator

# poisk
from .pods import pods_search


_css_to_xpath = HTMLTranslator().css_to_xpath


class PoiskException(ValueError):

    def __init__(self, needle, haystack):
        super().__init__(repr(needle))
        self.needle = needle
        self.haystack = haystack


class NotFound(PoiskException):
    pass


class ManyFound(PoiskException):
    pass


def find_all(needle, haystack, allow_mismatch=False, type=None, **kwargs):
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
