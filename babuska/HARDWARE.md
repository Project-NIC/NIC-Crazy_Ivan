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

**Energy.** With the Raspberry Pi the whole suit takes ~13–22 W, ~15 W typically: the sensing
modules ~5.5 W from the battery, the Raspberry Pi 5 3–8.8 W, the Hailo-10H 2.5–5 W, Mamka
~1.5–2 W, Nataša, the fan and the BMS ~0.6–1.2 W. Eight hours take ~120 Wh, 104–176 Wh across that
range.

With the ROCK 5T it is an estimate from others' measurements, not ours:

| computer | the computer | Hailo-10H | the whole suit | on 146 Wh (20–80%) |
|---|---|---|---|---|
| Raspberry Pi 5, one Hailo | 3–8.8 W | 2.5–5 W | 13–22 W | ~6.6–11 h |
| ROCK 5T, *normal*: one Hailo, the big cores held lower | ~4–8 W | 2.5–5 W | ~14–21 W | ~7–10 h |
| ROCK 5T, *brutal*: both Hailos, every core | ~4–17 W | 5–10 W | ~17–35 W | ~4–8.5 h |
| two computers: Baťa on a Raspberry Pi, Deduška on a ROCK 5T | 3–8.8 W and ~4–17 W | 2.5–15 W, one to three | ~17–49 W | ~3–8.5 h |

- The ROCK 5T idles at 3.9 W (LinuxLinks, its conditions not known). A ROCK 5B idled under
  1.4 W at the wall with Rockchip's kernel and only Gigabit Ethernet, and all eight cores at full
  load (7-zip) took ~6 W more (Thomas Kaiser); with mainline 6.8.1 it idled ~2 W higher (2024).
  Under stress-ng Jeff Geerling measured RK3588 boards at 10.9 W (Orange Pi 5 Max) to 17 W
  (ROCK 5B), whole boards; the brutal row takes the higher figure.
- What lowers it: the big cores' clock, or fewer of them, at run time; the memory's clock
  governor in Rockchip's kernel, ~0.5–0.6 W in idle; unused parts off in the device tree (Kaiser:
  2.5GbE instead of Gigabit ~0.3 W, a display ~0.35 W).
- Glasses on the ROCK 5T's USB-C come on top, a few watts, by model.
- 35 W from a pack at 20% (~11.5 V) is ~3 A, under the BMS's limit of 5 A.

**Chemistry.** No cobalt-based lithium-ion on the body, and none that may not be charged in the
cold. The candidates:

| | sodium-ion (Na-ion) | lithium titanate (LTO) |
|---|---|---|
| cell | 3.0–3.1 V (1.5–4.0 V) | 2.3–2.4 V (1.5–2.7 V) |
| energy per kg, cells | ~100–130 Wh | ~74–84 Wh |
| cold | makers give operation down to −40 °C | −40 to +55 °C, charged without warming |
| safety | no lithium; said to tolerate storage at 0 V, to check per cell | the safest lithium chemistry |
| cycles | 1,000–4,000 commonly quoted; EAST gives ≥6,000 for one of its cells | 6,000–45,000 |

Packs from ~110 Wh up (cells only):

| pack | cells | energy | ~15 W for | weight |
|---|---|---|---|---|
| Na-ion 32140, 3.05 V 10 Ah, 270 g | 4S1P, 4 cells | 122 Wh | ~8.1 h | ~1.08 kg |
| Na-ion 26700, 3.1 V 3.3 Ah, 82 g | 4S3P, 12 cells | 123 Wh | ~8.2 h | ~0.98 kg |
| Na-ion 32140 | 5S1P, 5 cells | 153 Wh | ~10.2 h | ~1.35 kg |
| Na-ion 32140 | 4S2P, 8 cells | 244 Wh | ~16 h, ~9.8 h at 20–80% | ~2.16 kg |
| LTO 18650, 2.4 V 1.3 Ah | 5S7P, 35 cells | 109 Wh | ~7.3 h | ~1.4–1.6 kg, estimated |
| LTO Toshiba SCiB 20Ah-HP, 2.3 V, 545 g | 5S1P, 5 cells | 230 Wh | ~15 h | ~2.7 kg |

- Sodium weighs about as much as LiFePO4 for the same energy; titanate takes ~0.4–0.7 kg more.

**The first pack: sodium-ion 32140 in 4S2P** (3.05 V, 10 Ah, 270 g a cell): eight cells,
244 Wh, ~2.16 kg. More pack types will follow; the rest of the suit does not depend on which.

**Charged between 20 and 80%,** for the cells' life. That leaves 146 Wh, ~9.8 h at 15 W. The
cell's voltage at 20% and at 80% is not yet measured; the 11.5–15.6 V (2.9–3.9 V a cell) that the
other pages use is an estimate from the published curve, to be replaced by the measurement. A
sodium cell's voltage rises steadily with its charge, unlike the flat curve of LiFePO4, so the
state of charge reads well from the voltage.

- **The top:** the charging source is set to the pack's voltage at 80%, from the cells'
  discharge curve; the BMS's over-voltage threshold sits a little above it as a backstop.
- **The bottom:** Mamka reads the state of charge from the BMS. Its 0–100% is set to the usable
  20–80% and re-anchored at every charge (see its settings below); the cells' voltages are the
  check. At its 0%, the pack's 20%, the suit warns the wearer and shuts down in order. The BMS's
  under-voltage threshold, 2.0 V a cell, stays as the last backstop.
- At 20% the pack is far above the ~6.5 V the 6 V rail needs.

- **Four cells, not five.** Full, four cells give 16 V. The tightest rail is Mamka's own 3.3 V:
  from 16 V at 2.2 MHz it is 94 ns of on-time against the converter's minimum of 75 ns at worst
  (SNVSBY5B, tON-MIN). Five cells give 20 V and exactly 75 ns, with nothing to spare, and a
  higher input costs more in switching losses at light load. The converters'
  trouble at light load in NIC-Heimdall was a buck idling at microamps; here the rails take
  ~1.1 A and ~0.13 A.
- **The low end.** The 6 V rail needs ~6.5 V at its converter. The BMS's backstop at 2.0 V a
  cell (8 V) keeps above it; close to the limit the converter stretches its period and keeps
  regulating.
- 16 V is nothing to the converters, so the 80% limit is for the cells' life only.


## The BMS

The BMS is *Ključnica*, Russian for the housekeeper with the keys: she holds the keys to
Babuška's pantry and decides what goes in and out.

**Protection (BMS): JK B1A8S10P** (Jikong), a smart BMS with thresholds set per cell:

- 4–8 cells in series, 100 A, active balancing at 1 A; sold for Li-ion, LiFePO4 and LTO.
- In its family (B1A8S20P / B2A8S20P) cell voltages are measured from 1 to 5 V, and over- and
  under-voltage protection is adjustable from 1.2 to 4.35 V, which covers sodium; the settings
  are below.
- 100 A is far more than the suit's ~1.2 A (~1.9 A at most with the Raspberry Pi, ~4.3 A with
  two computers, see [Power variants](#power-variants)); it is the smallest of the family
  with these figures confirmed.
- It talks over RS485 (or CAN). Mamka reads it on RS485 with JK's RS485 Modbus protocol (see
  [Mamka](../mamka/SOFTWARE.md#the-battery)): the cells, the current, the temperatures, the state
  of charge.

**The cell's limits**, Na-ion 32140, 10 Ah (maker's data as published by eastups):

| | |
|---|---|
| rated voltage | 3.05 V |
| end of charge | 3.95 V at 0–45 °C, 3.9 V at −10…0 °C, 3.8 V at −20…−10 °C |
| end of discharge | 1.5 V |
| charging current | 0.5 C at 0–45 °C, 0.2 C at −10…0 °C, 0.05 C at −20…−10 °C |
| resistance | AC ≤ 3 mΩ, DC ≤ 10 mΩ |
| size | Ø33.2 × 140 mm, 270 ± 5 g |
| discharging | −40…60 °C for EAST's power-type sodium cells, −40…50 °C for its energy-type layered-oxide ones (EAST's sheets of its prismatic cells); for the 32140 to confirm |


What is written into the BMS, threshold by threshold, is under [software](SOFTWARE.md).

## Charging

No USB-C: the connector is small and fragile. The backpack has one sturdy
charging connector, and a constant-current, constant-voltage source set to the pack's 80%
voltage charges it through the BMS. A charger made for 4S LiFePO4 stops at 14.6 V, which is
no voltage chosen for sodium. The suit may be worn while it charges; the charger's noise may
then show in the data, and the right-leg drive holds the common voltage against it (see
[Rubaška](../rubaska/HARDWARE.md#right-leg-drive)).


## Power variants

Two variants on the same battery and the same BMS: the JK B1A8S10P is a 100 A part, and the
limit is one of its settings.

| | 5 A | 10 A |
|---|---|---|
| for | one computer, Baťa: the Raspberry Pi, or the ROCK 5T in either profile | two computers, Baťa and Deduška beside him (see [Baťa](../bata/README.md)) |
| the BMS's discharge limit, 0x1038 | 5,000 mA | 10,000 mA |
| the most the suit takes, from a pack at 20% (~11.5 V) | ~35 W, ~3 A: the ROCK 5T in its brutal profile | ~49 W, ~4.3 A: both computers at full load, too close to 5 A for the peaks of USB devices and the glasses |
| each cell of the 4S2P pack | 2.5 A at most, 0.25 C | 5 A at most, 0.5 C |
| the fuse, the wires and the connector from the pack to the BMS, Mamka and Kormilica or Terem | rated for 5 A | rated for 10 A |
| the parts | a 5 × 20 mm ceramic, sand-filled, time-lag cartridge fuse of 5 A in a holder on the pack's lead (Littelfuse 215 series or the like: 1,500 A of breaking capacity at 250 V AC, where a glass or a blade fuse has tens); 0.75 mm² (18 AWG) wire; an Amass XT60 pair at the pack | the same with a 10 A fuse and 1.5 mm² (16 AWG) wire |

- The 32140's sheet (EAST Na-Ion 32140-MP10, as a search finds it; the sheet itself still to be
  read) gives 0.5 C, 5 A, as the standard continuous discharge and 3 C, 30 A, as the maximum.
  10 A from the 4S2P pack is each cell's standard rate.
- The charging limit (0x102C, 5 A over the charger's 4 A) is the same in both.


## Open questions

- the cell's voltage at 80%, for the charger and the BMS's over-voltage threshold: measured on
  a sample, charged by EAST's standard charge and discharged at 0.2 C while its voltage is
  logged; the 32140's own discharge temperatures,
- the charging connector on the backpack and the charging source,
- the ROCK 5T's consumption, measured in both profiles, and the glasses',
- the fuse's DC rating: Littelfuse gives the 215 series 250 V AC and its breaking capacity at
  AC; a DC figure for 16 V is to be read in the sheet or taken from a series that states one.
  Time-lag, not fast: the converters' and the eFuse's starts draw pulses, and a short is the
  BMS's to cut first,
- the XT60's rating from Amass's own sheet: its distributors give 30 A continuous and 60 A for
  under a minute, far above both variants, but the sheet itself was not read; and the 32140's
  discharge ratings from its own sheet,
- from JK: the BMS's own lowest supply voltage (4S at the 2.0 V backstop is 8 V; it is sold
  for LiFePO4 from 4S and LTO from 6S), and from EAST the 32140's own charging temperatures.
