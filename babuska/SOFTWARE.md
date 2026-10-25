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
| capacity | 0x107C CapBatCell | 12,000 mAh | the usable 60% of the EVE C40's 20 Ah, so that the BMS's 0–100% is the pack's 20–80% |
| cell over-voltage | 0x100C VolCellOV | under EVE's 3,650 mV, set with the top at 80% | a backstop over the charger, under the cell's end of charge (see [hardware](HARDWARE.md#the-battery)) |
| cell under-voltage | 0x1004 VolCellUV | 2,500 mV | EVE's end of discharge above 0 °C; the suit shuts itself down at 20% |
| shutdown | 0x1028 VolSysPwrOff | 2,000 mV | under the 2.5 V backstop, at EVE's lowest end (2.0 V at 0 °C and below); the default (2.8 V for Li-ion) would block the 2.5 V under-voltage |
| SOC 100% · 0% | 0x1018 · 0x101C | set with the top at 80%, from the measurement on a sample | JK counts the charge and sets it to 100% when a cell passes the first, to 0% when one falls under the second, so the count re-anchors at every charge (JK's Inverter BMS documentation; to confirm on the B1A8S10P); on LiFePO4's flat curve the two voltages lie close together |
| charge current, limit | 0x102C CurBatCOC | 6,000 mA | over the charger's 5 A |
| discharge current, limit | 0x1038 CurBatDcOC | 5,000 mA; 10,000 mA in the 10 A variant | at the nominal 12.8 V the suit takes ~0.9–1.3 A in the small fitting, ~1.1–2.0 A in the normal one, ~3.4 A at 43 W in the brutal one, ~4.7 A at 60 W with two computers, ~6 A near the 10 V end (see [power variants](HARDWARE.md#power-variants)) |
| charging, low temperature | 0x105C TMPBatCUT | 0.0 °C | EVE's sheet allows charging from 0 °C, at most 0.25 C up to 5 °C, which the charger's 5 A is |
| charging, high temperature | 0x104C TMPBatCOT | 40.0 °C | a margin under the 55 °C of EVE's sheet |
| discharging, high temperature | 0x1054 TMPBatDcOT | 50.0 °C | a margin under the 60 °C of EVE's sheet |
| balancing | 0x1014, 0x1084, 0x1048 | JK's defaults | |

- **The charger gives 5 A,** 0.25 C for the 20 Ah pack (see
  [hardware](HARDWARE.md#charging)). 20 to 80% is 12 Ah: ~2.4 h at 5 A with the suit off; a charge
  to 100% would be 16 Ah, ~3.2 h, and the constant-voltage tail (the top is open, see
  [hardware](HARDWARE.md#the-battery)). Worn while it charges, the suit takes ~1–1.8 A of the 5 A
  in the small and normal fittings, and 20 to 80% then takes ~3–3.8 h. EVE's standard charge is
  constant current at 0.5 C to 3.65 V, then constant voltage down to 0.05 C (RD-C40-S01-LF, 2.1);
  ours stops at 80%, how is open.
- The recoveries (over- and under-voltage 0x1010 and 0x1008, the temperatures 0x1050,
  0x1058 and 0x1060) sit a little inside their thresholds.
- **The order of writing.** JK refuses a write that breaks over-voltage > its recovery >
  under-voltage recovery > under-voltage > shutdown (JK's manual, its table of parameters). From the
  Li-ion defaults (4.2 V over-voltage, 4.1 V recovery, 2.8 V shutdown) the over-voltage's recovery
  0x1010 goes down before 0x100C, and 0x1028 before 0x1004.


## Open questions

- the top at 80% and with it the over-voltage and the SOC anchors (see
  [hardware](HARDWARE.md#open-questions)),
- the BMS's SOC-100% and SOC-0% re-anchoring, confirmed on the B1A8S10P itself,
- the byte order of the 32-bit values and whether the B1A8S10P's firmware accepts 2,500 mV,
  2,000 mV and 5,000 mA, which are asserted from the 20P family's documents.
