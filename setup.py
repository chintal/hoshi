import setuptools

_requires = [
    'babel',
    'setuptools-scm',
]

setuptools.setup(
    name='hoshi',
    url='https://github.com/chintal/hoshi',

    author='Chintalagiri Shashank',
    author_email='shashank.chintalagiri@gmail.com',

    description=' Python i18n for human beings ',
    long_description='',

    packages=setuptools.find_packages(),
    install_requires=_requires,
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Localization',
    ],
)
