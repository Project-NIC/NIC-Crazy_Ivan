<div align="center">

# Kormilica: hardware

**The power board's circuits:** what is on her, the 5.1 V for the Raspberry Pi, and the
Hailo-10H's 3.3 V and PCIe.

↑ [Kormilica](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## What is on her

| part | package | count | what it does |
|---|---|---|---|
| stacking header, 2 × 20 | 2.54 mm grid | 1 | the Raspberry Pi's header up to Mamka; Kormilica takes pins 2, 4 and the grounds |
| LM61460AANRJRR | VQFN-HR, 4.0 × 3.5 mm | 2 | 5.1 V for the Raspberry Pi, 3.3 V for its Hailo module |
| M.2 socket, Key M | 2280 | 1 | Umnica, the Hailo-10H module, held by a screw at 80 mm |
| FPC connector, 16 pins | 0.5 mm pitch | 1 | PCIe from the Raspberry Pi's connector, as on Raspberry Pi's M.2 HAT+ |
| EEHZA1H470P | SMD 8 × 10.2 mm | 2 | the bulk on the battery input: 47 µF 50 V hybrid polymer, NIC-Heimdall's house part |
| connectors | | 2 | the battery in; EN and PGOOD to Mamka |

## 5.1 V for the Raspberry Pi

The Raspberry Pi 5 takes 5.1 V, which none of Mamka's rails gives. A **TI LM61460**
(LM61460AANRJRR, datasheet SNVSBD5D) on Kormilica makes it straight from the battery: up to 6 A,
input 3.0–36 V (42 V tolerated), VQFN-HR 14 pins, 4.0 × 3.5 mm, auto mode at light load. The
cell, from the datasheet's tables for 5 V at 2.1 MHz:

| position | value |
|---|---|
| frequency | R_RT 5.90 kΩ → ~2.1 MHz (its equation 2). RT must not go to ground: the part then stays off |
| inductor | 1.5 µH, saturation at least 11.5 A, the high-side current limit's maximum |
| divider on FB, against 1.00 V | top 100 kΩ, bottom 24.3 kΩ → 5.12 V |
| C_OUT · C_FF | 3 × 22 µF ceramic · 33 pF, the datasheet's "better transient" row |
| C_IN | 4.7 µF 50 V at each VIN/PGND pair, with 100 nF 50 V X7R right beside each |
| C_BOOT · R_BOOT · C_VCC | 100 nF · 0 Ω · 1 µF |

- At 2.1 MHz and 105 °C around it the datasheet holds the part to 4 A (its figure 9-3); the
  load and the backpack stay well under both.
- Kormilica's battery terminals carry the same doubled house input bank as Mamka's (see
  [Mamka](../mamka/HARDWARE.md#converters)): two 47 µF hybrid polymers with 10 µF 50 V 1206 and
  100 nF. The LM61460 takes its current peaks from it.
- 5.1 V from a full 16 V pack is a 152 ns on-time against the 70 ns minimum.

- The load in use is ~2.4 A: the Raspberry Pi 3–8.8 W and an SSD for the recordings when one
  is fitted; the Hailo has its own 3.3 V (see [the Hailo-10H](#the-hailo-10h)). The design
  maximum is the 5 A the Raspberry Pi 5 asks of its supply for full USB, and the converter, the
  copper and the header pins are sized to it. It sits on Kormilica, right at the header, so no
  such current travels on a cable.
- The Raspberry Pi takes the 5.1 V on the 5 V pins of its GPIO header, 2 and 4, each with half
  the current, ~2.5 A at most. Without a USB-C supply that announces 5 A, it holds its USB ports
  to 600 mA, so `usb_max_current_enable=1` goes into `config.txt`. Its USB-C stays unused for
  power.
- **On and off:** the LM61460's EN takes a divider from the battery, and Mamka's open-drain line
  on the short cable can pull it low: Mamka switches the Raspberry Pi on with the power button
  and cuts its supply once it has shut down. Its PGOOD goes back to Mamka on the same cable.

## The Hailo-10H

Umnica, the Hailo-10H M.2 module, sits on Kormilica's wing, next to her own 3.3 V (see
[Baťa](../bata/HARDWARE.md#umnica) for the module itself), since the Raspberry Pi has no slot;
on a ROCK 5T the Umnicas sit in [Terem](../terem/README.md).

- **PCIe:** a 16-pin, 0.5 mm FPC cable from the Raspberry Pi's connector to the same connector
  on Kormilica, as Raspberry Pi's M.2 HAT+ does it, then the pairs to the M.2 socket: differential,
  of controlled impedance, a few centimetres. The connector's pinout comes from Raspberry Pi's
  documents.
- **Its 3.3 V:** a second LM61460 straight from the battery, the 5.1 V cell with the 3.3 V row
  of the datasheet's table 9-2 at 2.1 MHz: 1 µH (saturation at least 11.5 A, as there),
  3 × 22 µF ceramic, the divider 100 kΩ over 43.2 kΩ → 3.31 V, C_FF 10 pF. 6 A is far above a
  module of a few watts. The Raspberry Pi's PCIe connector gives only ~1 A at 5 V (Geekworm's
  figure for its X1002), so the module takes nothing from it.
- **The connector,** from Raspberry Pi's *Connector for PCIe* document: a 16-pin, 0.5 mm FFC;
  one lane of PCIe Gen 2 (Gen 3 works but is not officially supported) with CLKREQ_N and RST_B;
  5 V on pins 1 and 2 at 500 mA each, which Kormilica does not use; **PCIE_PWR_EN**, a 3.3 V
  output of the Raspberry Pi that tells the board to bring its supplies up, with a 100 kΩ
  pull-down on the board; **PCIE_DET_WAKE**, a 3.3 V input the Raspberry Pi reads to see a board,
  pulled high through a divider from the 5 V (3.6 kΩ over 6.8 kΩ) and pulled low by PCIe WAKE#;
  the FFC at most 50 mm. The pin numbers are in that document's figure.
- Its EN follows PCIE_PWR_EN, as the document asks: the module's 3.3 V comes up when the
  Raspberry Pi says so and goes with it, with no pin on the STM32H562. 3.3 V from a full 16 V
  pack is a 98 ns on-time against the 70 ns minimum. Its PGOOD goes onto header pin 18, the
  pin on which a ROCK reads Terem's Umnica A, so the Raspberry Pi reads it there the same way,
  with Mamka's 10 kΩ pull-up from pin 1; an EN line it does not need, PCIE_PWR_EN is the
  Raspberry Pi's own.
- **In `config.txt`:** without a HAT's EEPROM the Raspberry Pi neither turns the connector on
  nor switches to Gen 3 by itself, so `dtparam=pciex1` and `dtparam=pciex1_gen=3` go there. If
  Gen 3 gives errors, Gen 2 is the fallback; the suit's data need far less.
- **Heat:** the module lies on the wing in the backpack's air channel, under a heatsink, as
  Raspberry Pi advises for the AI HAT+ 2 with the same chip under a continuous load; to be
  confirmed in the module's datasheet (see [Babuška](../babuska/CONSTRUCTION.md#the-backpack)).

## Open questions

- the header's pins 2 and 4 at ~2.5 A each, and the stacking header's rating,
- Kormilica's battery terminals and copper for the 10 A power variant,
- the Raspberry Pi's PCIe connector: the pin numbers from the figure in its document, onto the
  footprint.
