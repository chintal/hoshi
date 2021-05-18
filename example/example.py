
import logging
logging.basicConfig(level=logging.DEBUG)

from pprint import PrettyPrinter
pp = PrettyPrinter().pprint

from hoshi.i18n import TranslationManager
from hoshi.sets import indian_languages

locale_dirs = ['locale']

tm = TranslationManager(indian_languages, locale_dirs)
tm.install()

tm.install_context('test', 'en_IN')
tm.install_context('test', 'hi_IN')

pp(tm._locales)
pp(tm.catalog_dirs)
pp(tm._contexts)

_ = tm.translator('test', 'hi_IN')
print(_("Hello World"))
print(_("Hello World2"))
print(_("Hello World2"))
