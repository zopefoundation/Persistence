Change log
==========

5.7 (unreleased)
----------------

- Make the ``Persistence.Persistent`` C type heap-allocated, and the
  ``Persistence._Persistence`` extension module use PEP 489
  multi-phase initialization.

  This change is required for compatibility with ``persistent``
  releases which heap-allocate their own ``Persistent`` type:  CPython
  forbids static types from inheriting from heap types.  The Zope
  stacks are known to define no C-level subclasses of
  ``Persistence.Persistent``; should any exist elsewhere, they must
  make the corresponding change.  The extension remains compatible
  with older, static-type ``persistent`` releases as well.

  Consequences of the type itself now being a heap type:

  - The type continues to enforce ExtensionClass's rule barring dunder
    attribute names on the class object (e.g.
    ``Persistence.Persistent.__foo__``), now through a private
    metaclass, itself a subclass of
    ``ExtensionClass.ExtensionClass``:  Python classes deriving from
    ``Persistence.Persistent`` resolve to it, as they previously
    resolved to ``ExtensionClass.ExtensionClass``, and inherit the
    same discipline.

  (A behavioral delta in ghosting of ``__slots__``-based subclasses
  traces to the related ``persistent`` change, not to this one;  see
  the persistent release notes for the details.)


5.6 (2026-11-21)
----------------

- Add support for Python 3.15.

- Drop support for Python 3.10.


5.5 (2026-08-20)
----------------

- Add support for Python 3.15.

- Add support for automatically building and publishing Windows/ARM64 wheels.

- Add support for automatically building and publishing source distributions.


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
