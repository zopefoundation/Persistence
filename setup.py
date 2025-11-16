import os
import platform

from setuptools import Extension
from setuptools import setup


# PyPy won't build the extension
py_impl = getattr(platform, 'python_implementation', lambda: None)
is_pypy = py_impl() == 'PyPy'
if is_pypy:
    ext_modules = []
else:
    ext_modules = [
        Extension("Persistence._Persistence",
                  [os.path.join('src', 'Persistence', '_Persistence.c')],
                  include_dirs=['include', 'src']),
    ]


setup(ext_modules=ext_modules)
