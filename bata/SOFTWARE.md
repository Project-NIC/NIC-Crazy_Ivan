<div align="center">

# Baťa: software

**What runs on the computer:** the system, the cores, the latency, the output modes, the learning
and the assistive use.

↑ [Baťa](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## The system

The modules are written in C with no operating system, but Baťa won't be programmed that way.
He needs the smallest system that runs on him: on the ROCK 5T Radxa's own system or one on a
mainline kernel (see the open questions), on the Raspberry Pi, Raspberry Pi OS Lite with its
services switched off, or an image of his own (Buildroot, for example).

**Baťa does little to the data.** He checks each record's CRC, computes the envelopes and the
IMUs' quaternions of the step (see [signals](SIGNALS.md)), ~10 MFLOP/s, and hands the model its
window; the Hailo does the rest, and the CPU keeps watch on the input and delivers the results
on the output.

- The Hailo reads its input from Baťa's RAM with its own DMA: HailoRT maps a buffer for
  it with `dma_map()` or `dma_map_dmabuf()`. There is no way round the RAM: in the kernel's
  device trees no PCIe controller is marked `dma-coherent`, neither the BCM2712's
  (`bcm2712.dtsi`) nor the RK3588's (`rk3588-base.dtsi`, `rk3588-extra.dtsi`, where PCIe goes
  through the SMMU), so devices on PCIe never see the CPU caches and read and write RAM directly.
- The RAM costs nothing here: a record of 768 B per cycle, ~2.9 MB/s, twelve cache lines.
- One copy: the SPI's DMA fills spidev's kernel buffer, and spidev copies it into the buffer
  mapped for the Hailo. Without a driver of our own there is no way round that copy, and 768 B
  per cycle cost next to nothing.

## The kernel

On the ROCK 5T Baťa runs a mainline kernel with two things of his own, an overlay and one patched
driver. Both are small and both are kept in `software/`.

- **The overlay:** SPI0_M2 and SPI1_M1 with chip select 1 for Mamka, I2S2_M1 as the slave with a
  dummy codec, I2C7_M3 with the ES8316 off, pin 36 and pin 37 as inputs with interrupts, pins
  18 and 33 as inputs for the Umnicas' PGOOD; and the two converters of
  [Terem](../terem/HARDWARE.md#the-converters) as regulators: `regulator-fixed`,
  `enable-active-high`, `gpios` on header pin 16 (GPIO3_A4) for A and pin 32 (GPIO3_C2) for B,
  `startup-delay-us = <4000>` for the LMR43620's 3.5 ms soft start (t_SS, SNVSBY5B),
  `vin-supply = <&vcc3v3_pcie30>`, and `vpcie3v3-supply` of `pcie3x4` set to A and of `pcie3x2`
  to B. The *normal* profile sets one port `status = "disabled"`.
- **The patched driver:** mainline `pcie-dw-rockchip.c` has no `remove` and sets
  `suppress_bind_attrs`, so a port can neither be unbound nor rebound while running, and
  its regulator, PERST# and clocks are held from boot to shutdown. The patch adds a `remove`
  that undoes probe in reverse, PERST# driven low first, then `dw_pcie_host_deinit`, the PHY
  off and out (`rockchip_pcie_phy_deinit`), the clocks off, the reset asserted, while the devm
  cleanup disables the regulator, and drops `suppress_bind_attrs`. Other DWC drivers in the tree
  carry a remove of that shape; it is tens of lines, kept as one patch file against the kernel
  version in use and re-applied on each kernel.
- **Off and on, one Umnica at a time:** off is `unbind` of her port in
  `/sys/bus/platform/drivers/rockchip-dw-pcie/`, after the Hailo's own driver has let her go:
  PERST# falls, the port goes, the regulator and with it her 3.3 V. On is `bind`: the regulator,
  its 4 ms, the PHY, PERST# held 100 ms (`PCIE_T_PVPERL_MS`) and released, the link trained and
  the device enumerated, the same sequence as at boot. A Hailo whose converter tripped (PGOOD
  low on pin 18 or 33) is taken off that way, and tried again once.

## Storož

*Storož*, Russian for the watchman, is one small daemon with one job: when something fatal
breaks, he stops the household, leaves the gate open and says why. One path for every fatal
fault instead of a recovery branch for each; our Tron, the program that fights for the users.

- **The services** of the suit, the SPI reader, the model, the output, the recorder and the
  assistants, are systemd units wanted by one target, `suit.target`. Storož is a unit of his
  own, started before them, `Restart=always`, and not part of that target.
- **What he watches:** Mamka's events and state on the control channel (a block gone, a BMS
  alarm, the eFuse's PGOOD); the Umnicas' PGOOD on header pins 18 and 33 (GPIO events); the
  Hailo devices on the bus (a `remove` from udev, HailoRT's errors); the record stream (no "data
  ready" for a second); the SoC's and the Hailos' temperatures in sysfs; the disk when
  recording; and systemd itself (a unit that failed twice in a minute).
- **Fatal:** an Umnica gone or her converter tripped (after the one `bind` retry of
  [the kernel](#the-kernel)), the record stream silent, Mamka silent, a temperature over its
  limit, a BMS alarm, the disk full while recording, a service that keeps dying, and a halt by
  hand. **Not fatal,** handled where it happens and logged: a bad record (Mamka repeats it), a
  block gone from a line (the data go on with a hole), the glove missing, a sensor off, a lost
  UDP frame.
- **What he does:** `systemctl isolate storoz.target`, a target that conflicts with
  `suit.target` and keeps the network, `sshd`, Storož and nothing else, so the services fall
  and the terminal stays. Then, once a second until told otherwise: an event packet (type 5,
  *halted*, the reason in `which`) to every subscriber, Deduška first, and 0x12 = 4 with the
  reason to Mamka, who plays a pattern on the headband and shows it in her state; the lines,
  the headband and Budilnik run on without Baťa. No reboot, no automatic retry: a person comes
  over SSH or from Deduška, reads the journal, clears the cause and says `storoz resume`, which
  isolates `suit.target` again and sends 0x12 = 5.
- **Reasons** (1 B): 1 an Umnica gone, 2 an Umnica's converter (PGOOD low), 3 the record stream
  silent, 4 Mamka silent, 5 over temperature, 6 a BMS alarm, 7 the disk full, 8 a service that
  keeps dying, 9 by hand.

## Cores on the ROCK 5T

| cores | job |
|---|---|
| cpu0–3, A55 | the system and everything else, interrupts included |
| cpu7, A76 | input: the "data ready" pin, SPI, hand-off to the Hailo |
| cpu6, A76 | output: the Hailo's results out over UDP or USB HID |
| cpu4–5, A76 | free: sound, the assistants, learning, applications |

- cpu6 and cpu7 are set aside (`isolcpus`, interrupts moved to the small cores, threads pinned
  with `SCHED_FIFO`).
- The clock is set per cluster: cpu0–3, cpu4–5 and cpu6–7 each have their own. cpu6–7 run at a
  fixed frequency so the response does not wander; the profiles hold cpu4–5 lower or let them go.
- The device tree gives every core a deep idle state (`CPU_SLEEP`, `rk3588-base.dtsi`); on the
  input core it is switched off (`cpuidle/state1/disable`), so the core waits in WFI and wakes
  quickly.

## Cores on the Raspberry Pi

| core | job |
|---|---|
| 0 | the system and everything else, interrupts included |
| 1 | input: the "data ready" pin, SPI, hand-off to the Hailo |
| 2 | output: the Hailo's results out over UDP or USB HID |
| 3 | free: sound, the assistants, learning, spare |

- Cores 1 and 2 are set aside (`isolcpus`, interrupts moved to core 0, threads pinned with
  `SCHED_FIFO`). Each core has its own 512 KB L2, so nothing else empties its caches.
- All four cores run at one frequency: the Raspberry Pi cpufreq driver works from CPU0's clock
  alone. The frequency is fixed (the `performance` governor) so the response does not wander.
  A core with nothing to do waits for an interrupt (WFI); the device tree has no deeper idle
  states, so it wakes quickly.

## Latency

From a sample to the output:

| stretch | time |
|---|---|
| sample to the STM32H562, by the block's slot | 31–227 µs; a cycle is complete at 227 µs |
| STM32H562 to Baťa over two SPIs, the whole cycle as a record of 2 × 384 B | 82 µs at 37.5 MHz on the ROCK 5T, 92 µs at 33.3 MHz on the Raspberry Pi; ~310–320 µs from DRDY in all |
| Linux waking on the "data ready" pin | tens of µs, sometimes more; to be measured |
| the step's envelope and the model's window | 8.3 ms for the step; the window of 267 ms is history, not delay (see [signals](SIGNALS.md)) |
| inference on the Hailo-10H | to be measured |
| output over USB HID | 1 ms (full speed) or 0.125 ms (high speed) |
| output over UDP on Wi-Fi | usually a few ms, with jitter |

Muscles fire before the body moves; the delay is on the order of tens of ms. A step to the side
can show in the EMG before the leg moves, which wins back part of the recognition time.

## Output modes

- **Vector mode:** the values described under [Porjadok](../porjadok/SOFTWARE.md#output) go out over
  UDP, on Wi-Fi, which joins nothing, or on Ethernet, whose transformers isolate it; only the
  capacitor many sockets put from the transformers to the shield bridges it for AC.
- **HID mode** for a computer outside the backpack (Deduška gets the same over the cable): Baťa
  plugs into it over USB as a keyboard and mouse, set up through
  Linux's USB gadget configuration (configfs) with no driver to write. Gestures turn into key
  presses, for older games for instance: steps on the spot move, the head looks around, the arm aims
  as the mouse.
  - On the ROCK 5T it goes out of the USB-C, which is dual-role and does not power the board;
    it is also the glasses' port, so the two do not run at once.
  - On the Raspberry Pi 5 the USB-C port has the `dwc2` overlay with `dr_mode=peripheral`. It is
    free, since Kormilica feeds the Raspberry Pi through its header; the gadget still needs
    trying.
  - Between the two computers sits a USB isolator, TI **ISOUSB211** (SLLSFC5D): a USB 2.0
    repeater at low, full and high speed (1.5, 12 and 480 Mbit/s), 5,700 Vrms of isolation,
    SSOP-28, no crystal, and automatic role reversal, so the ROCK 5T's dual-role USB-C works
    through it. Each side is fed on its own: side 1, the suit's, from Baťa's 5 V on VBUS1 (4.25
    to 5.5 V, an LDO inside makes its 3.3 V), side 2 from the other computer's VBUS; ~10–15 mA
    a side plus up to ~96 mA on the transmitting side at high speed. V1OK and V2OK tell each
    side the other is up. It sits in the backpack between Baťa's USB-C and the shell's socket,
    so the suit and the wearer stay apart from the other computer's ground, and its 5 V never
    meets the suit's.
- **The whole system on a ROCK 5T,** Deduška, or Baťa alone: the applications run on it, and its
  USB-C carries the picture to glasses that take DisplayPort over USB-C (VITURE, XREAL and the
  like), with their power and their head sensors on the same cable; the suit is the mouse, the
  keyboard and the hands. Radxa gives the port DisplayPort up to 4K at 60 Hz. In the mainline kernel
  (7.3) the ROCK 5T's device tree does not switch it on yet: the USB-C controller is marked `fail`
  there for the 5B, which a power-delivery reset takes off its supply, and the 5T, fed from DC, does
  not have that problem; the DisplayPort driver itself is in mainline, and other RK3588 boards
  switch it on. Its HDMI outputs are the fallback.

## Learning

The Hailo only runs models; HailoRT has no functions for training. Models are compiled for it
with the Hailo Dataflow Compiler on a PC: for the Hailo-10H its version 5.x, on x86 Ubuntu
22.04 or 24.04 (hailo_model_zoo, GETTING_STARTED), with 16 GB of RAM or more.

The goal is a suit that learns on its own: put it on and wear it for a week, at work, in town,
out picking mushrooms, charging the batteries as needed. Once it has learned, a small piece of
code runs on one core. The plan:

- **The IMUs teach the EMG.** What the IMUs measure becomes the target for the EMG part of the
  model, so nobody has to label anything by hand. The EMG runs ahead of the movement, so the
  model learns to see a movement coming.
- **A split model.** The large fixed part, which turns EMG and IMU data into features, runs on
  the Hailo. A small last part learns on a free core of Baťa, for this person and this fit of
  the suit, and afterwards runs on one core.
- **The general part** is trained on a PC from recordings and compiled for the Hailo.
- **Recordings** of the raw data take ~2.5 MB/s: ~8.8 GB an hour, ~1 TB for a week of 16-hour
  days. That calls for an SSD on USB 3, since PCIe goes to the Hailos on both computers, or for
  recording features only.
- Learning takes more battery than plain running. That is accepted.

## Assistive use

Muscles below a spinal cord injury often still carry signals even when nothing moves:

- A sleeve of electrodes on the forearm of a person with motor-complete tetraplegia decoded
  attempted movements of single fingers correctly 88 ± 24% of the time (J. Neurophysiol.
  126(6), 2021).
- Carnegie Mellon and Meta are testing a surface-EMG wristband with people with spinal cord
  injuries, who control computer games and screens with it from the first day.

So the suit could let a person who cannot move control a mouse by trying to move a hand. The
face works as in anyone else; a camera can add it. Two things differ from ordinary use: with no
movement the IMUs cannot teach, so the targets come from prompted attempts ("now try to raise
your hand"); and injuries differ in level and extent, so a model learned with one person is a
starting point that then adapts to each next one.

## Open questions

- the minimal system for each computer; on the ROCK 5T also the kernel: Rockchip's, which idled
  ~2 W lower than mainline 6.8.1 on a ROCK 5B (Thomas Kaiser, 2024), or mainline, where the
  ROCK 5T's DisplayPort on USB-C is still to be switched on in the device tree,
- the overlay and the driver patch written and tried on a ROCK 5T: the two regulators, the
  ports' supplies, unbind and bind with one module, then with two,
- to measure on both computers: SPI reads and waking on the "data ready" pin (cyclictest, or
  a PREEMPT_RT kernel), the latency of a small model on the Hailo-10H, the USB HID gadget, the
  Ethernet to Deduška,
- which layers the Hailo compiles (Hailo Dataflow Compiler User Guide), and the model's input:
  channels, window, data type,
- where learning recordings go: Deduška's disk, an SSD on USB 3, or features only.
