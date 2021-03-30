#!/usr/bin/env python3

# standards
import re
from typing import Any, Callable, TypeVar, Union

# 3rd parties
from typing_extensions import Protocol  # for pre-3.8 pythons


class HasXPathMethod(Protocol):

    @property
    def xpath(self) -> Callable[..., Any]:
        # This declaration here is not actually for a property, it's for a method called `xpath`, whose signature we don't care
        # about (beyond its name). Apparently this is the way you can get mypy to recognize this. This hacky solution of using a
        # @property was coined (by the BDFL) here: https://github.com/python/mypy/issues/9560#issuecomment-705955103
        ...


XPathType = TypeVar('XPathType', bound=HasXPathMethod)


RegexType = Union[str, re.Pattern]
