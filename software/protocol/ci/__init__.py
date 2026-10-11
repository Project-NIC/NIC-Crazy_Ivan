"""CI-STP and CI-BTP, the two protocols of NIC-CrazyIvan, as Python codecs.

CI-STP (the Small Crazy Ivan Transport Protocol) runs on the lines inside the suit:
porjadok/SOFTWARE.md, "The frame" and "The channel from the master". CI-BTP (the Big one) goes
out of Baťa over UDP: the same page, "Output". Everything here follows those pages byte by byte;
where the pages said nothing, the choice is noted in the docstring and was written back into them.
"""
from . import crc, stp, btp  # noqa: F401
