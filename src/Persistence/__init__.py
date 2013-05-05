import os

from ExtensionClass import Base
import persistent


class Persistent(Base, persistent.Persistent):
    pass


if not 'PURE_PYTHON' in os.environ:  # pragma no cover
    try:
        from _Persistence import Persistent
    except ImportError:
        pass

Overridable = Persistent
from Persistence.mapping import PersistentMapping
