"""Baťa's signal chain, the first version tried on recordings (bata/SIGNALS.md): the EMG's band,
the mains tracked and taken out, the envelopes a step; the QRS, the ECG out and the heart taken
out of the EMG. numpy and scipy (Debian's python3-numpy and python3-scipy); every filter causal,
block by block, as the live chain will run it.
"""
from .emg import EmgChain, ABSENT                      # noqa: F401
from .ecg import QrsDetector, EcgOut, HeartRemover, rmssd_ms   # noqa: F401
