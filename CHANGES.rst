Changelog
=========

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
