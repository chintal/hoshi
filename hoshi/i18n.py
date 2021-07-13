#!/usr/bin/env python
# encoding: utf-8

"""

The Translation Manager Module (:mod:`hoshi.i18n`)
==================================================

This module provides the main interfaces to ``hoshi``.

"""

import os
import six
import logging
import gettext
import weakref
import datetime
from functools import partial
from numbers import Number

from babel import Locale
from babel.messages import Catalog
from babel.messages import Message
from babel.messages.pofile import read_po
from babel.messages.pofile import write_po
from babel.messages.mofile import write_mo

from .messages import TranslatableStructuredMessage
from .translation import StrictTranslations
from .translation import TranslationMissingError

from .translators.base import TranslationFailure


def _mtime(filepath):
    return os.path.getmtime(filepath)


class TranslationManager(object):
    def __init__(self, supported_languages, catalog_dirs):
        """
        The TranslationManager object is the primary interface of the library
        to application code. Most applications using hoshi will instantiate
        this class exactly once and hold the instance in a globally
        accessible namespace, such as the application or config object.

        This class manages the translation contexts, locales, and external
        translators.

        :param supported_languages: A list of languages / locales the
                application intends to support
        :param catalog_dirs: A list of directories which hold the translation
                templates and catalogs
        """
        self._langages = supported_languages or ['en_US']
        self._catalog_dirs = catalog_dirs
        self._log = None
        self._locales = {}
        self._contexts = {}
        self._context_current = {}
        self._context_handlers = {}
        self._translators = []
        self._object_translators = {}

    def _install_object_translator(self, objtype, translator):
        self._object_translators[objtype] = translator

    def install_object_translator(self, objtype, translator):
        if isinstance(objtype, list):
            for otype in objtype:
                self._install_object_translator(otype, translator)
        else:
            self._install_object_translator(objtype, translator)

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
            self._log = logging.getLogger('hoshi')
        return self._log

    @property
    def primary_language(self):
        return self._locales[self._langages[0]]

    def install_language(self, language):
        """
        Install a single language to the application's locale set. This
        function uses babel to install the appropriate locale, which can
        later be used to render things like dates, numbers, and currencies.

        Locales should not be used directly, and instead should be used
        using the translator.

        It is currently not intended for languages to be installed on the
        fly. Do this before creating any contexts or attempting any
        translations.

        :param language: locale code in the form 'en_US'
        """
        lle = Locale.parse(language, sep='_')
        self.log.info("Installing Locale {0} : {1}"
                      "".format(language, lle.display_name))
        self._locales[language] = lle

    @staticmethod
    def _pot_path(context_name, catalog_dir):
        return os.path.join(catalog_dir, "{}.pot".format(context_name))

    def _create_context(self, context_name, catalog_dir, metadata):
        self.log.warning("Could not find Template file for {0} in {1}. "
                         "Creating.".format(context_name, catalog_dir))
        metadata.setdefault('project', context_name)
        metadata.setdefault('creation_date', datetime.datetime.now())
        with open(self._pot_path(context_name, catalog_dir), 'wb') as target:
            template = Catalog(**metadata)
            write_po(target, template)

    @staticmethod
    def _po_path(context_name, language, catalog_dir):
        return os.path.join(catalog_dir, language,
                            "LC_MESSAGES", "{}.po".format(context_name))

    @staticmethod
    def _mo_path(context_name, language, catalog_dir):
        return os.path.join(catalog_dir, language,
                            "LC_MESSAGES", "{}.mo".format(context_name))

    @staticmethod
    def _pass_through_strings(catalog):
        message: Message
        for message in catalog:
            if message.id == '':
                continue
            if not message.string:
                message.string = message.id

    def install_translator(self, translator):
        self._translators.append(translator)

    def translate(self, source_language, target_language, string):
        if len(self._translators):
            for translator in self._translators:
                try:
                    return translator.translate(source_language,
                                                target_language,
                                                string), \
                           translator.name
                except TranslationFailure:
                    continue
            raise TranslationFailure()
        else:
            raise NotImplementedError

    def _translate_string(self, language, string):
        return self.translate(self.primary_language, language, string)

    def _translate_strings(self, catalog):
        self.log.warning("Translating strings for catalog {0}"
                         "".format(catalog))
        message: Message
        for message in catalog:
            if message.id == '':
                continue
            if not message.string:
                self.log.info("Translating \"{0}\" to {1}"
                              "".format(message.id, catalog.locale))
                string, source = self._translate_string(catalog.locale,
                                                        message.id)
                message.string = string
                message.auto_comments.append(source)

    def _create_context_lang(self, context_name, language,
                             catalog_dir, metadata):
        self.log.warning("Could not find Language file {0} for {1} in {2}. "
                         "Creating.".format(language, context_name,
                                            catalog_dir))
        if not os.path.exists(self._pot_path(context_name, catalog_dir)):
            self._create_context(context_name, catalog_dir, metadata)
        os.makedirs(os.path.join(catalog_dir, language, "LC_MESSAGES"),
                    exist_ok=True)
        with open(self._pot_path(context_name, catalog_dir), 'rb') as template:
            catalog = read_po(template)
            catalog.locale = language
            catalog.creation_date = datetime.datetime.now()
            if catalog.locale == self.primary_language:
                self._pass_through_strings(catalog)
            else:
                try:
                    self._translate_strings(catalog)
                except (NotImplementedError, TranslationFailure):
                    pass
            _popath = self._po_path(context_name, language, catalog_dir)
            with open(_popath, 'wb') as target:
                write_po(target, catalog)

    def _update_context_lang(self, context_name, language, catalog_dir):
        p = (context_name, language, catalog_dir)
        self.log.info("Updating po file for language {1} of {0} in {2}"
                      "".format(*p))
        _potpath = self._pot_path(context_name, catalog_dir)
        with open(_potpath, 'rb') as template:
            template = read_po(template)
        with open(self._po_path(*p), 'rb') as po_file:
            catalog = read_po(po_file)
        catalog.update(template, no_fuzzy_matching=True)

        if catalog.locale == self.primary_language:
            self._pass_through_strings(catalog)
        else:
            try:
                self._translate_strings(catalog)
            except (NotImplementedError, TranslationFailure):
                pass

        with open(self._po_path(*p), 'wb') as po_file:
            write_po(po_file, catalog)

    def _compile_context_lang(self, context_name, language,
                              catalog_dir, metadata):
        p = (context_name, language, catalog_dir)
        self.log.info("(re)compiling mo file {1} for {0} in {2}.".format(*p))

        if not os.path.exists(self._po_path(*p)):
            self._create_context_lang(*p, metadata)

        if _mtime(self._po_path(*p)) < \
                _mtime(self._pot_path(context_name, catalog_dir)):
            self._update_context_lang(*p)

        with open(self._po_path(*p), 'rb') as pofile:
            catalog = read_po(pofile)
            with open(self._mo_path(*p), 'wb') as mofile:
                write_mo(mofile, catalog)

    def install_context(self, context_name, language,
                        catalog_dir=None, metadata=None):
        """
        Install an i18n context. Language would be a locale code of the form
        "en_US". While not mandated, context name would typically be of the
        form "<module>".

        i18n Contexts are objects which can manage specific i18n strategies
        and contain and apply special helper functions for translating a
        string.
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
            self.log.error("Asked to use a catalog which is not configured!"
                           "Using {0} instead.".format(self._catalog_dirs[0]))
            catalog_dir = self._catalog_dirs[0]

        ctx = "{0}.{1}".format(context_name, language)
        if ctx in self._contexts.keys():
            raise KeyError(ctx)

        p = (context_name, language, catalog_dir)

        if not os.path.exists(self._mo_path(*p)) or \
                _mtime(self._mo_path(*p)) < _mtime(self._po_path(*p)) or \
                _mtime(self._mo_path(*p)) < \
                _mtime(self._pot_path(context_name, catalog_dir)):
            self._compile_context_lang(*p, metadata)

        translator = gettext.translation(context_name, catalog_dir,
                                         languages=[language],
                                         class_=StrictTranslations)
        translator.install()

        _potpath = self._pot_path(context_name, catalog_dir)
        with open(_potpath, 'rb') as pot_file:
            template = read_po(pot_file)

        self._contexts[ctx] = {
            'name': "{0}.{1}".format(context_name, language),
            'locale': self._locales[language],
            'i18n': translator.gettext,
            'catalog_dir': catalog_dir,
            'template': template,
            'template_path': self._pot_path(context_name, catalog_dir),
            'catalog': self._po_path(context_name, language, catalog_dir),
            'language': language,
        }

        if context_name not in self._context_current.keys():
            self._context_current[context_name] = ctx
            self._context_handlers[context_name] = []

    def install_change_handler(self, context_name, handler):
        self._context_handlers[context_name].append(weakref.ref(handler))

    def set_language(self, context_name, language, fallback=True):
        old_ctx = self._context_current[context_name]
        ctx = "{0}.{1}".format(context_name, language)

        if fallback and (ctx not in self._contexts.keys()):
            fallback_ctx = "{0}.{1}".format(context_name,
                                            self.primary_language)
            if fallback_ctx in self._contexts.keys():
                ctx = fallback_ctx

        if old_ctx == ctx:
            return

        self.log.info("Setting language for context '{0}' to {1}"
                      "".format(context_name, language))

        self._context_current[context_name] = ctx

        for handler_ref in self._context_handlers[context_name]:
            handler = handler_ref()
            if handler:
                handler()

    def set_global_language(self, language):
        self.log.info("Setting global language to {0}".format(language))
        for context in self._context_current.keys():
            self.set_language(context, language)

    def _i18n_msg(self, context, message):
        """
        Translate an atomic string message using the provided context.
        Conversion by this function applies a standard gettext / po
        mechanism. If the string is not included in the i18n catalogs, it
        will be added for later manual translation. Note that the po files
        will be updated only on the next application run.
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

    def _translate(self, context, obj, *args, **kwargs):
        """
        Translate a translatable object using the provided context. This
        function should dispatch to specific functions depending on the type
        of the object. If the context has special helper / preprocessing
        functions installed, they are applied here.
        - Numbers, dates, times, currencies : Locale
        - Strings : _i18n
        """
        if not obj:
            return ''
        if isinstance(context, six.text_type):
            context = self._contexts[self._context_current[context]]
        if isinstance(obj, six.text_type):
            return self._i18n_msg(context, obj)
        if isinstance(obj, Number):
            return str(obj)
        if isinstance(obj, TranslatableStructuredMessage):
            return obj.translated(self._translate, context)
        for otype in self._object_translators.keys():
            if isinstance(obj, otype):
                return self._object_translators[otype](obj, *args, **kwargs)
        raise TypeError("Cannot translate {} of type {}"
                        "".format(obj, type(obj)))

    def translator(self, context_name, language=None):
        """
        Generate and return an i18n function which uses the provided context.
        This can be used to replicate the typical _() structure.
        """
        if language:
            ctx = self._contexts["{0}.{1}".format(context_name, language)]
        else:
            ctx = context_name
        return partial(self._translate, ctx)

    def locale(self, language):
        """
        Return the babel locale associated with the provided language.
        """
        return self._locales[language]

    def current_language(self, context):
        return self._context_current[context].rsplit('.')[-1]

    def current_locale(self, context):
        return self.locale(self.current_language(context))
