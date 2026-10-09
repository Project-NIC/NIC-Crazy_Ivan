<div align="center">

# Mamka: software

**What the two processors do:** the control channel and the UART to Baťa, the sound and the
suit's clock on Baťa's side, the BMS's protocol, the memory, the firmware and its update.

↑ [Mamka](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Both processors are in C with no operating system, like every module; Baťa's software is under
[Baťa](../bata/SOFTWARE.md). Processor 1 bridges the four body lines to Baťa's SPIs, as
[Porjadok](../porjadok/SOFTWARE.md#into-baťa) describes; processor 2 runs the head line,
the sound and the household. Their pins are under [hardware](HARDWARE.md#what-is-on-it).

## The control channel

The control channel is processor 2's and carries the head's slow, simple things: Nataša's
buttons, the vibration, the head's settings, Míša's sphere, the battery's state and the GPS. The
body's chip settings go over processor 1's UART instead, since only it has the body's lines. It is
I2C on header pins 3 and 5, with processor 2 as the slave: I2C1 on the Raspberry Pi 5, I2C7_M3 on
the ROCK 5T. The computer is the master and starts every transfer, so processor 2 raises pin 37 when
it has a message waiting.

- **On the ROCK 5T** I2C7 already serves the board's audio codec, the ES8316 behind its
  headphone jack, on the M0 pins (the device tree it shares with the 5B and 5B+,
  `rk3588-rock-5b-5bp-5t.dtsi`). One controller is one bus, so pins 3 and 5 work only after an
  overlay of our own turns the codec off and moves I2C7 to M3. The jack is not used: the sound
  goes through Mamka. Radxa offers its I2C7-M3 overlay only for the 5T Industrial, and its table
  for the 5T V1.2 lists no I2C on pins 3 and 5.
- **The header's other I2Cs are taken** on the ROCK 5T: 7 by the second SPI's chip select,
  32 by Umnica B's EN, 13 and 15 by the second SPI's data, 8 and 10 by the console and the bus
  of the NPU's regulator, 27 and 28 by the bus of the CPU's regulators, 29 and 31 by the bus of
  the USB-C controller.
- 400 kHz, or 1 MHz (Fast-mode Plus) where the computer manages it: some 40–100 kB/s, far more
  than these need.
- The Raspberry Pi has 1.8 kΩ pull-ups on pins 3 and 5 of its own; the ROCK 5T has none
  (schematic V1.2), so Mamka's own are fitted for it, fed from header pin 1, the computer's own
  3.3 V, so that they go with it.

**The messages** are CI-STP containers, the same header, data and CRC-16 as on the lines (see
[Porjadok](../porjadok/SOFTWARE.md#the-channel-from-the-master)), only longer: on I2C the data may
be up to 122 B, so Míša's sphere (~112 B) and a piece of firmware ride in one. Every transfer is a
fixed **128 B**: the container, then zeros. Processor 2 answers at the 7-bit address **0x5C**, to be
changed only should a computer carry something at it.

- **Down,** a write of 128 B: a container for a unit on the head line, `addr` as the line has it
  (Nataša 1, the others as they join), which processor 2 puts into the head line's channel in the
  next cycle as it came; or a container for processor 2 herself, `addr` 0.
- **Up,** a read of 128 B: the oldest message in processor 2's queue, an answer from the head
  line (0x80 + type, the same `seq`) or one of her own. Pin 37, "a message waiting", is high while
  the queue holds anything, so the computer reads until it falls. A read with nothing waiting
  returns a container of type 0, zeros.
- **From Nataša's frame** (see [Nataša](../natasa/SOFTWARE.md#natašas-frame)) processor 2
  makes three things: the microphones' samples go on into the SAI's stream, a changed button bit
  becomes an event (0x15), and the sphere, once its 14 positions are complete with a new frame
  number, goes up as a container of type 10 from `addr` 0x81, as Míša sent it.
- **Processor 2's own types,** `addr` 0:

  | `type` | message | data |
  |---|---|---|
  | 0x10 | her state | asked with no data; answered with: firmware version (2 B), the firmware's state (1 B: running unconfirmed, the last update failed), the head line's blocks present (1 B), the converters' PGOOD and EN (1 B), the fan's speed (2 B, rpm), her temperature (2 B, 0.1 °C) |
  | 0x11 | the battery | answered with the BMS's live block as she last read it (see [the battery](#the-battery)): the cells (4 × 2 B, mV), the pack (2 B, mV), the current (2 B, mA, signed), the temperatures (3 × 2 B, 0.1 °C), the alarms (2 B), the state of charge (1 B, %), the remaining capacity (2 B, mAh) |
  | 0x12 | the power | from the computer: 1 = shut the suit down in order and then off altogether (see [Budilnik](HARDWARE.md#budilnik)), 2 = the computers' supply off once they have halted, 3 = the fan's duty (1 B, %), 4 = Baťa halted by [Storož](../bata/SOFTWARE.md#storož) with his reason (1 B): she plays a pattern on the headband and shows it in her state, 5 = Baťa running again |
  | 0x13 | the GPS | sent on her own when a fix comes: the position (2 × 4 B, 10⁻⁷ °), the height (2 B, m), the fix's quality (1 B) |
  | 0x14 | the UTC label | sent on her own at every PPS: the suit's sample number (4 B) at which that UTC second began, and the second itself (4 B, Unix time) |
  | 0x15 | an event | sent on her own: a button pressed or released, the power button, a BMS alarm, Nataša's warning from Míša's sphere: what (1 B), which (1 B), the sample number (4 B) |
  | 5, 6 | firmware | pieces of processor 2's own new firmware and its control, as for a block |

- **Rate:** 128 B at 400 kHz is ~3.2 ms, so 256 KB of firmware in pieces of 112 B take ~7.5 s;
  at 1 MHz a third of that. Everything else on this channel is a few messages a second.

## The UART

The UART on pins 8 and 10 is processor 1's: diagnostics, the new firmware for processor 1
and for the body's blocks, and the blocks' chip settings. Processor 1 knows that only its own
framed packets come this way (a header, the length, the data and a CRC, the lines' containers)
and drops anything else. On the ROCK 5T this UART is the debug console, which prints the boot
there at 1.5 Mbaud; processor 1 can keep the last lines of it, to tell why the computer did not
start.

- **Speed:** the RP1's UART reaches 6.25 Mbaud at most (a 100 MHz clock, 16 samples a bit),
  without DMA; the RK3588's 4 Mbps (its datasheet); the STM32H562's 20 Mbaud. 1–3 Mbaud is safe
  on both computers, and a few hundred kilobytes of firmware then take seconds.
- **The U(S)ARTs:** the datasheet gives the USARTs and UARTs alike 20 Mbaud with DMA (DS14258,
  3.37.1), and LQFP64 has five of each. Processor 1 uses five, the four body lines and this
  UART; processor 2 two, the head line and the BMS, three with the GPS.

**The packets.** The UART runs at **1,500,000 Bd**, 8N1: the ROCK 5T's console rate, so its boot
is readable too; processor 1 makes it from 196.608 MHz ÷ 131, 0.05% off, and the Raspberry Pi
from the RP1's 100 MHz with its fractional divider. A packet is a sync word, the line, and a
CI-STP container as the lines carry it (see
[Porjadok](../porjadok/SOFTWARE.md#the-channel-from-the-master)):

| bytes | field | meaning |
|---|---|---|
| 0–1 | `sync` | 0xC1A1, little-endian: 0xA1 then 0xC1 on the wire |
| 2 | `line` | 1–4 the body lines, 0xFF every line, 0 processor 1 herself |
| 3… | the container | `addr`, `type`, `len`, `seq`, data, `crc16`, as on the lines, up to 66 B |

- **Down:** processor 1 puts a container for a line into that line's channel in the next cycle,
  as it came; with 0xFF into all four. The body's chip settings, the blocks' firmware and their
  readbacks all go this way; Baťa builds the containers, processor 1 only carries them.
- **Up:** every answer from a block comes back as a packet with its line; processor 1 adds
  nothing. Her own messages have `line` 0 and the same types as processor 2's 0x10 (her state:
  firmware version and state, the blocks present on each line as four bytes, her temperature,
  the ring's fill), 0x15 (an event: a block gone or back, the ring overflowed) and 5, 6 (her own
  firmware).
- **Sync:** processor 1 reads the stream byte by byte, looks for 0xA1 0xC1, takes the packet by
  its `len` and checks the CRC; anything else, the ROCK's boot lines among it, is kept in a small
  log for diagnostics and otherwise dropped. A packet with a bad CRC is dropped without an answer;
  Baťa resends after 10 ms with the same `seq`.
- **Rate:** 1.5 MBd is ~150 kB/s, ~2,460 packets of 61 B a second. A block's image of up to
  128 KB, 2,731 pieces of 48 B, passes in ~1.1 s, to all four lines at once with `line` 0xFF and
  to all the blocks on a line with `addr` 0, each answering in its own slot. Processor 1's own
  image of 256 KB takes ~2.2 s.

## The cycle to Baťa over SPI

Processor 1 hands Baťa every cycle as one **record of 768 B** in two halves of 384 B, six cache
lines each, one half on each SPI. Baťa is the master, processor 1 the slave: SPI mode 0 (CPOL 0,
CPHA 0), MSB first, 8-bit words, NSS low for one half, 37.5 MHz on the ROCK 5T and 33.3 MHz on
the Raspberry Pi (see [Porjadok](../porjadok/SOFTWARE.md#into-baťa)). A half has the same shape
whatever the suit's population, so Baťa's DMA reads a fixed 384 B:

| bytes | field | content |
|---|---|---|
| 0–1 | `sample` | u16: the cycle's sample number |
| 2 | `flags` | bit 0: which half, 0 for lines 1 and 2, 1 for lines 3 and 4; bit 1: the record waited a cycle for a repeated frame; bit 2: a frame is missing after the repeat failed too; bit 3: cycles were dropped before this one, the ring had overflowed |
| 3 | `pending` | how many more cycles wait in the ring after this one |
| 4–5 | `present` | u16: a bit for each of the half's eight blocks (bits 0–7, line and slot order) and for its glove (bit 8), set when its frame is in |
| 6–7 | reserved | zeros |
| 8–327 | the frames | eight frames of 40 B, the half's two lines, four slots each, in line and slot order; an absent block's slot is zeros |
| 328–367 | the glove | the frame of the glove on that half's forearm module, the first glove in half 0, the second in half 1; zeros when none |
| 368–381 | reserved | zeros |
| 382–383 | `crc16` | CRC-16/CCITT-FALSE over bytes 0–381 |

- **"Data ready"** (PB1, header pin 36) goes high when a record waits and stays high while any
  does. Baťa reads half 0 on the first SPI and half 1 on the second, one DMA transfer of 384 B
  each, and goes on reading while `pending` says more wait or the pin stays high. With one SPI
  only, both halves come on the first SPI, half 0 then half 1.
- **A repeated frame.** When a frame of a cycle was bad, the record waits one cycle for the
  repeat (bit 1) and goes out complete and in order; should the repeat fail too, it goes with the
  slot zeroed, its `present` bit clear and bit 2 set. Baťa so always gets the cycles in order and
  whole; a bad frame costs that one record 260 µs.
- **The ring:** 512 KB of SRAM in records of 768 B holds 682 cycles, ~178 ms. When it fills, the
  oldest record goes and the next one out carries bit 3; the jump in `sample` shows it too.
- **An underrun.** A slave clocked beyond what it has sends zeros, so the CRC fails and Baťa
  drops the half and reads it again; the STM32H5's SPI reports the underrun as well (UDR, RM0481
  58.4). The SPI's FIFO is 16 B, and the DMA feeds it straight from the ring.
- **Timing:** 384 B take 82 µs at 37.5 MHz and 92 µs at 33.3 MHz, both halves at once, so a
  sample reaches Baťa ~310 µs after DRDY on the ROCK 5T and ~320 µs on the Raspberry Pi; on one
  SPI alone 164 or 184 µs, still inside the 260 µs cycle.

## Baťa and the suit's clock

Neither of the two computers takes an outside clock. The RP1 on the Raspberry Pi cannot: according
to the Linux RP1 clock driver, all its PLLs derive from its own 50 MHz crystal on the board, and
none of its clock sources is a GPIO input; its UART clock tops out at 100 MHz. The RK3588 runs from
its own 24 MHz crystal (`xin24m` in its device tree).

That need not matter:

- The samples are taken in the blocks on the suit's clock; Baťa need not share it.
- The I2S of both can run as a slave and take BCLK from outside: the RP1's as it is, the
  RK3588's through an overlay of our own with a dummy codec as the clock master (Radxa's
  I2S2-M1 overlay with a dummy codec is the starting point). With processor 2 as the I2S
  master, the sound runs from the suit's clock, in the standard format of 48 kHz, 16 bits,
  stereo (see [Nataša](../natasa/SOFTWARE.md#sound-across-the-suit)), and Baťa needs no
  conversion of the sample rate.

## The battery

The BMS of the battery sits in the same backpack and talks over RS485. Processor 2 reads it
on a UART through a THVD1450, the half-duplex driver the lines already use for the
clock: the cells' voltages, the current, the temperatures and the state of charge (see
[Babuška](../babuska/HARDWARE.md#the-bms)). JK's BMS speak their RS485 Modbus protocol (V1.0,
9,600 Bd), so this is Modbus RTU, which NIC-Heimdall already has.

- **The BMS as a slave:** its address on its switches is 1 to 15. Address 0x00 would make it a
  Modbus master that polls other packs.
- **Protocol 013** in JK's app: JK BMS RS485 Modbus V1.0 at 9,600 Bd; 001 is the same at
  115,200 Bd. It knows only function 0x03 (read) and 0x10 (write multiple registers).
- **Registers:** JK numbers each one as a base plus the field's byte offset: the settings from
  0x1000, the live data from 0x1200, the device from 0x1400, the commands from 0x1600 (JK BMS
  RS485 Modbus general protocol V1.0 and V1.1).
- **About once a second** processor 2 reads the live block from 0x1200 in one request and
  takes the fields by their offsets: the cells from 0x1200 (mV), the pack 0x1290 (mV), the
  current 0x1298 (mA, signed), the temperatures 0x129C and 0x129E and the MOSFETs' 0x128A
  (0.1 °C), the alarms 0x12A0 (one bit each: over- and under-voltage, over-current, short
  circuit, temperatures, the MOSFETs), the state of charge in 0x12A6 and the remaining capacity
  0x12A8 (mAh). At 9,600 Bd the ~0.18 kB take ~0.2 s.
- The byte order of the 32-bit values is to be confirmed on a sample.

Processor 2 passes the battery's state to Baťa over
[the control channel](#the-control-channel). Baťa tells the wearer, by voice or vibration through
Nataša, and at 20% shuts the suit down in order.

## Memory

The STM32H562 has 640 KB of RAM in three blocks, SRAM1 of 256 KB, SRAM2 of 64 KB and SRAM3 of
320 KB, and 4 KB of backup SRAM (ST's CMSIS header stm32h562xx.h). The STM32H563 has the same
memory and adds Ethernet, with its own DMA on the bus, and a second SDMMC; Mamka needs neither,
the network is Baťa's. The STM32H523 has 272 KB, 128, 80 and 64 KB, and 2 KB of backup SRAM.
All three have two GPDMAs of eight channels, channels 6 and 7 of each with 2D addressing.

- **The bus is no limit.** Processor 1 moves 640 B every 260 µs: 2.3 MiB/s in from the lines
  and as much out over the SPIs, under 1% of a 32-bit bus at 197 MHz. Each SRAM block is its
  own slave on the bus matrix, so the DMA and the core do not wait for each other in different
  blocks; in one block they take turns, by round robin (AN5872 Rev 5, 1.5 and 1.7).
- **The reserve for Baťa.** Linux is not real time, and when Baťa misses a "data ready" the
  cycles wait in processor 1, ~2.9 KB a millisecond in records of 768 B (see
  [the cycle to Baťa](#the-cycle-to-baťa-over-spi)). A ring of 512 KB holds ~178 ms and leaves
  128 KB for the rest. "Data ready" stays high while a cycle waits, and Baťa reads whatever has
  piled up in one go. Should the ring fill, the oldest cycles go, and Baťa sees the gap in the
  sample numbers. The STM32H523 would hold ~65 ms in 192 KB.
- **The rest is small:** the lines' receive buffers, 2 × 640 B, and on processor 2 the sound,
  ~1.9 KB per 10 ms each way.
- **While the blocks' firmware goes down the lines** nothing is measured; processor 1 passes
  the pieces on and holds no image.
- **Processor 2** needs little memory, and the STM32H523 would do for it. It has no SAI, so the
  sound would go through an SPI in I2S mode as on Nataša. For now both are STM32H562: one part
  on the board and one base for the firmware.

## Firmware

- **Booting:** each starts by itself from its own flash, with BOOT0 pulled low on the board; Baťa
  takes no part in it.
- **The silicon:** revision X or W (REV_ID 0x1007 or 0x100F in DBGMCU_IDCODE). On revisions A
  and Z a read from flash can fail in VOS1, the range Mamka runs in (ES0565 Rev 8, 2.2.18); the
  firmware checks the revision at start. The STM32H523 has only revision A and no such erratum
  (ES0621 Rev 3).
- **Updates:** the procedure is one for the whole suit, under
  [Porjadok](../porjadok/SOFTWARE.md#updating-firmware): the new image goes into the other bank
  of the flash in pieces of 48 B, the unit checks its CRC-32, swaps the banks with the option bit
  SWAP_BANK and resets, and the master confirms the new firmware within 30 s or the unit swaps
  back by itself. Here the two banks are 512 KB each (DS14258 Rev 6, 3.4), processor 1 takes
  her image over the UART in ~2.2 s for 256 KB, processor 2 hers over the I2C in pieces of 112 B,
  seven flash words, the one place a piece is longer than 48 B (see Porjadok), ~7.5 s at
  400 kHz; both with `addr` 0, kinds 5 and 6. While the other bank is written, the
  flash runs with no wait states only to 32 MHz, so LATENCY goes up for the update and back
  afterwards (ES0565, 2.2.9); the first write after power-up also freezes the core for ~120 µs
  (2.2.33), which the stopped measurement does not mind. The backup registers that hold the
  update's note can come up with random contents after a brownout (2.2.20, with VBAT on VDD),
  which the note's check pattern covers.
- **The blocks' firmware** goes down the lines in the same containers, the body's from
  processor 1 as UART packets with their `line`, the head's from processor 2 as I2C messages with
  the unit's address on the head line, one piece of 48 B a transfer: Nataša's 128 KB in ~8.7 s at
  400 kHz. Neither processor looks inside; Baťa drives the update and reads the answers.
- **A hang** without an update is the independent watchdog's: it restarts the processor.
- **SWD pads** for each processor take a programmer on the bench, should the update itself ever
  go wrong. They cost no header pin, so nothing on the header resets the processors.

## Open questions

- the ring's size against Baťa's real gaps: how long Linux keeps him from "data ready", measured
  under load,
- the I2C7-M3 overlay with the ES8316 off on the ROCK 5T, and the I2S slave with a dummy codec,
  tried on the board,
- the BMS's byte order and its SOC registers, on a sample.
