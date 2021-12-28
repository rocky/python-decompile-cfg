#!/usr/bin/env python
import sys

"""Setup script for the 'decompile_ng' distribution."""

SYS_VERSION = sys.version_info[0:2]
if SYS_VERSION < (3, 6):
    mess = f"\nThis package is not supported for Python version {sys.version[0:3]}."
    mess += "\nFor earlier versions, use decompile3 or uncompyle6."
    print(mess)
    raise Exception(mess)
elif SYS_VERSION < (3, 10):
    mess = f"\nThis package does not decompile for Python version {sys.version[0:3]}, just 3.10."
    print(mess)

from __pkginfo__ import (
    author,
    author_email,
    install_requires,
    license,
    long_description,
    classifiers,
    entry_points,
    modname,
    py_modules,
    short_desc,
    __version__,
    web,
    zip_safe,
)

from setuptools import setup, find_packages

setup(
    author=author,
    author_email=author_email,
    classifiers=classifiers,
    description=short_desc,
    entry_points=entry_points,
    install_requires=install_requires,
    license=license,
    long_description=long_description,
    name=modname,
    packages=find_packages(),
    py_modules=py_modules,
    test_suite="nose.collector",
    url=web,
    tests_require=["nose>=1.0"],
    version=__version__,
    zip_safe=zip_safe,
)
