#!/usr/bin/env python3

# standards
import re as _re
from typing import Callable, Iterable, List, Optional, Type, TypeVar, overload

# 3rd parties
from typing_extensions import Literal  # for pre-3.8 pythons

# poisk
from . import many
from .exceptions import ManyFound
from .pods import SearchablePods
from .types import XPathType


T = TypeVar('T')  # pylint: disable=invalid-name

TPrime = TypeVar('TPrime')


@overload
def re(
    needle: str,
    haystack: str,
    parse: None = None,
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
    flags: int = 0,
) -> str:
    """
    Find and return the only match of `needle` (a regex) in `haystack` (a str). If `parse` is None, and allow_mismatch is False,
    then we return a str.
    """

@overload
def re(
    needle: str,
    haystack: str,
    parse: None = None,
    *,
    allow_mismatch: Literal[True],
    allow_many: bool = False,
    flags: int = 0,
) -> Optional[str]:
    """
    When `parse` is None and `allow_mismatch` is True, then we return an `Optional[str]`.
    """

@overload
def re(
    needle: _re.Pattern,
    haystack: str,
    parse: None = None,
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
) -> str:
    """
    Regex needles can also be expressed as `re.Pattern` objects. Note that in that case the `flags` kwarg can't be used.
    """

@overload
def re(
    needle: _re.Pattern,
    haystack: str,
    parse: None = None,
    *,
    allow_mismatch: Literal[True],
    allow_many: bool = False,
) -> Optional[str]:
    """
    When `needle` is a compiled re.Pattern, `parse` is None, and `allow_mismatch` is True, then we return an `Optional[str]`. Here
    again there are no **kwargs.
    """

@overload
def re(
    needle: str,
    haystack: str,
    parse: Callable[[str], T],
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
    flags: int = 0,
) -> T:
    """
    When `parse` is given, then we return whatever type `parse` returns.
    """

@overload
def re(
    needle: str,
    haystack: str,
    parse: Callable[[str], T],
    *,
    allow_mismatch: Literal[True],
    allow_many: bool = False,
    flags: int = 0,
) -> Optional[T]:
    """
    When `parse` is not None, and `allow_mismatch` is True, then we return whatever type `parse` returns, or None.
    """

@overload
def re(
    needle: _re.Pattern,
    haystack: str,
    parse: Callable[[str], T],
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
) -> T:
    """
    In this case too, `needle` can be a `re.Pattern` object. Again in this case the `flags` kwarg can't be used.
    """

@overload
def re(
    needle: _re.Pattern,
    haystack: str,
    parse: Callable[[str], T],
    *,
    allow_mismatch: Literal[True],
    allow_many: bool = False,
) -> Optional[T]:
    """
    And if `allow_mismatch` is True, then the result is optional.
    """

def re(needle, haystack, parse=None, *, allow_mismatch=False, allow_many=False, flags=0):
    return _one(
        needle,
        haystack,
        many.re(
            needle,
            haystack,
            parse,
            allow_mismatch=allow_mismatch,
            flags=flags,
        ),
        allow_many,
    )


@overload
def etree(
    needle: str,
    haystack: XPathType,
    parse: None = None,
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
    **kwargs
) -> XPathType:
    """
    `needle` is an XPath/CSS query. If `parse` is None, we return an Element. See notes at `many.etree`.
    """

@overload
def etree(
    needle: str,
    haystack: XPathType,
    parse: None = None,
    *,
    allow_mismatch: Literal[True],
    allow_many: bool = False,
    **kwargs
) -> Optional[XPathType]:
    """
    When `parse=None` and `allow_mismatch=True`, we return an `Optional[Element]`
    """

@overload
def etree(
    needle: str,
    haystack: XPathType,
    parse: Callable[[XPathType], T],
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
    **kwargs
) -> T:
    """
    When `parse` is not None, we return whatever type `parse` returns.
    """

@overload
def etree(
    needle: str,
    haystack: XPathType,
    parse: Callable[[XPathType], T],
    *,
    allow_mismatch: Literal[True],
    allow_many: bool = False,
    **kwargs
) -> Optional[T]:
    """
    When `parse` is not None and `allow_mismatch=True`, we return whatever type `parse` returns, or None.
    """

@overload
def etree(
    needle: str,
    haystack: XPathType,
    parse: Callable[[str], T],
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
    **kwargs
) -> T:
    """
    When `parse` is a callable that accepts a `str`, we return whatever type `parse` returns. See notes at the parallel annotation
    for `many.etree`.
    """

@overload
def etree(
    needle: str,
    haystack: XPathType,
    parse: Callable[[str], T],
    *,
    allow_mismatch: Literal[True],
    allow_many: bool = False,
    **kwargs
) -> Optional[T]:
    """
    When `parse` is a callable that accepts a `str` and `allow_mismatch=True`, we return whatever type `parse` returns, or None.
    """

def etree(needle, haystack, parse=None, *, allow_mismatch=False, allow_many=False, **kwargs):
    return _one(
        needle,
        haystack,
        many.etree(
            needle,
            haystack,
            parse,
            allow_mismatch=allow_mismatch,
            **kwargs,
        ),
        allow_many,
    )


@overload
def pods(
    needle: str,
    haystack: SearchablePods,
    parse: None = None,
    *,
    type: None = None,
    allow_mismatch: Literal[False] = False,
) -> object:
    """
    When `parse` is None and `type` is None, we return an object.
    """

@overload
def pods(
    needle: str,
    haystack: SearchablePods,
    parse: None = None,
    *,
    type: Type[T],
    allow_mismatch: Literal[False] = False,
) -> T:
    """
    If `type` is specified, we return that.
    """

@overload
def pods(
    needle: str,
    haystack: SearchablePods,
    parse: None = None,
    *,
    type: None = None,
    allow_mismatch: Literal[True],
) -> Optional[object]:
    """
    If `allow_mismatch` is True and `type` is None, we return an `object`, or None
    """

@overload
def pods(
    needle: str,
    haystack: SearchablePods,
    parse: None = None,
    *,
    type: Type[T],
    allow_mismatch: Literal[True],
) -> Optional[T]:
    """
    If `type` is specified and `allow_mismatch=True`, we return a `type` instance, or None.
    """

@overload
def pods(
    needle: str,
    haystack: SearchablePods,
    parse: Callable[[object], T],
    *,
    type: None = None,
    allow_mismatch: Literal[False] = False,
) -> T:
    """
    If `parse` is not None, we return whatever type `parse` returns.
    """

@overload
def pods(
    needle: str,
    haystack: SearchablePods,
    parse: Callable[[T], TPrime],
    *,
    type: Type[T],
    allow_mismatch: Literal[False] = False,
) -> TPrime:
    """
    If `parse` is set and `type` is set, then `parse` must accept an instance of `type`, and we return whatever `parse` returns
    """

@overload
def pods(
    needle: str,
    haystack: SearchablePods,
    parse: Callable[[object], T],
    *,
    type: None = None,
    allow_mismatch: Literal[True],
) -> Optional[T]:
    """
    If `parse` is set and `allow_mismatch=True`, we return whatever type `parse` returns, or None.
    """

@overload
def pods(
    needle: str,
    haystack: SearchablePods,
    parse: Callable[[T], TPrime],
    *,
    type: Type[T],
    allow_mismatch: Literal[True],
) -> Optional[TPrime]:
    """
    If `type` is set, `parse` is set and `allow_mismatch=True`, `parse` must accept an instance of `type`, and we return whatever
    type `parse` returns, or None.
    """

def pods(needle, haystack, parse=None, *, type=None, allow_mismatch=False, allow_many=False):
    return _one(
        needle,
        haystack,
        many.pods(
            needle,
            haystack,
            parse,
            type=type,
            allow_mismatch=allow_mismatch,
        ),
        allow_many,
    )


@overload
def filter(
    needle: Callable[[T], object],
    haystack: Iterable[T],
    parse: None = None,
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
) -> T:
    """
    `haystack` is a sequence of T elements, and `needle` must accept `T` values. If `parse` is None, and allow_mismatch=False, we
    return a T.
    """

@overload
def filter(
    needle: Callable[[T], object],
    haystack: Iterable[T],
    parse: None = None,
    *,
    allow_mismatch: Literal[True],
    allow_many: bool = False,
) -> Optional[T]:
    """
    `haystack` is a sequence of T elements, and `needle` must accept `T` values. If `parse` is None, and allow_mismatch=True, we
    return a T, or None.
    """

@overload
def filter(
    needle: Callable[[T], object],
    haystack: Iterable[T],
    parse: Callable[[T], TPrime],
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
) -> TPrime:
    """
    If `parse` is not None, and `allow_mismatch=False`, then we return whatever type `parse` returns.
    """

@overload
def filter(
    needle: Callable[[T], object],
    haystack: Iterable[T],
    parse: Callable[[T], TPrime],
    *,
    allow_mismatch: Literal[True],
    allow_many: bool = False,
) -> Optional[TPrime]:
    """
    If `parse` is not None, and `allow_mismatch=True`, then we return whatever type `parse` returns, or None.
    """

def filter(needle, haystack, parse=None, *, allow_mismatch=False, allow_many=False):
    return _one(
        needle,
        haystack,
        many.filter(
            needle,
            haystack,
            parse,
            allow_mismatch=allow_mismatch,
        ),
        allow_many,
    )


def _one(needle: object, haystack: object, results: List[T], allow_many: bool):
    if not results:
        return None  # allow_mismatch must have been True
    if len(results) > 1 and not allow_many:
        raise ManyFound(needle, haystack)
    return results[0]