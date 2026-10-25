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
- **Cobalt-based lithium-ion** on the body. LiFePO4 and sodium-ion carry no cobalt. A chemistry
  that may not be charged in the cold was barred too at first, but the suit charges only from 0 °C
  anyway (below), so LiFePO4 came in on 23 Oct 2026.
- **Sodium-ion 32140 in 4S2P as the first pack** (to 23 Oct 2026). The EVE C40, LiFePO4, gives the
  same energy in four cells instead of eight and ~0.74 kg lighter, 180 Wh a kilogram against 113,
  with the BMS and the chargers made for it. Sodium stays in reserve, better in the cold, and said
  to tolerate storage at 0 V.
- **Lithium titanate (LTO).** The safest lithium chemistry and 6,000–45,000 cycles, but ~74–84 Wh
  a kilogram against sodium's ~100–130: ~0.4–0.7 kg more for the same energy. It stays in
  reserve, with the 18650 and Toshiba's SCiB packs worked out, should the other two disappoint.
- **Five cells in series.** Full, five LiFePO4 cells give 18.25 V, and Mamka's 3.3 V from it at
  2.2 MHz is 82 ns of on-time against the LMR43610's worst-case minimum of 75 ns, little to spare;
  four give 14.6 V and 103 ns. Five sodium cells, 20 V, came to exactly 75 ns. A higher input also
  costs more switching loss at light load.
- **Smaller cells, 26700 in 4S3P.** The same energy as 32140 in 4S1P with three times the cells,
  the welds and the balancing; the 32140 won among the sodium cells.
- **Charging the pack to 100% and down to 0%.** Between 20 and 80% the cells live longer, and the
  suit still gets 154 Wh; the BMS's 0–100% is remapped onto that window. On LiFePO4's flat curve
  the top at 80% cannot be the charger's voltage, so a full charge comes back only should the BMS
  not stop the charge by its count (see [hardware](HARDWARE.md#the-battery)).
- **Charging in the cold.** The EVE C40 takes no charge under 0 °C, and the sodium 32140 only at
  a lower voltage and current, which a plain CC/CV source cannot give; the BMS stops charging
  under 0 °C.
- **A second BMS for the 10 A variant.** The JK B1A8S10P is a 100 A part; 5 A and 10 A are one
  register (0x1038). Only the fuses and the connector differ; the wire is 2.5 mm² in both.
- **USB-C for charging.** The connector is small and fragile; the backpack has one sturdy
  charging connector and a bought LiFePO4 charger plugs into it.
- **A charger made for 4S sodium-ion,** AccuPower's NATEC at 15.2 V, the first candidate.
  It went with the sodium pack; LiFePO4's chargers stop at 14.6 V, EVE's 3.65 V a cell.
- **An LED driver as the charger,** a constant-voltage and constant-current one with trimmers
  (Mean Well HLG-60H-15A: 13.5–17 V, 2.4–4 A, HLG-60H-SPEC). It is sold for LEDs, not for
  batteries, the owner's experience of such drivers on batteries is poor, and a bought charger
  for LiFePO4 does the job.

## The backpack

- **A 3D-printed backpack.** A whole backpack would take a large printer; a home printer prints
  the insert, and the shell is bought.
- **A dark shell.** In the sun it could come near the 40 °C and 50 °C the BMS allows for charging
  and discharging; the shell is light-coloured.
- **A fan on the Hailos.** The modules lie in the channel under one heatsink, as Raspberry Pi
  advises a heatsink for its AI HAT+ 2 with the same chip; a measurement is to confirm that the
  channel's air is enough.
- **The glasses' cable through a connector in the shell.** It passes through a grommet and plugs
  in inside, its strain held there, so it stays an ordinary cable.
- **One connector for the whole suit,** an Amphenol PT 24-61 (MIL-DTL-26482 Series 1, 61
  contacts, a quarter-turn bayonet, IP67), until 24 Oct 2026. It took five lines of 11 contacts;
  eight lines take 88, and a piece of the suit is better taken off by itself.
