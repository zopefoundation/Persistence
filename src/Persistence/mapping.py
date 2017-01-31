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

from _weakrefset import WeakSet
from abc import ABCMeta
from abc import _InstanceType

from ExtensionClass import ExtensionClass
from persistent.mapping import PersistentMapping as _BasePersistentMapping
import six

from Persistence import Persistent


class _Meta(ExtensionClass, ABCMeta):
    # persistent.mapping is based on collections.UserDict,
    # which has an ABCMeta class. Reconcile this with the
    # ExtensionClass meta class, by ignoring the ABCMeta registration.

    _abc_invalidation_counter = 0

    def __new__(cls, *args, **kw):
        # Ignore ABCMeta.
        cls._abc_registry = WeakSet()
        cls._abc_cache = WeakSet()
        cls._abc_negative_cache = WeakSet()
        cls._abc_negative_cache_version = _Meta._abc_invalidation_counter

        return ExtensionClass.__new__(cls, *args, **kw)

    def __instancecheck__(cls, instance):
        """Override for isinstance(instance, cls)."""
        # Inline the cache checking when it's simple.
        subclass = getattr(instance, '__class__', None)
        if subclass is not None and subclass in cls._abc_cache:
            return True
        subtype = type(instance)
        # Old-style instances
        if subtype is _InstanceType:
            subtype = subclass
        if subtype is subclass or subclass is None:
            if (cls._abc_negative_cache_version ==
                    _Meta._abc_invalidation_counter and
                    subtype in cls._abc_negative_cache):
                return False
            # Fall back to the subclass check.
            return cls.__subclasscheck__(subtype)
        return (cls.__subclasscheck__(subclass) or
                cls.__subclasscheck__(subtype))

    def __subclasscheck__(cls, subclass):
        """Override for issubclass(subclass, cls)."""
        # Check cache
        if subclass in cls._abc_cache:
            return True
        # Check negative cache; may have to invalidate
        if cls._abc_negative_cache_version < _Meta._abc_invalidation_counter:
            # Invalidate the negative cache
            cls._abc_negative_cache = WeakSet()
            cls._abc_negative_cache_version = _Meta._abc_invalidation_counter
        elif subclass in cls._abc_negative_cache:
            return False
        # Check the subclass hook
        ok = cls.__subclasshook__(subclass)
        if ok is not NotImplemented:
            assert isinstance(ok, bool)
            if ok:
                cls._abc_cache.add(subclass)
            else:
                cls._abc_negative_cache.add(subclass)
            return ok
        # Check if it's a direct subclass
        if cls in getattr(subclass, '__mro__', ()):
            cls._abc_cache.add(subclass)
            return True
        # Check if it's a subclass of a registered class (recursive)
        for rcls in cls._abc_registry:
            if issubclass(subclass, rcls):
                cls._abc_cache.add(subclass)
                return True
        # Check if it's a subclass of a subclass (recursive)
        for scls in cls.__subclasses__():
            if issubclass(subclass, scls):
                cls._abc_cache.add(subclass)
                return True
        # No dice; update negative cache
        cls._abc_negative_cache.add(subclass)
        return False


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

else:  # pragma: no cover

    def with_metaclass(meta, *bases):
        # Adopted from six.with_metaclass.

        # Create a base class with a metaclass.
        # This requires a bit of explanation: the basic idea is to make a dummy
        # metaclass for one level of class instantiation that replaces itself
        # with the actual metaclass.

        class metaclass(meta):  # NOQA

            def __new__(cls, name, this_bases, d):
                return meta(name, bases, d)
        # Use ExtensionClass.__new__ instead of type.__new__
        return ExtensionClass.__new__(metaclass, 'temporary_class', (), {})

    class PersistentMapping(with_metaclass(
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
