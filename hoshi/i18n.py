

import os
import logging
import gettext
import datetime
from functools import partial

from babel import Locale
from babel.messages import Catalog
from babel.messages.pofile import read_po
from babel.messages.pofile import write_po
from babel.messages.mofile import write_mo

from .translation import StrictTranslations
from .translation import TranslationMissingError

try:
    from twisted import logger
except ImportError:
    logger = None


def _mtime(filepath):
    return os.path.getmtime(filepath)


class TranslationManager(object):
    def __init__(self, supported_languages, catalog_dirs, twisted_logging=False):
        self._langages = supported_languages or ['en_US']
        self._catalog_dirs = catalog_dirs
        self._twisted_logging = twisted_logging
        self._log = None
        self._locales = {}
        self._contexts = {}

    def install(self):
        for language in self._langages:
            self.install_language(language)
        self._install_catalogs()

    def _install_catalogs(self):
        for d in self._catalog_dirs:
            os.makedirs(d, exist_ok=True)

    @property
    def catalog_dirs(self):
        return self._catalog_dirs

    @property
    def log(self):
        if not self._log:
            if self._twisted_logging:
                self._log = logger.Logger(namespace="hoshi", source=self)
            else:
                self._log = logging.getLogger('i18n')
        return self._log

    def install_language(self, language):
        """
        Install a single language to the application's locale set. This function uses babel
        to install the appropriate locale, which can later be used to render things like
        dates, numbers, and currencies.

        Locales should not be used directly, and instead should be used using the
        translator.

        It is currently not intended for languages to be installed on the fly. Do this before
        attempting any translations.

        :param language: locale code in the form 'en_US'
        """
        lle = Locale.parse(language, sep='_')
        self.log.info("Installing Locale {0} : {1}".format(language, lle.display_name))
        self._locales[language] = lle

    def _pot_path(self, context_name, catalog_dir):
        return os.path.join(catalog_dir, "{}.pot".format(context_name))

    def _create_context(self, context_name, catalog_dir, metadata):
        self.log.warn("Could not find Template file for {0} in {1}. Creating."
                      "".format(context_name, catalog_dir))
        metadata.setdefault('project', context_name)
        metadata.setdefault('creation_date', datetime.datetime.now())
        with open(self._pot_path(context_name, catalog_dir), 'wb') as target:
            template = Catalog(**metadata)
            write_po(target, template)

    def _po_path(self, context_name, language, catalog_dir):
        return os.path.join(catalog_dir, language, "LC_MESSAGES", "{}.po".format(context_name))

    def _mo_path(self, context_name, language, catalog_dir):
        return os.path.join(catalog_dir, language, "LC_MESSAGES", "{}.mo".format(context_name))

    def _create_context_lang(self, context_name, language, catalog_dir, metadata):
        self.log.warn("Could not find Language file {0} for {1} in {2}. Creating."
                      "".format(language, context_name, catalog_dir))
        if not os.path.exists(self._pot_path(context_name, catalog_dir)):
            self._create_context(context_name, catalog_dir, metadata)
        os.makedirs(os.path.join(catalog_dir, language, "LC_MESSAGES"), exist_ok=True)
        with open(self._pot_path(context_name, catalog_dir), 'rb') as template:
            catalog = read_po(template)
            catalog.locale = language
            catalog.creation_date = datetime.datetime.now()
            with open(self._po_path(context_name, language, catalog_dir), 'wb') as target:
                write_po(target, catalog)

    def _update_context_lang(self, context_name, language, catalog_dir, metadata):
        p = (context_name, language, catalog_dir)
        self.log.info("Updating po file for language {1} of {0} in {2}".format(*p))
        with open(self._pot_path(context_name, catalog_dir), 'rb') as template:
            template = read_po(template)
        with open(self._po_path(*p), 'rb') as po_file:
            catalog = read_po(po_file)
        catalog.update(template, no_fuzzy_matching=True)
        with open(self._po_path(*p), 'wb') as po_file:
            write_po(po_file, catalog)

    def _compile_context_lang(self, context_name, language, catalog_dir, metadata):
        p = (context_name, language, catalog_dir)
        self.log.info("(re)compiling mo file {1} for {0} in {2}.".format(*p))

        if not os.path.exists(self._po_path(*p)):
            self._create_context_lang(*p, metadata)

        if _mtime(self._po_path(*p)) < _mtime(self._pot_path(context_name, catalog_dir)):
            self._update_context_lang(*p, metadata)

        with open(self._po_path(*p), 'rb') as pofile:
            catalog = read_po(pofile)
            with open(self._mo_path(*p), 'wb') as mofile:
                write_mo(mofile, catalog)

    def install_context(self, context_name, language, catalog_dir=None, metadata=None):
        """
        Install an i18n context. Language would be a locale code of the form "en_US".
        While not mandated, context name would typically be of the form "<module>".

        i18n Contexts are objects which can manage specific i18n strategies and contain
        and apply special helper functions for translating a string.
        """
        metadata = metadata or {}

        if not self._catalog_dirs:
            raise AttributeError("Atempted to create an i18n context without "
                                 "configuring any catalog directories!")

        if not catalog_dir:
            self.log.info("Catalog directory not specified. Using {0}."
                          "".format(self._catalog_dirs[0]))
            catalog_dir = self._catalog_dirs[0]

        if catalog_dir not in self._catalog_dirs:
            self.log.error("Attempted to use a catalog which is not configured! "
                           "Using {0} instead.".format(self._catalog_dirs[0]))
            catalog_dir = self._catalog_dirs[0]

        ctx = "{0}.{1}".format(context_name, language)
        if ctx in self._contexts.keys():
            raise KeyError(ctx)

        p = (context_name, language, catalog_dir)

        if not os.path.exists(self._mo_path(*p)) or \
                _mtime(self._mo_path(*p)) < _mtime(self._po_path(*p)) or \
                _mtime(self._mo_path(*p)) < _mtime(self._pot_path(context_name, catalog_dir)):
            self._compile_context_lang(*p, metadata)

        translator = gettext.translation(context_name, catalog_dir,
                                         languages=[language],
                                         class_=StrictTranslations)
        translator.install()

        with open(self._pot_path(context_name, catalog_dir), 'rb') as pot_file:
            template = read_po(pot_file)

        self._contexts[ctx] = {
            'name': "{0}.{1}".format(context_name, language),
            'locale': self._locales[language],
            'i18n': translator.gettext,
            'catalog_dir': catalog_dir,
            'template': template,
            'template_path': self._pot_path(context_name, catalog_dir),
            'catalog': self._po_path(context_name, language, catalog_dir)
        }

    def _i18n_msg(self, context, message):
        """
        Translate an atomic string message using the provided context. Conversion by
        this function applies a standard gettext / po mechanism. If the string is not
        included in the i18n catalogs, it will be added for later manual translation.
        Note that the po files will be updated only on the next application run.
        """
        try:
            return context['i18n'](message)
        except TranslationMissingError:
            self.log.debug("Translation for \"{0}\" not found in context {1}"
                           "".format(message, context['name']))
            template: Catalog = context['template']
            if template.get(message):
                return message
            self.log.info("Adding \"{0}\" to context {1}"
                          .format(message, context['name']))
            with open(context['template_path'], 'rb') as pot_file:
                template = read_po(pot_file)
                template.add(message)
            with open(context['template_path'], 'wb') as pot_file:
                write_po(pot_file, template)
            context['template'] = template
            return message

    def _translate(self, context, obj):
        """
        Translate a translatable object using the provided context. This function
        should dispatch to specific functions depending on the type of the object.
        If the context has special helper / preprocessing functions installed, they
        are applied here.
          - Numbers, dates, times, currencies : Locale
          - Strings : _i18n
        """
        return self._i18n_msg(context, obj)

    def translator(self, context_name, language):
        """
        Generate and return an i18n function which uses the provided context. This
        can be used to replicate the typical _() structure.
        """
        ctx = self._contexts["{0}.{1}".format(context_name, language)]
        return partial(self._translate, ctx)
