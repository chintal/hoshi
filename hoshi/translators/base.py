#!/usr/bin/env python
# encoding: utf-8

"""

External Translator Adapter Base (:mod:`hoshi.translators.base`)
================================================================

This module provides the prototypes for integration of external translators.

"""

import babel.core


class TranslationFailure(Exception):
    """
    The Exception to be raised when a translation request fails for any reason.
    """
    pass


class TranslatorBase(object):
    """
    The base class for External Translator Adapters.
    """
    def __init__(self):
        """
        Any initialization required to start or connect to the external
        translator should be done here.
        """
        pass

    def translate(self, source_language, target_language, string):
        """
        Given a ``string`` in the ``source_language``, return the string as
        translated into the ``target_language``. Both languages are to be
        instances of ``babel.core.Locale``.
        """
        source_language: babel.core.Locale
        target_language: babel.core.Locale
        raise NotImplementedError
