<div align="center">

# Babuška: why not

**The graveyard:** what was considered for the battery and the backpack and why it is not used.

↑ [Babuška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Each entry says what it was and why it went, so that nobody digs it up without knowing. Where a
thing waits in reserve, it says so.

## The battery

- **A bought pack.** In a bought pack the cells, the welds and the protection cannot be checked.
  The pack is assembled from cells, with a BMS whose every threshold is set by us.
- **Cobalt-based lithium-ion** on the body, and any chemistry that may not be charged in the
  cold. Sodium-ion carries no lithium and is said to tolerate storage at 0 V; the cold charging
  the suit does not use anyway (see below).
- **Lithium titanate (LTO).** The safest lithium chemistry and 6,000–45,000 cycles, but ~74–84 Wh
  a kilogram against sodium's ~100–130: ~0.4–0.7 kg more for the same energy. It stays the
  second candidate, with the 18650 and Toshiba's SCiB packs worked out, should sodium cells
  disappoint.
- **Five cells in series.** Full, five cells give 20 V, and Mamka's 3.3 V from 20 V at 2.2 MHz
  is exactly the LMR43610's worst-case minimum on-time of 75 ns, with nothing to spare; four
  cells give 16 V and 94 ns. A higher input also costs more switching loss at light load.
- **Smaller cells, 26700 in 4S3P.** The same energy as 32140 in 4S1P with three times the cells,
  the welds and the balancing; the 32140 won, and 4S2P of them is the first pack.
- **Charging the pack to 100% and down to 0%.** Between 20 and 80% the cells live longer, and the
  suit still gets 146 Wh; the BMS's 0–100% is remapped onto that window.
- **Charging in the cold.** The 32140's published limits allow it below 0 °C only at a lower
  voltage and current, which a plain CC/CV source cannot give; the BMS stops charging under 0 °C.
- **A second BMS for the 10 A variant.** The JK B1A8S10P is a 100 A part; 5 A and 10 A are one
  register (0x1038). Only the fuse, the wires and the connector differ.
- **USB-C for charging.** The connector is small and fragile; the backpack has one sturdy
  charging connector and a CC/CV source set to the pack's 80% voltage.
- **A charger made for 4S LiFePO4.** It stops at 14.6 V, no voltage chosen for sodium.

## The backpack

- **A 3D-printed backpack.** A whole backpack would take a large printer; a home printer prints
  the insert, and the shell is bought.
- **A dark shell.** In the sun it could come near the 40 °C and 50 °C the BMS allows for charging
  and discharging; the shell is light-coloured.
- **A fan on the Hailo.** The module lies in the channel under a heatsink, as Raspberry Pi
  advises for the AI HAT+ 2 with the same chip; a measurement is to confirm that the channel's
  air is enough.
- **The glasses' cable through a connector in the shell.** It passes through a grommet and plugs
  in inside, its strain held there, so it stays an ordinary cable.
