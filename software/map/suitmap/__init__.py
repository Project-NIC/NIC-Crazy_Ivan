"""Baťa's map (bata/SOFTWARE.md, *The map*): the suit's table of what is fitted and every unit's
settings, keyed by the UID, kept in one JSON file and shown and set through plain HTML forms.

The codecs are the protocol's (`software/protocol/ci`), found beside this folder.
"""
import os
import sys

_PROTOCOL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(
    __file__)))), "protocol")
if _PROTOCOL not in sys.path:
    sys.path.insert(0, _PROTOCOL)

from .lists import PLACES, JOINTS, IMU_PLACES, place_of_line   # noqa: E402,F401
from .core import Map, Seen                                       # noqa: E402,F401
