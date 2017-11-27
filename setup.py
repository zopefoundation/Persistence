import os
import platform

from setuptools import setup, find_packages, Extension

README = open('README.rst').read()
CHANGES = open('CHANGES.rst').read()

# PyPy won't build the extension
py_impl = getattr(platform, 'python_implementation', lambda: None)
is_pypy = py_impl() == 'PyPy'
is_pure = 'PURE_PYTHON' in os.environ
if is_pypy or is_pure:
    ext_modules = []
else:
    ext_modules = [
        Extension("Persistence._Persistence",
                  [os.path.join('src', 'Persistence', '_Persistence.c')],
                  include_dirs=['include', 'src']),
    ]

version = '3.0b2'

setup(
    name='Persistence',
    version=version,
    url='http://pypi.python.org/pypi/Persistence',
    license='ZPL 2.1',
    description='Persistent ExtensionClass',
    author='Zope Foundation and Contributors',
    author_email='zope-dev@zope.org',
    long_description='\n\n'.join([README, CHANGES]),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Web Environment",
        "Framework :: Zope2",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    ext_modules=ext_modules,
    install_requires=[
        'ExtensionClass >= 4.2.0',
        'persistent >= 4.1.1',
        'six',
    ],
    include_package_data=True,
    zip_safe=False,
)
