# Software

**What runs on the suit's computers and on a PC,** beside the pages that describe the parts.

| folder | what is in it |
|---|---|
| [protocol/](protocol/README.md) | CI-STP and CI-BTP as Python codecs with tests, and the suit simulator that writes the SPIs' transfers and the live output |
| [signals/](signals/README.md) | Baťa's signal chain on recordings: the EMG's band, the mains tracked and taken out, the envelopes, the QRS, the ECG and the heart taken out of the EMG (numpy, scipy) |
| [map/](map/README.md) | Baťa's map: what is fitted and every unit's settings by UID, a page of plain HTML forms; the place list and a first joint list |
| [recorder/](recorder/README.md) | Baťa's recorder: Mamka's transfers into BDF+, every EMG channel and IMU step as the chips gave them, the gaps and events as annotations |

Baťa's programs come here as they are written. Firmware in C waits for the first board: it is
not written against paper.
