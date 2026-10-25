<div align="center">

# Babuška: hardware

**The battery:** the energy the suit needs, the chemistry, the pack, its limits, the BMS, the
charging and the two power variants.

↑ [Babuška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## The battery

The pack is described here and assembled from cells, not bought: in a bought pack the cells,
the welds and the protection cannot be checked.

**Energy.** Besides the computer and its Hailos the suit takes ~11.5–12.5 W from the battery,
with Mamka's converters at an estimated 85–90 %: the modules and the gloves on lines 1–7 ~1.3 A
at 4 V and ~0.13 A at 6 V, ~6.8–7.2 W; Nataša and Míša on line 8 ~0.35 A at 4 V, ~1.6 W; Mamka's
own 3.3 V ~0.72–0.77 A, ~2.6–3.0 W (see [Mamka](../mamka/HARDWARE.md#converters)); the fan and
the BMS ~0.5 W. The ROCK 5T's share is an estimate from others' measurements, not ours:

| fitting | the computer | Hailo-10H | the whole suit | on 154 Wh (20–80%) |
|---|---|---|---|---|
| ROCK 5T, *small*: no Hailo, the model on its own NPU | ~4–8 W | none | ~16–21 W | ~7.3–9.6 h |
| ROCK 5T, *normal*: one Hailo, the big cores held lower | ~4–8 W | 2.5–8.25 W | ~18–29 W | ~5.3–8.6 h |
| ROCK 5T, *brutal*: both Hailos, every core | ~4–17 W | 5–16.5 W | ~21–46 W | ~3.3–7.3 h |
| two computers: Baťa in any fitting, Borovičok on a ROCK 5T with no Hailo | ~4–17 W and ~4–17 W | 0–16.5 W | ~20–63 W | ~2.4–7.7 h |

- **The run time asked for** is a working day, ~8 h, in the small and the normal fittings at an
  ordinary load; the brutal fitting and two computers may run shorter.
- The ROCK 5T idles at 3.9 W (LinuxLinks, its conditions not known). A ROCK 5B idled under
  1.4 W at the wall with Rockchip's kernel and only Gigabit Ethernet, and all eight cores at full
  load (7-zip) took ~6 W more (Thomas Kaiser); with mainline 6.8.1 it idled ~2 W higher (2024).
  Under stress-ng Jeff Geerling measured RK3588 boards at 10.9 W (Orange Pi 5 Max) to 17 W
  (ROCK 5B), whole boards; the brutal row takes the higher figure.
- What lowers it: the big cores' clock, or fewer of them, at run time; the memory's clock
  governor in Rockchip's kernel, ~0.5–0.6 W in idle; unused parts off in the device tree (Kaiser:
  2.5GbE instead of Gigabit ~0.3 W, a display ~0.35 W).
- Glasses on the ROCK 5T's USB-C come on top, a few watts, by model.
- 43 W from the pack at its nominal 12.8 V is ~3.4 A, under the BMS's limit of 5 A. The Hailos'
  share is the datasheet's 8.25 W each at most; under a typical load they take 2.5 W.

**Chemistry.** No cobalt-based lithium-ion on the body, and no charging in the cold: the BMS
stops it under 0 °C. The candidates:

| | LiFePO4 | sodium-ion (Na-ion) | lithium titanate (LTO) |
|---|---|---|---|
| cell | 3.2 V (2.5–3.65 V) | 3.0–3.1 V (1.5–4.0 V) | 2.3–2.4 V (1.5–2.7 V) |
| energy per kg, cells | 180 Wh for the EVE C40 | ~100–130 Wh | ~74–84 Wh |
| cold | the EVE C40 charged from 0 °C, discharged from −20 °C with at least 70% at 1 C | makers give operation down to −40 °C | −40 to +55 °C, charged without warming |
| safety | no cobalt | no lithium; said to tolerate storage at 0 V, to check per cell | the safest lithium chemistry |
| cycles | the EVE C40 2,000 to 70%, 3,500 at 90% depth | 1,000–4,000 commonly quoted; EAST gives ≥6,000 for one of its cells | 6,000–45,000 |

Packs from ~110 Wh up (cells only):

| pack | cells | energy | ~15 W for | weight |
|---|---|---|---|---|
| **LiFePO4 EVE C40, 3.2 V 20 Ah, 356 g** | **4S1P, 4 cells** | **256 Wh** | **~17 h, ~10 h at 20–80%** | **~1.42 kg** |
| LiFePO4 DFD 60130, 3.2 V 46 Ah, 820 g | 4S1P, 4 cells | 589 Wh | ~39 h | ~3.28 kg |
| Na-ion 32140, 3.05 V 10 Ah, 270 g | 4S1P, 4 cells | 122 Wh | ~8.1 h | ~1.08 kg |
| Na-ion 26700, 3.1 V 3.3 Ah, 82 g | 4S3P, 12 cells | 123 Wh | ~8.2 h | ~0.98 kg |
| Na-ion 32140 | 5S1P, 5 cells | 153 Wh | ~10.2 h | ~1.35 kg |
| Na-ion 32140 | 4S2P, 8 cells | 244 Wh | ~16 h, ~9.8 h at 20–80% | ~2.16 kg |
| LTO 18650, 2.4 V 1.3 Ah | 5S7P, 35 cells | 109 Wh | ~7.3 h | ~1.4–1.6 kg, estimated |
| LTO Toshiba SCiB 20Ah-HP, 2.3 V, 545 g | 5S1P, 5 cells | 230 Wh | ~15 h | ~2.7 kg |

- The EVE C40 holds 180 Wh a kilogram against the sodium 32140's 113, so a pack of the same
  energy weighs a third less; titanate takes ~0.4–0.7 kg more than sodium.

**The first candidate: LiFePO4, the EVE C40 in 4S1P** (3.2 V, 20 Ah, 356 g a cell): four cells,
256 Wh, ~1.42 kg of cells, against the sodium 4S2P's 244 Wh in eight cells and 2.16 kg. The pack
as a whole is chosen just before building, since cells change month by month; the sodium-ion
32140 in 4S2P stays in reserve, better in the cold, and the DFD 60130 was weighed for a run time
that matters more than the weight. More pack types will follow; the rest of the suit does not
depend on which.

**Charged between 20 and 80%,** for the cells' life. That leaves 154 Wh, ~10 h at 15 W. The top
can no longer be the charger's voltage, as it was meant for sodium, whose voltage rises steadily
with its charge: LiFePO4's curve is flat over the middle, so either the BMS stops the charge by
its count, or the pack charges to 100%. Which, JK's BMS has to say; the pack's voltages at 20
and 80% come from a measurement on a sample.

- **The bottom:** Mamka reads the state of charge from the BMS. Its 0–100% is set to the usable
  20–80% and re-anchored at every charge (see its settings below); the cells' voltages are only a
  rough check on the flat curve. At its 0%, the pack's 20%, the suit warns the wearer and shuts
  down in order. The BMS's under-voltage threshold, 2.5 V a cell, EVE's end of discharge above
  0 °C, stays as the last backstop.
- At 20% the pack is far above the ~6.5 V the 6 V rail needs.

- **Four cells, not five.** Full, four cells give 14.6 V, and Mamka's own 3.3 V from it at
  2.2 MHz is 103 ns of on-time against the converter's minimum of 75 ns at worst (SNVSBY5B,
  tON-MIN); five would give 18.25 V and 82 ns, and a higher input costs more in switching losses
  at light load. Light load is no trouble here: the rails take ~1.7 A and ~0.13 A.
- **The low end.** The 6 V rail needs ~6.5 V at its converter. The BMS's backstop at 2.5 V a
  cell (10 V) keeps above it; close to the limit the converter stretches its period and keeps
  regulating.
- 14.6 V is nothing to the converters, so the 80% limit is for the cells' life only.


## The BMS

The BMS is *Ključnica*, Russian for the housekeeper with the keys: she holds the keys to
Babuška's pantry and decides what goes in and out.

**Protection (BMS): JK B1A8S10P** (Jikong), a smart BMS with thresholds set per cell:

- 4–8 cells in series, 100 A, active balancing at 1 A; sold for Li-ion, LiFePO4 and LTO, for
  LiFePO4 from 4S.
- In its family (B1A8S20P / B2A8S20P) cell voltages are measured from 1 to 5 V, and over- and
  under-voltage protection is adjustable from 1.2 to 4.35 V, which covers LiFePO4's 2.5–3.65 V;
  the settings are below.
- 100 A is far more than the suit's ~1.1–2.0 A in the *normal* fitting at the nominal 12.8 V
  (~3.4 A at most with one ROCK 5T, ~4.7 A with two computers, see
  [Power variants](#power-variants)); it is the smallest of the family with these figures
  confirmed.
- It talks over RS485 (or CAN). Mamka reads it on RS485 with JK's RS485 Modbus protocol (see
  [Mamka](../mamka/SOFTWARE.md#the-battery)): the cells, the current, the temperatures, the state
  of charge.

**The cell's limits,** the EVE C40, from EVE's specification RD-C40-S01-LF rev. A (10 Mar 2022,
the datasheet attached at mivvyenergy.cz; where the shop's own page differs, the sheet counts):

| | |
|---|---|
| rated voltage | 3.2 V |
| capacity | 20 Ah at 0.5 C, 20.5 Ah median at 0.33 C, 19.5 Ah at least |
| end of charge | 3.65 V, the charge ending at 0.05 C |
| end of discharge | 2.5 V above 0 °C, 2.0 V at 0 °C and below |
| charging current | 0.5 C standard, 1 C fast; at most 0.25 C at 0–5 °C, 0.3 C at 5–10 °C, 0.4 C at 10–15 °C, 0.5 C at 15–55 °C |
| discharging current | 0.5 C standard, 3 C at most continuous |
| resistance | AC ≤ 3 mΩ (1 kHz), DC ≤ 8 mΩ (2 C, 30 s), at 30% |
| size | Ø40.5 × 135 mm, 356 ± 10 g, an aluminium case |
| discharging | −20…60 °C; at −20 °C at least 70% of the capacity at 1 C |
| cycles | 2,000 to 70% at 25 °C, 1,000 at 45 °C, 3,500 at 90% depth |


What is written into the BMS, threshold by threshold, is under [software](SOFTWARE.md).

## Charging

No USB-C: the connector is small and fragile. The backpack has one sturdy charging connector, and a
bought charger for 4S LiFePO4 plugs into it from outside, through the BMS; the charger is not part
of the backpack. Its usual end is 14.6 V, 3.65 V a cell, EVE's end of charge; 5 A is 0.25 C for
the 20 Ah pack, inside EVE's standard 0.5 C and inside its 0.25 C even at 0–5 °C. Whether the
charger or the BMS stops at 80% is the question above. The suit may be worn while it charges;
the charger's noise may then show in the data, and the right-leg drive holds the common voltage
against it (see [Rubaška](../rubaska/HARDWARE.md#right-leg-drive)).


## Power variants

Two variants on the same battery and the same BMS: the JK B1A8S10P is a 100 A part, and the
limit is one of its settings.

| | 5 A | 10 A |
|---|---|---|
| for | one computer, Baťa: the ROCK 5T in any fitting | two computers, Baťa and Borovičok beside him (see [Baťa](../bata/README.md)) |
| the BMS's discharge limit, 0x1038 | 5,000 mA | 10,000 mA |
| the most the suit takes | ~43 W: ~3.4 A at 12.8 V, ~4.3 A at the 10 V end; the ROCK 5T in its brutal fitting | ~60 W: ~4.7 A at 12.8 V, ~6 A at the 10 V end, past 5 A; both computers at full load |
| each cell of the 4S1P pack | 5 A at most, 0.25 C | 10 A at most, 0.5 C, EVE's standard discharge |
| the fuse, the wires and the connector from the pack through the BMS to Mamka | rated for 5 A; the wire 2.5 mm² in both, more than the electrician's 1.5 mm² for wire not specially chosen and held | rated for 10 A |
| the parts | a 5 × 20 mm fast-acting ceramic sand-filled fuse in the pack, before the BMS (Littelfuse 216 series or the like: IEC 60127-2 sheet 1, 1,500 A of breaking capacity at 250 V AC by Littelfuse's product page), its value the lowest that survives the measured start currents; 2.5 mm² flexible PVC wire, CYA (H07V-K); an Amass XT60 pair at the pack | the same, the fuse sized for both computers' starts |

- EVE's sheet gives 0.5 C, 10 A, as the standard discharge and 3 C, 60 A, as the most
  continuous, so the 10 A variant is the cell's standard rate.
- The charging limit (0x102C, 6 A over the charger's 5 A) is the same in both.


## Open questions

- the top at 80%: whether the BMS stops the charge by its count or the pack charges to 100%,
  from JK; the pack's voltages at 20 and 80%, measured on a sample charged by EVE's standard
  charge and discharged at 0.2 C while its voltage is logged,
- the charging connector on the backpack; the charger's own sheet: its end of charge and its
  connector,
- the ROCK 5T's consumption, measured in both profiles, and the glasses',
- the fuses' values, the pack's, Mamka's and Terem's: the start currents measured, plugging the
  pack in with Mamka's and Terem's input banks and starting the converters and the eFuses, and
  the lowest fast-acting value that survives them taken for each; whatever wants several amps
  more at 12 V is already burning. The 216's DC rating to be read in its own sheet,
- the XT60's rating from Amass's own sheet: its distributors give 30 A continuous and 60 A for
  under a minute, far above both variants, but the sheet itself was not read,
- from JK: the BMS's own lowest supply voltage, 10 V for 4S at the 2.5 V backstop, inside what it
  is sold for, LiFePO4 from 4S.
