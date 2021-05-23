
import os
import setuptools


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    orig_content = open(os.path.join(os.path.dirname(__file__), fname)).readlines()
    content = ""
    in_raw_directive = 0
    for line in orig_content:
        if in_raw_directive:
            if not line.strip():
                in_raw_directive = in_raw_directive - 1
            continue
        elif line.strip() == '.. raw:: latex':
            in_raw_directive = 2
            continue
        content += line
    return content


core_dependencies = [
    'babel',
    'setuptools-scm',
    'google-cloud-translate',
]

install_requires = core_dependencies + ['wheel']

setup_requires = ['setuptools_scm']

doc_requires = setup_requires + ['sphinx', 'alabaster']

test_requires = doc_requires + ['tox', 'tox-pyenv',
                                'pytest-sphinx', 'pytest',
                                'pytest-flake8', 'pytest-cov', 'coveralls[yaml]']

build_requires = test_requires  # + ['doit', 'pyinstaller']

publish_requires = build_requires + ['twine', 'pygithub']

setuptools.setup(
    name='hoshi',
    url='https://github.com/chintal/hoshi',

    author='Chintalagiri Shashank',
    author_email='shashank.chintalagiri@gmail.com',

    description='Python i18n for human beings',
    long_description='\n'.join([read('README.rst'), read('CHANGELOG.rst')]),
    long_description_content_type='text/x-rst',

    project_urls={
        'Documentation': 'https://hoshi.readthedocs.io/en/latest',
        'Bug Tracker': 'https://github.com/chintal/hoshi/issues',
        'Source Repository': 'https://github.com/chintal/hoshi',
    },

    packages=setuptools.find_packages(),
    use_scm_version=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Localization',
    ],
    python_requires='>=3.7',
    install_requires=install_requires,
    setup_requires=setup_requires,
    extras_require={
        'docs': doc_requires,
        'tests': test_requires,
        'build': build_requires,
        'publish': publish_requires,
        'dev': build_requires,
    },
    platforms='any',
)
