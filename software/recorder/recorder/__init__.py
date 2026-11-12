"""Baťa's recorder: Mamka's two processors' transfers in, the samples as the chips gave them out
into BDF+, made only when asked (bata/SOFTWARE.md, *The model*; porjadok/SOFTWARE.md, *CI-BTP*).

The codecs are the protocol's own (`software/protocol/ci`), found beside this folder.
"""
import os
import sys

_PROTOCOL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(
    __file__)))), "protocol")
if _PROTOCOL not in sys.path:
    sys.path.insert(0, _PROTOCOL)

from .table import Unit, load_table, processor      # noqa: E402,F401
from .bdf import Signal, Writer, read                 # noqa: E402,F401
from .record import Recorder, read_transfers          # noqa: E402,F401
