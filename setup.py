

import setuptools

_requires = [
    'babel',
    'setuptools-scm',
    'google-cloud-translate',
]

setuptools.setup(
    name='hoshi',
    url='https://github.com/chintal/hoshi',

    author='Chintalagiri Shashank',
    author_email='shashank.chintalagiri@gmail.com',

    description='Python i18n for human beings',
    long_description='',

    packages=setuptools.find_packages(),
    install_requires=_requires,
    setup_requires=['setuptools_scm'],
    use_scm_version=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Localization',
    ],
)
