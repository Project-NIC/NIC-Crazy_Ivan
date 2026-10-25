<div align="center">

# Baťa: hardware

**The computers:** which computer, Umnica, Borovičok and Ďaďa Sem.

↑ [Baťa](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## Which computer

Baťa is a **Radxa ROCK 5T**, with Mamka on his header (see
[Mamka](../mamka/HARDWARE.md#on-baťas-header)); why not the Raspberry Pi 5 is under
[WHY](WHY.md#the-computers).

| | Radxa ROCK 5T |
|---|---|
| processor | RK3588: 4 × Cortex-A76 and 4 × Cortex-A55, and an NPU of its own (the kernel's `accel/rocket`) |
| board | 110 × 82 mm |
| Umnica, the Hailo-10H | none, one or two 2280 modules on Terem in its two M.2 Key M slots on its underside, two PCIe 3.0 lanes each, a converter each |
| power | its DC jack, 9–20 V, straight from the battery through its eFuse on Mamka |
| Mamka's SPIs | SPI1_M1 on header pins 11, 13, 15 and 7 to processor 1; SPI0_M2 on 19, 21, 23, 24 and SPI3_M0 on 18, 27, 28 with 29 to processor 2 (see [Mamka](../mamka/HARDWARE.md#on-baťas-header)) |
| on its header | Mamka |
| picture | DisplayPort on its USB-C (up to 4K at 60 Hz, Radxa), two HDMI |
| Bluetooth | 5.2 |

- **Why the ROCK 5T:** eight cores and an NPU of its own, room for two Hailo-10H, a DC input that
  takes the battery as it is (the pack gives 10–14.6 V at its limits, 12.8 V nominal), and a
  picture on USB-C that glasses take with their power and their sensors on one cable. The V1.2,
  not the Industrial V2.01, which lacks SPI3_M0 on the header (see
  [Mamka](../mamka/WHY.md)); other boards were weighed for their header's SPIs and none had the
  rest too (see [WHY](WHY.md)).
- **Three ways to fit him:** *small*, no Hailo and no Terem, a small model on the RK3588's own
  NPU, for a suit of a headband and a few modules; *normal*, one Hailo and the big cores held
  lower; *brutal*, both Hailos and every core. The budget is under
  [Babuška](../babuska/HARDWARE.md#the-battery); how large a model the NPU takes is to be tried.
- **The USB-C for the glasses** is wired for DisplayPort: in the RK3588 the port's four fast
  pairs are shared with DP0_TX0–3 and its SBU pins with DP0's AUX, "USB3.0 OTG/DP1.4 Alt" (the
  ROCK 5T schematic V1.2, sheet 7), and they go straight to the connector J11 (sheet 30). The
  picture is a matter of software (see [software](SOFTWARE.md#the-kernel)). VBUS comes from the
  board's 5 V through an onsemi FPF2595 (U4) whose 340 Ω on ISET sets the limit at 3.0 A, 2.7 to
  3.3 A (FPF2595/D Rev. 2, table 1); above it the switch holds a constant current until its
  150 °C shutdown. Glasses that take 5 V at 1 A, as the XREAL One Pro does, have three times that.
  A FUSB302B (U2602) on I2C4 handles the CC pins.
- The ROCK 5B+ has the same header pins but for pin 37, its GPIO0_A0, and takes its power over
  USB-C.

## Umnica

*Umnica*, Russian for the clever one, is the daughter: the Hailo-10H as an M.2 module, one or
two 2280 modules on [Terem](../terem/README.md) in the ROCK 5T's slots, each with 8 GB of its own
RAM.

- **The module:** the Hailo-10H M.2 Key M, 2242 or 2280, with 4 or 8 GB of LPDDR4/4X, PCIe
  Gen 3 ×4, 40 TOPS in INT4 and 20 in INT8, 2.5 W typical, −40 to 85 °C (Hailo's product
  brief of the M.2 ET module, 7/25). Hailo's datasheet of the 2280 (*Hailo-10H M.2 Key M ET
  Module Data Sheet* Rev. 1.0, June 2025) gives up to **8.25 W** and under 2.5 W under a typical
  workload (ResNet-50 at 1,015 frames a second 2.5 W, Qwen2 1.5B at 11 tokens a second 2.2 W,
  section 3), 3.3 V ± 5%, parts 1.5 mm tall on top and 0.5 mm under (2.1), and no heatsink and
  no thermal resistance; it names HM22HB1C2FAE for 8 GB and HM22HB2C2FAE for 4 GB, and does
  not cover the 2242. Terem is made for the 2280, as long as the ROCK's slots, and takes the
  **8 GB 2280**, HM22HB1C2FAE; distributors list the 2242 with 4 GB (a starter kit,
  HM22HB2C2XBE, at EBV) and 8 GB only in 2280 so far. It has PCIe Gen 3 ×4; the ROCK 5T gives
  each slot two lanes, so the link comes up ×2, which is room enough: the suit's envelopes in
  and the model's answers out are a trickle beside it (the owner).
- **What it runs beside the suit's model:** Hailo's list of generative models for the 10H has the
  vision-language models Qwen2-VL-2B and Qwen3-VL-2B and the language models Qwen2-1.5B and Llama
  3.2-1B; Hailo gives under 1 s to the first token and over 10 tokens a second for models of 2
  billion parameters (its announcement of general availability). Whether a VLM of 2B fits beside the
  suit's model in 8 GB is to be tried. Pomoščnik's "what is it" runs on the second Umnica in the
  brutal fitting (see [Pomoščnik](../pomoscnik/README.md)).

**In the ROCK 5T**

- Its two M.2 Key M slots lie on its underside, with holes for 2280 (Radxa).
- Its PCIe 3.0 lanes are split two and two between two controllers, `pcie3x4` and `pcie3x2`
  (the mainline `rk3588-rock-5t.dts`), so each module has a root port of its own and the two
  run as separate devices, each with its own job. Each slot has its own reset (PERST#).
- Both slots take their 3.3 V, `VCC3V3_PCIE30`, from one buck converter on the board, a Silergy
  SY8113B fed from the 5 V (the ROCK 5T schematic V1.2, sheet of the M.2 sockets): a 3 A synchronous
  buck for 4.5–18 V, its valley current limit 3–4.25 A, in TSOT23-6 with θJA 100 °C/W (Silergy,
  AN_SY8113B Rev 0.1). Two Hailo-10H at their typical 2.5 W are ~1.5 A, at 5 W each the full 3 A and
  at the datasheet's 8.25 W ~5 A, past it; at 3 A its switches alone lose ~0.6 W from 5 V, ~60 K
  over the air (an estimate from the typical 80 and 40 mΩ): the *brutal* profile would run at that
  converter's edge in current and in heat, which is why the Hailos sit on Terem and it feeds
  nothing.
- The ROCK switches the slots' 3.3 V itself, by GPIO1_A4 (`PCIE30x4_PWREN_H`, the SY8113B's
  EN), and Terem's converters the same way: each is a GPIO regulator in the device tree, EN A on
  header pin 16 and EN B on 32, which that slot's PCIe driver turns on before PERST#. Each
  Umnica's PGOOD comes back on a free header GPIO, chosen when Terem is drawn (see
  [Terem](../terem/HARDWARE.md#the-converters)).
- The *normal* profile leaves one module off by disabling its port in the overlay, so its EN
  never rises; what a Hailo-10H takes at rest while running its datasheet does not give.
- **A supply of their own.** The slots' 3.3 V cannot be fed from outside: a second regulator in
  parallel with the board's SY8113B would fight it. So the Hailos sit on
  [Terem](../terem/HARDWARE.md), one board in both slots with a 2280 socket and a 4 A converter
  for each, the edges' 3.3 V pins left open, and the SY8113B feeds nothing.

## Borovičok

*Borovičok*, Staričok-Borovičok, the little old mushroom man of the fairy tales and Babuška's
husband, is computer B: a full computer beside Baťa with
no Mamka of his own. He is a ROCK 5T too, fed and switched by Mamka like Baťa, and talks to
him only over Ethernet.

- **What he does:** the applications and the glasses on his USB-C; the suit is his mouse, his
  keyboard and his hands. He has no Umnica and no Terem: the RK3588's own NPU is there should an
  application want one, and an NVMe SSD sits in one of his M.2 slots.
- **His system:** Debian 13 in Armbian's build, as Baťa's, with Xfce, a light desktop, and the
  same kernel, which switches the USB-C's DisplayPort on for the glasses (see
  [software](SOFTWARE.md#the-system)). Armbian offers desktops for the ROCK 5T in Ubuntu; Debian
  with Xfce is to be built with its framework and tried.
- **The link:** Baťa's results go to him over UDP on a short Ethernet cable, as to any other
  computer (see [output modes](SOFTWARE.md#output-modes)). The ROCK 5T has two 2.5GbE ports, one
  for Baťa and one free for the outside.
- **Its latency** is a matter of settings, not of the network card: the ROCK 5T's are two
  Realtek RTL8125B on PCIe, so their interrupt coalescing goes off (`ethtool -C`), PCIe's power
  saving (ASPM) goes off on that link and their interrupt goes to a core of its own. A small
  packet then takes tens to ~200 µs, now and then a few ms when Linux is busy elsewhere: far
  under the tens of ms by which the muscles run ahead of the movement.
- **HID over the cable:** Baťa sends the gestures as key presses and mouse moves in the same UDP,
  and a small program on Borovičok turns them into a keyboard and a mouse through Linux's `uinput`.
  Inside the backpack there is no USB between them and no isolator: both run from Babuška.
- **Recordings,** when made, go over the same cable to Borovičok's SSD, so Baťa needs none; all
  the EMG in BDF, ~1.5 MB/s, is far inside what a PCIe 3.0 ×2 slot carries.
- **Baťa then needs little memory,** since the data are ~3.7 MB/s and the model sits in Umnica's
  own 8 GB; in the small fitting it sits in the ROCK's own memory, so whether 2 GB leaves room
  for it and for learning is to be tried.
- **Power:** Borovičok's eFuse sits on Mamka beside Baťa's (see
  [Mamka](../mamka/HARDWARE.md#the-computers-supply)), so Mamka
  switches both computers, and the backpack takes the 10 A power variant (see
  [Babuška](../babuska/HARDWARE.md#power-variants)).

## Ďaďa Sem

*Ďaďa Sem*, Russian for Uncle Sam, is the uncle from America, the one who watches everything: the
cameras. Two cheap USB cameras on the head go into Baťa's USB ports, one each and on two USB
controllers, since one USB 2 host carries ~24 MB/s in all (see below). The pictures go to an NPU
on Baťa: his second Umnica in the brutal fitting, the RK3588's own NPU in the small and normal
ones, so no third computer is needed.

- **USB:** from the head to the backpack is a metre or two, well inside USB 2's 5 m; the cables go
  through the backpack's grommet with the glasses'. Both computers have four USB ports, two of
  them USB 3. MIPI CSI does not reach so far without serializers, and network cameras compress the
  picture, which delays it by hundreds of ms, and bring a switch with them.
- **The camera: Iconer IC-U2BP4,** a mini bullet of Ø20 mm (its length not given), 2 MP, UVC
  on USB 2, MJPG up to 1920 × 1080 at 30 frames a second and YUY2 at 640 × 480 at 30 (at
  1920 × 1080 only 5), a 3.7 mm pinhole lens at F2.0, a 2 m cable, under 200 mA at 5 V; from the
  maker's listing on Made-in-China, which gives the sensor as both 1/2.7" and 1/3" and no field
  of view. From the lens and those sizes it is ~65–75° across, an estimate.
- **The cameras snap on and off:** one simple snap mount, the same on the glasses' temple, in a
  clip, and on the headband at the temple (see
  [Nataša](../natasa/CONSTRUCTION.md#on-the-head)). With the glasses on they ride on the glasses
  and see past them, which Pomoščnik needs; without, on the headband, which is enough for a blind
  wearer. The narrower they are, the better: a camera narrower than 20 mm is still to be found.
- **640 × 480 is enough** to find and name what is around: a door, a step, a person.
- **Uncompressed:** 640 × 480 in YUYV at 30 frames a second is ~18 MB/s a camera, inside the
  ~24 MB/s that USB 2 carries in an isochronous stream (3 × 1024 B every 125 µs); the processor
  then decodes nothing and only hands the pictures to the NPU. MJPEG would cost decoding, estimated
  at tens of percent of one core a camera.
- **Two cameras are not in step:** their frames can be up to one frame apart, 33 ms. That does
  not matter for finding and naming things; it would for depth from the two pictures while the
  head moves, where a stereo camera, both pictures in one frame on one USB 3 port, keeps them in
  step.
- **What goes on:** only the results, such as "a door 2 m ahead, on the left", to Borovičok with the
  rest, and to [Míša](../misa/README.md). Baťa stamps them with the suit's time; a frame every
  33 ms needs no closer sync.

## Open questions

- Umnica: its current at rest and in reset, whether it slows down by itself when hot (Hailo's
  datasheet gives neither),
- Ďaďa Sem: the Iconer on a sample, its sensor and its field of view, and whether its 640 × 480
  is scaled from the whole sensor or cut from its middle, which would narrow the view; how much
  of a core the cameras take; in the small fitting, how much of the RK3588's NPU they leave to
  the suit's model.
