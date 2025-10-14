#!/usr/bin/env python

"""Setup script for the 'decompile-cfg' distribution."""

import sys
from setuptools import find_packages, setup

from __pkginfo__ import (
    __version__,
    author,
    author_email,
    classifiers,
    entry_points,
    install_requires,
    license,
    long_description,
    modname,
    py_modules,
    short_desc,
    web,
    zip_safe,
)

major = sys.version_info[0]
minor = sys.version_info[1]

if major != 3 or not 8 <= minor < 10:
    sys.stderr.write(
        "This installation medium is only for Python 3.8 to Python 3.10. You are running Python %s.%s.\n"
        % (major, minor)
    )

    if major == 3 and minor > 11:
        sys.stderr.write(
            "Please install using the master branch or python-decompile-cfg-x.y.z.tar.gz from https://github.com/rocky/python-decompile-cfg/releases\n"
        )
        sys.exit(1)

#!/usr/bin/env python
"""Setup script for the 'decompyle3' distribution."""

setup(
    author=author,
    author_email=author_email,
    classifiers=classifiers,
    description=short_desc,
    # entry_points=entry_points,
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
