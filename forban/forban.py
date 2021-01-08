#!/usr/bin/env python3

# standards
import re

try:
    # forban can be used with or without lxml. We'll fail at runtime if we try to select from an etree and lxml isn't loaded
    import lxml.etree as ET
except ImportError:
    ET = None

try:
    # Similarly, the cssselect package may or may not be present. We'll fail at runtime if trying to select from an etree using a
    # css expression
    from cssselect import HTMLTranslator
    css_to_xpath = HTMLTranslator().css_to_xpath
except ImportError:
    def css_to_xpath(*args, **kwargs):
        raise NotImplementedError('You must install cssselect in order to use CSS selectors')


class Mismatch(ValueError):
    pass

class MoreThanOne(ValueError):
    pass


def many(test, collection, allow_mismatch=False, **kwargs):
    if isinstance(collection, str):
        results = re.findall(test, collection, **kwargs)
    elif ET is not None and isinstance(collection, ET._Element):  # pylint: disable=protected-access
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
