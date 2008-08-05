##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for the Acquisition egg package
"""
import os
from setuptools import setup, find_packages, Extension

setup(name='Persistence',
      version = '2.11.1',
      url='http://cheeseshop.python.org/pypi/Persistence',
      license='ZPL 2.1',
      description='Persistent ExtensionClass',
      author='Zope Corporation and Contributors',
      author_email='zope-dev@zope.org',
      long_description="""\
This package provides a variant of the persistent base class that's an
ExtensionClass.  Unless you need ExtensionClass semantics, you
probably want to use persistent.Persistent from ZODB3.""",

      packages=find_packages('src'),
      package_dir={'': 'src'},

      ext_modules=[Extension("Persistence._Persistence",
                             [os.path.join('src', 'Persistence',
                                           '_Persistence.c')],
                             include_dirs=['include', 'src']),
                   ],
      install_requires=['ExtensionClass', 'ZODB3'],
      include_package_data=True,
      zip_safe=False,
      )
