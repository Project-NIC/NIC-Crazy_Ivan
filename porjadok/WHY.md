<div align="center">

# Porjadok: why not

**The graveyard:** what was considered for the household's rules and why it is not used.

↑ [Porjadok](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Each entry says what it was and why it went, so that nobody digs it up without knowing. Where a
thing waits in reserve, it says so.

## The lines

- **M-LVDS** for the lines. Considered for its speed; classic RS-422/485 stayed because of what
  the drivers and the parts around them consume, and the THVD145x reach 50 Mbit/s anyway.
- **The RP1's UARTs for the lines,** on the Raspberry Pi. They reach 6.25 Mbit/s at most,
  without DMA; the lines end at Mamka's STM32H562s at up to 19.66 Mbaud, and Baťa gets whole
  cycles over SPI.
- **The Raspberry Pi as the SPI slave.** The Linux driver did not support it; the
  computer is the master and Mamka raises "data ready" when a cycle waits.
- **Category 5e or 6 Ethernet cable** for the lines, with 100 Ω terminations. It would do; the
  3M 1785 flat cable takes IDC sockets anywhere on a flat stretch, so a unit taps in without a
  connector of its own. The Ethernet cable stays as the fallback.
- **The lines twisted or untwisted.** Not decided: the untwisted 3M 3517 is a variant to try,
  held to two tests (see [hardware](HARDWARE.md#cable-and-connectors-in-the-suit)); until they
  pass, the twisted 1785 is the design.
- **Four long lines** (to 24 Oct 2026), up to four modules a line and a glove behind a forearm's
  module, wherever the units sat on the body, all at 19.66 Mbaud. A line then crossed the
  suit's pieces, so a suit in pieces would have needed connectors along it; eight short lines, a
  line a piece, go straight to the backpack.
- **The body's six lines on processor 1, the head alone on processor 2** (24 Oct 2026, the same
  day). The limbs are processor 1's and the head and the trunk processor 2's, a suit for the head
  and the trunk needing processor 2 alone.
- **The shoulders on the trunk's line in front** (24 Oct 2026). They go with the arms now, the
  arm's cable running from the backpack over the shoulder and down the arm, which chains the
  units along it and eases processor 2, whose work is the most varied (25 Oct 2026).
- **Three units a line at 9.83 Mbaud** (24 Oct 2026), the half rate for margin on the cable. A
  driver draws its ~37 mA only while it sends, so a frame in half the time costs half: every
  line is at 19.66 Mbaud again, four slots of 128 B, ~75 % of a line free in a usual cycle.
- **The glove behind the forearm's module** (to 24 Oct 2026), on the module's
  UART, the module sending it in the line's fifth slot. The glove is now a unit on its arm's
  line with its own drivers: the module carries nothing for it.
- **One connector for the whole suit, the Amphenol PT 24-61, or one a processor** (to 24 Oct
  2026). A connector a branch, eight in the backpack's shell, lets the suit come apart in its
  pieces; the Weipu SP21 of 12 pins is the part, the GX16 for the trials.
- **The Amphenol PT 12-10 a branch** (24 Oct 2026), a bayonet and IP67: over 10,000 CZK for eight
  pairs against ~2,500 CZK for the SP21, which is IP68 and screws on.
- **Six grounds in the cable** (the 3M 1785/16, 16 wires). Ten pins a branch take two wires into
  each supply pin, so the cable has 14 wires and four grounds: on a metre at ~0.38 A the drop is
  ~57 mV against 51 mV, and a unit sits ≤ ~30 mV off Mamka's ground at the worst line.
- **The clock drivers' DE on a pin a line** (24 Oct 2026, morning) **or tied on** (the
  afternoon). Each processor switches her own lines' clock on one pin: ~0.3 A of the eight
  drivers comes off while her lines are off or asleep, and no line is switched alone.
- **The digital rail at 3.7 V** (to 10 Oct 2026). It saved ~0.3 W across the suit against 4 V, but
  at the worst corner the cable, the filters and the connectors left the modules' TPS7A2033 ~3.35 V,
  under the 3.44 V its dropout (at most 140 mV) needs and the 3.6 V its ±1.5% asks (SBVS338H, 5.5),
  and the head's motors ~3.5–3.6 V, short of the 3.55 V their overdrive needs (SLOS754C). 4 V gives
  both room for ~0.3 W. The analog rail stays at 6 V: 5.5 V would save only ~0.06 W, and the
  headroom helps the TPS7A47 reject ripple.

## The frame and the output

- **A short START pulse.** Conversions run only while START is high; a pulse would stop the
  measurement after the first conversion (SBAS499C, 9.4.1 and 9.4.5). START stays high.
- **More than one byte per joint axis** on the output. Over 120° a byte's step is 0.47° and its
  rounding 0.14° RMS, under what IMUs and EMG deliver; more bits would carry noise, and the
  Hailo, where one is fitted, hands out UINT8 as it is.
- **Three angles for the shoulder and the hip.** Any three angles in a row have a pose where the
  first and third axes line up, and for the shoulder in the ISB convention it is the arm hanging
  at the side. They go out as a swing and a twist instead, with the unreachable pose put behind
  the head or the back.
- **A second number in the output frame.** RTP carries a sequence number and a timestamp, the
  one to see a loss, the other to place the data in time. CI-BTP carries the sample number
  alone, at the owner's wish: a lost snapshot frame shows as a jump in it, a lost event is caught
  by the event packet's own counter, and a meta packet comes again within a second.
- **Signing the firmware.** MCUboot checks a SHA-256 and a signature on every image. The suit
  takes images from Baťa alone, and whoever has Baťa has the suit with or without a signature,
  so the CRC-32 guards against a bad transfer and nothing more; a signature would cost a key and
  a verification in every unit.
- **Framing on the lines.** Byte stuffing or a sync word, as HDLC or COBS do, is not needed: the
  slots say where a frame begins, and every kind of frame has one length and its own CRC.
- **Labelling the contact points by hand.** The rule that marks them, a limb that neither hangs
  nor is held must rest on something, marks the recordings as well, so nobody labels.

## The frames and the modes

What was tried for the frames and the modes and left:

- **The frame of 40 B with an info byte to each channel,** the ADS1299's status word
  regrouped into every frame. The lead-off bits go in the diagnostics, 120 times a second, which
  is soon enough for an electrode come off.
- **A control frame of 6 B and containers of eleven types.** Two frames, 34 B and 8 B, now
  carry the data and the whole setting both ways, a command, a chip and its registers; firmware
  has a frame of its own, 519 B.
- **A universal list of container types for the whole suit** (22 Oct 2026): the owner wanted no
  universal protocol grown out of it, but the bytes link by link, alike where they can be. A new
  sensor takes a chip's number and a map of registers, and no command of its own.
- **A mailbox of 1–64 B** for the answers (22 Oct 2026). An answer is a frame of 8 or 34 B in
  the free part of the unit's slot.
- **The cycle packed by the map on the lines,** as EtherCAT packs its process data, the units one
  after another and one shared window at the cycle's end (22 Oct 2026, a misreading of the
  owner's map). The map is the table of what is fitted and says what the bytes mean; the fixed
  slots stay on the lines and say who sends when.
- **A unit's number and tables in its flash,** on 22 Oct 2026 also in two copies, A and B, in
  the flash's high-cycle area, with a *save* command. A unit keeps nothing in flash but its
  firmware: the map and every setting live on Baťa, keyed by the UID, and go down at every
  start, so a unit replaced is only a new UID.
- **A tag of 16 bits, the CRC of the UID,** to tell the units apart in *assign*: two units
  with the same tag would have taken the same number. The whole UID cannot clash.
- **The ADS1299's registers in the rotation,** and **the answer to a write as the registers
  read back** (to 24 Oct 2026). The answer is the result in 8 B; whoever wants to check
  reads the registers.
- **START low while stopped.** What it would save the datasheet does not give, and every new
  start would need the sync again; the ADS1299s run on idle through the whole active mode, and
  only the lines' power off and on ends the sync.
- **The line clock as the switch between the modes** (23 Oct 2026): every
  unit on its HSI at 38,400 Bd until Mamka raised its line's clock, then at 19.66 Mbaud, and back
  when the clock went. It took a second setting of every peripheral for the HSI and a change of
  rate on every wire at once, and a unit that missed the change was deaf at the other rate.
  Professional systems start on their own oscillator, lock to the reference and stay on it, as
  a studio's clocks do, and change their states by command at one rate, as EtherCAT and CANopen
  do; so the clock runs from Mamka's start and every wire keeps one rate (24 Oct 2026), a change
  in the software alone.
- **"The first block erases the bank"** instead of an explicit *begin*. A first block lost in the
  broadcast would leave the bank unerased, and sent again it would erase all that came meanwhile.
- **Mamka's record of 768 B in two halves of 384 B,** a half on each SPI with a header and
  a CRC each. Each processor sends one transfer in places of 34 B, processor 2's striped in words
  of 4 B over her two SPIs.
- **The frame of data of 37 B in the active mode** (to 24 Oct 2026): the address,
  an IMU multiplex of 4 B, a rotation of 4 B and a sample number of 16 bits in each. The owner's
  frame of 34 B took its place, the unit's number and the cycle's in every frame, the IMUs'
  steps sent at once after the step (24 Oct 2026, evening).
- **The trimmed frames of data** (24 Oct 2026, afternoon): 30 B a module, 13 B the glove, 7 B
  Nataša, the address left to the CRC, the IMUs and a rotation of 128 B spread a byte at a time
  over 32 and 128 frames, the sample's low byte. A frame that says neither whose it is nor which
  cycle, and slow data spread over a hundred frames, are hard to check and to mend; one frame of
  34 B for every unit's data, and the slow data in the diagnostics every 32 cycles, replaced them.
- **The cycle repacked by the map on the SPIs** (24 Oct 2026, afternoon): the units' payloads
  under one CRC-32, a header of 8 B, late frames 0x20 for the repeats, ~30 % less on the SPIs.
  The frames go as they came again, their CRC guarding the SPI too, in places of 34 B with no
  header; the data have no repeat (24–25 Oct 2026).
- **A repeat of a frame of data** (to 24 Oct 2026): the unit kept its last 16 frames and sent
  a bad one again in its slot, Mamka filing it late. A frame that fails its CRC is a gap now,
  which the filters and the model take; the sound alone is repeated, a lost packet being silence.
- **CI-UTP, the firmware's container** behind the mark 0xC1A1 (to 24 Oct 2026). A block of
  firmware is a frame of its own kind, 519 B, so the suit has two protocols, CI-STP inside and
  CI-BTP out; the mark is left to CI-BTP's *subscribe*.
- **A bank byte in every command** (to 24 Oct 2026). An IMU switches its bank by its own
  REG_BANK_SEL like any register, and the unit's own chip has one space of registers in ranges,
  so a read is the chip, the register and the count in 8 B.
- **The address by nibbles,** the line and the unit on it (23–24 Oct 2026). A unit's number is
  given by *assign*, 1–0x7F, the system's parts keeping theirs fixed; whether a number splits
  into a line and a unit is open.
- **Line 8's cycle kept by Nataša's timer** (to 25 Oct 2026). Nataša is optional, Bluetooth
  headphones taking her place; every unit on line 8 keeps the cycle on its own timer from the
  suit clock, Mamka's heartbeat the correction, and one unit alone runs its slot by itself.
- **Nataša's raw frame to disk,** CI-BTP's packet 17. Her microphones' frames come to 296 kB/s
  against the 150 kB/s of processor 2's UART of the time, and all the frame held reaches Baťa
  anyway: the sound over the I2S, the buttons and the state as events.
- **The raw recording,** CI-BTP's packet 16, a processor's cycle to disk, ~2 MB/s (to 25 Oct 2026),
  and an archive of our own, compressed, weighed as an example. Nothing
  is recorded unless asked, and then perhaps only parts, uncompressed, in a format someone
  already uses: BDF for the signals, CSV for small parts.