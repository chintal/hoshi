

import babel.core


class TranslationFailure(Exception):
    pass


class TranslatorBase(object):
    def __init__(self):
        pass

    def translate(self, source_language, target_language, string):
        source_language: babel.core.Locale
        target_language: babel.core.Locale
        raise NotImplementedError
