#!/usr/bin/env python3

# standards
from typing import Any, Callable, Iterable, List, Optional, Tuple, Type, TypeVar, overload

# 3rd parties
from typing_extensions import Literal  # for pre-3.8 pythons

# poisk
from . import many
from .exceptions import ManyFound, NotFound
from .pods import SearchablePods
from .types import RegexType, XPathType


T = TypeVar('T')  # pylint: disable=invalid-name

TPrime = TypeVar('TPrime')


@overload
def re(
    needle: RegexType,
    haystack: str,
    parse: None = None,
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
    allow_duplicates: bool = False,
    flags: int = 0,
) -> str:
    """
    Find and return the only match of `needle` (a regex) in `haystack` (a str). If `parse` is None, and allow_mismatch is False,
    then we return a str.
    """

@overload
def re(
    needle: RegexType,
    haystack: str,
    parse: None = None,
    *,
    allow_mismatch: Literal[True],
    allow_many: bool = False,
    allow_duplicates: bool = False,
    flags: int = 0,
) -> Optional[str]:
    """
    When `parse` is None and `allow_mismatch` is True, then we return an `Optional[str]`.
    """

@overload
def re(
    needle: RegexType,
    haystack: str,
    parse: Callable[[str], T],
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
    allow_duplicates: bool = False,
    flags: int = 0,
) -> T:
    """
    When `parse` is given, then we return whatever type `parse` returns.
    """

@overload
def re(
    needle: RegexType,
    haystack: str,
    parse: Callable[[str], T],
    *,
    allow_mismatch: Literal[True],
    allow_many: bool = False,
    allow_duplicates: bool = False,
    flags: int = 0,
) -> Optional[T]:
    """
    When `parse` is not None, and `allow_mismatch` is True, then we return whatever type `parse` returns, or None.
    """

def re(needle, haystack, parse=None, *, allow_mismatch=False, allow_many=False, allow_duplicates=False, flags=0):
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
        allow_duplicates,
    )


@overload
def re_groups(
    needle: RegexType,
    haystack: str,
    parse: None = None,
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
    allow_duplicates: bool = False,
    flags: int = 0,
) -> Tuple[str, ...]:
    ...

@overload
def re_groups(
    needle: RegexType,
    haystack: str,
    parse: None = None,
    *,
    allow_mismatch: Literal[True],
    allow_many: bool = False,
    allow_duplicates: bool = False,
    flags: int = 0,
) -> Optional[Tuple[str, ...]]:
    ...

@overload
def re_groups(
    needle: RegexType,
    haystack: str,
    parse: Callable[[Tuple[str, ...]], T],
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
    allow_duplicates: bool = False,
    flags: int = 0,
) -> T:
    ...

@overload
def re_groups(
    needle: RegexType,
    haystack: str,
    parse: Callable[[Tuple[str, ...]], T],
    *,
    allow_mismatch: Literal[True],
    allow_many: bool = False,
    allow_duplicates: bool = False,
    flags: int = 0,
) -> Optional[T]:
    ...

def re_groups(needle, haystack, parse=None, *, allow_mismatch=False, allow_duplicates=False, allow_many=False, flags=0):
    return re(
        needle,
        haystack,
        parse,
        allow_mismatch=allow_mismatch,
        allow_many=allow_many,
        allow_duplicates=allow_duplicates,
        flags=flags,
    )

re_groups = re  # type: ignore


@overload
def etree(
    needle: str,
    haystack: XPathType,
    parse: None = None,
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
    allow_duplicates: bool = False,
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
    allow_duplicates: bool = False,
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
    allow_duplicates: bool = False,
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
    allow_duplicates: bool = False,
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
    allow_duplicates: bool = False,
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
    allow_duplicates: bool = False,
    **kwargs
) -> Optional[T]:
    """
    When `parse` is a callable that accepts a `str` and `allow_mismatch=True`, we return whatever type `parse` returns, or None.
    """

def etree(
    needle,
    haystack,
    parse=None,
    *,
    allow_mismatch=False,
    allow_many=False,
    allow_duplicates=False,
    **kwargs,
):
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
        allow_duplicates,
    )


@overload
def attrib(
    needle: str,
    haystack: XPathType,
    parse: None = None,
    *,
    allow_mismatch: Literal[False] = False,
) -> str:
    ...

@overload
def attrib(
    needle: str,
    haystack: XPathType,
    parse: None = None,
    *,
    allow_mismatch: Literal[True],
) -> Optional[str]:
    ...

@overload
def attrib(
    needle: str,
    haystack: XPathType,
    parse: Callable[[str], T],
    *,
    allow_mismatch: Literal[False] = False,
) -> T:
    ...

@overload
def attrib(
    needle: str,
    haystack: XPathType,
    parse: Callable[[str], T],
    *,
    allow_mismatch: Literal[True],
) -> Optional[T]:
    ...

def attrib(needle, haystack, parse=None, *, allow_mismatch=False):
    try:
        value = haystack.attrib[needle]
    except KeyError as error:
        if allow_mismatch:
            return None
        else:
            raise NotFound(needle, haystack) from error
    if parse:
        return parse(value)
    return value


@overload
def pods(
    needle: str,
    haystack: SearchablePods,
    parse: None = None,
    *,
    type: None = None,
    allow_mismatch: Literal[False] = False,
) -> Any:
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
) -> Optional[Any]:
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
    parse: Callable[[Any], T],
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
    parse: Callable[[Any], T],
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

def pods(
    needle,
    haystack,
    parse=None,
    *,
    type=None,
    allow_mismatch=False,
    allow_many=False,
    allow_duplicates=False,
):
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
        allow_duplicates,
    )


@overload
def filter(
    needle: Callable[[T], object],
    haystack: Iterable[T],
    parse: None = None,
    *,
    allow_mismatch: Literal[False] = False,
    allow_many: bool = False,
    allow_duplicates: bool = False,
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
    allow_duplicates: bool = False,
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
    allow_duplicates: bool = False,
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
    allow_duplicates: bool = False,
) -> Optional[TPrime]:
    """
    If `parse` is not None, and `allow_mismatch=True`, then we return whatever type `parse` returns, or None.
    """

def filter(
    needle,
    haystack,
    parse=None,
    *,
    allow_mismatch=False,
    allow_many=False,
    allow_duplicates=False,
):
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
        allow_duplicates,
    )


def _one(needle: object, haystack: object, results: List[T], allow_many: bool, allow_duplicates: bool):
    if not results:
        return None  # allow_mismatch must have been True
    if allow_duplicates:
        seen = set()
        deduplicated: List[T] = []
        for element in results:
            if element not in seen:
                seen.add(element)
                deduplicated.append(element)
        results = deduplicated
    if len(results) > 1 and not allow_many:
        raise ManyFound(needle, haystack)
    return results[0]
