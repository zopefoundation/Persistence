import os
from setuptools import setup, find_packages, Extension

README = open('README.rst').read()
CHANGES = open('CHANGES.rst').read()

ext_modules = [
    Extension("Persistence._Persistence",
              [os.path.join('src', 'Persistence',
              '_Persistence.c')],
              include_dirs=['include', 'src']),
]

setup(
    name='Persistence',
    version='3.0dev',
    url='http://pypi.python.org/pypi/Persistence',
    license='ZPL 2.1',
    description='Persistent ExtensionClass',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    long_description='\n\n'.join([README, CHANGES]),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    ext_modules=ext_modules,
    install_requires=[
        'ExtensionClass >= 4.1a1',
        'persistent',
    ],
    include_package_data=True,
    zip_safe=False,
)
