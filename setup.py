#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name="logger",
    version='0.1',
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
    setup_requires=["nose>=1.0", "coverage", "pymongo", "apachelog"],
    tests_require=["mocker"],
    test_suite="nose.collector",
)
