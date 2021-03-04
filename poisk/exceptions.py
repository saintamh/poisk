#!/usr/bin/env python3


class PoiskException(ValueError):

    def __init__(self, needle, haystack):
        super().__init__(repr(needle))
        self.needle = needle
        self.haystack = haystack


class NotFound(PoiskException):
    pass


class ManyFound(PoiskException):
    pass
