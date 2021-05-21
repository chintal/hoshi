

def pytest_configure():
    from hoshi.i18n import TranslationManager
    tm = TranslationManager(['en_IN'], ["_tmp/locale"])
    tm.install()
    tm.install_context('test', 'en_IN')
    _ = tm.translator("test")
    _('Hello World')
