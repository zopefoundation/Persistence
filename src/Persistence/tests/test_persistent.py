#############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
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

import pickle
import time
import unittest
from struct import pack

from persistent import PickleCache
from persistent.TimeStamp import TimeStamp

from Persistence import CAPI
from Persistence import IS_PURE
from Persistence import IS_PYPY
from Persistence import Persistent


def p64(v):
    """Pack an integer or long into a 8-byte string"""
    return pack(">Q", v)


class Jar(object):
    """Testing stub for _p_jar attribute."""

    def __init__(self):
        self.cache = PickleCache(self)
        self.oid = 1
        self.registered = {}

    def add(self, obj):
        obj._p_oid = p64(self.oid)
        self.oid += 1
        obj._p_jar = self
        self.cache[obj._p_oid] = obj

    def close(self):
        pass

    # the following methods must be implemented to be a jar

    def setklassstate(self):
        # I don't know what this method does, but the pickle cache
        # constructor calls it.
        pass

    def register(self, obj):
        self.registered[obj] = 1

    def setstate(self, obj):
        # Trivial setstate() implementation that just re-initializes
        # the object.  This isn't what setstate() is supposed to do,
        # but it suffices for the tests.
        obj.__class__.__init__(obj)


class P(Persistent):
    pass


class H1(Persistent):

    def __init__(self):
        self.n = 0

    def __getattr__(self, attr):
        self.n += 1
        return self.n


class H2(Persistent):

    def __init__(self):
        self.n = 0

    def __getattribute__(self, attr):
        supergetattr = super(H2, self).__getattribute__
        try:
            return supergetattr(attr)
        except AttributeError:
            n = supergetattr("n")
            self.n = n + 1
            return n + 1


class PersistenceTest(unittest.TestCase):

    def setUp(self):
        self.jar = Jar()

    def tearDown(self):
        self.jar.close()

    def test_oid_jar_attrs(self):
        obj = P()
        self.assertEqual(obj._p_oid, None)
        obj._p_oid = 12
        self.assertEqual(obj._p_oid, 12)
        del obj._p_oid

        self.jar.add(obj)

        # Can't change oid of cache object.
        with self.assertRaises(ValueError):
            del obj._p_oid

        with self.assertRaises(ValueError):
            obj._p_oid = 12

        with self.assertRaises(ValueError):
            del obj._p_jar

        with self.assertRaises(ValueError):
            obj._p_jar = 12

    def testChanged(self):
        obj = P()
        self.jar.add(obj)

        # The value returned for _p_changed can be one of:
        # 0 -- it is not changed
        # 1 -- it is changed
        # None -- it is a ghost

        obj.x = 1
        self.assertEqual(obj._p_changed, 1)
        self.assertIn(obj, self.jar.registered)

        obj._p_changed = 0
        self.assertEqual(obj._p_changed, 0)
        self.jar.registered.clear()

        obj._p_changed = 1
        self.assertEqual(obj._p_changed, 1)
        self.assertIn(obj, self.jar.registered)

        # setting obj._p_changed to None ghostifies if the
        # object is in the up-to-date state, but not otherwise.
        obj._p_changed = None
        self.assertEqual(obj._p_changed, 1)
        obj._p_changed = 0
        # Now it's a ghost.
        obj._p_changed = None
        self.assertEqual(obj._p_changed, None)

        obj = P()
        self.jar.add(obj)
        obj._p_changed = 1
        # You can transition directly from modified to ghost if
        # you delete the _p_changed attribute.
        del obj._p_changed
        self.assertEqual(obj._p_changed, None)

    def testSerial(self):
        noserial = b'\000' * 8
        obj = P()
        self.assertEqual(obj._p_serial, noserial)

        def set(val):
            obj._p_serial = val
        self.assertRaises(ValueError, set, 1)
        self.assertRaises(ValueError, set, "0123")
        self.assertRaises(ValueError, set, "012345678")
        self.assertRaises(ValueError, set, u"01234567")

        obj._p_serial = b"01234567"
        del obj._p_serial
        self.assertEqual(obj._p_serial, noserial)

    def testMTime(self):
        obj = P()
        self.assertEqual(obj._p_mtime, None)

        t = int(time.time())
        ts = TimeStamp(*time.gmtime(t)[:6])
        obj._p_serial = ts.raw()
        self.assertEqual(obj._p_mtime, t)
        self.assertIsInstance(obj._p_mtime, float)

    def testPicklable(self):
        obj = P()
        obj.attr = "test"
        s = pickle.dumps(obj)
        obj2 = pickle.loads(s)
        self.assertEqual(obj.attr, obj2.attr)

    def testGetattr(self):
        obj = H1()
        self.assertEqual(obj.larry, 1)
        self.assertEqual(obj.curly, 2)
        self.assertEqual(obj.moe, 3)

        self.jar.add(obj)
        obj._p_deactivate()

        # The simple Jar used for testing re-initializes the object.
        self.assertEqual(obj.larry, 1)
        # The getattr hook modified the object, so it should now be
        # in the changed state.
        self.assertEqual(obj._p_changed, 1)
        self.assertEqual(obj.curly, 2)
        self.assertEqual(obj.moe, 3)

    def testGetattribute(self):
        obj = H2()
        self.assertEqual(obj.larry, 1)
        self.assertEqual(obj.curly, 2)
        self.assertEqual(obj.moe, 3)

        self.jar.add(obj)
        obj._p_deactivate()

        # The simple Jar used for testing re-initializes the object.
        self.assertEqual(obj.larry, 1)
        # The getattr hook modified the object, so it should now be
        # in the changed state.
        self.assertEqual(obj._p_changed, 1)
        self.assertEqual(obj.curly, 2)
        self.assertEqual(obj.moe, 3)

    # TODO:  Need to decide how __setattr__ and __delattr__ should work,
    # then write tests.

    def test_compilation(self):
        self.assertEqual(CAPI, not (IS_PYPY or IS_PURE))
        try:
            import persistent.cPersistence  # noqa: F401 unused, needed for Py3

            from Persistence import _Persistence
            cPersistent = _Persistence.Persistent
        except ImportError:
            cPersistent = None  # PyPy never has a C module.
        if CAPI:  # pragma: no cover
            self.assertEqual(Persistent, cPersistent)
        else:
            self.assertNotEqual(Persistent, cPersistent)
