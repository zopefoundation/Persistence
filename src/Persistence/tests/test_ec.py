##############################################################################
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

from doctest import DocTestSuite

from Persistence import Persistent


def print_dict(d):
    d = d.items()
    print('{%s}' % (', '.join(
        [(f'{k!r}: {v!r}') for (k, v) in sorted(d)]
    )))


def test_basic():
    """

    >>> from ExtensionClass import Base

    - Support for a class initialiser:

      >>> class C(Persistent):
      ...   def __class_init__(self):
      ...      print('class init called')
      ...      print(self.__name__)
      ...   def bar(self):
      ...      return 'bar called'
      class init called
      C
      >>> c = C()
      >>> int(c.__class__ is C)
      1
      >>> int(c.__class__ is type(c))
      1

    - Provide an inheritedAttribute method for looking up attributes in
      base classes:

      >>> class C2(C):
      ...   def bar(*a):
      ...      return C2.inheritedAttribute('bar')(*a), 42
      class init called
      C2
      >>> o = C2()
      >>> o.bar()
      ('bar called', 42)

      This is for compatability with old code. New code should use super
      instead.

    The base class, Base, exists mainly to support the __of__ protocol.
    The __of__ protocol is similar to __get__ except that __of__ is called
    when an implementor is retrieved from an instance as well as from a
    class:

    >>> class O(Base):
    ...   def __of__(*a):
    ...      return a

    >>> o1 = O()
    >>> o2 = O()
    >>> C.o1 = o1
    >>> c.o2 = o2
    >>> c.o1 == (o1, c)
    1
    >>> C.o1 == o1
    1
    >>> int(c.o2 == (o2, c))
    1

    We accomplish this by making a class that implements __of__ a
    descriptor and treating all descriptor ExtensionClasses this way. That
    is, if an extension class is a descriptor, it's __get__ method will be
    called even when it is retrieved from an instance.

    >>> class O(Base):
    ...   def __get__(*a):
    ...      return a
    ...
    >>> o1 = O()
    >>> o2 = O()
    >>> C.o1 = o1
    >>> c.o2 = o2
    >>> int(c.o1 == (o1, c, type(c)))
    1
    >>> int(C.o1 == (o1, None, type(c)))
    1
    >>> int(c.o2 == (o2, c, type(c)))
    1
    """


def test_mixing():
    """Test working with a classic class

    >>> class Classic:
    ...   def x(self):
    ...     return 42

    >>> class O(Persistent):
    ...   def __of__(*a):
    ...      return a

    >>> class O2(Classic, O):
    ...   def __of__(*a):
    ...      return (O2.inheritedAttribute('__of__')(*a),
    ...              O2.inheritedAttribute('x')(a[0]))

    >>> class C(Persistent):
    ...   def __class_init__(self):
    ...      print('class init called')
    ...      print(self.__name__)
    ...   def bar(self):
    ...      return 'bar called'
    class init called
    C

    >>> c = C()
    >>> o2 = O2()
    >>> c.o2 = o2
    >>> int(c.o2 == ((o2, c), 42))
    1

    Test working with a new style

    >>> class Modern(object):
    ...   def x(self):
    ...     return 42

    >>> class O2(Modern, O):
    ...   def __of__(*a):
    ...      return (O2.inheritedAttribute('__of__')(*a),
    ...              O2.inheritedAttribute('x')(a[0]))

    >>> o2 = O2()
    >>> c.o2 = o2
    >>> int(c.o2 == ((o2, c), 42))
    1
    """


def test_class_creation_under_stress():
    """
    >>> numbers = []
    >>> for i in range(100):
    ...     class B(Persistent):
    ...         numbers.append(i)
    >>> numbers == list(range(100))
    True

    >>> import gc
    >>> x = gc.collect()
    """


def proper_error_on_deleattr():
    """
    Florent Guillaume wrote:

    ...

    Excellent.
    Will it also fix this particularity of ExtensionClass:


    >>> class A(Persistent):
    ...   def foo(self):
    ...     self.gee
    ...   def bar(self):
    ...     del self.gee

    >>> a=A()
    >>> a.foo()  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    AttributeError: 'A' object has no attribute 'gee'

    >>> a.bar()  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    AttributeError: 'A' object has no attribute 'gee'

    I.e., the fact that KeyError is raised whereas a normal class would
    raise AttributeError.
    """


def test__basicnew__():
    """
    >>> x = Simple.__basicnew__()
    >>> x.__dict__
    {}
    """


def cmpattrs(self, other, *attrs):
    for attr in attrs:
        if attr[:3] in ('_v_', '_p_'):
            continue
        c = getattr(self, attr, None) == getattr(other, attr, None)
        if c:
            return c
    return 0


class Simple(Persistent):
    def __init__(self, name, **kw):
        self.__name__ = name
        self.__dict__.update(kw)
        self._v_favorite_color = 'blue'
        self._p_foo = 'bar'

    def __eq__(self, other):
        return cmpattrs(self, other, '__class__', *(self.__dict__.keys()))


def test_basic_pickling():
    """
    >>> x = Simple('x', aaa=1, bbb='foo')

    >>> print_dict(x.__getstate__())
    {'__name__': 'x', 'aaa': 1, 'bbb': 'foo'}

    >>> f, (c,), state = x.__reduce__()
    >>> f.__name__
    '__newobj__'
    >>> f.__module__ in ('copyreg', 'copy_reg')
    True
    >>> c.__name__
    'Simple'

    >>> print_dict(state)
    {'__name__': 'x', 'aaa': 1, 'bbb': 'foo'}

    >>> import pickle
    >>> pickle.loads(pickle.dumps(x)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 0)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 1)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 2)) == x
    1

    >>> x.__setstate__({'z': 1})
    >>> x.__dict__
    {'z': 1}
    """


class Custom(Simple):

    def __new__(cls, x, y):
        r = Persistent.__new__(cls)
        r.x, r.y = x, y
        return r

    def __init__(self, x, y):
        self.a = 42

    def __getnewargs__(self):
        return self.x, self.y

    def __getstate__(self):
        return self.a

    def __setstate__(self, a):
        self.a = a


def test_pickling_w_overrides():
    """
    >>> x = Custom('x', 'y')
    >>> x.a = 99

    >>> (f, (c, ax, ay), a) = x.__reduce__()
    >>> f.__name__
    '__newobj__'
    >>> f.__module__ in ('copy_reg', 'copyreg')
    True
    >>> c.__name__
    'Custom'
    >>> ax, ay, a
    ('x', 'y', 99)

    >>> import pickle
    >>> pickle.loads(pickle.dumps(x)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 0)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 1)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 2)) == x
    1
    """


class Slotted(Persistent):
    __slots__ = 's1', 's2', '_p_splat', '_v_eek'

    def __init__(self, s1, s2):
        self.s1, self.s2 = s1, s2
        self._v_eek = 1
        self._p_splat = 2


class SubSlotted(Slotted):
    __slots__ = 's3', 's4'

    def __init__(self, s1, s2, s3):
        Slotted.__init__(self, s1, s2)
        self.s3 = s3

    def __eq__(self, other):
        return cmpattrs(self, other, '__class__', 's1', 's2', 's3', 's4')


def test_pickling_w_slots_only():
    """
    >>> x = SubSlotted('x', 'y', 'z')

    >>> d, s = x.__getstate__()
    >>> d
    >>> print_dict(s)
    {'s1': 'x', 's2': 'y', 's3': 'z'}

    >>> import pickle
    >>> pickle.loads(pickle.dumps(x)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 0)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 1)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 2)) == x
    1

    >>> x.s4 = 'spam'

    >>> d, s = x.__getstate__()
    >>> d
    >>> print_dict(s)
    {'s1': 'x', 's2': 'y', 's3': 'z', 's4': 'spam'}

    >>> pickle.loads(pickle.dumps(x)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 0)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 1)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 2)) == x
    1
    """


class SubSubSlotted(SubSlotted):

    def __init__(self, s1, s2, s3, **kw):
        SubSlotted.__init__(self, s1, s2, s3)
        self.__dict__.update(kw)
        self._v_favorite_color = 'blue'
        self._p_foo = 'bar'

    def __eq__(self, other):
        return cmpattrs(self, other,
                        '__class__', 's1', 's2', 's3', 's4',
                        *(self.__dict__.keys()))


def test_pickling_w_slots():
    """
    >>> x = SubSubSlotted('x', 'y', 'z', aaa=1, bbb='foo')

    >>> d, s = x.__getstate__()
    >>> print_dict(d)
    {'aaa': 1, 'bbb': 'foo'}
    >>> print_dict(s)
    {'s1': 'x', 's2': 'y', 's3': 'z'}

    >>> import pickle
    >>> pickle.loads(pickle.dumps(x)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 0)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 1)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 2)) == x
    1

    >>> x.s4 = 'spam'

    >>> d, s = x.__getstate__()
    >>> print_dict(d)
    {'aaa': 1, 'bbb': 'foo'}
    >>> print_dict(s)
    {'s1': 'x', 's2': 'y', 's3': 'z', 's4': 'spam'}

    >>> pickle.loads(pickle.dumps(x)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 0)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 1)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 2)) == x
    1
    """


def test_pickling_w_slots_w_empty_dict():
    """
    >>> x = SubSubSlotted('x', 'y', 'z')

    >>> d, s = x.__getstate__()
    >>> print_dict(d)
    {}
    >>> print_dict(s)
    {'s1': 'x', 's2': 'y', 's3': 'z'}

    >>> import pickle
    >>> pickle.loads(pickle.dumps(x)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 0)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 1)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 2)) == x
    1

    >>> x.s4 = 'spam'

    >>> d, s = x.__getstate__()
    >>> print_dict(d)
    {}
    >>> print_dict(s)
    {'s1': 'x', 's2': 'y', 's3': 'z', 's4': 'spam'}

    >>> pickle.loads(pickle.dumps(x)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 0)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 1)) == x
    1
    >>> pickle.loads(pickle.dumps(x, 2)) == x
    1
    """


def test_setattr_on_extension_type():
    """
    >>> for name in 'x', '_x', 'x_', '__x_y__', '___x__', '__x___', '_x_':
    ...     setattr(Persistent, name, 1)
    ...     print(getattr(Persistent, name))
    ...     delattr(Persistent, name)
    ...     print(getattr(Persistent, name, 0))
    1
    0
    1
    0
    1
    0
    1
    0
    1
    0
    1
    0
    1
    0

    >>> Persistent.__foo__ = 1  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    TypeError: can't set attributes of built-in/extension type """ \
        """'Persistence.Persistent' if the attribute name begins """ \
        """and ends with __ and contains only 4 _ characters

    >>> Persistent.__foo__  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ...
    AttributeError: ...

    >>> try:
    ...     del Persistent.__foo__
    ... except (AttributeError, TypeError):  # different on pypy
    ...     print('error')
    error
    """


def test_suite():
    return DocTestSuite()
