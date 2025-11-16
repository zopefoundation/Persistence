Change log
==========

5.4 (2025-11-16)
----------------

- Move all supported package metadata into ``pyproject.toml``.


5.3 (2025-11-15)
----------------

- Fix the GitHub workflow for publishing wheels, which failed for Linux/arm64.
  (`#348 <https://github.com/zopefoundation/zope.interface/issues/348>`_)


5.2 (2025-11-06)
----------------

- Add support for Python 3.14.

- Drop support for Python 3.8, 3.9.


5.1 (2024-09-17)
----------------

- Add final support for Python 3.13.


5.0 (2024-05-30)
----------------

- Drop support for Python 3.7.

- Add preliminary support for Python 3.13 as of 3.13a3.

- Build Windows wheels on GHA.


4.1 (2023-10-05)
----------------

- Add support for Python 3.12.


4.0.post1 (2023-03-24)
----------------------

- Add missing ``python_requires`` in ``setup.py``.


4.0 (2023-03-24)
----------------

- Build Linux binary wheels for Python 3.11.

- Drop support for Python 2.7, 3.5, 3.6.

- Add preliminary support for Python 3.12a5.


3.6 (2022-11-17)
----------------

- Add support for building arm64 wheels on macOS.


3.5 (2022-11-03)
----------------

- Add support for final Python 3.11 release.


3.4 (2022-10-11)
----------------

- Add support for Python 3.11 as of (3.11.0rc2).

- Disable unsafe math optimizations in C code.
  (`#55 <https://github.com/zopefoundation/ExtensionClass/pull/55>`_)


3.3 (2022-03-10)
----------------

- Add support for Python 3.11 as of (3.11.0a5).


3.2 (2022-03-02)
----------------

- Add support for Python 3.10.


3.1 (2021-07-23)
----------------

- Create wheels for Linux (2010, 2014 and aarch64) and MacOS.

- Add support for Python 3.9.

- On CPython no longer omit compiling the C code when ``PURE_PYTHON`` is set.
  Just evaluate it at runtime.
  (`#27 <https://github.com/zopefoundation/Persistence/issues/27>`_)


3.0 (2019-05-08)
----------------

Changes since 2.13.2:

- Add support for Python 3.5, 3.6, 3.7 and 3.8a3.

- Drop support for Python 2.6.

- Make tests compatible with `persistent >= 4.2.3`.

- Fix for compilers that only support C89 syntax (e.g. on Windows).

- Ensure our dependencies match our expectations about C extensions.
  (`#4 <https://github.com/zopefoundation/Persistence/issues/4>`_)

- Update ExtensionClass and persistent headers.

- Fix isinstance/issubclass for the Python version of PersistentMapping.

- Add AppVeyor configuration to automate building Windows eggs.


2.13.2 (2010-06-16)
-------------------

- LP #587760: Handle tp_basicsize correctly.


2.13.1 (2010-04-30)
-------------------

- Removed undeclared testing dependency on zope.testing.


2.13.0 (2010-02-23)
-------------------

- Update to include ExtensionClass 2.13.0.


2.12.0 (2010-02-14)
-------------------

- Added support for method cache in Persistence. Patch contributed by
  Yoshinori K. Okuji. See https://bugs.launchpad.net/zope2/+bug/486193.

- Updated C includes to ExtensionClass 2.12.0.

- Updated package metadata and remove old build artifacts.


2.11.1 (2009-02-19)
-------------------

- First egg release.
