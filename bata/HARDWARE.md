<div align="center">

# Baťa: hardware

**The computers:** which computer, Umnica, Deduška and Ďaďa Sem.

↑ [Baťa](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## Which computer

Baťa is a **Radxa ROCK 5T** or a **Raspberry Pi 5**. The same Mamka sits on either, with no
variants and no jumpers (see [Mamka](../mamka/HARDWARE.md#on-baťas-header)).

| | Radxa ROCK 5T | Raspberry Pi 5 |
|---|---|---|
| processor | RK3588: 4 × Cortex-A76 and 4 × Cortex-A55 | BCM2712: 4 × Cortex-A76 |
| board | 110 × 82 mm | 85 × 56 mm |
| Umnica, the Hailo-10H | one or two 2242 modules on Terem in its two M.2 Key M slots on its underside, two PCIe 3.0 lanes each, a converter each | one, on Kormilica, one PCIe lane |
| power | its DC jack, 9–20 V, straight from the battery through the eFuse on Terem | 5.1 V from Kormilica on header pins 2 and 4 |
| the second SPI | header pins 11, 13 and 15 | header pins 26, 31 and 29 |
| on its header | Mamka | Kormilica, and Mamka on top |
| picture | DisplayPort on its USB-C (up to 4K at 60 Hz, Radxa), two HDMI | two micro-HDMI |
| Bluetooth | 5.2 | 5.0 |

- **Why the ROCK 5T:** twice the cores, room for two Hailo-10H, a DC input that takes the
  battery as it is (the pack gives ~11.5–15.6 V between 20 and 80%), and a picture on USB-C that
  glasses take with their power and their sensors on one cable.
- **Two profiles on the ROCK 5T:** *normal*, with one Hailo and the big cores held lower, takes
  about what the Raspberry Pi takes; *brutal* runs both Hailos and every core. The budget is
  under [Babuška](../babuska/HARDWARE.md#the-battery).
- The ROCK 5B+ has the same header pins but for pin 37 (its GPIO0_A0, an input for Mamka either
  way) and takes its power over USB-C.

## Umnica

*Umnica*, Russian for the clever one, is the daughter: the Hailo-10H as an M.2 module: one or two
2242 modules on [Terem](../terem/README.md) in the ROCK 5T's slots, one 2280 on
[Kormilica](../kormilica/HARDWARE.md#the-hailo-10h) for the Raspberry Pi. On the Raspberry Pi it
sits there rather than as the AI HAT+ 2: the same chip with 8 GB of its own RAM and the same
software.

- **The module:** the Hailo-10H M.2 Key M with 8 GB, in two lengths, 2242 and 2280 (Hailo's
  product page); the June 2025 datasheet of the 2280 gives HM22HB1C2FAE for 8 GB and
  HM22HB2C2FAE for 4 GB, the 2242's code is still to be found. It has PCIe Gen 3 ×4; the
  ROCK 5T gives each slot two lanes and the Raspberry Pi one, so the link comes up ×2 in the
  ROCK 5T and ×1 on the Raspberry Pi, as on
  the AI HAT+ 2.

**In the ROCK 5T**

- Its two M.2 Key M slots lie on its underside, with holes for 2280 (Radxa).
- Its PCIe 3.0 lanes are split two and two between two controllers, `pcie3x4` and `pcie3x2`
  (the mainline `rk3588-rock-5t.dts`), so each module has a root port of its own and the two
  run as separate devices, each with its own job. Each slot has its own reset (PERST#).
- Both slots take their 3.3 V, `VCC3V3_PCIE30`, from one buck converter on the board, a Silergy
  SY8113B fed from the 5 V (the ROCK 5T schematic V1.2, sheet of the M.2 sockets); Silergy sells
  it as a 3 A part, its sheet not read here. Two Hailo-10H at their typical 2.5 W are ~1.5 A,
  at 5 W each the full 3 A: the *brutal* profile runs at that converter's edge.
- The 40-pin header's pins 3 and 5 go straight from the RK3588 to the header with no pull-ups on
  the board (schematic V1.2, sheets of the header and the SoC's I/O), so Mamka's own are fitted
  for the ROCK 5T, fed from header pin 1.
- The ROCK switches the slots' 3.3 V itself, by GPIO1_A4 (`PCIE30x4_PWREN_H`, the SY8113B's
  EN), and Terem's converters the same way: each is a GPIO regulator in the device tree, EN A on
  header pin 16 and EN B on 32, which that slot's PCIe driver turns on before PERST#. Each
  Umnica's PGOOD comes back on pins 18 and 33 (see
  [Terem](../terem/HARDWARE.md#the-converters)).
- The *normal* profile leaves one module off by disabling its port in the overlay, so its EN
  never rises; what a Hailo-10H takes at rest while running is a question for its datasheet.
- **A supply of their own.** The slots' 3.3 V cannot be fed from outside: a second regulator in
  parallel with the board's SY8113B would fight it. So the Hailos sit on
  [Terem](../terem/HARDWARE.md), one board in both slots with a 2242 socket and a 2 A converter
  for each, the edges' 3.3 V pins left open, and the SY8113B feeds nothing.

## Deduška

*Deduška*, Russian for grandpa, Babuška's husband, is computer B: a full computer beside Baťa with
no Mamka of his own, and the old man has the big one. A ROCK 5T will do, or anything stronger,
since he only talks to Baťa over Ethernet.

- **What he does:** the applications, the glasses on his USB-C, his Hailo slots free for speech
  or a small language model; the suit is his mouse, his keyboard and his hands.
- **The link:** Baťa's results go to him over UDP on a short Ethernet cable, as to any other
  computer (see [output modes](SOFTWARE.md#output-modes)). The ROCK 5T has two 2.5GbE ports, one
  for Baťa and one free for the outside.
- **Its latency** is a matter of settings, not of the network card: the ROCK 5T's are two
  Realtek RTL8125B on PCIe, so their interrupt coalescing goes off (`ethtool -C`), PCIe's power
  saving (ASPM) goes off on that link and their interrupt goes to a core of its own. A small
  packet then takes tens to ~200 µs, now and then a few ms when Linux is busy elsewhere: far
  under the tens of ms by which the muscles run ahead of the movement.
- **HID over the cable:** Baťa sends the gestures as key presses and mouse moves in the same UDP,
  and a small program on Deduška turns them into a keyboard and a mouse through Linux's `uinput`.
  Inside the backpack there is no USB between them and no isolator: both run from Babuška.
- **Recordings** for learning go over the same cable to Deduška's disk, so Baťa needs no SSD.
- **Baťa then needs little memory,** since the data are 2.5 MB/s and the model sits in Umnica's
  own 8 GB; whether 2 GB leaves room for learning is to be tried.
- **Power:** Deduška has a [Terem](../terem/README.md) of his own with its eFuse, so Mamka
  switches both computers, and the backpack takes the 10 A power variant (see
  [Babuška](../babuska/HARDWARE.md#power-variants)).

## Ďaďa Sem

*Ďaďa Sem*, Russian for Uncle Sam, is the uncle from America, the one who watches everything: the
cameras. Two cheap USB cameras on the head go into Baťa's USB ports, one each and on two USB
controllers, since one USB 2 host carries ~24 MB/s in all (see below), and Baťa's second Umnica
looks at the pictures, so no third computer is needed.

- **USB:** from the head to the backpack is a metre or two, well inside USB 2's 5 m; the cables go
  through the backpack's grommet with the glasses'. Both computers have four USB ports, two of
  them USB 3. MIPI CSI does not reach so far without serializers, and network cameras compress the
  picture, which delays it by hundreds of ms, and bring a switch with them.
- **640 × 480 is enough** to find and name what is around: a door, a step, a person.
- **Uncompressed:** 640 × 480 in YUYV at 30 frames a second is ~18 MB/s a camera, inside the
  ~24 MB/s that USB 2 carries in an isochronous stream (3 × 1024 B every 125 µs); the processor
  then decodes nothing and only hands the pictures to Umnica. MJPEG would cost decoding, estimated
  at tens of percent of one core a camera.
- **Two cameras are not in step:** their frames can be up to one frame apart, 33 ms. That does
  not matter for finding and naming things; it would for depth from the two pictures while the
  head moves, where a stereo camera, both pictures in one frame on one USB 3 port, keeps them in
  step.
- **What goes on:** only the results, such as "a door 2 m ahead, on the left", to Deduška with the
  rest, and to [Míša](../misa/README.md). Baťa stamps them with the suit's time; a frame every
  33 ms needs no closer sync.
- **On a Raspberry Pi** Baťa has only one Umnica, so Ďaďa Sem goes into Deduška instead.

## Open questions

- from the ROCK 5T's 2D drawing (dl.radxa.com): its holes on the header's side; the SY8113B's
  rating from Silergy's sheet,
- Umnica from the Hailo-10H M.2 module's datasheet: its current, in reset too, its heatsink,
  whether it slows down by itself when hot, that the 8 GB version can be bought in 2242,
- Ďaďa Sem: which cameras, and how much of a core they take.
