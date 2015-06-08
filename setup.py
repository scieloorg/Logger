#!/usr/bin/env python
import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.rst')) as f:
    CHANGES = f.read()

install_requires = [
    'requests>=2.6.0',
    'apachelog>=1.1',
    'pymongo>=2.8'
]

tests_require = [
    'mocker'
]

setup(
    name="logger",
    version='0.1.2',
    description="A SciELO tool to load apache log files and register access into Ratchet.",
    author="SciELO",
    author_email="scielo-dev@googlegroups.com",
    license="BSD 2-clause",
    url="http://docs.scielo.org",
    packages=['logger'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Internal Service",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Operating System :: POSIX :: Linux",
        "Topic :: System",
        "Topic :: Utilities",
    ],
    install_requires=install_requires,
    setup_requires=["nose>=1.0", "coverage"],
    tests_require=tests_require,
    test_suite="nose.collector",
    entry_points="""\
    [console_scripts]
    logger_loadlogs = logger.scielo:main
    logger_loadlogs_readcube = logger.readcube:main
    """,
)
