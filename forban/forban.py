#!/usr/bin/env python3

# standards
import re

# 3rd parties
from cssselect import HTMLTranslator


css_to_xpath = HTMLTranslator().css_to_xpath


class Mismatch(ValueError):
    pass


class MoreThanOne(ValueError):
    pass


def many(test, collection, allow_mismatch=False, **kwargs):
    """
    Finds and returns all matches of `test` within `collection`. If no match is found and `allow_mismatch` is `False` (the
    default), a `Mismatch` exception is raised. In other words an empty list is never returned, unless `allow_mismatch` is set to
    `True`.

    Behaviour and remaining `**kwargs` depend on the type of the collection:

    If `collection` is a string, `test` is a regular expression, either as a string or as a compiled regex object. The returned
    list will be the same as returned by `re.findall`: if the regex has capturing groups, we'll return a list of tuples containing
    the captured groups of all matches, and if the regex has no groups, we'll return a list of the matching strings. The `**kwargs`
    are passed to `re.findall`, and so the only allowed key is `flags`.

    If `collection` is an ElementTree object, `test` is an XPath or CSS selector, and the returned list will contain the
    subelements matched by the selector.

    If `test` is a function, it will be called in turn with each element of `collection`, and the returned list will contain only
    those elements for which the function returned a truthy value. This is done by calling `filter`, which accepts no kwargs, and
    so in this case no `**kwargs` may be provided.
    """
    if isinstance(collection, str):
        results = re.findall(test, collection, **kwargs)
    elif callable(getattr(collection, 'xpath', None)):
        if '/' in test:
            test = re.sub(r'^/*', './/', test)
        else:
            test = css_to_xpath(test)
        results = collection.xpath(test, **kwargs)
    elif callable(test):
        results = list(filter(test, collection, **kwargs))
    else:
        raise TypeError(f"Don't know how to select from {type(collection)}")
    if not results and not allow_mismatch:
        raise Mismatch(test)
    return results


def one(test, collection, allow_mismatch=False, allow_many=False, **kwargs):
    """
    Finds and returns the only match of `test` within `collection`. If no match is found and `allow_mismatch` is `False` (the
    default), a `Mismatch` exception is raised; if `allow_mismatch` is True, `None` is returned. If more than one match is found
    and `allow_many` is `False` (the default), a `MoreThanOne` exception is raised; if `allow_many` is True, the first match is
    returned.

    In other words this function ensures that only a single value exists that matches the given selector, unless `allow_mismatch`
    or `allow_many` is set to `True`.

    Behaviour and remaining `**kwargs` depend on the type of the collection, see the docstring for `many` for details.
    """
    results = many(test, collection, allow_mismatch=allow_mismatch, **kwargs)
    if not results:
        assert allow_mismatch
        return None
    if len(results) > 1 and not allow_many:
        raise MoreThanOne(test)
    return results[0]


def one_of(collection, *tests, allow_mismatch=False, allow_many=False):
    return one(
        bool,
        [
            one(t, collection, allow_mismatch=True, allow_many=allow_many)
            for t in tests
        ],
        allow_mismatch=allow_mismatch,
        allow_many=allow_many,
    )
