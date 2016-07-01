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
import os

from ExtensionClass import Base
import persistent


class Persistent(Base, persistent.Persistent):
    """Legacy persistent class

    This class mixes in :class:`ExtensionClass.Base` if it is present.

    Unless you actually want ExtensionClass semantics, use
    :class:`persistent.mapping.Persistent` instead.
    """
    pass


if 'PURE_PYTHON' not in os.environ:  # pragma no cover
    try:
        from _Persistence import Persistent  # NOQA
    except ImportError:
        pass

Overridable = Persistent

# API Import after setting up the base class
from Persistence.mapping import PersistentMapping  # NOQA
