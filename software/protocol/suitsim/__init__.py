"""A suit on paper: units on their lines, Mamka's transfers, Baťa's output.

Everything is built from the codecs in `ci`, cycle by cycle, so the converters and readers can be
written and tried before a board exists. Nothing here measures anything: the signals are made up,
the timing is counted in cycles, not seconds.
"""
from .suit import Suit, Module, Glove, Natasa, Misa   # noqa: F401
from .bata import Bata                                # noqa: F401
from .files import read_frames, write_frames, summarize   # noqa: F401
