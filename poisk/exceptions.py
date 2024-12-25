#!/usr/bin/env python3


class PoiskException(ValueError):
    def __init__(self, needle, haystack):
        super().__init__(self._compose_message(needle, haystack))
        self.needle = needle
        self.haystack = haystack

    @staticmethod
    def _compose_message(needle, haystack):
        message = repr(needle)
        if isinstance(haystack, (str, list, tuple, set, dict)):
            haystack_repr = repr(haystack)
            if len(haystack_repr) > 100:
                haystack_repr = haystack_repr[:50] + "…" + haystack_repr[-50:]
            message += " in " + haystack_repr
        return message


class NotFound(PoiskException):
    pass


class ManyFound(PoiskException):
    pass
