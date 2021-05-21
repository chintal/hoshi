

Usage
=====

A runnable example is included in the sources in ``example/example.py``. This
document attempts to mirror that file.

Useful Concepts
---------------

``hoshi`` attempts to use standard nomenclature and concepts established by
``gettext`` and ``babel`` where possible. However, not everything perfectly
aligns. When using ``hoshi``, the following nomenclature is used and should
be understood.

.. rubric:: Locale

A locale is what is generally is. It is something of the form ``en_US``, and
specifies the language and territory that applies. Locales are usually provided
by your application as strings, and passed around internally as ``babel.core.Locale``
instances.

Locales are responsible for correct rendering of numbers, dates, and currencies.

.. warning::
    The code currently extant within ``hoshi`` does nothing to handle numbers,
    dates and currencies. You can, however, use ``hoshi`` to make sure you use
    the correct ``babel.core.Locale`` instance with suitable ``babel`` functions.


.. rubric:: Context

A context is a context within which a translation must be done. These may refer
to ``domains`` in ``babel`` documentation, though I am not certain. Each context
has its own template and catalog files.

The context used in the example below is`test`, and the contexts are therefore
named, for example, ``test.en_IN`` and ``test``.

Here, ``test.en_IN`` is a localized context, which is of a standard form and
contains various information related to the context and its localization.
``test`` by itself, however, is a Tracking Context, and at any time simply points
to the correct localized context configured for `test`.

For this example, the relevant i18n files are the template at ``catalog_dir/test.pot``
and the catalog at ``catalog_dir/en_IN/LC_MESSAGES/test.po``.

A context can be used to differentiate between application modules / regions, or
divide responsibility for translations. Contexts may also be provided specialized
translation functions which may allow the user to provide the additional context
needed to correctly translate text.

.. note::
    These specialized translation functions are not currently implemented.

.. rubric:: Catalog Directories

Catalog directories are directories like `locale` which contain translation
catalogs. Depending on the structure of your application, you can configure
multiple catalog directories. The case of complex applications split across
multiple packages, for example. In such cases, you would provide a list of
directories containing the translation templates and catalogs. ``hoshi`` will
use the first catalog template it finds in those directories with the correct
context name.

.. rubric:: Typical Implementations

Most small applications can probably do with a single catalog directory,
containing a single context. As the application grows more complex, it may be
required to create additional contexts. When applications grow into multiple
distinct components, it may be necessary to have multiple catalog directories
as well.

Example Usage
-------------

Specify the locale / catalog directories. These are directories
containing the po templates and per-language folders of catalogs.

>>> catalog_dirs = ['_tmp/locale']

Create and initialize a translation manager. Also specify the locales of
interest so that they can be installed and ready for use. ``hoshi.sets``
contains helpful groups of languages. These locales are largely responsible
for proper rendering of dates and associated string forms, number formats
and currencies.

>>> from hoshi.i18n import TranslationManager
>>> from hoshi.sets import indian_languages
>>> tm = TranslationManager(indian_languages, catalog_dirs)
>>> tm.install()


.. important::
    The first language in the ``supported_languages`` list is a special language,
    and is called the ``primary_language``. This distinction is important when you
    use ``hoshi``. Translation catalogs for the primary language are constructed by
    simply passing through the ``msgid`` to the ``msgstring`` - it does not get sent
    to the external translator. In otherwords, ``hoshi`` makes the assumption that
    your ``msgid`` is the string in the ``primary_language``. This is a somewhat weak
    assumption, in that if you were to manually edit your translation catalogs,
    nothing should break. Do exercise caution, however.

This ``TranslationManager`` instance would typically be installed to a
globally available namespace of some kind. Typical examples would be as an
instance variable in some application or configuration class or as a module
variable in a configuration module. The best place to put it in your
application will depend on your framework, architecture, and code style.
The recommended location would be one which you can access with something
like  ``app.i18n``.

If you application used twisted, you may wish to add ``twisted_logging=True``
to the instantiation of the ``TranslationManager``. This will use twisted's
logging infrastructure instead of Python's built-in logging.

Next, install the Google Cloud Translator. This is an optional step. Once
installed, hoshi will attempt to generate translated strings in the target
languages using Google Cloud Translator's basic service. Note that you need
to have API credentials to use this. Put the credentials file in the path
shown here or adjust it to suit your needs.

>>> import os
>>> from hoshi.translators.gcloud import GoogleCloudTranslator
>>> gcloud_json_credentials = "hoshi-gct.json"
>>> if os.path.exists(gcloud_json_credentials):
...     tm.install_translator(GoogleCloudTranslator(credentials=gcloud_json_credentials))

Note that translations provided by this service will most likely be incorrect.
It may, however, be a useful starting point for you manually correct and enter
the translations in the appropriate catalog files.

We also prepare a pretty printer for some of the remaining examples. This is,
obviously, a very optional step:

>>> from pprint import PrettyPrinter
>>> pp = PrettyPrinter().pprint

Now, create a context for all languages you wish to support. The languages here
are all locale codes in the ``en_IN`` form.

>>> for language in indian_languages:
...     tm.install_context('test', language)

This creates contexts in the manager. Each `context` is a dictionary of the form:

>>> pp(tm._contexts['test.en_IN'])
{'catalog': '_tmp/locale/en_IN/LC_MESSAGES/test.po',
 'catalog_dir': '_tmp/locale',
 'i18n': <bound method GNUTranslations.gettext of <hoshi.translation.StrictTranslations object>>,
 'locale': Locale('en', territory='IN'),
 'name': 'test.en_IN',
 'template': <Catalog None>,
 'template_path': '_tmp/locale/test.pot'}

User code should typically not interact with this dictionary directly, and avoid
doing so in all but the most deperate cases. In case you find you need to directly
interact with this dictionary, you are either doing something wrong or have found
a gap in the module's functionality. Please file an issue on github to let me know
so the gap can be filled.

This also creates a tracking context ``test``, which points to the first context
created.

>>> pp(tm._context_current['test'])
'test.en_IN'

Again, this ``_context_current`` dictionary is not something you would directly
use. It is shown here for the sake of clarity.

The most simple use of the Translation Manager is to convert a string into a
specified context. This kind of conversion may be required for printing to the
terminal as shown below. It can also be applied to any other purpose requiring
a string, such as to generate the text for a Button.

To do this, obtain a translator bound to the specified context and language,
and use it to render strings as shown below. Note that this is not the optimal
level of abstraction for most applications. It can, in principle, create the
most flexible implementation. But it does so by leaving a great deal of the
implementation to the application.


>>> for language in indian_languages:
...     _ = tm.translator('test', language)
...     print(language, ":", _("Hello World"))
en_IN : Hello World
hi_IN : नमस्ते दुनिया
te_IN : హలో వరల్డ్
ta_IN : ஹலோ வேர்ல்ட்
bn_IN : ওহে বিশ্ব
pa_IN : ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਦੁਨਿਆ
ur_IN : ہیلو ورلڈ
kn_IN : ಹಲೋ ವರ್ಲ್ಡ್
or_IN : ନମସ୍କାର ବିଶ୍ୱବାସି
gu_IN : હેલો વર્લ્ડ
ml_IN : ഹലോ വേൾഡ്


Notice that the manager's translators were able to convert the string provided
into various languages. This is made possible by the Google Cloud Translate API.
Even here, not all of these translations are correct - in fact, a number of them
are simply phonetic translations into the target script.

Additionally, the results here are translated immediately because additional code
is run before this code is for the doctests (see conftest.py).

.. important::
    In general, translations will be ready only when the python interpreter is
    restarted after the string is first encountered. There does not seem to be
    a good workaround for this problem.

Typically, as your application uses the translators provided by the translation
manager to render strings, they are added to the catalog templates for each
appropriate context / domain.

The catalogs are checked when they are loaded at startup and are updated using
the current templates, if necessary. At this point, one would generally manually
enter the correct translations in the appropriate catalog  (``.po``) file.

If an external string translator, such as the GoogleCloudTranslator is
installed, then generated translations are automatically included in the
catalogs. The translations are obtained and incorporated into the catalogs
only at the next run. Performance is protected by avoiding long network API
calls and unnecessary file IO in the middle of the application's execution.
The automatically obtained translations will need manual correction anyway.


More conveniently, it is possible to create a translator which follows the
current configured language for that context. This allows global language
controls to be implemented with relative ease, and is more along the lines of
the typical ``gettext`` based implementation. One of the two following
approaches likely represents the optimal level of abstraction for the
typical application.


>>> _ = tm.translator('test')


>>> for language in indian_languages:
...     tm.set_language('test', language)
...     print(language, ":", _("Hello World"))
en_IN : Hello World
hi_IN : नमस्ते दुनिया
te_IN : హలో వరల్డ్
ta_IN : ஹலோ வேர்ல்ட்
bn_IN : ওহে বিশ্ব
pa_IN : ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਦੁਨਿਆ
ur_IN : ہیلو ورلڈ
kn_IN : ಹಲೋ ವರ್ಲ್ಡ್
or_IN : ନମସ୍କାର ବିଶ୍ୱବାସି
gu_IN : હેલો વર્લ્ડ
ml_IN : ഹലോ വേൾഡ്


>>> for language in indian_languages:
...     tm.set_global_language(language)
...     print(language, ":", _("Hello World"))
en_IN : Hello World
hi_IN : नमस्ते दुनिया
te_IN : హలో వరల్డ్
ta_IN : ஹலோ வேர்ல்ட்
bn_IN : ওহে বিশ্ব
pa_IN : ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਦੁਨਿਆ
ur_IN : ہیلو ورلڈ
kn_IN : ಹಲೋ ವರ್ಲ್ಡ್
or_IN : ନମସ୍କାର ବିଶ୍ୱବାସି
gu_IN : હેલો વર્લ્ડ
ml_IN : ഹലോ വേൾഡ്

It is also possible to install a handler on a context, which can be
responsible for triggering any actions the application must take when the
context's configured language changes.


>>> def change_handler():
...     print("In handler :", _("Hello World"))
>>> tm.install_change_handler('test', change_handler)
>>> for language in indian_languages:
...     tm.set_language('test', language)
In handler : Hello World
In handler : नमस्ते दुनिया
In handler : హలో వరల్డ్
In handler : ஹலோ வேர்ல்ட்
In handler : ওহে বিশ্ব
In handler : ਸਤਿ ਸ੍ਰੀ ਅਕਾਲ ਦੁਨਿਆ
In handler : ہیلو ورلڈ
In handler : ಹಲೋ ವರ್ಲ್ಡ್
In handler : ନମସ୍କାର ବିଶ୍ୱବାସି
In handler : હેલો વર્લ્ડ
In handler : ഹലോ വേൾഡ്


.. note::
    It is also possible (and probably safer) for you to manage this sort of
    activity from the control path which causes the language change in the first
    place, and avoid using this functionality entirely.

    This functionality is provided for applications which are either fairly
    small and just need a quick way to get things done, and for very complex
    applications which may have multiple triggers for language changes.


This library will only store a weak reference to the handler function you
provide. If this function or the object it belongs to is at risk of being
garbage collected, but you still require the function to be called, you must
ensure that you hold a reference to it elsewhere.


>>> del change_handler
>>> for language in indian_languages:
...     tm.set_language('test', language)


Other Helpful Functions
-----------------------

.. rubric:: :meth:`hoshi.i18n.TranslationManager.primary_language`

This method returns the ``primary_language`` configured. ``hoshi`` assumes
the ``msgid`` is the correct translation of the intended string in the primary
language.

>>> tm.primary_language
Locale('en', territory='IN')


.. rubric:: :meth:`hoshi.i18n.TranslationManager.current_language`

This method returns the language configured for the provided tracking context.

>>> tm.current_language('test')
'ml_IN'


.. rubric:: :meth:`hoshi.i18n.TranslationManager.current_locale`

This method returns the locale configured for the provided tracking context. This
can be used with various ``babel`` functions to ensure correct localization of
numbers, dates, etc.

>>> tm.current_locale('test')
Locale('ml', territory='IN')


.. rubric:: :meth:`hoshi.i18n.TranslationManager.locale`

This method can eb used to access any of the ``babel.core.Locale`` instances
installed in the manager. You can, of course, always instantiate one yourself
at any time as well. Which is a better approach might depend on your coding
style.

>>> tm.locale('en_IN')
Locale('en', territory='IN')


.. rubric:: :meth:`hoshi.i18n.TranslationManager.translate`

This method acts as a proxy to the installed external translators, and allows
your application to bypass the bulk of the ``i18n`` infrastructure and get
translations directly from the installed translators.

>>> tm.translate(tm.locale('en_IN'), tm.locale('hi_IN'), "Some Text")
('कुछ पाठ', 'gcloud translate v2')

The returned value is a tuple containing the translation result as well as the
translator which was used to generate it.


Further Learning
----------------

To get a more thorough understanding of the i18n process envisaged by ``hoshi``,
I recommend you take some time and play with the example code in ``example/example.py``.
That is more or less identical to the code shown here, but will give you informative
log output as well. It is also much easier to edit and run a python file than it is
doctests. While you do so, I also recommend you keep an eye on the contents of the
catalog and templates. In particular, you would want to see ``locale/test.pot`` and
``locale/hi_IN/LC_MESSAGES/test.po``.

Further, to experience the i18n workflow, you should manually `correct` one of the
translations in a catalog (``test.po``) and repeat the process with a new ``msgid``.
You should see that the manually entered translation in ``test.po`` is preserved,
while the new ``msgid`` has been added to the template as well as each catalog.

The various file and folder formats used are the same as that expected by ``gettext``,
and ``hoshi`` does use ``gettext`` and ``babel`` extensively. As such, most standard
tools and techniques which apply to gettext based i18n can be used alongside
``hoshi`` with no additional risks.
