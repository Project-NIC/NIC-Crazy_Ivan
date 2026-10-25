<div align="center">

# Porjadok: software

**What every unit shares in firmware:** the modes, the frames and their slots, the commands and
the registers, the service mode, the start, the errors, the way into Baťa, the firmware and the
output of the whole suit.

↑ [Porjadok](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Every unit is C, hard-coded, with no operating system. The lines these frames travel on are
under [hardware](HARDWARE.md#links-between-boards). Two protocols live here:

- **CI-STP,** the Small Crazy Ivan Transport Protocol, inside the suit: four frames of fixed
  lengths, 34 B and 8 B for everything, 519 B for firmware and 198 B for the sound, on the lines
  and the SPIs to Baťa, Mamka's frames passed on along the glove's wires too;
- **CI-BTP,** the Big one, out of Baťa to any computer (see [Output](#output)).

The lines follow the body's pieces (see [hardware](HARDWARE.md#links-between-boards)), at most
four units a line: lines 1–4 on Mamka's processor 1 carry the limbs, an arm's line its shoulder,
upper arm, forearm and glove, a leg's its hip, thigh and calf; lines 5–7 on her processor 2 the
head, the chest and the back; line 8, on processor 2 too, [Nataša](../natasa/SOFTWARE.md) and
[Míša](../misa/SOFTWARE.md), with the sound. **The map** is the suit's table of what is fitted:
what sits on which line and in which slot, what each unit has and where on the body. It lives
on Baťa, keyed by each unit's UID, and from it Mamka and Baťa agree at the start on a table of
what each unit's number is and how its frames run.

## The modes

Two modes for the whole system:

1. **service,** from power-on to the first *start*: there is no DRDY, so everything on lines
   1–7 goes as question and answer, with no slots (see [Bring-up](#bring-up)). Discover and
   assign, the units' tables, the settings, firmware; last the bus test and *get ready* to each
   unit (see [Before the first start](#before-the-first-start)); nothing else runs but tests by
   hand.
2. **active,** from the first *start*: *start* on lines 1–7 at once takes START high on every
   ADS1299. From then on DRDY is always there and **the slots always count from it.**

**One rule:** on lines 1–7, no DRDY, question and answer; DRDY, the slots, each DRDY correcting the
cycle anew. **Line 8 runs by its slots always** (see [Line 8](#line-8)). **The clock switches
nothing:** it runs on every line from Mamka's start, stopped only while a line is off or asleep,
every unit takes it straight after its reset, with a number or without one, and every line runs at
19.66 Mbaud (see [the clock tree](#the-clock-tree)). A unit with no number stays silent but for
*discover*.

**The ADS1299s run on idle through the whole active mode.** The active mode has two states,
*stopped* and *measuring*, and a later *stop* or *start* leaves START alone: it only says from
which cycle the data count. Idle costs what the chip costs converting, 39 mW typical and
42 mW at most (SBAS499C, Electrical Characteristics, at 250 SPS), 0.62 W for sixteen; what START
low would save the datasheet does not give. Only the lines' power off and on ends the sync,
Mamka's power command 3 (see [Mamka](../mamka/SOFTWARE.md#mamkas-own-registers)): every unit
starts again as after power-on, in the service mode. A bring-up of 5–10 minutes is fine.

**The master's heartbeat:** while measuring Mamka speaks only when she has something to say, and
otherwise sends *heartbeat* (0x14) every **1 s**, the cycle's number in it. A unit that has heard
nothing for **3 s** asks *Mamka?* (0x15) in its slot, which every unit on the line hears on the
return pair; with no frame from Mamka within **1 s** more, all of them stop: *stopped*, the ADS1299s
on idle and still in step. It is done in software, in the interrupt that takes Mamka's frames
anyway.

## The frames

Four frames, each of one length, and **every kind of frame has one length:** zeros fill what is
not used, and a frame of another length is an error before anything in it is read. There is no
length byte: Mamka knows each kind's length, and the CRC on every frame catches a byte too many
or too few.

| frame | B | what | where |
|---|---|---|---|
| the frame of 34 B | the unit's number 1, the kind 1, the frame's number 2, 28 B by the kind, CRC-16 2 | the data, the diagnostics, the answers with values, the writes of several registers | every line, both ways, in every mode |
| the frame of 8 B | the unit's number 1, the kind 1, the command's number 1, 3 B by the kind, CRC-16 2 | the questions and the short answers | every line, both ways, in every mode |
| the firmware's frame, 519 B | the unit's number 1 (0 every unit), the kind 1, the kind of unit it is for 1, the block's number 2, 512 B of the image, CRC-16 2 | a block of firmware | down only, in the service mode |
| the sound's packet, 198 B | the unit's number and the kind 2, the packet's number 2, 192 B of sound, CRC-16 2 | 1 ms of sound | line 8, both ways (see [Nataša](../natasa/SOFTWARE.md#sound-across-the-suit)) |

- **The unit's number** alone says what the unit is: 1–0x7F for the sensing units, given at the
  start by the UID (*discover*, then *assign*); the system's parts have theirs fixed, Mamka's
  processors 0xF1 and 0xF2, Nataša 0x81 and Míša 0x82, both always on line 8; 0 is every unit.
  Whether a number is split into a line and a unit on it is open.
- **The frame's number is the cycle's number,** the same for every unit in a cycle: Mamka gives
  the first in *start*, and every unit counts its cycles from then by the suit clock. A frame
  lost, a frame late or old, and a unit out of step show by it, and Baťa pairs one cycle's frames
  by it. 2 B, wrapping after 17 s; the full count is kept by Mamka and Baťa. In the commands and
  their answers the same place carries the command's number, in the firmware's frame the
  block's.
- **Little-endian,** every field of 16 and 32 bits, the CRC too; the ADS1299's samples go most
  significant first, as the chip sends them, and an IMU's TEMP_DATA too, as the chip gives it.
- **The CRC-16** of every frame is CRC-16/CCITT-FALSE: polynomial 0x1021, initial value 0xFFFF,
  no reflection, no final XOR, over the bytes in the order they are sent, stored little-endian.
  The STM32H5's CRC unit computes it in hardware: its polynomial and its size, 7, 8, 16 or 32
  bits, are programmable (RM0481 Rev 5, 19.2 and 19.5.5).

### A unit's data

The frame of data, kind 0x20, the one sent 3,840 times a second:

| B | a module's frame of data |
|---|---|
| 0 | the unit's number |
| 1 | 0x20 |
| 2–3 | the frame's number, the cycle's |
| 4–27 | the ADS1299's 8 channels, 3 B each, as the chip sends them; its 3 B of status are not in the frame |
| 28–31 | 4 B of the IMUs' steps |
| 32–33 | CRC-16 |

- **The IMUs' steps:** a step is 32 ADS samples, 1/120 s: the IMU's turn and mean force over it,
  summed by the unit from ten samples at 1,200 Hz, or the chip's own 120 Hz sample (see
  [Rubaška](../rubaska/SOFTWARE.md#the-imus-settings)), 12 B an IMU. The unit lays its IMUs'
  steps one after another in the order of its table and sends them at once after the step, 4 B a
  frame, the frame whose number mod 32 is k carrying the bytes 4k to 4k + 3: a module's four IMUs
  in the frames 0–11 of the 32, zeros after them until the next step.
- **The glove's** frame of data is the same 34 B, its steps in all 28 B: 20 IMUs in 9 frames of
  the 32, then zeros (see [Rubaška](../rubaska/SOFTWARE.md#the-glove)); the 28 B would hold up to
  74 IMUs in the 32 frames.
- **Nataša and Míša** send their frame of data once every 32 cycles, in the cycle whose number
  mod 32 is 15, half a round from the diagnostics: Nataša's slot of 256 B would not hold her frame
  of data, her diagnostics and a packet of the microphones at once, 266 B (see
  [Nataša](../natasa/SOFTWARE.md#natašas-frames) and [Míša](../misa/SOFTWARE.md#data)).
- **No lead-off byte and no health byte in it:** a dead sensor is sent as zeros, which a working
  one never gives in full, an IMU's step or the 24 B of EMG; Mamka watches the places that should
  carry data, and zeros there many times running mean the sensor is gone. The rest of a unit's
  health goes in its diagnostics.

### The diagnostics

A frame of 34 B of its own kind, 0x21, from every unit on a line once every 32 cycles (the
Bratiški send none, their IMUs being in their Staršaja's), all in the same
cycle, the one whose number mod 32 is 31, in the free part of each unit's slot; Mamka passes them
on over the SPI from a queue in the next cycles. **Its bits are 1 while all is well** and stay 0
once anything went wrong in those 32 samples, so a scan of the words for all ones is enough, and
a zero is looked into only when found.

| B | the diagnostics |
|---|---|
| 0–3 | the unit's number, 0x21, the frame's number |
| 4–7 | the sensors alive, a bit a chip in the order of the unit's table; unused bits 1 |
| 8–11 | the sensors without an error over the 32 samples, the same bits |
| 12 | the electrodes P1–P8 on the skin, a bit each |
| 13 | the electrodes N1–N8 on the skin |
| 14 | bit 0 the bias electrode on the skin, bit 1 the frames from Mamka without an error; the rest 1 |
| 15 | the processor's temperature, signed, in °C |
| 16 | the lowest 3.3 V since the last diagnostics, in 10 mV above 2.00 V |
| 17–28 | the IMUs' temperatures, 2 B each as the chip gives them (TEMP_DATA), six at most |
| 29–31 | zeros |
| 32–33 | CRC-16 |

- **The electrodes:** the ADS1299's own bits are 1 for an electrode off (LOFF_STATP and
  LOFF_STATN, SBAS499C, table 23), read with every sample in its status word; the module turns
  them over and keeps a 0 for the 32 samples. **The bias electrode** is BIAS_STAT, CONFIG3 bit 0
  (SBAS499C, 9.6.1.4), 1 for off, turned over the same way. A unit with no ADS1299 sends ones.
- **The processor's temperature** stands for the board's: the ADS1299 has no temperature
  register, its sensor being read only by switching a channel's MUX to it.
- **The lowest 3.3 V** is measured by the processor's own ADC against its VREFINT, no part added.
- **More than six IMUs** go by turns, which six told by the frame's number: the glove's 20 in
  four diagnostics, ~33 ms. A temperature once a minute would do.

### How a unit builds the frame

The ADS1299's read is 216 bits: the status word of 24 bits, then 8 channels of 24. The STM32H523's
SPI takes frames of 4 to 32 bits (DS14540, table 10), so it reads in frames of 8 bits and the GPDMA
moves the 27 bytes as they come, by a linked list of two nodes (RM0481 Rev 5, 16.4.13): the status
word's three bytes to the side, where its lead-off bits go into the diagnostics, and the channels
straight into bytes 4–27 of the frame. The processor adds the number, the kind, the frame's number
and the IMU bytes, starts the hardware CRC and the DMA to the USART. On the receiving side a channel
is `v = (int32_t)(b0 << 24 | b1 << 16 | b2 << 8) >> 8`.

## Timing of one cycle

260.4 µs at 3,840 SPS, every line at 19.66 Mbaud, 196.608 MHz ÷ 10: a byte in 0.51 µs, 512 B a
cycle, a frame of 34 B in 17.3 µs. **Four slots of 128 B a line,** one a unit, the same on every
line of the body. A unit sends its frame of data at its slot's start; the rest of the slot, 94 B,
is its own, for the diagnostics and an answer.

| µs from DRDY | four slots |
|---|---|
| 0 | DRDY, every ADS1299 at once |
| 0–11.0 | each unit reads its ADS1299 (216 bits on SPI at 19.66 MHz); on the line at most the last slot's tail |
| slot 1 | 11.0–76.1, the frame 11.0–28.3 |
| slot 2 | 76.1–141.2, the frame 76.1–93.4 |
| slot 3 | 141.2–206.3, the frame 141.2–158.5 |
| slot 4 | 206.3–271.4, the frame 206.3–223.6 |
| free in a slot after the frame of data | 47.8 µs, 94 B |
| the line busy on an arm's, four units | 27 %, 53 % in the diagnostics' cycle |

- **Four units a line:** an arm's line is full, its shoulder, upper arm, forearm and glove; a
  leg's has a slot free, the trunk's and the head's more. One rule for every line, one firmware.
- **The last slot's end** falls 11 µs into the next cycle, while the units read their ADS1299,
  which needs no line.
- **The guard,** the last 1 µs of every slot, is twenty times what the drivers need: a THVD1452
  lets go of the pair within 25 ns of DE falling and drives it within 50 ns of DE rising, with its
  receiver on (SLLSEY3E, 7.8), and the slots are placed by the suit clock to within the ~0.2 µs
  the START spread allows.
- **The time to build a frame** after the read is not counted; it is measured on the first board.
- **At 1,920 SPS,** the setting to try (CONFIG1 0xD3, see
  [Rubaška](../rubaska/SOFTWARE.md#the-ads1299s-settings)), the cycle is 520.8 µs: the same slots,
  the cycle's second half quiet, the IMU step and the envelope, counted in 32 samples, at 60 Hz.

The ADS1299 takes SCLK at most at 20 MHz (a 50 ns period), and the STM32H523's SPI kernel clock
at most 100 MHz in VOS1 (DS14540, table 20), so the line's 196.608 MHz cannot feed it. PLL1's
second output does: the suit clock straight in, × 40 = a 393.216 MHz VCO, which gives the SPI
78.6432 MHz ÷ 5; the SPI divides that by 4 to 19.66 MHz (50.9 ns). The input and the VCO lie in
the PLL's wide range of 2–16 MHz and 128–560 MHz (DS14540, table 46); the read takes 11.0 µs.

### Line 8

**Line 8 runs by its slots always,** measuring or not, since the sound runs always: two slots of
130.2 µs, 256 B each, Nataša's and Míša's. Each counts the cycle on a timer of its own from the
suit clock, so they run round by themselves and never part. **Mamka's *heartbeat* is the
correction:** on line 8 she sends it once a second in every mode, at a cycle's start, with the
cycle's number; after power-on a unit finds the cycle's start by it and stays silent until then,
and later it only confirms that nothing slipped. Either unit may be missing: one alone runs its
slot by itself. What goes in the slots is under [Nataša](../natasa/SOFTWARE.md#line-8).

## The commands

Mamka's pair down is hers alone: she sends a frame whenever she has one, for the whole system, a
line, one unit or one chip, in the service mode and the active mode alike. **The lines with
modules share a sender a processor:** processor 1's one TX drives lines 1–4's drivers at once,
processor 2's lines 5–7's, 512 B a cycle, 15 frames of 34 B, and every unit takes what its number
names and drops the rest. Little goes down: the heartbeat once a second, commands and the settings
at the start; firmware goes to all at once anyway. Line 8 has a sender of its own.

A question goes down in 8 B; the answer comes in 8 B, a result, or in 34 B, registers' values,
with the command's number back. One register is written in 8 B, more in 34 B.

| B | the frame of 8 B | the frame of 34 B with a command |
|---|---|---|
| 0 | the unit's number, 0 every unit | the same |
| 1 | the kind | the same |
| 2 | the command's number | 2–3: the command's number, the high byte zero |
| 3–5 / 4–31 | by the kind | 28 B by the kind |
| 6–7 / 32–33 | CRC-16 | CRC-16 |

**The kinds,** bit 7 set in an answer:

| code | kind | B | way | by the kind |
|---|---|---|---|---|
| 0x01 | *discover* | 8 | down | zeros |
| 0x81 | *discover*'s answer | 34 | up | the UID, 12 B (RM0481, 67.1), then zeros |
| 0x02 | *assign* | 34 | down | the UID, 12 B, and the new number |
| 0x82 | *assign*'s answer | 8 | up | the result |
| 0x03 | read | 8 | down | the chip, the first register, the count, 25 at most |
| 0x83 | its answer | 34 | up | the chip, the register, the count and 25 B of values |
| 0x04 | write one register | 8 | down | the chip, the register, the value |
| 0x06 | write several registers | 34 | down | the chip, the first register, the count and 25 B of values |
| 0x84, 0x86 | the answer to a write | 8 | up | the result |
| 0x05 | direct write into a chip, for debugging | 34 | down | the chip, the count and 26 B at most |
| 0x10 | *get ready*; its answer 0x90 | 8 | down, up | zeros; the answer the result |
| 0x11 | *start* | 8 | down | the first cycle's number, 2 B |
| 0x12 | *stop* | 8 | down | the cycle from which the data no longer count, 2 B |
| 0x13 | repeat a sound packet | 8 | up, down | the packet's number, 2 B |
| 0x14 | *heartbeat* | 8 | down | Mamka's cycle's number, 2 B |
| 0x15 | *Mamka?*, after 3 s without a heartbeat | 8 | up | zeros |
| 0x16 | the bus test | 34 | both | a pattern of 28 B |
| 0x20 | data | 34 | up | see [A unit's data](#a-units-data) |
| 0x21 | diagnostics | 34 | up | see [The diagnostics](#the-diagnostics) |
| 0x22 | the sound for the headphones, 1 ms | 198 | down | see [Nataša](../natasa/SOFTWARE.md#sound-across-the-suit) |
| 0x23 | the microphones, 1 ms | 198 | up | the same |
| 0x30 | a block of firmware | 519 | down | see [Updating firmware](#updating-firmware) |

- **The result** in the answers: 0 done; otherwise an error's code, 1 the chip did not answer, 2
  no such chip, 3 no such register, 4 the unit refuses for its state. *Get ready*'s answer: 0
  ready, 1 the ADS1299 does not answer, 2 an IMU missing against its table, 3 settings missing.
- **The chips:** 0x00 the unit itself, 0x01 the ADS1299, 0x02 the sound, 0x03 the motors, 0x04
  the BMS (Mamka's processor 2), 0x05 Míša's sphere, 0x0F every IMU, 0x10… one IMU. An IMU's
  bank is switched by writing its own REG_BANK_SEL (0x76, DS-000347 rev. 1.2, 14.59) like any
  register.
- **Each unit takes only what it has:** a write to the ADS1299 for the whole system reaches the
  16 modules and the gloves skip it; a write to every IMU reaches the modules' and the gloves'. The
  ADS1299's registers 01h–17h, 23 B, go in one frame; the unit skips LOFF_STATP and LOFF_STATN
  (12h and 13h, read only, SBAS499C, 9.6), since what writing them does is not given. Starting one
  unit alone is safe, the ADS1299s running on idle.
- **Direct write:** up to 26 B that the unit passes to the chip as they are, the ADS1299's own
  commands (WREG, RREG, SDATAC) or an ICM's register and data. It goes past the unit's knowledge
  of the chip, so it is a tool for debugging, with no answer: in RDATAC the ADS1299 takes another
  command only after SDATAC (SBAS499C, 9.5.3.7).
- **The ADS1299 while running:** the commands go on the pair down, Mamka's alone, and take
  nothing from the slots up; between two reads the unit sends SDATAC, WREG and RDATAC again.
  Conversions go on and START stays high. The bytes of a multi-byte command must be 4 CLK periods
  apart (~2.0 µs), so writing one register takes an estimated ~16 µs.
- **Kept free for what comes later:** the kinds 0x07–0x0F, 0x17–0x1F, 0x24–0x2F and 0x31–0x7F,
  the chips 0x06–0x0E. A new sensor takes a chip's number and a map of registers and needs no
  kind of its own; its slow data are read, its steady data come in the free part of its unit's
  slot.

**The answer to a write is its result,** no registers read back: whoever wants to check reads
them (0x03). In the active mode the answer goes in the free part of the unit's slot, a cycle later
at the earliest; with the diagnostics it still fits, 94 B being free after the frame of data. In
the service mode it follows the question at once. To a write for the whole system each unit
answers in its own slot; in the service mode, with no slots, a write to more than one unit gets no
answer, and Mamka asks each unit by itself. What a unit sends by itself, as Míša's sphere, is an
answer to a read sent unasked.

## The registers

**The unit itself is one more chip,** 0x00, one space of registers:

| registers | what |
|---|---|
| 0x00–0x3F | the unit's settings, held in RAM and sent at every start: 0x00 the bias, 0 off and 1 on, whether this unit drives the bias electrode through its TMUX1101 on PA1; 0x01 the IMU mode, 0 ten samples at 1,200 Hz summed into the step, the main mode, 1 the chip's own 120 Hz, the fallback; on Mamka's processors their state and their commands instead |
| 0x40–0x7F | the unit's table, read only (below) |
| 0x80–0xBF | the firmware's update (see [Updating firmware](#updating-firmware)) |
| 0xC0–0xFF | Mamka's events, the GPS and the UTC label, on her processors only (see [Mamka](../mamka/SOFTWARE.md#mamkas-own-registers)) |

Everything else is a chip's own register, the gain, the lead-off, the channels on, MISC1, or no
setting at all: the timings, the heartbeat's 1, 3 and 1 s and the sleep after ~10 s, are fixed in
the firmware, the number is given by *assign*, the IMU bytes' places by the frame's number.
Nataša's and Míša's maps are on their pages; Mamka's two processors, 0xF1 and 0xF2, are units of
this kind too (see [Mamka](../mamka/SOFTWARE.md#mamkas-own-registers)).

**The unit's table,** from register 0x40 of chip 0x00, read only, read 25 B at a time: its layout
is fixed in the firmware, and the unit fills it in RAM at every start.

| B | field |
|---|---|
| 0 | the table's length, so Mamka knows how many reads it takes |
| 1 | the unit's kind: 1 EMG, 2 IMU (the glove), 3 Nataša, 4 Míša, 5 a Bratiška |
| 2 | the firmware's kind: 1 a module's Staršaja, 2 the glove's Staršaja, 3 a Bratiška, 4 Nataša, 5 Míša, 6 Mamka's processor 1, 7 her processor 2 |
| 3–4 | the firmware's version |
| 5–16 | the UID, 12 B |
| 17 | how many chips follow |
| 18… | 2 B a chip: its number (0x01, 0x10…) and its part: 1 the ADS1299, 2 the ICM-42688-P, 3 the ICM-45686, 4 the sound (TAD5142 and ICS-43434), 5 the motors (DRV2603), 6 Míša's sphere |

- **Two kinds of sensing unit:** *EMG*, an ADS1299 and IMUs; *IMU*, IMUs alone, as the glove. A
  chip's part says which map of registers applies, so another kind of IMU may sit at 0x1n with
  nothing else changed.
- **The chips' order:** the IMUs from 0x10, a module's 0x10–0x13, two on I3C1 and two on I3C2;
  the glove's 20 from 0x10 to 0x23, by Bratiška.
- A module's table is 28 B, two reads; the glove's 58 B, three.
- **Not in the table:** where the unit sits (Baťa holds it by the UID), its number (given by
  *assign*), its settings (sent at every start). **A unit keeps nothing in flash but its
  firmware:** the map and every setting live on Baťa, keyed by the UID.

## The units behind a unit

**The glove,** Vešč, is a unit of its own on its arm's line, in the fourth slot, with its own
drivers and number, part of every suit with arms: its Staršaja on the sleeve before the wrist,
and five Bratiški, one a finger, four IMUs each, on her five wires (see
[Rubaška](../rubaska/HARDWARE.md#the-glove)). **The Bratiški are units behind her:** she passes
a frame for them on its own wire unchanged and sends their answers up in the free part of her own
slot; they get their own numbers at the start, *discover* passed on through her. Their IMU steps
go in her frame of data, not in frames of their own.

## Bring-up

Before anything is measured Mamka learns who is on each line and gives each unit its number.
Until the first *start* there are no slots on lines 1–7, and a unit without a number stays silent
but for *discover*, so it cannot talk into anyone else's answer. All of it is question and
answer, a question of 8 B and its answer of 34 B in ~22 µs.

- **The clock from the start.** Each processor raises her lines' clock drivers' DE at her start
  and lowers it only while her lines are off or asleep (see
  [hardware](HARDWARE.md#clock-a-one-way-rs-485-channel)). Every unit takes
  the clock straight after its reset and only then sets its peripherals (see
  [the clock tree](#the-clock-tree)). A unit whose pair is quiet sees its receiver hold the clock
  input high (the receiver's fail-safe, SLLSEY3E) and waits, silent. Mamka runs from her
  oscillator.
- ***Discover*** (0x01) to every unit (0): the body's lines share one sender, and a unit with no
  number knows no line yet. Every unit with no number answers once, 0x81 with its whole UID, on
  its own line's return pair, so the receiver it comes in on tells Mamka the line. It waits first
  by CRC-16/CCITT-FALSE over its 96-bit UID × 10 µs, 0–655 ms, and listens before it talks: its
  echo hears the return pair, so an edge while it waits starts the wait again, and a collision
  shows as a bad CRC, after which it waits anew, by CRC-16 over the UID and the attempt's number.
  700 ms of silence closes the round; Mamka asks once more, and a second silence of 700 ms says
  the lines are complete, all at once, in a few seconds. A unit that holds a number stays silent.
- ***Assign*** (0x02), the UID and the new number: a unit with no number knows no line, so the
  UID alone decides, and the unit with it takes the number and answers from it. The whole UID
  cannot clash, where a tag of 16 bits could.
- **The table** is then read from each unit, from register 0x40 of its chip 0x00, two or three
  reads.
- **Line 8's units** have their numbers fixed, 0x81 and 0x82, so they stay silent at *discover*,
  and Mamka reads their tables by number; the Bratiški answer through their Staršaja.
- **Where a unit sits** no unit can tell: which band a module is on. For that and the map Baťa
  has an application (see [Baťa](../bata/SOFTWARE.md#the-map)). A module replaced shows a new
  UID, and the application asks where it sits.
- **Asleep:** a unit in the service mode sleeps after ~10 s of silence, in Stop mode, its ADS1299
  in standby by the STANDBY command (04h, 5.1 mW with the internal reference; WAKEUP, 02h, on
  waking; SBAS499C, 9.5.3.2–3), its IMUs asleep. A byte on its line wakes it, every USART and UART
  of the STM32H5 waking from Stop (RM0481 Rev 5, table 625): Mamka raises the clock's DE again,
  sends a byte and waits ~10 ms.
  It wakes on its HSI and takes the clock again as after a reset (see
  [the clock tree](#the-clock-tree)); how the byte at the line's rate wakes it is open (see
  [Open questions](#open-questions)). A suit left hanging long is switched off by
  [Budilnik](../mamka/HARDWARE.md#budilnik).
- **A unit reset while the suit runs,** or one plugged in, forgets its number and joins at the
  next bring-up: it takes the clock, stays silent with no number, and Mamka sees its slot empty.
- **Each processor brings up her own lines,** processor 1 lines 1–4 and processor 2 lines 5–8,
  once their chain of converters shows its last PGOOD: processor 2 switches both chains and
  reads both, processor 1 reads the limbs' PGOOD on a wire of its own (see
  [Mamka](../mamka/SOFTWARE.md#the-wires-between-the-processors)).
- **Again:** Baťa asks processor 2 for the lines' power off and on (her power command 3); the
  PGOODs fall and rise, and each processor brings up her lines again by herself.

## Before the first start

Before the first *start* there is no DRDY, so everything on lines 1–7 goes as question and
answer, each processor's lines' answers coming in side by side.

**The bus test** (0x16) runs first, and may be left running for minutes while the wearer moves,
bends and jumps, a tool for the prototype, for trying cables and connectors. Its frame of 34 B
carries the test's running number in bytes 2–3 and 28 B of PRBS-9 in bytes 4–31: frame n of a test
carries the sequence's bytes 28n to 28n + 27, running on from frame to frame and repeating every
511 B. Down, the unit compares the bytes with the sequence and counts the errors; up, it sends the
same back and Mamka counts. The result per unit and direction Mamka reads from the unit's
counters. The PRBS is PRBS-9 of ITU-T O.150, x⁹ + x⁵ + 1, as Osmocom's libosmocore implements it
(the Recommendation's own text not read). While measuring, the diagnostics watch the cables, so no
test runs then.

***Get ready*** (0x10) goes to each unit by itself, well under a millisecond for the whole body.
The unit sets its ADS1299, holds START low, turns off its other interrupts and waits only for
*start*; it answers 0x90 with its result. With no *start* within 1 s it gives up waiting, and
Mamka calls *get ready* again.

### Starting a measurement

Every ADS1299 in the suit should start converting at the same moment:

1. Mamka sends each unit its settings, and the unit writes them into the ADS1299 and the IMUs,
   even if the chips should still remember them; the ADS1299 is reset and prepared with its START
   pin held low. The rate, 3,840 SPS or the 1,920 to try, is set here only: a write of CONFIG1
   resets the ADS1299's digital filter (SBAS499C, 9.4.2), which while running would break the
   sync.
2. *Get ready* to each unit, as above.
3. **The first *start*** (0x11) goes down lines 1–4 on processor 1's one sender and down lines
   5–7 on processor 2's at the same moment: processor 1 raises the START wire to processor 2,
   and both send *start* a fixed count of suit-clock ticks after its edge (see
   [Mamka](../mamka/SOFTWARE.md#the-wires-between-the-processors)). Each unit takes the START pin
   of its ADS1299 high after a fixed number of suit-clock ticks (below) and leaves it there.

**START stays high for the whole active mode.** According to the datasheet (sections 9.4.1 and
9.4.5), conversions begin once START has been high for at least 2 CLK periods and go on until
START goes low; a short pulse would stop them after the first conversion. The delay from START to
the first DRDY is fixed for a given data rate: 2,057 CLK periods at the 4 kSPS setting, 3,840 SPS
here, 1.05 ms; 4,105 at the 2 kSPS setting, 2.09 ms (table 7).

The spread between units, an estimate:

| cause | estimate |
|---|---|
| a unit's reaction | a few cycles, 20.3 ns a cycle at 49.152 MHz |
| lines 5–7 from the other processor | one edge on the START wire, captured by a timer, a few of Mamka's cycles of 5.1 ns |
| difference between the drivers and the receivers | 20–30 ns |
| difference in cable length | under 10 ns |
| path from the processor pin to the ADS pin | the same on every unit, same boards |
| **total** | **~100 ns** |

The ADS1299 reads START on its own clock (1.96608 MHz, a 509 ns period). If the dividers that
make it on the units are not in the same phase, conversions can drift apart by up to one ADS
clock period, about 0.5 µs. That is still 0.2% of the sample period (260 µs); for a 1 kHz signal,
a phase error of ~0.2°.

**Aligning to the ADS clock edge.** Every line takes its clock from one source through the same
buffers (three SN74LVC126A on Mamka, straight from the oscillator), so the suit clock is the same
on every unit apart from the drivers' and the cable's spread. The ADS clock's dividers, though,
come up in a different phase on each unit, so they are cleared at the start: on the start command
the unit clears its divider and starts a timer counting suit-clock ticks. After a fixed number of
ticks the timer takes START high in the middle of the ADS clock's low half. The datasheet does
not say which CLK edge reads START, nor give any setup time. In the middle of the low half START
is about a quarter period (~130 ns) from both edges, so every ADS reads it on the same edge,
whichever it is. What remains is the spread in the command's arrival rounded to suit-clock
ticks, on the order of 100–200 ns. The timer is only needed at the start and is free the rest of
the time.

**Later,** *stop* (0x12) and *start* leave START alone: they only mark, by the cycle's number
they carry, from which cycle the data count.

## Errors

Every frame has a CRC, and every unit's echo watches its own sending. **The data have no
repeat:** a frame that fails its CRC at Mamka's input is not passed on, its place on the SPI
stays zeros, and the cycle has a gap there; Baťa's filters and the model take a gap, and the
frames' numbers show it. The diagnostics count what goes wrong: a sensor's error, a frame from
Mamka with a bad CRC, an electrode off, once every 32 cycles. **The sound alone is repeated**
(0x13), its lost packet being 1 ms of silence (see
[Nataša](../natasa/SOFTWARE.md#sound-across-the-suit)).

## Into Baťa

**Three SPIs, each processor on her own:** Mamka's processor 1 hands Baťa the limbs, lines 1–4,
over one, the ROCK 5T's SPI1_M1; her processor 2 the head and the trunk, lines 5–7, line 8 and the
household over two, SPI0_M2 and SPI3_M0, and the sound over the I2S (see
[Mamka](../mamka/SOFTWARE.md)). Baťa is the master of all three, Mamka the slave, and each
processor's "data ready" stays high while she has anything to send: a cycle while measuring, an
answer in the service mode.

- **The rates:** the RK3588's five SPIs take an even divider of the same 200, 150 or 24 MHz
  sources (`clk-rk3588.c`, `CLK_SPI0` to `CLK_SPI4`). SPI1_M1 goes straight to the header from a
  bank at 3.3 V and runs at 37.5 MHz, 150 MHz ÷ 4, the fastest under the STM32H562's 43 MHz as a
  slave (DS14258, table 115): ~4.7 MB/s each way. SPI0_M2 and SPI3_M0 come from banks at 1.8 V
  through Union's UM3204 translators on the ROCK's board (its schematic V1.2: U90080, U90081,
  U90084), which pass 24 Mbps at most and a pulse of 41 ns at least (UM3204 Rev.16, timing
  requirements): 11.1 MHz, 200 MHz ÷ 18, a half period of 45 ns, ~1.39 MB/s each, ~2.8 MB/s the
  pair.
- **Processor 2's transfer is striped** over her two SPIs in words of 4 B: bytes 0–3 on SPI0_M2,
  4–7 on SPI3_M0 and so on, so both carry the same share and finish together; processor 1's goes
  whole on SPI1.

**The frames go to Baťa as they came,** their CRC kept, which guards the SPI too; a frame that
failed its CRC on the line is not passed on. While measuring, a transfer of one length every
cycle, both ways at once, **in places of 34 B,** with no header:

- **The data frames in the table's order,** by line and on each line by slot, so Baťa knows whose
  is where; an empty place is zeros, the kind 0 being none.
- **Four places more** for the diagnostics, the answers and Mamka's own frames, the BMS, the GPS,
  the power; one cycle's diagnostics are let out of a queue over the next cycles. A frame of 8 B
  takes a place with zeros after it, its kind giving its length.
- **Processor 1:** 14 places of data and the four, 18 × 34 = 612 B a cycle, 131 µs at 37.5 MHz,
  50 % of SPI1; her 14 diagnostics go out in four cycles.
- **Processor 2:** six places of data, the head, the chest, the two of the back, Nataša and Míša,
  and the four, 340 B a cycle, 85 words of 4 B and one of zeros, so 172 B on each SPI, 124 µs
  at 11.1 MHz, 48 %. On her SPIs also go the events she makes of Nataša's frames and Míša's
  sphere as it came; the sound both ways goes on the I2S.
- **Down,** in the same places: the frames for her lines and for herself, 0xF1 or 0xF2, which she
  keeps instead of sending them on. A frame for the whole system Baťa sends on every SPI, the first
  *start* too, which each processor holds until the moment the START wire gives (see
  [Mamka](../mamka/SOFTWARE.md#the-wires-between-the-processors)). The SPIs have no addresses, the
  number being in the frame.
- **When Baťa is late** the cycles wait in a ring on each processor (see
  [Mamka](../mamka/SOFTWARE.md#memory)), "data ready" stays up, and a cycle lost shows as a jump
  in the frames' numbers.
- **In the service mode** Baťa sets a transfer's length by what he sends down, in places of 34 B,
  a firmware frame in 16; Mamka's answers fill the places up, and she keeps "data ready" up while
  more wait.
- **A sample reaches Baťa** ~0.36 ms after DRDY: the last frame in at 224 µs, then the transfer.
  Baťa puts both processors' frames of one cycle together by the frames' number.

## Updating firmware

Firmware goes in the service mode only, broadcast to every unit of a kind on all lines at once,
overnight, the suit on a hanger, by a script on Baťa. One image for each kind of unit; the
firmware is split into parts only in its source, the communication one library for every kind.
The way is made so that no unit is ever lost and a bad version returns to the old by itself.

**Two banks.** Every STM32H5 here has its flash in two banks and reads one while writing the
other (DS14540 Rev 3 and DS14258 Rev 6, 3.4; DS14053 Rev 4 for the STM32H503), so a failed update
never leaves a unit without a firmware. An image is at most one bank: 128 KB on a module's
STM32H523CC (two equal banks of its 256 KB, RM0481 Rev 5, table 53), 64 KB on a Bratiška's
STM32H503KB (two banks of eight 8 KB pages, DS14053), 256 KB on Nataša's STM32H523RE and 512 KB
on Mamka's STM32H562VG; the glove's Staršaja by the part chosen for her. The map of the blocks
received holds 256, 128 KB, so a larger image, Nataša's or Mamka's, is open (see
[Open questions](#open-questions)). A bank is erased in
64 ms, 320 ms at most, and 16 B are written in 31 µs, 100 µs at most, so a block of 512 B in
~1 ms, 3.2 ms at most, against the 0.26 ms it takes to come at 19.66 Mbaud: the flash sets the
pace. The program flash takes 10,000 cycles (DS14540 Rev 3, tables 49 and 50).

| register (chip 0x00) | what |
|---|---|
| 0x80 | the command: 1 *begin* (erases the other bank), 2 *check and restart*, 3 *confirm*, 4 *abort* |
| 0x81 | the firmware's kind (see [the unit's table](#the-registers)) |
| 0x82–0x85 | the image's length |
| 0x86–0x87 | the version |
| 0x88 | the state, read only: 0 idle, 1 erasing, 2 receiving, 3 the CRC wrong, 4 on trial, 5 the last update failed |
| 0x90–0xAF | the map of the blocks received, read only, a bit a block |

**The firmware's frame,** 519 B, carries one block: the unit's number, 0 to every unit, the kind
0x30, the kind of unit it is for, the block's number, 512 B of the image, padded by its sender to
a multiple of 16 B for the flash, and the CRC-16. It goes down all the lines of both processors at
once, to every unit of a kind; no unit answers a block.

**The way:**

1. ***Begin:*** Mamka writes every unit (0), chip 0x00: the firmware's kind, the image's length
   and version, and the command 1. The units of that kind erase their other bank and clear their
   map of the blocks received. An explicit *begin*, not "the first block erases the bank": a
   first block lost in the broadcast would leave the bank unerased, and sent again it would erase
   all that came meanwhile.
2. **The blocks,** each with its number and 512 B of the image, written into the other bank and
   marked in the map: 256 blocks for 128 KB, one every 3.2 ms, the flash's longest write,
   ~0.8 s. Smaller images to load would gain nothing.
3. **The missing blocks:** Mamka reads each unit's map (32 B, two reads) and sends again only
   what someone lacks.
4. ***Check and restart:*** the unit computes the CRC-32 over the image and compares it with the
   CRC-32 at the image's end, and checks that the image's first sector is byte for byte its own
   (below). If both hold it writes a note into its backup registers, programs the option bit
   SWAP_BANK (RM0481, 7.3.11, the sequence in seven steps) and restarts; if not it stays on the
   old and shows the state 3.
5. **On trial:** the new version runs on trial, and **Mamka confirms** it by writing the command
   3 once the unit reports its new version, so a script on Baťa can test it first and a version
   that talks but measures wrongly is never confirmed. Unconfirmed within **30 s**, or reset
   before it got its confirm, the unit goes back to the old one by itself, and its state at 0x88
   shows 5, the last update failed. *Abort* (4) forgets the update.

- **The CRC-32** is the one zlib computes: polynomial 0x04C11DB7, reflected input and output,
  initial value and final XOR 0xFFFFFFFF. The CRC unit does it with its default polynomial and
  the reversal of its input and output set (RM0481, 19.4.3 and 19.5.3).
- **The note** in the backup registers, which no system reset clears (RM0481, 52.4.10): a check
  pattern, a phase and a count of starts. *Check and restart* writes the phase *trying* with the
  count 0 before the swap. Every firmware, old or new, reads the note first thing after a start,
  and only when the pattern matches, since the registers can come up with random contents after
  a brownout (ES0565 Rev 8, 2.2.20): in *trying* it adds one to the count; a count of 1 is the
  first start of the new image, which runs with a 30 s timer waiting for *confirm*; a count of 2
  or more is a start after a reset nobody asked for, so the firmware writes the phase *failed*,
  swaps the banks back and resets, and the old image comes up and shows the failure. The timer
  running out does the same. The independent watchdog starts by hardware, the option bit IWDG_SW
  cleared (RM0481, 7.4.4; RM0492, 7.4.5), so a new image that hangs before it feeds the watchdog
  still ends in a reset and the swap back; the option bytes are not swapped with the banks.
- **The zero stage.** MCUboot, the usual bootloader of this class, keeps the test-and-revert
  decision in a bootloader of its own that no update touches (its design, *Flash map* and *Image
  trailers*). Here the first sector of every image, 8 KB, is that stage: the same bytes in every
  image, built once and linked in at offset 0. It does one thing: reads the note, adds the start,
  swaps back when the count says so, and jumps to the application in the rest of the bank. A unit
  refuses an image whose first sector is not its own, so the stage never changes by an update;
  a new stage, should one ever be needed, goes in over SWD.
- **Through the glove's Staršaja:** she passes the firmware's frames for the Bratiški on their
  wires unchanged, as any frame for them. Mamka's own images are under
  [Mamka](../mamka/SOFTWARE.md#firmware).

## Output

The suit puts out up to 127 values for the whole body, one byte each. A joint has one, two or
three axes, each with its own range from a table: 0 and 255 are the ends of that joint's range,
for example 0–140° for the knee.

- One byte is plenty. Over 120° a step is 0.47° and the rounding error 0.14° RMS; over 180° the
  step is 0.7°. Published work typically puts joint angles from IMUs a few degrees off, and EMG
  adds its own error, so more bits would only carry noise.
- More bits would not make the model heavier either: its cost comes from its size, not from the
  precision of its output. The Hailo, where one is fitted, computes in integers and can hand its
  output straight out as `UINT8` (HailoRT also offers `UINT16` and `FLOAT32`).
- The axes follow anatomy: flexion and extension, abduction and adduction, rotation.
- Three angles in a row always have a pose where the first and third axes line up and both
  describe the same movement (a singularity, gimbal lock). For the shoulder in the usual ISB
  convention it is the arm hanging at the side. Joints with one or two axes and a limited range
  keep it outside their range. The shoulder and the hip cannot, so they go out as a swing and a
  twist, still 3 B: two numbers tilt the bone from its rest direction in one go, forward and
  out to the side, and the third turns it about its own axis. Unreal's physics constraints
  limit a joint the same way, as Swing 1, Swing 2 and Twist.
- The swing has one pose it cannot describe: the bone pointing straight away from rest, 180°
  off. Rest is chosen to put that pose out of reach. For the arm it is raised 45° in the plane
  halfway between forward and sideways, which leaves the bad pose up behind the head over the
  other shoulder; for the leg it is down and a little forward, which leaves it up behind the
  back. Over ±150° a step of the swing is 1.2°, and over ±90° a step of the twist 0.7°.
- **Contact points:** 32 bits, 4 B in every snapshot, for where the body rests on something: a
  wall, the floor, a chair, the hands and feet in a push-up. Each bit is one area of the body,
  and a pose is only a combination of them: sitting on the floor is the buttocks, the heels and
  the balls of the feet; a chair with a back and arms adds the backs of the thighs, the back and
  the forearms. The model sees it in the EMG and the IMUs: a limb that neither hangs nor is held
  by its muscles must rest on something, on the side gravity pulls towards. The same rule marks
  the contacts in the recordings, so nobody labels them by hand. A game engine keeps a foot on
  the ground planted instead of sliding, and the steps give the path walked. Which area each bit
  stands for is set by a table, like the joints; these are the basic 32, and more can come in
  time.

  | part of the body | areas | bits |
  |---|---|---|
  | the head | the front, the back, the left, the right | 4 |
  | the shoulders | each from the front, the side and the back | 6 |
  | the trunk | the chest, the belly, the upper back, the lower back | 4 |
  | the trunk's sides | left, right | 2 |
  | the hips, from the side | left, right | 2 |
  | the buttocks | left, right | 2 |
  | the backs of the thighs | left, right | 2 |
  | the elbows and forearms | left, right | 2 |
  | the palms | left, right | 2 |
  | the knees and shins | left, right | 2 |
  | the heels | left, right | 2 |
  | the balls of the feet and the toes | left, right | 2 |
  | **all** | | **32** |

- At 120 snapshots a second, the joints' 127 B and the contacts' 4 B make ~16 kB/s.
- Neural networks learn rotations better in a six-number form than as angles or quaternions
  (Zhou et al., *On the Continuity of Rotation Representations in Neural Networks*, CVPR 2019).
  The model can put that out and the output core converts it at the end.

### CI-BTP

**Out of the suit: CI-BTP,** the Big Crazy Ivan Transport Protocol, a transport and nothing more.
Baťa sends over UDP frames in three classes, **128, 256 or 512 B**, and **32, 64, 128 or 256
frames a second**; the client picks both. The frame of 512 B in blocks of 8 B comes from the
owner's design of March 2026, the classes and the header from 0.4; CI-BTP keeps packet types of
its own, apart from the frames inside the suit.

| B | the frame |
|---|---|
| 0–3 | the sample number, u32: the frames' 16-bit number widened by Mamka and Baťa, so a recording carries its time in samples from the start, 310 hours before it wraps at 3,840 SPS |
| 4 | bits 7–6 the class: 0 128 B, 1 256 B, 2 512 B, 3 free; bits 5–0 the kind: 0 alive and empty, 1 packets |
| 5 | the count of packets |
| 6… | the packets, each from an 8 B boundary counted from byte 6: 120, 248 or 504 B |
| last 2 | CRC-16/CCITT-FALSE over all before it, the same CRC as on the lines |

**Packets** fill the data: a header of 4 B and its data, the next packet on the next 8 B
boundary: `type` (u8), `sub` (u8, by type), `len` (u16, the data's length in bytes). **A packet
never splits:** the class must hold the largest packet a client asks for, and Baťa says the
class in his answer to *subscribe*. The snapshot is a packet like any other, sent with each step,
120 Hz at most; whatever else is due in that moment, an event, a few bytes of ECG, the sphere, is
packed in behind it in the same frame. The frames beyond the snapshots carry the meta packets and
bulk. Every value has a fixed place in its packet, set by a table, so a converter into another
format is a table too. A frame of the kind 0, alive and empty, goes once a second when nothing
else does, so that a listener knows the suit is still there.

| `type` | packet | data | `sub` |
|---|---|---|---|
| 1 | snapshot | the joints' 127 B and the contacts' 4 B | its place in the cycle |
| 2 | meta | one of the eight meta packets below | which of the eight, 1–8 |
| 3 | ECG | the ECG separated from the EMG, **1 B a sample** a channel: the first sample's number (2 B), the count (1 B), the channels (1 B), then the bytes, channel by channel; 480 SPS by default (see [Baťa](../bata/SIGNALS.md#the-ecg-and-the-breath)) | the decimation, 1–32 |
| 4 | sphere | Míša's sphere, 112 B | |
| 5 | event | 8 B: a running count of events (1 B), what (1 B: a button, a BMS alarm, an electrode off, start, stop, a sound Soňa heard, *halted* by [Storož](../bata/SOFTWARE.md#storož) with his reason in *which*), which (1 B), 5 B by kind; the event's time is the frame's sample | |
| 6 | vitals | 8 B once a second: the heart rate (bpm), its variability (RMSSD, ms), the breathing rate, the skin temperature (°C), the ECG's quality and the breath's source, 3 B zeros (see [Baťa](../bata/SIGNALS.md#the-ecg-and-the-breath)) | |
| 7–255 | reserved | | |

**The meta packets,** one in each frame beyond the snapshots, so at 128 frames a second the set
comes once a second. All numbers little-endian; a temperature is an i16 in 0.1 °C, 0x7FFF for
none. The meta packets 3 and 4 want the class of 512 B.

| `sub` | packet | data | B |
|---|---|---|---|
| 1 | the suit, the run and the map | the suit's serial (8 B), the run's number (u32) and its start (u32, Unix time), Baťa's software version (u16), Mamka's two processors' firmware (2 × u16), the snapshot rate's code (u8), the numbers of joint values, contacts and ECG channels in use (3 × u8), the units in the map (u8, up to 20: 18 on lines 1–7, Nataša, Míša), then 6 B a unit: its number, the kind (1 EMG, 2 IMU, 3 Nataša, 4 Míša), the place on the body (from the place list), the IMUs (how many), the firmware's version (u16); then the units present (u32, a bit a unit in the map's order) | ~151 |
| 2 | the bones | the wearer's height (u16, mm) and mass (u16, 0.1 kg), then the lengths in mm (u16 each): the neck, the torso from the shoulders to the hips, the shoulder width, the pelvis width, and left then right the upper arm, the forearm, the hand, the thigh, the shin and the foot | 36 |
| 3 | the joint table, values 0–63 | 4 B a value: the joint (u8, from the joint list), the axis (u8: 1 flexion, 2 abduction, 3 rotation, 4 swing forward, 5 swing out, 6 twist), the range's low and high ends (2 × i8, in 2°); the value's place in the snapshot is its index | 256 |
| 4 | the joint table, values 64–126, and the contacts | 63 values as above, then the 32 contact areas (u8 each, from the area list) | 284 |
| 5 | the electrodes | the EMG units' channels in the map's order, 8 a unit, up to 128 × 1 B: bit 0 P off, bit 1 N off (from the diagnostics), bit 2 the channel is on, bit 3 the channel measures against the reference, bits 4–7 the signal's quality 0–15 as Baťa rates it; then the unit driving the bias as its place in the map (u8), the bias electrodes found connected at start (u32, a bit a unit, from the diagnostics) and the driving unit's bias electrode now (u8, 1 off) | 134 |
| 6 | temperatures and the battery | the units' processors in the map's order (20 × i16), the IMUs in the map's order, unit by unit, as many as meta 1 says (i8, °C, 0x7F none), up to 113: the modules' 64, the gloves' up to 48 and Míša's; Mamka's two processors and Baťa's CPU (3 × i16); the battery as the BMS gives it (23 B, see [Mamka](../mamka/SOFTWARE.md#mamkas-own-registers)); the power's bits (u16) and the fan (u16, rpm) | ~186 |
| 7 | the muscles' fatigue | the muscle group of each of the 128 channels in the map's order (u8 each, 0 none), then the fatigue of groups 1–64 (u8 each, 0 fresh to 255) | 192 |
| 8 | time and place | the UTC label: the suit's sample (u32) at which a UTC second began and that second (u32, Unix time), 0 while no PPS has come; the position (2 × i32, 10⁻⁷ °), the height (i16, m), the fix's quality (u8), the satellites (u8), 4 B zeros | 24 |

The joint list, the area list and the place list, the names behind the numbers, are tables in
Baťa's software and a client's reader, not in the stream.

**Subscribe.** A client that wants the native stream sends Baťa *subscribe* on his port, 8 B, and
repeats it every second; Baťa stops sending five seconds after the last one. He answers with the
same 8 B, saying what he sends: the class raised, when need be, to hold the largest packet asked
for, the snapshot wanting 256 and the meta packets 3 and 4 512.

| B | *subscribe*, and Baťa's answer |
|---|---|
| 0–1 | 0xC1A1, C1 first |
| 2–5 | the packet types as a mask, u32, bit n type n |
| 6 | the rate: 0 32, 1 64, 2 128, 3 256 frames a second |
| 7 | the class: 0 128, 1 256, 2 512 B |

| frames a second | snapshots | the rest | the whole set of meta packets every |
|---|---|---|---|
| 256 | 120 Hz | 136: meta packets and bulk, the trunk's 24 channels of ECG unprocessed at 960 SPS, say | 1 s |
| 128 | 120 Hz | 8: meta packets | 1 s |
| 64 | 60 Hz | 4 | 2 s |
| 32 | 30 Hz | 2 | 4 s |

- **The flow** is at most 256 × 512 B = 128 kB/s, which Wi-Fi carries with room; the full set of
  128 frames of 512 B is 64 kB/s.
- **The snapshots are the suit's own:** the IMUs give a step every 32 ADS samples, so every
  snapshot at 120 Hz is a measured one, 60 Hz takes every other and 30 Hz every fourth; at the
  1,920 SPS to try the steps come at 60 Hz. UDP needs no common clock with the suit, and every
  snapshot carries its number.
- **Ties to time.** The frame's sample is the suit's clock, so the snapshot, the ECG and an event
  in one frame share one time; the meta packets carry the UTC label for it. A lost frame shows as
  a jump in the sample; a lost event would not, so the event packet counts its events.
- **The ECG at one byte.** Cheap ECG recorders resolve about as much, and a doctor reads it. What
  matters is the sample number: every ADS1299 in the suit samples in the same instant on the same
  clock, so the ECG bytes of the trunk's electrodes line up to the sample, and a picture of how
  the current passes through the chest can be put together from them later.
- **Recordings** are made only when asked, and then perhaps only parts: the EMG of a few
  channels, the IMUs, the snapshots. Nothing is compressed and no format of our own is made:
  Perevodčica writes them like any other output, into a file, in the simplest format someone
  already uses, **BDF** for the signals, 24 bits a sample as the ADS1299 gives them and a rate a
  channel, which EDFbrowser, MNE and EEGLAB read, and CSV for small parts.
- **Converters run on Baťa,** not on the computer that listens: **Perevodčica**, the interpreter,
  is the set of programs on Baťa, Live Link, VMC over OSC, LSL, HID and the rest, that read the
  native stream and send out the format the other side knows (see
  [Baťa](../bata/SOFTWARE.md#output-modes)).
- **Formats a converter can feed:** Unreal Engine's Live Link; VMC over OSC for Unity, VRChat and
  VTubing; SteamVR trackers; OSC or MIDI for music; LSL with XDF for research; BDF or EDF+ for
  the EMG and the ECG; BVH, FBX or glTF for animation; C3D and OpenSim for biomechanics; ROS 2
  for robots; and USB HID for anything with a USB port.

## The GPDMA

Every processor on the suit clock, the STM32H523s and Mamka's two STM32H562s, has two GPDMAs
of eight channels, and any request goes to any channel by REQSEL in GPDMA_CxTR2
(RM0481 Rev 5, 16.3.4, table 142). The channels differ (table 140): 0–3 have a FIFO of 8 B and are
meant for a peripheral and SRAM, 4–5 one of 32 B, 6–7 one of 32 B with 2D addressing. Each
processor's table is on its own page ([the module and the glove](../rubaska/SOFTWARE.md#dma),
[Mamka](../mamka/SOFTWARE.md#dma), [Nataša](../natasa/SOFTWARE.md#dma),
[Míša](../misa/SOFTWARE.md#dma)); they share these rules:

- **A fast link splits:** a line's or an SPI's receiving on GPDMA1, its sending on GPDMA2, so the
  two directions have a controller and its master ports each. The slow ones fill what is left.
- **The peripherals on channels 0–3,** the next ones on 4–5; 6 and 7 stay free everywhere, for a
  memory copy should one be needed.
- **Priority,** GPDMA_CxCR.PRIO (16.4.11): 3, the time-sensitive class with a fixed precedence
  over the rest, for the lines, the ADS1299's read and the SPIs to Baťa; 2 for the sound and the
  glove's wires; 1 for the IMUs and Míša's radar; 0 for settings. The slow UARTs, the BMS's, the
  GPS's and the one between Mamka's processors, take no channel: their FIFO of 8 B and an
  interrupt are enough.
- **Receiving is circular:** a linked list whose last node points back to its first (16.4.13),
  so a channel runs from the start on and the core reads behind it. **Sending** is one block a
  frame or a message, made ready before it is due.
- **The I3C** takes two channels a bus with two IMUs: its control words, which its C-FIFO of two
  words cannot hold for a frame of two reads, and its RX-FIFO of 8 B, which a read of 2 × 12 B
  overfills (55.3.4, table 611). The two register addresses go into its TX-FIFO beforehand, by
  the core. With one IMU on the bus, two control words fit the C-FIFO and the RX alone is DMA.
- **The CRC unit** is fed by the core, its data register taking words and bytes alike: for a
  frame of 34 B the 32 B before its CRC as eight words, for a frame of 8 B the six as a word and
  two bytes.
- **Counted per processor,** none takes more than 12 of the 16 channels: Mamka's processor 2,
  her four lines receiving, their two senders, two SPIs both ways and the SAI's two.

## The clock tree

Every processor of the suit but a Bratiška runs from the suit clock, 9.8304 MHz, as a digital clock
into the HSE in bypass, and all set their clocks the same way (RM0481 Rev 5, 11.8; DS14540 Rev 3 and
DS14258 Rev 6 for the limits). **The units' cores run at 49.152 MHz,** a quarter of Mamka's, their
lines' USARTs on a PLL of their own at 196.608 MHz: there is no constraint between a USART's bus
clock and its kernel clock (RM0481 Rev 5, 56.5.3), a USART takes pclk, PLL2 Q or PLL3 Q (RCC_CCIPR1,
11.8.40), and its kernel clock of 157–200 MHz needs VOS1 (DS14540 Rev 3, table 20). **Míša is set as
Mamka for now,** at 196.608 MHz, his line on the APB clock: where the table says "on Mamka" it holds
for him too. Each processor's own outputs and dividers are on its page ([the module and the
glove](../rubaska/SOFTWARE.md#clocks), [Mamka](../mamka/SOFTWARE.md#clocks),
[Nataša](../natasa/SOFTWARE.md#clocks), [Míša](../misa/SOFTWARE.md#clocks)).

| what | setting | why |
|---|---|---|
| the HSE | HSEON, HSEBYP and HSEEXT = 1: a digital clock in bypass (RCC_CR, 11.8.1) | the suit clock is a square wave, 4–50 MHz allowed (DS14540, table 38) |
| PLL1's input | PLL1SRC = 11 (HSE), PLL1M = 1 (÷ 1), PLL1RGE = 11 (8–16 MHz), PLL1VCOSEL = 0 (wide), PLL1FRACEN = 0 (RCC_PLL1CFGR, 11.8.7) | 9.8304 MHz straight in |
| PLL1's VCO | PLL1N = 40 (field 0x027): 393.216 MHz (RCC_PLL1DIVR, 11.8.10) | in the wide range of 128–560 MHz (DS14540, table 46); a whole multiplier, no fractional mode |
| the system clock | PLL1P ÷ 2 (field 1): 196.608 MHz on Mamka; ÷ 8 (field 7): 49.152 MHz on a unit; SW = 11 (PLL1); VOS1 on both | VOS1 allows 200 MHz (DS14540, table 20) and the units' USART kernel wants it; P takes even dividers only |
| the buses | HPRE, PPRE1, PPRE2, PPRE3 ÷ 1: AHB and APB at the system clock; TIMPRE = 0, so the timers too (RCC_CFGR1 and CFGR2, 11.8.5–6) | APB to 200 MHz in VOS1 (table 20) |
| the flash | LATENCY = 5, WRHIGHFREQ = 10 on Mamka; LATENCY = 1, WRHIGHFREQ = 00 on a unit (FLASH_ACR) | 170–200 MHz and 34–68 MHz in VOS1 (RM0481, table 48) |
| the lines, 19,660,800 Bd | on Mamka the APB clock (USARTxSEL = 000); on a unit PLL3 Q, PLL3 from the HSE as PLL1, ÷ 1 and × 40, Q ÷ 2: 196.608 MHz (USARTxSEL = 010); OVER8 = 1, BRR = 0x0012 | USARTDIV = 20 at 8×, BRR[2:0] its low four bits shifted right (56.5.8); 200 MHz allowed (table 20) |
| the ADC | 49.152 MHz: CKMODE = 11, the AHB clock ÷ 4, on Mamka; = 01, ÷ 1, on a unit (ADC_CCR, 28.7.2) | at most 75 MHz (DS14540, table 89) |

- **The other outputs:** PLL1 Q makes the SPI's clock (÷ 5, 78.6432 MHz) on the module and
  Mamka's processor 1, and the sound's (÷ 32, 12.288 MHz, 256 × 48 kHz) on Nataša and Mamka's
  processor 2; R is off everywhere; PLL3 Q the lines' on a unit, off on Mamka; PLL2 off.
- **The timers** count at the system clock, so a divider "÷ 5 of the suit clock" is ÷ 25 in a
  unit's timer and ÷ 100 in Mamka's; the pages give both.
- **A Bratiška** runs on his own HSI and never takes the suit clock: his IMUs sample on the CLKIN
  that his Staršaja makes from it, and he only reads them (see
  [Rubaška](../rubaska/SOFTWARE.md#the-glove)).
- **After a reset** every processor runs on its HSI, 32 MHz in VOS3 (RM0481 Rev 5, 10.7.2 and
  11.8.1), and takes the suit clock before anything else: VOS1, waiting for VOSRDY; the flash's
  latency; the HSE, waiting for HSERDY; the PLLs, waiting for their lock, 45 µs and 100 µs at most
  (DS14540, table 46); the system clock on PLL1; the HSE's clock security on (HSECSSON). Only then
  does it set its peripherals, one setting each and none for the HSI. With no clock it waits for
  HSERDY, silent (see [Bring-up](#bring-up)).
- **After Stop** it wakes on its HSI (STOPWUCK = 0, RCC_CFGR1, 11.8.5), its peripherals keeping
  their settings, and takes the suit clock again the same way before it goes on.
- **The clock lost while running:** the clock security switches the processor to its HSI by
  itself, turns off the HSE and the PLLs and raises an NMI (RM0481 Rev 5, 11.4.10). The unit
  cannot keep its line's rate on the HSI, so it falls silent and resets, waits for the clock and
  joins at the next bring-up; Mamka sees its slot empty.
- **Current:** a core at 49.152 MHz saves an estimated ~14 mA a processor against 196.608 MHz:
  DS14540's table 26 gives VOS1 down to 150 MHz only, 16.2 mA there against 21.3 mA at 200 MHz,
  and below it a straight line is assumed; for the modules, the gloves' Staršaja and Nataša
  ~0.27 A in all. Míša and Mamka's processors stay at 196.608 MHz until checked.
- **Checked on the first board:** the suit clock at the buffers' output against a counter, the
  line at its rate, the ADS1299's CLK and the IMUs' CLKIN at their pins.

## Interrupts

The STM32H5's NVIC has 16 levels, four bits of priority (RM0481 Rev 5, 17.1); all four bits
preempt, with no subpriorities. The suit's levels are the same on every processor, and each
processor's table is on its page ([the module and the glove](../rubaska/SOFTWARE.md#interrupts),
[Mamka](../mamka/SOFTWARE.md#interrupts), [Nataša](../natasa/SOFTWARE.md#interrupts),
[Míša](../misa/SOFTWARE.md#interrupts)):

| level | for |
|---|---|
| 0 | the measurement's moment: the ADS1299's DRDY, line 8's cycle |
| 1 | the frame out: the read done, a slot's start |
| 2 | the lines in: Mamka's frames and the echo; on Mamka the frames in and the SPIs to Baťa |
| 4 | the links and the sound: the glove's wires on her Staršaja, the link between Mamka's processors, the SAI and the I2S |
| 6 | the sensors: the I3C, the radar, the ultrasound |
| 8 | the slow ones: the ADC, the flash, the BMS, the GPS, the fan |

- **At 0 and 1 a handler only starts a transfer or sets a register;** the work runs lower or in
  the main loop.
- **A received frame is one interrupt,** the USART's idle line once the frame has ended; the DMA
  puts the bytes into memory by itself and takes no interrupt. A sending channel that ends a
  block takes one; the sound's circular channels take theirs at each half, to hand it on.
- **During *get ready*** every interrupt is masked (PRIMASK) and the start is polled, as above.
- **The masters keep no cycle of their own** on lines 1–7: the units keep it from DRDY, the
  glove's Staršaja from *start* on her timer, and Mamka follows the frames coming in. On line 8
  every unit keeps it on its timer, and Mamka's heartbeat corrects it (see [Line 8](#line-8)).

## Open questions

- the ADS1299 read at 19.66 MHz, which its DVDD of 3.3 V allows (SCLK period at least 50 ns at
  2.7–3.6 V, datasheet section 7.6), the slots' 1 µs guards and the time a unit takes to build its
  frame after the read, seen on the first board,
- the ADS1299: the datasheet does not say which CLK edge reads START; confirm by measurement,
- the PRBS-9's polynomial against ITU-T O.150's own text,
- an image beyond the map's 256 blocks, 128 KB, as Nataša's bank of 256 KB and Mamka's of 512 KB
  allow,
- how a byte at the line's rate wakes a unit from Stop: an edge on RX through the EXTI, or the
  USART's kernel clock on the HSI for the sleep alone, which the wake-up from Stop needs
  (RM0481 Rev 5, 11.4.9 and 56.5.22); tried on the first board,
- whether a unit's number is split into a line and a unit on it,
- the lowest 3.3 V by VREFINT, to verify in DS14540,
- the glove's wires, Staršaja to the Bratiški: their rate, set on the first board (see
  [Rubaška](../rubaska/SOFTWARE.md#the-glove)),
- what Baťa's application for the map shows and asks,
- the contact points: how well the model learns them, tried on recordings,
- processor 2's two SPIs at 11.1 MHz through the ROCK's UM3204s, read back on the first board:
  the clock out and the data back pass the translator each, whether the RK3588 must sample
  later (`rx-sample-delay-ns` of its SPI) is seen there,
- the first *start* across the START wire: the head's and the trunk's first DRDY against a
  limb's, on a scope.
