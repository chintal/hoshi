import gettext


class TranslationMissingError(Exception):
    def __init__(self, msg):
        self._msg = msg


class FailingFallback(gettext.NullTranslations):
    def gettext(self, msg):
        raise TranslationMissingError(msg)


class StrictTranslations(gettext.GNUTranslations, object):
    def __init__(self, *args, **kwargs):
        super(StrictTranslations, self).__init__(*args, **kwargs)
        self.add_fallback(FailingFallback())