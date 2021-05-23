#!/usr/bin/env python
# encoding: utf-8

"""

Google Cloud Translator Adapter (:mod:`hoshi.translators.gcloud`)
=================================================================

This module provides the the adapter for the integration Google Cloud
Translate's Basic (v2) API. Note that this translator requires that you
have a valid API key.

"""


import os
import logging
from google.cloud import translate_v2 as translate
from .base import TranslatorBase


class GoogleCloudTranslator(TranslatorBase):
    _name = 'gcloud translate v2'

    def __init__(self, credentials=None):
        super(GoogleCloudTranslator, self).__init__()
        self._silence_logging()
        if credentials:
            os.environ.setdefault('GOOGLE_APPLICATION_CREDENTIALS',
                                  credentials)
        self._client = translate.Client()

    _upstream_loggers = [
        'urllib3.util.retry',
        'urllib3.connectionpool',
        'google.auth.transport.requests',
        'google.auth._default'
    ]

    @property
    def name(self):
        return self._name

    def _silence_logging(self):
        for logger in self._upstream_loggers:
            logging.getLogger(logger).setLevel(logging.INFO)

    def translate(self, source_language, target_language, string):
        source = source_language.language
        target = target_language.language

        result = self._client.translate(string,
                                        target_language=target,
                                        source_language=source)
        return result['translatedText']
