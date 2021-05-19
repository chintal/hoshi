
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


# As you application uses the translation manager to render strings, they
# are added to the catalog templates for each appropriate context / domain.
# At each execution of the typical application, the catalogs are checked
# during loading. If necessary, they are updated using the current templates.
# If a translator is installed, then translator provided translations are also
# included in the catalogs. These translations are often, if not almost always
# wrong. These should be manually corrected later on.
for language in indian_languages:
    _ = tm.translator('test', language)
    print(language, ":", _("Hello World"))
