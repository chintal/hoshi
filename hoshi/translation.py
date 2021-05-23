#!/usr/bin/env python
# encoding: utf-8

"""

Specialized ``gettext`` Subclasses (:mod:`hoshi.translations`)
==============================================================

These classes are used internally to modify the behavior of ``gettext``.

Most applications would not need to touch this module directly.

"""

import gettext


class TranslationMissingError(Exception):
    def __init__(self, msg):
        """
        An exception that is raised if an attempt to translate a string did
        not find a suitable translation to return. This may happen because the
        ``msgid`` does not exist in the template, or if the translation in the
        catalog is blank.
        """
        self._msg = msg


class FailingFallback(gettext.NullTranslations):
    """
    ``gettext.NullTranslations`` subclass which simply raises a
    ``TranslationMissingError``. When used as a Fallback Translation, this
    results in the exception being thrown whenever translations are missing.
    """
    def gettext(self, message):
        raise TranslationMissingError(message)


class StrictTranslations(gettext.GNUTranslations, object):
    def __init__(self, *args, **kwargs):
        """
        ``gettext.GNUTranslations`` subclass which uses the ``FailingFallback``
        This is used by the ``hoshi.TranslationManager`` to provide its
        functionality.
        """
        super(StrictTranslations, self).__init__(*args, **kwargs)
        self.add_fallback(FailingFallback())

    def __repr__(self):
        return "<{0}.{1} object>".format(self.__module__,
                                         self.__class__.__name__)
