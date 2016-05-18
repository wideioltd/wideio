"""
MIMEJSON Serialization.

MIMEJSON extends JSON to allow automatically serialization of large binary objects as "attached" objects.

These large object can then be LAZILY loaded. This is an ALPHA software - the exact specification
of MIMEJSON is likely to evolve through iteration.
"""
import os
from . import llapi
from . import hlapi

try:
    __version__ = open(os.path.join(os.path.dirname(__file__), "VERSION"), "r").read()
except:
    __version__ = "N/A"

__all__ = ('llapi', 'hlapi', '__version__')
