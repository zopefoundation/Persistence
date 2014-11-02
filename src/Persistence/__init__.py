import os

from ExtensionClass import Base
import persistent


class Persistent(Base, persistent.Persistent):
    pass


if 'PURE_PYTHON' not in os.environ:  # pragma no cover
    try:
        from _Persistence import Persistent  # NOQA
    except ImportError:
        pass

Overridable = Persistent
from Persistence.mapping import PersistentMapping  # NOQA
