##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

from abc import ABCMeta

from ExtensionClass import ExtensionClass
from persistent.mapping import PersistentMapping as _BasePersistentMapping
import six

from Persistence import Persistent


class _Meta(ExtensionClass, ABCMeta):
    # persistent.mapping is based on collections.UserDict,
    # which has an ABCMeta class. Reconcile this with the
    # ExtensionClass meta class, by ignoring the ABCMeta registration.

    def __new__(cls, *args, **kw):
        # Ignore ABCMeta.
        return ExtensionClass.__new__(cls, *args, **kw)


if six.PY2:
    # Neither six.with_metaclass nor six.add_metaclass work under
    # both Python 2 and 3 for us, so we provide to code paths.

    class PersistentMapping(Persistent, _BasePersistentMapping):
        """Legacy persistent mapping class

        This class mixes in :class:`ExtensionClass.Base` if it is present.

        Unless you actually want ExtensionClass semantics, use
        :class:`persistent.mapping.PersistentMapping` instead.
        """
        __metaclass__ = _Meta

        def __setstate__(self, state):
            if 'data' not in state:
                state['data'] = state['_container']
                del state['_container']
            self.__dict__.update(state)

else:

    class PersistentMapping(six.with_metaclass(
            _Meta, Persistent, _BasePersistentMapping)):
        """Legacy persistent mapping class

        This class mixes in :class:`ExtensionClass.Base` if it is present.

        Unless you actually want ExtensionClass semantics, use
        :class:`persistent.mapping.PersistentMapping` instead.
        """

        def __setstate__(self, state):
            if 'data' not in state:
                state['data'] = state['_container']
                del state['_container']
            self.__dict__.update(state)
