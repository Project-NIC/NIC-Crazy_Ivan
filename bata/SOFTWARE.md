<div align="center">

# Baťa: software

**What runs on the computer:** the system, the cores, the latency, the output modes, the learning
and the assistive use.

↑ [Baťa](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## The system

The modules are written in C with no operating system, but Baťa won't be programmed that way.
He runs **Debian 13 (trixie), arm64, in Armbian's Minimal / IOT build** for the ROCK 5T: no
desktop, an image of ~300 MB as Armbian's trixie minimal images go, and on it only the suit's
services, Storož, the assistants' programs and the Hailo's driver. Armbian brings the board's
boot loader and support, and its build takes patches of one's own, so the kernel is ours (see
[the kernel](#the-kernel)); systemd, which Storož works through, is Debian's.

- **The ground it stands on:** the eMMC, 8 GB of RAM at least (no ROCK 5T of 2 GB), a fallback
  kernel in the boot menu, journald capped, the map's JSON written atomically, a new file renamed
  over the old. On a shared network the suit's services listen on Ethernet and Baťa's own access
  point only, nftables closing the rest, SSH by keys only.
- **Nothing runs by itself.** No updates in the background: APT's two timers, `apt-daily.timer`
  and `apt-daily-upgrade.timer`, are masked and unattended-upgrades is not installed (Debian
  ships it switched off anyway). Nothing else the suit does not use is installed. Baťa does the
  suit's work and nothing more, and through Storož watches that no service does what it should
  not.
- **Updates by hand,** from Borovičok or another computer over SSH, or with one script run from
  there that stops the suit, updates Baťa, starts the suit again and checks it; never while the
  suit is worn.
- **Borovičok** runs the same Debian with a desktop (see
  [hardware](HARDWARE.md#borovičok)), and the same kernel.
- **The microphones only while someone listens:** one unit, `microphones.service`, with
  `StopWhenUnneeded=yes`, writes 1 to register 0x00 of Nataša's sound chip when it starts and 0 when
  it stops, and `headphones.service` does the same with register 0x01, bound by every service that
  plays, so the headphones' stream is said to start and stop and never guessed from silence (see
  [Nataša](../natasa/SOFTWARE.md#sound-across-the-suit)), through Mamka as Storož writes to her.
  Every service that listens binds to it, `BindsTo=` and `After=`: Soňa, Taťána, Nikita in his
  listening mode and Pomoščnik. systemd starts it with the first of them and stops it after the
  last, so the headband's *quiet*, which stops Soňa, also stops the microphones when nobody else
  listens.

**Baťa does little to the data.** He checks each frame's CRC, computes the envelopes and the
IMUs' quaternions of the step (see [signals](SIGNALS.md)), ~10 MFLOP/s, and hands the model its
window; the Hailo does the rest, and the CPU keeps watch on the input and delivers the results
on the output.

- The Hailo reads its input from Baťa's RAM with its own DMA: HailoRT maps a buffer for it with
  `dma_map()` or `dma_map_dmabuf()`. There is no way round the RAM: in the kernel's device trees the
  RK3588's PCIe controllers are not marked `dma-coherent` (`rk3588-base.dtsi`, `rk3588-extra.dtsi`,
  where PCIe goes through the SMMU), so devices on PCIe never see the CPU caches and read and write
  RAM directly.
- The RAM costs nothing here: both processors' transfers, 1,448 B a cycle, ~2.8 MB/s, ~23 cache
  lines.
- One copy: the SPI's DMA fills spidev's kernel buffer, and spidev copies it to the reader; the
  Hailo gets only the windows of values the CPU builds from it (see [signals](SIGNALS.md)). Without
  a driver of our own there is no way round that copy, and 1,448 B a cycle cost next to nothing.

## The kernel

On the ROCK 5T Baťa runs a mainline kernel with two things of his own, an overlay and one patched
driver. Both are small and both are kept in `software/`.

- **The overlay:** SPI1_M1 with chip select 1 at 37.5 MHz for Mamka's processor 1; SPI0_M2 with
  chip select 0 and SPI3_M0 with `cs-gpios` on header pin 29 at 11.1 MHz for her processor 2,
  their `rx-sample-delay-ns` set if the first board asks for it; I2S2_M1 as the slave with a
  dummy codec; pins 36 and 31 as inputs with an interrupt, "data ready"; two free header GPIOs,
  chosen when Terem is drawn, as inputs for the Umnicas' PGOOD; the console on pins 8 and 10 left
  to the ROCK; and the two converters of
  [Terem](../terem/HARDWARE.md#the-converters) as regulators: `regulator-fixed`,
  `enable-active-high`, `gpios` on header pin 16 (GPIO3_A4) for A and pin 32 (GPIO3_C2) for B,
  `startup-delay-us = <7000>` for the LMR60440's 6 ms soft start (t_SS, SNAS877), no
  `vin-supply` (Terem's converters run from the battery; naming the ROCK's `vcc3v3_pcie30` would
  make the kernel raise GPIO1_A4 and run the ROCK's own converter idle whenever a Hailo is
  powered, so that rail stays unused and the core disables it), and `vpcie3v3-supply` of
  `pcie3x4` set to A and of `pcie3x2` to B. The *normal* profile sets one port
  `status = "disabled"`. And the USB-C's DisplayPort, which the ROCK 5T's mainline device tree
  leaves off though the board is wired for it (see
  [hardware](HARDWARE.md#which-computer)): the FUSB302B on I2C4 with its interrupt, the
  connector with DisplayPort's alternate mode and the PHY's DisplayPort side, after the RK3588
  boards whose device trees have it already; as a source it offers 5 V at 1.5 A, over the
  glasses' 1 A.
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
  its 7 ms, the PHY, PERST# held 100 ms (`PCIE_T_PVPERL_MS`) and released, the link trained and
  the device enumerated, the same sequence as at boot. A Hailo whose converter tripped (PGOOD
  low) is taken off that way, and tried again once.

## Storož

*Storož* (Tron), Russian for the watchman, is one small daemon with one job: when something fatal
breaks, he stops the household, leaves the gate open and says why. One path for every fatal
fault instead of a recovery branch for each; our Tron, the program that fights for the users.

- **The services** of the suit, the SPI reader, the model, the output, the recorder and the
  assistants, are systemd units wanted by one target, `suit.target`. Storož is a unit of his
  own, started before them, `Restart=always`, and not part of that target; he, `sshd` and the
  network carry `IgnoreOnIsolate=yes`, and both targets `AllowIsolate=yes`, since an isolate
  stops every unit the new target does not pull in and a unit stopped on purpose is not
  restarted by its `Restart=` (systemd.unit(5), systemd.service(5)): without it `storoz resume`
  would stop the watchman and the SSH session that said it.
- **Baťa always starts halted:** the default target is `storoz.target`, and Storož looks for the
  mark a clean shutdown leaves, a file written as the system goes down. Found, he removes it and
  isolates `suit.target`, which asks Mamka for the suit (her power command 6); missing, he stays
  halted with the reason 10, an unclean start: the watchdog, a kernel panic or the power lost. The
  watchdog's driver tells no boot status (`dw_wdt.c`), so the mark is what tells the three from a
  clean start. Started again while the suit runs, after a crash of his own or his `WatchdogSec`, he
  finds `suit.target` active and carries on; the mark decides only when neither target is up.
- **Watchdogs:** the RK3588's own, `watchdog@feaf0000` (`rockchip,rk3588-wdt`, `snps,dw-wdt`,
  enabled in mainline's `rk3588-base.dtsi`), driven by systemd, `RuntimeWatchdogSec=30s`: systemd
  pings it at least every half of it, so a hung kernel or a hung systemd reboots the board, the
  driver taking the nearest of its sixteen periods (systemd-system.conf(5)). Every service of the
  suit, and Storož, has `WatchdogSec=` of a few seconds and pings from its main loop
  (`sd_notify`, `WATCHDOG=1`): a service that hangs without dying is aborted and restarted by its
  `Restart=` (systemd.service(5)), and one that keeps doing it is Storož's reason 8.
- **What he watches:** Mamka's state and events, processor 1's on her SPI (a unit's place empty) and
  processor 2's on hers (a unit gone, a BMS alarm, the eFuses' PG, either processor silent to the
  other); the Umnicas' PGOOD on their header GPIOs (GPIO events); the Hailo devices on the bus (a
  `remove` from udev, HailoRT's errors); the SPIs' stream while measuring (no "data ready" for a
  second); the SoC's and the Hailos' temperatures in sysfs; the disk when recording; and systemd
  itself (a unit that failed twice in a minute).
- **Fatal:** an Umnica gone or her converter tripped (after the one `bind` retry of
  [the kernel](#the-kernel)), the SPIs' stream silent, Mamka silent, a temperature over its
  limit, a BMS alarm of the protective kind (a cell under or over its voltage, over temperature,
  a short, over-current on discharge), two modules driving the bias, a service that keeps
  dying, and a halt by hand; the second Umnica in the brutal fitting is not fatal, the cameras
  moving to the RK3588's NPU. **Not fatal,** handled where it happens and logged: a damaged frame
  (a gap), a unit gone from a line (the data go on with a hole), the glove missing, a sensor
  off, a lost UDP frame; the disk full, which stops the recording and not the suit; a low state of
  charge, which halts nobody in the street: a warning on
  the headband at a first threshold and the power's command 1, the suit shut down in order, at
  a second, both set on Baťa, Mamka's own threshold on the pack's voltage behind them (see
  [Mamka](../mamka/SOFTWARE.md#mamkas-own-registers)).
- **What he does:** `systemctl isolate storoz.target`, a target that conflicts with `suit.target`
  and keeps the network, `sshd`, Storož and nothing else, so the services fall and the terminal
  stays. Then, once a second until told otherwise: an event packet (type 5, *halted*, the reason in
  `which`) to every subscriber, Borovičok first, and to Mamka the power's command 4 with the reason
  (her processor 2, chip 0x00, register 0x10, see
  [Mamka](../mamka/SOFTWARE.md#mamkas-own-registers)), who plays a pattern on the headband; the
  lines, the headband and Mamka run on without Baťa. No reboot, no automatic retry: a person
  comes over SSH or from Borovičok, reads the journal, clears the cause and says `storoz resume`,
  which isolates `suit.target` again and writes the command 5; for the reasons 8–10 a long press
  of Nataša's button resumes too.
- **The Mamka link,** one small daemon outside `suit.target`, `IgnoreOnIsolate=yes`, owns the
  spidevs and every frame to and from Mamka; Storož, the services and the status page speak
  through it, so command 4 and the events still reach her while `storoz.target` holds. Storož
  keeps the subscribers' list, and the status page stays up.
- **Reasons** (1 B): 1 an Umnica gone, 2 an Umnica's converter (PGOOD low), 3 the SPIs' stream
  silent, 4 Mamka silent, 5 over temperature, 6 a protective BMS alarm, 7 free, 8 a service that
  keeps dying, 9 by hand, 10 an unclean start, 11 two modules driving the bias.

## Budilnik

*Budilnik*, Russian for the alarm clock, wakes a wearer who has left the suit alone, and if nobody
answers it puts the household to bed. A service of Baťa's: with every IMU at rest, no button
pressed on Nataša and no subscriber, it plays a line in the headphones after a first time, and
after a second asks Mamka for the suit shut down in order (the power's command 1, see
[Mamka](../mamka/HARDWARE.md#on-and-off)). A movement or a press starts the count again. The
times, the lines and the voice are settings, as many lines as anyone wants: our own, in Russian,
recorded or synthesized on Baťa.

## Cores on the ROCK 5T

| cores | job |
|---|---|
| cpu0–3, A55 | the system and everything else, interrupts included |
| cpu7, A76 | input: the "data ready" pin, SPI, hand-off to the Hailo |
| cpu6, A76 | output: the Hailo's results out over UDP or USB HID |
| cpu4–5, A76 | free: sound, the assistants, learning, applications |

- **The assistants run on cpu4–5 alone,** with no NPU and no Hailo: Soňa's YAMNet, Taťána's
  Parakeet, Nikita's BeatNet and Pomoščnik's OCR (see [Soňa](../sona/README.md),
  [Taťána](../tatana/README.md), [Nikita](../nikita/README.md),
  [Pomoščnik](../pomoscnik/README.md)). The first Umnica is the suit's; the second, in the brutal
  fitting, is for Ďaďa Sem's cameras and Pomoščnik's "what is it" only. Without it the cameras go
  to the RK3588's NPU and "what is it" online.
- cpu6 and cpu7 are set aside (`isolcpus`, interrupts moved to the small cores, threads pinned
  with `SCHED_FIFO`).
- **The three SPIs read at once:** processor 1's on SPI1 and processor 2's on SPI0 and SPI3 are
  three controllers, each with its own DMA, so a thread for each, pinned to cpu7, or `spi_async`,
  ends a cycle's transfers ~227 µs after "data ready", against 503 µs one after another; the "data
  ready" pins' and the controllers' interrupts on cpu7; spidev's buffer raised from its 4,096 B
  (`spidev.bufsiz`) to 64 KB, ~60 of processor 1's cycles, so a late wake catches up in one
  transfer.
- The clock is set per cluster: cpu0–3, cpu4–5 and cpu6–7 each have their own. cpu6–7 run at a
  fixed frequency so the response does not wander; the profiles hold cpu4–5 lower or let them go.
- The device tree gives every core a deep idle state (`CPU_SLEEP`, `rk3588-base.dtsi`); on the
  input core it is switched off (`cpuidle/state1/disable`), so the core waits in WFI and wakes
  quickly.

## Latency

From a sample to the output:

| stretch | time |
|---|---|
| sample to Mamka's processors, by the unit's slot | 54–249 µs; a cycle's frames of data are complete at 249 µs |
| Mamka's processors to Baťa, the frames as they came in places by the unit's kind | processor 1's 1,064 B in 227 µs at 37.5 MHz, processor 2's 384 B over her two SPIs in 138 µs at 11.1 MHz, the three read at once; ~0.48 ms from DRDY in all |
| a step's IMU data, carried in the frames 0–11 | ~6 ms, the step's last bytes in its twelfth frame |
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
- **HID mode** for a computer outside the backpack (Borovičok gets the same over the cable): Baťa
  plugs into it over USB as a keyboard and mouse, set up through
  Linux's USB gadget configuration (configfs) with no driver to write. Gestures turn into key
  presses, for older games for instance: steps on the spot move, the head looks around, the arm aims
  as the mouse.
  - On the ROCK 5T it goes out of the USB-C, which is dual-role and does not power the board;
    it is also the glasses' port, so the two do not run at once.
  - Between Baťa and the other computer sits a USB isolator, TI **ISOUSB211** (SLLSFC5D): a USB 2.0
    repeater at low, full and high speed (1.5, 12 and 480 Mbit/s), 5,700 Vrms of isolation,
    SSOP-28, no crystal, and automatic role reversal, so the ROCK 5T's dual-role USB-C works
    through it. Each side is fed on its own: side 1, the suit's, from Baťa's 5 V on VBUS1 (4.25
    to 5.5 V, an LDO inside makes its 3.3 V), side 2 from the other computer's VBUS; ~10–15 mA
    a side plus up to ~96 mA on the transmitting side at high speed. V1OK and V2OK tell each
    side the other is up. It sits in the backpack between Baťa's USB-C and the shell's socket,
    so the suit and the wearer stay apart from the other computer's ground, and its 5 V never
    meets the suit's.
- **The whole system on a ROCK 5T,** Borovičok, or Baťa alone: the applications run on it, and its
  USB-C carries the picture to glasses that take DisplayPort over USB-C (VITURE, XREAL and the
  like), with their power and their head sensors on the same cable; the suit is the mouse, the
  keyboard and the hands. Radxa gives the port DisplayPort up to 4K at 60 Hz. In the mainline kernel
  (7.3) the ROCK 5T's device tree does not switch it on yet: the USB-C controller is marked `fail`
  there for the 5B, which a power-delivery reset takes off its supply, and the 5T, fed from DC, does
  not have that problem; the DisplayPort driver itself is in mainline, and other RK3588 boards
  switch it on, so Baťa's overlay does too (see [the kernel](#the-kernel)). The fallback is an
  HDMI output through a powered HDMI-to-USB-C adapter, which XREAL's manual shows for computers
  with HDMI only.

## Learning

The Hailo only runs models; HailoRT has no functions for training. Models are compiled for it
with the Hailo Dataflow Compiler on a PC: for the Hailo-10H its version 5.x, on x86 Ubuntu
22.04 or 24.04 (hailo_model_zoo, GETTING_STARTED), with 16 GB of RAM or more.

- **A layout is judged on three putting-ons at least,** the spread between them given beside its
  score, so that one good fit is not taken for a good layout.

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
- **Recordings** are made only when asked, and then perhaps only parts, in BDF, the events as BDF+
  annotations so that the profession's software reads them (see
  [Porjadok](../porjadok/SOFTWARE.md#ci-btp)): all the EMG, 280 channels of 24 bits at 1,920 SPS,
  is 1.61 MB/s, ~5.8 GB an hour, and a part a fraction of it. The large ones go to Borovičok's
  NVMe SSD, since Baťa's PCIe goes to the Hailos in the normal and brutal fittings.
- Learning takes more battery than plain running. That is accepted.
- **The model's shape: convolutions only,** so that one model runs on the Hailo, on the
  RK3588's own NPU and on the cores alike, and the small fitting's fallback is the same model:
  - **The input as an image,** 1 × 32 × 928: the window of 32 steps, the 280 envelopes and the
    108 IMUs' 6 values of each step, 928 values a step, variant A's (see [signals](SIGNALS.md)).
    Variant B's EMG comes as 1 × 512 × 280, the raw samples, into a front of convolutions over
    time with a stride of 16 down to the 32 steps, then 1 × 1 across the channels, joined to the
    IMUs' 1 × 32 × 648; the body after it is variant A's.
  - **Convolutions over time** with a kernel of 1 × k, **1 × 1 across the channels**, which also
    stands for the fully connected head; the 32 steps are covered by stacking layers or by a
    stride of 2, not by dilation.
  - **ReLU and residual additions right after a convolution,** where both can fuse them.
  - **INT8 quantised per tensor,** not per channel.
  - **No recurrent layers and no attention:** a window of 32 steps needs neither.
- **Why:** the Hailo's compiler takes convolutions, depthwise convolutions, element-wise
  operations, average pooling and ReLU, SiLU, Hard-Swish, Mish, PReLU, Tanh; GeLU is a preview,
  and recurrent layers, attention, softmax and layer normalisation are not in that list (the
  Hailo Community's list of supported operators); a layer it does not take fails the whole
  compile, nothing falls back to the CPU. Mesa's Teflon on the RK3588 accelerates convolutions
  only, per-tensor quantised and without dilation, with an addition or a ReLU fused into them;
  everything else runs on the CPU (Mesa's Teflon page; its Rocket driver as reported in 2026).

## The map

The map, the suit's table of what is fitted, and every unit's settings live here, keyed by each
unit's UID; a unit keeps nothing in its flash but its firmware, and Mamka sends the settings at
every start (see [Porjadok](../porjadok/SOFTWARE.md#the-registers)). Where a unit sits on the
body no unit can tell, so Baťa asks: an application over plain HTTP, minimal in what it needs and
in its graphics, opened in the browser of a phone or of Borovičok.

- **What it knows without asking:** the line tells the piece of the suit, each of Mamka's headers
  being its line's (see [Mamka](../mamka/HARDWARE.md#lines)); the kind tells the glove and the
  sock, the fourth slot of an arm's or a leg's line; lines 5 and 6 carry one module each, line 8
  Nataša and Míša by their numbers. A module replaced, a new
  UID on a line where one of the map is missing, takes the missing one's place, and the
  application only confirms it.
- **What it asks:** the order on a line, at the first fitting or when two modules of one line change
  at once. The module's status LED blinks (register 0x02, see
  [Porjadok](../porjadok/SOFTWARE.md#the-registers)) and the application asks which place it is,
  offering the line's free places; the map gives it its number, its type's next free one. A unit of
  the map missing at a bring-up stays in it, shown as missing, until the person forgets it.
- **What it shows,** one page, a table by line: the place, the UID's last four hex digits, the
  kind, the firmware's version, present or missing; for a module whether it drives the bias and
  its strip's ground layer; from the diagnostics, the electrodes off by the last check, the
  temperature, the lowest 3.3 V and the last reset's cause; and Storož's state, running or
  halted and why, with no button: resuming stays over SSH.
- **What it sets:** which module drives the bias, the strips' ground layers on ground or driven,
  the IMU mode; only in the service mode, in effect from the next start, since Mamka sends the
  settings at every start.
- **How:** one Python program, the standard library only; plain HTML forms with no JavaScript,
  the page reloading itself every 2 s; the map one JSON file keyed by the UID, which can be edited
  over SSH too; listening on Baťa's local network only.

**The place list,** the numbers behind meta 1's places (see
[Porjadok](../porjadok/SOFTWARE.md#ci-btp)), by line, so the line follows from the place; 0 an
unknown place:

| line | places |
|---|---|
| 1 | 1 the left shoulder, 2 the left upper arm, 3 the left forearm, 4 the left hand: the glove, or the sock on it |
| 2 | 5–8 the same on the right |
| 3 | 9 the left hip, 10 the left thigh, 11 the left calf, 12 the left foot, the sock |
| 4 | 13–16 the same on the right |
| 5 | 17 the head |
| 6 | 18 the chest and abdomen |
| 7 | 19 the neck and upper back, 20 the lower back |
| 8 | 21 Nataša, 22 Míša |

**The joint list,** a first draft (11 Nov 2026), the numbers behind the joint table of meta 3 and
4 (see [Porjadok](../porjadok/SOFTWARE.md#ci-btp)): 56 joints, 96 of the snapshot's 127 values,
each the turn of its child bone in its parent bone's frame, from the IMUs' places in Bogatyr's
CONSTRUCTION ([the IMUs](../bogatyr/CONSTRUCTION.md#the-imus)); the bones' IMUs in the order of
each unit's table, the glove's zones taken as index, middle, ring, little, thumb, carpus and the
sock's four trial places guessed until their tables are fixed. The ranges are first guesses
with room to spare, set by the recordings, in the table in 2° steps; the shoulder and the hip as
a swing and a twist (see [Porjadok](../porjadok/SOFTWARE.md#output)). In code:
`software/map/suitmap/lists.py`.

| joint | name | parent → child | axes, degrees |
|---|---|---|---|
| 1 | head on neck | C2 → skull | flexion -60 to 60, abduction -50 to 50, rotation -90 to 90 |
| 2 | neck | upper thorax → C2 | flexion -60 to 60, abduction -50 to 50, rotation -90 to 90 |
| 3 | thoracic spine | lower thorax → upper thorax | flexion -40 to 60, abduction -40 to 40, rotation -50 to 50 |
| 4 | lumbar spine | pelvis → lower thorax | flexion -40 to 80, abduction -40 to 40, rotation -40 to 40 |
| 5 | left scapula on thorax | upper thorax → left scapula | flexion -40 to 40, abduction -40 to 40, rotation -40 to 40 |
| 6 | left clavicle on sternum | sternum → left clavicle | flexion -40 to 40, abduction -40 to 40 |
| 7 | left shoulder | left scapula → left humerus | swing forward -150 to 150, swing out -150 to 150, twist -90 to 90 |
| 8 | left elbow | left humerus → left ulna | flexion -10 to 160 |
| 9 | left forearm | left ulna → left radius | rotation -100 to 100 |
| 10 | left wrist | left radius → left hand | flexion -90 to 90, abduction -40 to 40 |
| 11 | left thumb CMC | left hand → left thumb metacarpal | flexion -30 to 60, abduction -20 to 80 |
| 12 | left thumb MCP | left thumb metacarpal → left thumb proximal | flexion -20 to 80 |
| 13 | left thumb IP | left thumb proximal → left thumb distal | flexion -30 to 100 |
| 14 | left index MCP | left hand → left index proximal | flexion -40 to 100, abduction -30 to 30 |
| 15 | left index PIP | left index proximal → left index middle | flexion -10 to 120 |
| 16 | left index DIP | left index middle → left index distal | flexion -20 to 100 |
| 17 | left middle MCP | left hand → left middle proximal | flexion -40 to 100, abduction -30 to 30 |
| 18 | left middle PIP | left middle proximal → left middle middle | flexion -10 to 120 |
| 19 | left middle DIP | left middle middle → left middle distal | flexion -20 to 100 |
| 20 | left ring MCP | left hand → left ring proximal | flexion -40 to 100, abduction -30 to 30 |
| 21 | left ring PIP | left ring proximal → left ring middle | flexion -10 to 120 |
| 22 | left ring DIP | left ring middle → left ring distal | flexion -20 to 100 |
| 23 | left little MCP | left hand → left little proximal | flexion -40 to 100, abduction -30 to 30 |
| 24 | left little PIP | left little proximal → left little middle | flexion -10 to 120 |
| 25 | left little DIP | left little middle → left little distal | flexion -20 to 100 |
| 26 | left hip | pelvis → left femur | swing forward -150 to 150, swing out -150 to 150, twist -90 to 90 |
| 27 | left knee | left femur → left tibia | flexion -10 to 160, rotation -40 to 40 |
| 28 | left ankle | left tibia → left calcaneus | flexion -60 to 40, abduction -40 to 40 |
| 29 | left midfoot | left calcaneus → left forefoot | flexion -30 to 30, abduction -30 to 30 |
| 30 | left big toe | left forefoot → left hallux | flexion -40 to 90 |
| 31 | right scapula on thorax | upper thorax → right scapula | flexion -40 to 40, abduction -40 to 40, rotation -40 to 40 |
| 32 | right clavicle on sternum | sternum → right clavicle | flexion -40 to 40, abduction -40 to 40 |
| 33 | right shoulder | right scapula → right humerus | swing forward -150 to 150, swing out -150 to 150, twist -90 to 90 |
| 34 | right elbow | right humerus → right ulna | flexion -10 to 160 |
| 35 | right forearm | right ulna → right radius | rotation -100 to 100 |
| 36 | right wrist | right radius → right hand | flexion -90 to 90, abduction -40 to 40 |
| 37 | right thumb CMC | right hand → right thumb metacarpal | flexion -30 to 60, abduction -20 to 80 |
| 38 | right thumb MCP | right thumb metacarpal → right thumb proximal | flexion -20 to 80 |
| 39 | right thumb IP | right thumb proximal → right thumb distal | flexion -30 to 100 |
| 40 | right index MCP | right hand → right index proximal | flexion -40 to 100, abduction -30 to 30 |
| 41 | right index PIP | right index proximal → right index middle | flexion -10 to 120 |
| 42 | right index DIP | right index middle → right index distal | flexion -20 to 100 |
| 43 | right middle MCP | right hand → right middle proximal | flexion -40 to 100, abduction -30 to 30 |
| 44 | right middle PIP | right middle proximal → right middle middle | flexion -10 to 120 |
| 45 | right middle DIP | right middle middle → right middle distal | flexion -20 to 100 |
| 46 | right ring MCP | right hand → right ring proximal | flexion -40 to 100, abduction -30 to 30 |
| 47 | right ring PIP | right ring proximal → right ring middle | flexion -10 to 120 |
| 48 | right ring DIP | right ring middle → right ring distal | flexion -20 to 100 |
| 49 | right little MCP | right hand → right little proximal | flexion -40 to 100, abduction -30 to 30 |
| 50 | right little PIP | right little proximal → right little middle | flexion -10 to 120 |
| 51 | right little DIP | right little middle → right little distal | flexion -20 to 100 |
| 52 | right hip | pelvis → right femur | swing forward -150 to 150, swing out -150 to 150, twist -90 to 90 |
| 53 | right knee | right femur → right tibia | flexion -10 to 160, rotation -40 to 40 |
| 54 | right ankle | right tibia → right calcaneus | flexion -60 to 40, abduction -40 to 40 |
| 55 | right midfoot | right calcaneus → right forefoot | flexion -30 to 30, abduction -30 to 30 |
| 56 | right big toe | right forefoot → right hallux | flexion -40 to 90 |

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

- the joint list's first draft: its ranges, the spine's four joints, the glove's zone order and
  the sock's trial places, on the first recordings,
- the ROCK's header 3.3 V off at a poweroff, the RK806 the system-power-controller (likely):
  else the clean-shutdown mark and "pin 1 has fallen" mislead, and every start is reason 10,
- the USB-C device role behind the ISOUSB211: Rd on CC and VBUS from the host's side, from
  SLLSFC5D when drawn,
- the system measured: its RAM and its boot time; Armbian gives no figure for its minimal image,
- the kernel: ours on mainline, against Rockchip's, which idled ~2 W lower than mainline 6.8.1 on
  a ROCK 5B (Thomas Kaiser, 2024); the overlay's DisplayPort on USB-C tried with the glasses,
- Mesa's Teflon with the Rocket driver, which came in Mesa 25.3: trixie ships
  `mesa-teflon-delegate` 25.0.7, trixie-backports 26.1.6 for arm64 (packages.debian.org,
  10 Oct 2026), so the small fitting takes it from the backports, or from trixie's own by then,
- the overlay and the driver patch written and tried on a ROCK 5T: the two regulators, the
  ports' supplies, unbind and bind with one module, then with two,
- to measure: SPI reads and waking on the "data ready" pin (cyclictest, or
  a PREEMPT_RT kernel), the latency of a small model on the Hailo-10H, the USB HID gadget, the
  Ethernet to Borovičok,
- the model's shape above tried: through Hailo's parser on the Dataflow Compiler 5.x, whose
  own list of layers sits behind Hailo's login, and through Teflon on a ROCK 5T,
- where learning recordings go without Borovičok: an SSD on Baťa's USB 3, in the small fitting
  an NVMe SSD in one of his free M.2 slots, or features only,
- the *small* fitting: a model on the RK3588's own NPU through `accel/rocket` and Mesa's Teflon,
  how large it may be and how fast it runs,
