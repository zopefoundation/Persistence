##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Setup for the Persistence distribution
"""
import os
from setuptools import setup, find_packages, Extension

README = open('README.txt').read()
CHANGES = open('CHANGES.txt').read()

setup(name='Persistence',
      version = '2.13.1',
      url='http://pypi.python.org/pypi/Persistence',
      license='ZPL 2.1',
      description='Persistent ExtensionClass',
      author='Zope Foundation and Contributors',
      author_email='zope-dev@zope.org',
      long_description='\n\n'.join([README, CHANGES]),

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
