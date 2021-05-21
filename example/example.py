
import os
import logging
logging.basicConfig(level=logging.DEBUG)

from pprint import PrettyPrinter
pp = PrettyPrinter().pprint

from hoshi.i18n import TranslationManager
from hoshi.sets import indian_languages

from hoshi.translators.gcloud import GoogleCloudTranslator


# Most small applications can probably do with a single locale
# directory, containing a single context (in multiple languages).
# As the application grows more complex, it may be required to create
# additional contexts. When applications grow into multiple distinct
# components, it may be necessary to have multiple catalog directories
# as well.

# Specify the locale / catalog directories. These are directories
# containing the po templates and per-language folders of catalogs.
catalog_dirs = ['locale']

# Create and initialize a translation manager. Also specify the
# locales of interest so that they can be installed and ready for use.
# `hoshi.sets` can contain helpful groups of languages.
# These locales are largely responsible for proper rendering of dates
# and associated string forms, number formats and currencies.
tm = TranslationManager(indian_languages, catalog_dirs)
tm.install()

# Install the Google Cloud Translator. Note that you need to have API
# credentials to use this. Put the credentials file in the following
# path or adjust the path instead.
gcloud_json_credentials = "/opt/google-cloud-sdk/hoshi-service.json"
if os.path.exists(gcloud_json_credentials):
    tm.install_translator(GoogleCloudTranslator(credentials=gcloud_json_credentials))

# Create context for all languages you wish to translate to.
for language in indian_languages:
    tm.install_context('test', language)


print("Using Catalog Directories:")
pp([os.path.abspath(x) for x in tm.catalog_dirs])


print("Installed Contexts:")
pp(tm._contexts)


# As your application uses translators provided by the translation manager
# to render strings, they are added to the catalog templates for each
# appropriate context / domain.
#
# At each execution of the typical application, the catalogs are checked
# during loading and are updated using the current templates, if necessary.
#
# If an external string translator, such as the GoogleCloudTranslator is
# installed, then generated translations are also included in the catalogs.
# These translations are often, if not almost always wrong. These should be
# manually corrected later on.

# Obtain a translator bound to the specified context and language, and use
# it to render strings. Note that this is not the optimal level of
# abstraction for most applications. It can, in principle, create the most
# flexible implementation. But it does so by leaving a great deal of the
# implementation to the application.
for language in indian_languages:
    _ = tm.translator('test', language)
    print(language, ":", _("Hello World"))


# Alternatively, it is possible to create a translator which follows the
# current configured language for that context. This allows global language
# controls to be implemented with relative ease, and more along the lines of
# the typical gettext based implementation. One to the two following
# approaches likely represents the optimal level of abstraction for the
# typical application.

_ = tm.translator('test')

for language in indian_languages:
    tm.set_language('test', language)
    print(language, ":", _("Hello World"))

for language in indian_languages:
    tm.set_global_language(language)
    print(language, ":", _("Hello World"))


# It is also possible to install a handler on a context, which can be
# responsible for triggering any actions the application must take when the
# context's default language changes.
#
# It is also possible (and probably safer) for you to manage this activity
# from the control path which causes the language change in the first place.
#
# This functionality is provided for applications which are either fairly
# small and just need a quick way to get things done, and for very complex
# applications which may have multiple triggers for language changes.
#
# Note that this library will only store a weak reference to the handler
# function you provide. If this function or the object it belongs to is
# at risk of being garbage collected, but you still require the function
# to be called, you must ensure that you hold a reference to it elsewhere.

def change_handler():
    print("In handler :", _("Hello World"))


tm.install_change_handler('test', change_handler)

for language in indian_languages:
    tm.set_language('test', language)

print("Deleting change handler.")
del change_handler

for language in indian_languages:
    tm.set_language('test', language)
