<div align="center">

# Babuška: software

**What is written into the BMS:** its thresholds, the state of charge anchored to the pack's
20–80%, the current limits, the temperatures, and the order the registers take.

↑ [Babuška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

The BMS, [Ključnica](HARDWARE.md#the-bms), keeps these settings itself; Mamka reads it over Modbus
(see [Mamka](../mamka/SOFTWARE.md#the-battery)) and passes the state of charge on to Baťa.

## The BMS's settings

Written over Modbus or in JK's app. JK numbers each register as a base
plus the field's byte offset (JK BMS RS485 Modbus general protocol V1.0 and V1.1):

| setting | register | value | why |
|---|---|---|---|
| cells | 0x106C CellCount | 4 | 4S |
| capacity | 0x107C CapBatCell | 12,000 mAh | the usable 60% of 2P × 10 Ah, so that the BMS's 0–100% is the pack's 20–80% |
| cell over-voltage | 0x100C VolCellOV | a little above the measured 80% voltage, under 3,950 mV | a backstop over the charger, under the cell's 3.95 V limit; if the 80% voltage comes out near 3.9 V, the margin is small and the charger's setting carries the protection |
| cell under-voltage | 0x1004 VolCellUV | 2,000 mV | a backstop over 1.5 V; the suit shuts itself down at 20% |
| shutdown | 0x1028 VolSysPwrOff | 1,800 mV | between the 2.0 V backstop and the cell's 1.5 V end; the default (2.8 V for Li-ion) would block the 2.0 V under-voltage |
| SOC 100% · 0% | 0x1018 · 0x101C | the cell's voltage at 80%, a little under the charger's final voltage · its voltage at 20%; both from the measurement on a sample | JK counts the charge and sets it to 100% when a cell passes the first, to 0% when one falls under the second, so the count re-anchors at every charge (JK's Inverter BMS documentation; to confirm on the B1A8S10P) |
| charge current, limit | 0x102C CurBatCOC | 5,000 mA | over the charger's 4 A |
| discharge current, limit | 0x1038 CurBatDcOC | 5,000 mA; 10,000 mA in the 10 A variant | the suit takes ~1.2 A, ~1.9 A at 22 W from a pack at 20% (~11.5 V), ~3 A at 35 W with the ROCK 5T in its brutal profile, ~4.3 A at 49 W with two computers (see [power variants](HARDWARE.md#power-variants)) |
| charging, low temperature | 0x105C TMPBatCUT | 0.0 °C | the 32140's published limits allow charging below 0 °C only at a lower voltage and current (3.9 V and 0.2 C at −10…0 °C), which a plain CC/CV source cannot give, so the suit charges from 0 °C |
| charging, high temperature | 0x104C TMPBatCOT | 40.0 °C | a margin under the 45 °C of the 32140's published limits |
| discharging, high temperature | 0x1054 TMPBatDcOT | 50.0 °C | the lower of EAST's two figures, until the 32140's own is known |
| balancing | 0x1014, 0x1084, 0x1048 | JK's defaults | |

- **The charger gives 4 A,** 0.2 C for the 20 Ah pack. 20 to 80% is 12 Ah: ~3 h of constant current
  with the suit off, plus the constant-voltage tail. Worn while it charges, the suit takes 1.2–1.9 A
  of the 4 A, and the charge takes ~4.5–5.5 h. EAST's standard charge for its layered-oxide cells is
  constant current to 3.95 V, then constant voltage down to 0.05 C; ours stops earlier, at the 80%
  voltage.
- The recoveries (over- and under-voltage 0x1010 and 0x1008, the temperatures 0x1050,
  0x1058 and 0x1060) sit a little inside their thresholds.
- **The order of writing.** JK refuses a write that breaks over-voltage > its recovery >
  under-voltage recovery > under-voltage > shutdown (JK's manual, its table of parameters). From the
  Li-ion defaults (4.2 V over-voltage, 4.1 V recovery, 2.8 V shutdown) the recovery 0x1010 goes down
  before 0x100C, and 0x1028 before 0x1004.


## Open questions

- the BMS's SOC-100% and SOC-0% re-anchoring, confirmed on the B1A8S10P itself,
- the byte order of the 32-bit values and whether the B1A8S10P's firmware accepts 2,000 mV,
  1,800 mV and 5,000 mA, which are asserted from the 20P family's documents.
