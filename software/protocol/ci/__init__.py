"""CI-STP and CI-BTP, the two protocols of NIC-CrazyIvan, as Python codecs.

CI-STP (the Small Crazy Ivan Transport Protocol) runs inside the suit: porjadok/SOFTWARE.md, "The
frames", "The commands", "The registers" and "Into Baťa". CI-BTP (the Big one) goes out of Baťa
over UDP: the same page, "Output". Everything here follows those pages byte by byte; where the
pages say nothing, the choice is noted in the docstring.
"""
from . import crc, stp, btp  # noqa: F401
