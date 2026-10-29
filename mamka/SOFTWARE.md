<div align="center">

# Mamka: software

**What the two processors do:** processor 1's SPI to Baťa, processor 2's two, the wires between
them, Mamka's own registers, the sound and the suit's clock on Baťa's side, the BMS's protocol, the
memory, the firmware and its update.

↑ [Mamka](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Both processors are in C with no operating system, like every unit; Baťa's software is under
[Baťa](../bata/SOFTWARE.md). Processor 1 bridges the limbs' lines 1–4 to Baťa's fast SPI, as
[Porjadok](../porjadok/SOFTWARE.md#into-baťa) describes; processor 2 bridges the head's and the
trunk's lines 5–7 and line 8 to two slower ones, and runs the sound and the household. Their pins
are under [hardware](HARDWARE.md#what-is-on-it). What travels, the frames, their commands and the
registers, is under [Porjadok](../porjadok/SOFTWARE.md).

**Every flow to Baťa has a way of its own:** the limbs on processor 1's SPI, the head, the trunk
and the household on processor 2's, the sound on the I2S. A firmware update, a button or the
sound never stands in another flow's way, and the processors share only the four wires between
them.

## Processor 1's SPI

Processor 1 hands Baťa lines 1–4 over SPI1, the slave of the ROCK 5T's SPI1_M1 at 37.5 MHz, both
ways at once, as [Porjadok](../porjadok/SOFTWARE.md#into-baťa) lays it out: the frames as they
came, in places sized by the unit's kind, 58 B for a module of two chips and 34 B for the rest,
with no header. Baťa is the master, processor 1 the slave: SPI mode 0
(CPOL 0, CPHA 0), MSB first, 8-bit words, NSS low for a transfer.

- **"Data ready"** (PB1, header pin 36) stays high while she has anything to send: a cycle while
  measuring, an answer in the service mode.
- **A cycle** is closed by TIM2 once slot 4's frame is due: each frame checked by its CRC as it came
  and put in its place by the table's order, a bad or a missing one leaving its place zeros, then
  the four places of 34 B for the diagnostics, the answers and her own frames; 1,064 B.
- **The ring:** 512 KB of SRAM in cycles of 1,064 B holds ~490 cycles, ~0.26 s. When it fills, the
  oldest goes, and the jump in the frames' numbers shows it.
- **An underrun.** A slave clocked beyond what it has sends zeros, which read as empty places,
  and the frames' CRCs catch the rest; the STM32H5's SPI reports the underrun as well (UDR,
  RM0481 58.4). The SPI's FIFO is 16 B, and the DMA feeds it straight from the ring.
- **Timing:** the limbs' 1,064 B a cycle take 227 µs at 37.5 MHz, so a sample reaches Baťa
  ~0.47 ms after DRDY.
- **Down, in the same places:** the frames for lines 1–4 and for processor 1 herself, 0xF1, and
  the firmware's frames. Processor 1 puts a frame down her lines' one sender as it came, at the
  next free moment; she builds none but the heartbeat.
- **Without a measurement** there are no cycles: Baťa clocks a transfer of the length of what he
  sends, and processor 1 raises "data ready" while answers wait for him.

## Processor 2's two SPIs

Processor 2 hands Baťa lines 5–7, line 8 and the household striped over two SPIs: SPI2 as the
slave of the ROCK 5T's SPI0_M2 and SPI1 as the slave of his SPI3_M0, at 11.1 MHz through the
ROCK's translators (see [hardware](HARDWARE.md#on-baťas-header)), with the same layout and
settings as processor 1's. SPI3_M0's chip select is Baťa's GPIO on header pin 29, and her "data
ready" PB0 on pin 31, one for both.

- **Striped:** she lays the transfer word by word, 4 B at a time, into the two SPIs' buffers as
  she builds it, and each SPI's DMA sends its own; both finish together.
- **A cycle:** five places of data, the head's, the chest's and the lower back's of 58 B, the
  neck's and Nataša's of 34 B, and the four, 378 B, with zeros to 96 words 192 B a SPI, 138 µs at
  11.1 MHz; closed by TIM5 once slot 4's frame is due, as processor 1's by her TIM2.
- **Line 8:** Nataša's frame of data goes in her place, once every 32 cycles; Míša, who sends
  none, has no place, and his sphere, five answers as they came, and line 8's other answers go
  in the four. From Nataša's
  microphones (see [Nataša](../natasa/SOFTWARE.md#sound-across-the-suit)) processor 2 feeds the
  SAI's stream through a buffer of her own, and she makes an event of each change of a button and
  of Nataša's warning.
- **Her own:** her answers and what she sends unasked, the GPS, the UTC label and the events (see
  [her registers](#mamkas-own-registers)), and the BMS as her chip 0x04.
- **Down:** the frames for lines 5–7, for line 8, Nataša 0x81 and Míša 0x82, and for herself,
  0xF2; the firmware's frames for her lines and herself. A frame for the whole system comes on
  every SPI, so she puts it on her lines as processor 1 on hers.
- **The ring:** 256 KB in cycles of 384 B holds ~680 cycles, ~0.36 s, longer than processor 1's
  0.26 s.

## The wires between the processors

Four wires join the two processors, two of them a UART; everything else each does with Baťa over
her own SPI.

| wire | from, to | what |
|---|---|---|
| START | processor 1's PB15 (TIM12_CH2, an output compare) to processor 2's PB15 (TIM12_CH2) | the moment of the first *start* |
| the limbs' PGOOD | the limbs' last 4 V converter to processor 1's PC1 and processor 2's PE9 | the limbs' lines powered |
| the UART, TX and RX crossed | UART4 on PA0 and PA1 of each, 115,200 Bd, 8N1 | a frame of 34 B a second each way: her state |

- **The limbs' power:** processor 2 switches both chains (see [Budilnik](HARDWARE.md#budilnik));
  processor 1 brings up lines 1–4 when the limbs' PGOOD rises and marks their units gone when it
  falls (see [Porjadok](../porjadok/SOFTWARE.md#bring-up)). Power command 3 needs no message:
  the PGOOD falls and rises, and she brings up her lines again.
- **The first *start*** for the whole system Baťa sends on every SPI, once every unit has
  answered *get ready*. Both processors' TIM12 count the suit clock (PSC = 19), and neither masks
  an interrupt:
  1. processor 1 raises START at a tick T by her TIM12's output compare and sets its TRGO at
     T + 100 ticks, ~10 µs;
  2. processor 2's TIM12 is reset by the edge on TI2 (its slave mode) and sets its TRGO 100 ticks
     later;
  3. on each, TRGO triggers the GPDMA channel holding the *start* frame (TRIGSEL 36, tim12_trgo,
     RM0481 Rev 5, table 146), which sends it down the processor's lines with modules.

  The two frames leave a few cycles apart, the capture's resynchronisation and the DMA's start,
  within what the start allows (see [Porjadok](../porjadok/SOFTWARE.md#starting-a-measurement)).
  Later *stop* and *start* only mark the cycle.
- **The UART:** once a second each sends the other a frame of 34 B, her chip 0x00's registers
  from 0x00 as an answer to a read sent unasked: her state, her firmware's version and her
  temperature. A
  frame missing for 3 s the other reports to Baťa as an event; she never acts on it, a hang being
  the watchdog's. UART4 runs from the APB clock, 16×, BRR = 1,707: 196.608 MHz ÷ 1,707 = 115,178 Bd,
  0.02 % off, on interrupts with its FIFO of 8 B and no DMA channel.

## Mamka's own registers

Each processor is a unit of its own, 0xF1 and 0xF2, with a chip 0x00 of its own: no new kinds,
the reads and the writes as for any unit (see
[Porjadok](../porjadok/SOFTWARE.md#the-commands)), the answer to a write its result, and what
comes by itself an answer to a read sent unasked, as Míša's sphere.

| processor 2 (0xF2), chip 0x00, registers | what | |
|---|---|---|
| 0x00–0x01 | the firmware's version | read |
| 0x02 | the state: bit 0 the firmware on trial, 1 the last update failed, 2 Nataša present, 3 Míša present | read |
| 0x03–0x04 | the power (u16): bits 0–1 the limbs' 4 V chain's first EN and last PGOOD, 2–3 the head's and the trunk's, 4–5 the 6 V's EN and PGOOD, 6–7 Baťa's eFuse's SHDN and PGOOD, 8–9 Borovičok's | read |
| 0x05–0x06 | the fan, rpm | read |
| 0x07–0x08 | her temperature, 0.1 °C | read |
| 0x09 | the last reset's cause, as a unit's (see [Porjadok](../porjadok/SOFTWARE.md#watchdogs)) | read |
| 0x10 | the power's command: 1 the suit shut down in order and then off (see [Budilnik](HARDWARE.md#budilnik)), 2 the computers' supply off once they have halted, 3 the lines' 4 V and the 6 V off and on again in the order of the start, every unit starting again in the service mode, and then the lines brought up, 5–8 by her and 1–4 by processor 1 as the limbs' PGOOD rises (see [the wires](#the-wires-between-the-processors) and [Porjadok](../porjadok/SOFTWARE.md#bring-up)), 4 Baťa halted by [Storož](../bata/SOFTWARE.md#storož): she plays a pattern on the headband, 5 Baťa running again | write |
| 0x11 | Storož's reason, 1–10 | write |
| 0x12 | the fan's duty, % | write |
| 0x40… | her table, as for every unit | read |
| 0x80… | the firmware, as for every unit | |
| 0xC0–0xC5 | an event: what (u8), which (u8), the cycle's number (u32) | unasked |
| 0xD0–0xDB | the GPS, sent at a fix: the latitude and longitude (2 × i32, 10⁻⁷ °), the height (i16, m), the fix's quality (u8), the satellites (u8) | unasked |
| 0xE0–0xE7 | the UTC label, sent at every PPS: the suit's cycle (u32) at which a UTC second began, and that second (u32, Unix time) | unasked |

| event, what | which |
|---|---|
| 1 a button pressed, 2 released | the button, 0–15 |
| 3 Budilnik's button | 0 |
| 4 a BMS alarm | the alarm's bit |
| 5 Nataša's warning begun, 6 ended | 0 |
| 7 the other processor silent on the UART for 3 s, either one's event | the silent one, 1 or 2 |

- **The BMS is chip 0x04 of processor 2,** from register 0x00, read only: its live block as she
  last read it, once a second (see [the battery](#the-battery)): the cells (4 × u16, mV), the pack
  (u16, mV), the current (i16, mA), three temperatures (3 × i16, 0.1 °C), the alarms (u16), the
  state of charge (u8, %), the remaining capacity (u16, mAh); 23 B, one read.
- **Processor 1 (0xF1), chip 0x00:** from 0x00, read only, the firmware's version (2 B), the
  state (1 B: bit 0 on trial, 1 the last update failed, 2 the limbs' PGOOD), her temperature (2 B,
  0.1 °C), the ring's fill in cycles (2 B), the last reset's cause (1 B, at 0x07); her table from
  0x40, the firmware from 0x80, her event from 0xC0, as processor 2's. A unit gone shows as zeros
  in its place, the ring overflowed as a jump in the frames' numbers.

## Baťa and the suit's clock

Baťa takes no outside clock: the RK3588 runs from its own 24 MHz crystal (`xin24m` in its device
tree).

That need not matter:

- The samples are taken in the units on the suit's clock; Baťa need not share it.
- The RK3588's I2S can run as a slave and take BCLK from outside, through an overlay of our own
  with a dummy codec as the clock master (Radxa's
  I2S2-M1 overlay with a dummy codec is the starting point). With processor 2 as the I2S
  master, the sound runs from the suit's clock, in the standard format of 48 kHz, 16 bits,
  stereo (see [Nataša](../natasa/SOFTWARE.md#sound-across-the-suit)), and Baťa needs no
  conversion of the sample rate.

## The battery

The BMS of the battery sits in the same backpack and talks over RS485. Processor 2 reads it
on a UART through a THVD1450, the half-duplex driver the lines already use for the
clock: the cells' voltages, the current, the temperatures and the state of charge (see
[Babuška](../babuska/HARDWARE.md#the-bms)). JK's BMS speak their RS485 Modbus protocol (V1.0,
9,600 Bd), so this is Modbus RTU.

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

Processor 2 keeps what she read as her chip 0x04 (see [her registers](#mamkas-own-registers)),
which Baťa reads over [her SPI](#processor-2s-two-spis). Baťa tells the wearer, by
voice or vibration through Nataša, and at 20% shuts the suit down in order.

## Memory

The STM32H562 has 640 KB of RAM in three blocks, SRAM1 of 256 KB, SRAM2 of 64 KB and SRAM3 of
320 KB, and 4 KB of backup SRAM (ST's CMSIS header stm32h562xx.h). The STM32H563 has the same
memory and adds Ethernet, with its own DMA on the bus, and a second SDMMC; Mamka needs neither,
the network is Baťa's. The STM32H523 has 272 KB, 128, 80 and 64 KB, and 2 KB of backup SRAM.
All three have two GPDMAs of eight channels, channels 6 and 7 of each with 2D addressing.

- **The bus is no limit.** Processor 1 moves ~1,064 B every 521 µs, ~2.0 MB/s in from the lines
  and
  as much out over her SPI, well under 1% of a 32-bit bus at 197 MHz. Each SRAM block is its own
  slave on the bus matrix, so the DMA and the core do not wait for each other in different
  blocks; in one block they take turns, by round robin (AN5872 Rev 5, 1.5 and 1.7).
- **The reserve for Baťa.** Linux is not real time, and when Baťa misses a "data ready" the cycles
  wait in processor 1 (see [her SPI](#processor-1s-spi)). A ring of 512 KB holds ~0.26 s and
  leaves 128 KB for the rest; processor 2's of 256 KB holds ~0.36 s. "Data ready" stays
  high while a cycle waits, and Baťa reads whatever has piled up in one go. Should the ring fill,
  the oldest cycles go, and Baťa sees the gap in the frames' numbers.
- **The rest is small:** the lines' receive buffers, a cycle's 1,024 B each at 19.66 Mbaud, and on
  processor 2 the sound, ~1.9 KB per 10 ms each way and the last ~10 packets down kept for a
  repeat.
- **While firmware goes down the lines** nothing is measured; processor 1 passes the blocks on
  and holds no image.
- **Processor 2** needs as many UARTs and SPIs as processor 1 and more, and a ring of her own;
  both are the STM32H562VG, one part on the board and one base for the firmware.

## Clocks

By the suit's clock tree (see [Porjadok](../porjadok/SOFTWARE.md#the-clock-tree)); on silicon A or Z
in VOS0 with LATENCY = 4 (see [firmware](#firmware)). Both processors take:

| what | setting |
|---|---|
| UART4, to the other processor | the APB clock, 16×, BRR = 1,707: 196.608 MHz ÷ 1,707 = 115,178 Bd, 0.02 % off |
| TIM12, START | PSC = 19: a tick of the suit clock; on processor 1 CH2 an output compare raising START at a tick T and CH1 the TRGO at T + 100; on processor 2 reset by the edge on TI2 (slave mode), CH1 the TRGO 100 ticks later; the TRGO triggers the GPDMA channel of the *start* frame |

**Processor 1** adds:

| what | setting |
|---|---|
| SPI1, the slave to Baťa | PLL1Q ÷ 5: 78.6432 MHz, SPI1SEL = 000 (RCC_CCIPR3, 11.8.42); Baťa drives it at 37.5 MHz |
| lines 1–4, 19,660,800 Bd | the lines' setting: OVER8 = 1, BRR = 0x0012; USART2 receives line 1 and sends for all four, the other three only receive |
| TIM2, the cycle's end | PSC = 19: a tick of the suit clock; started by a cycle's first frame, it closes the cycle once slot 4's frame is due |

**Processor 2** adds:

| what | setting |
|---|---|
| SAI1, the sound to Baťa | PLL1Q ÷ 32 (field 31): 12.288 MHz, SAI1SEL = 000 (RCC_CCIPR5, 11.8.44); the SAI's ÷ 4 to a bit clock of 3.072 MHz |
| SPI2 and SPI1, the slaves to Baťa | PLL1Q, the SAI's 12.288 MHz (SPI2SEL and SPI1SEL = 000, RCC_CCIPR3); a slave in the Motorola mode shifts on Baťa's SCK, 11.1 MHz, and needs its kernel clock only in the TI mode (RM0481 Rev 5, 58.4.1 and 58.5.1) |
| lines 5–7, 19,660,800 Bd | OVER8 = 1, BRR = 0x0012; USART1 receives line 5 and sends for all three, USART6 and UART7 only receive |
| USART3, line 8 | OVER8 = 1, BRR = 0x0012: 19,660,800 Bd |
| TIM6, line 8's cycle | PSC = 19: a tick of the suit clock; ARR = 5,119, a cycle of 520.8 µs, at whose start the heartbeat goes down line 8 once a second |
| UART5 to the BMS | the APB clock, 16×, BRR = 0x5000: 9,600 Bd |
| LPUART1 to the GPS | the APB3 clock ÷ 8 (LPUART1SEL = 000, PRESCALER = 0100), BRR = 0xA0000: 9,600 Bd, the kernel clock 2,560 times the rate, within its 3 to 4,096 (RM0481 Rev 5, 57.4.8 and 57.7.13) |
| TIM2, the GPS's PPS | PSC = 19: a tick of the suit clock, 101.7 ns |
| TIM5, the cycle's end | as processor 1's TIM2 |
| TIM4, the fan | PSC = 0, ARR = 7,863: 25.0 kHz |
| TIM3, the fan's speed | input capture |

Each processor raises her lines' clock drivers' DE at her start, on one plain pin chosen when the
board is drawn, and lowers it while her lines are off or asleep (see
[hardware](HARDWARE.md#clock)).

## DMA

By the suit's rules (see [Porjadok](../porjadok/SOFTWARE.md#the-gpdma)). **Processor 1,** 7
channels:

| channel | request (REQSEL) | what | priority | how |
|---|---|---|---|---|
| GPDMA1 0–3 | 23, 25, 31, 21 | USART2, USART3, USART6, USART1 RX: lines 1–4 | 3 | circular, into the receive buffers |
| GPDMA1 4 | 6, spi1_rx | SPI1 RX: the transfer down | 3 | circular |
| GPDMA2 0 | 24, usart2_tx | USART2 TX: Mamka's frames down lines 1–4, the first *start* on TIM12's TRGO (TRIGSEL 36) | 3 | one block a frame |
| GPDMA2 4 | 7, spi1_tx | SPI1 TX: the transfer up | 3 | from the ring, a block a transfer |

**Processor 2,** 12 channels:

| channel | request (REQSEL) | what | priority | how |
|---|---|---|---|---|
| GPDMA1 0–2 | 21, 31, 33 | USART1, USART6, UART7 RX: lines 5–7 | 3 | circular, into the receive buffers |
| GPDMA1 3 | 25, usart3_rx | USART3 RX: line 8 | 3 | circular |
| GPDMA1 4 | 8, spi2_rx | SPI2 RX: its share of the transfer down | 3 | circular |
| GPDMA1 5 | 6, spi1_rx | SPI1 RX: its share of the transfer down | 3 | circular |
| GPDMA2 0 | 22, usart1_tx | USART1 TX: the frames down lines 5–7, the first *start* on TIM12's TRGO | 3 | one block a frame |
| GPDMA2 1 | 26, usart3_tx | USART3 TX: the frames down line 8, the sound among them | 3 | one block a frame |
| GPDMA2 2 | 53, sai1_a_dma | SAI1 block A, the master, transmitting: the microphones to Baťa | 2 | circular |
| GPDMA2 3 | 54, sai1_b_dma | SAI1 block B, synchronous, receiving: the headphones' sound from Baťa | 2 | circular |
| GPDMA2 4 | 9, spi2_tx | SPI2 TX: its share of the transfer up | 3 | from the ring, a block a transfer |
| GPDMA2 5 | 7, spi1_tx | SPI1 TX: its share of the transfer up | 3 | from the ring, a block a transfer |

The SPIs run full duplex: what Baťa writes while he reads comes in on the receiving channels.
Free: channels 6–7 of every controller. The slow UARTs, to the other processor, the BMS and the
GPS, take no channel: their FIFO of 8 B and an interrupt are enough. The places are laid by the
core. SD_A on PC1 goes to header pin 38, the RK3588's I2S2_SDI_M1, and SD_B on
PA3 comes from pin 40, its I2S2_SDO_M1 (the ROCK 5T schematic V1.2, CON1; see
[hardware](HARDWARE.md#on-baťas-header)).

## Interrupts

By the suit's levels (see [Porjadok](../porjadok/SOFTWARE.md#interrupts)); the numbers are the
vector table's (RM0481 Rev 5, table 152). **Processor 1:**

| level | interrupt | what it does |
|---|---|---|
| 2 | USART2, USART3, USART6, USART1 (59, 60, 85, 58) | a frame in, on the idle line; a cycle's first frame starts TIM2 |
| 2 | TIM2 (45) | the cycle's end: its places laid, "data ready" raised |
| 2 | SPI1 (55) | Baťa's transfer: the next one made ready |
| 4 | UART4 (61) | the other processor's frame, from its FIFO |
| 8 | ADC1 (37), FLASH (6) | her temperature, the firmware update |

**Processor 2:**

| level | interrupt | what it does |
|---|---|---|
| 2 | USART1, USART6, UART7, USART3 (58, 85, 98, 60) | lines 5–8's frames in, on the idle line; a cycle's first frame starts TIM5 |
| 2 | TIM5 (48) | the cycle's end: its places laid, "data ready" raised |
| 0 | TIM6 (49) | line 8's cycle: once a second the heartbeat started at its start |
| 2 | SPI2, SPI1 (56, 55) | Baťa's transfer: the next one made ready |
| 4 | GPDMA2 channels 2 and 3 (92, 93) | the sound's halves, both ways |
| 4 | UART4 (61) | the other processor's frame, from its FIFO |
| 8 | UART5 (62), LPUART1 (63), TIM2 (45), TIM3 (46), ADC1 (37), FLASH (6) | the BMS, the GPS and its PPS, the fan's speed, her temperature, the update |

The first *start* takes no interrupt: TIM12's TRGO starts its DMA on both (see
[the wires](#the-wires-between-the-processors)).

## Firmware

- **Booting:** each starts by itself from its own flash, with BOOT0 pulled low on the board; Baťa
  takes no part in it.
- **The silicon:** revision X or W (REV_ID 0x1007 or 0x100F in DBGMCU_IDCODE) is preferred. On
  revisions A and Z a read from flash can fail in VOS1, the range Mamka runs in, with a double
  ECC error and an NMI (ES0565 Rev 8, 2.2.18). The erratum's workaround is to read and run from
  flash only in VOS3 or VOS0, and to go from VOS3 to VOS0 with the code in SRAM. So A and Z
  still do:
  - The firmware reads REV_ID at start, while the chip is still in VOS3 after reset. On A or Z
    a routine in SRAM sets VOS0 in PWR_VOSCR and waits for VOSRDY in PWR_VOSSR; the clock then
    goes up as on X and W (RM0481 Rev 5, 10.11.5 and 10.11.6).
  - At 196.608 MHz the flash then needs 4 wait states instead of VOS1's 5, with WRHIGHFREQ the
    same (RM0481 Rev 5, table 48).
  - Each processor draws more: 69.5 mA typical and 102 mA at TJ 85 °C with every peripheral
    clocked, against 60.7 and 82 mA in VOS1 (DS14258 Rev 6, table 28). Mamka's 3.3 V carries
    up to ~40 mA more, inside its margin (see [hardware](HARDWARE.md#mamkas-own-supply)).
    VOS0 is characterised to TJ 105 °C, VOS1 to 130 °C.
  - On A and Z the flash also lasts only 1,000 cycles (2.2.13, no workaround), plenty for
    firmware updates.

  The STM32H523 has only revision A and no such erratum (ES0621 Rev 3).
- **Updates:** the way is one for the whole suit, under
  [Porjadok](../porjadok/SOFTWARE.md#updating-firmware): *begin*, the blocks of 512 B into the other
  bank, the missing ones again by the map's four windows, the CRC-32 checked, SWAP_BANK, and the
  confirm within 30 s, written
  by Mamka once Baťa has tried the new version, or the unit swaps back by itself. Here the two banks
  are 512 KB each (DS14258 Rev 6, 3.4); each processor takes her image over her own SPI, a block in
  0.11 ms on processor 1's, 0.19 ms on processor 2's two, the flash's write setting the pace; the
  kinds 6 and 7, chip 0x00 of 0xF1 and 0xF2. While the other bank is written, the flash runs with no
  wait states only to 32 MHz, so LATENCY goes up for the update and back afterwards (ES0565, 2.2.9);
  the first write after power-up also freezes the core for ~120 µs (2.2.33), which the service mode
  does not mind. The backup registers that hold the update's note can come up with random contents
  after a brownout (2.2.20, with VBAT on VDD), which the note's check pattern covers.
- **The units' firmware** goes down the lines in the service mode, in the firmware's frames, lines
  1–4's from processor 1 and lines 5–8's from processor 2, each out of her own SPI's way down: a
  module's 128 KB in ~1 s, all lines at once, the flash's write setting the pace. Neither processor
  looks inside; Baťa drives the update and reads the answers.
- **A hang** without an update is the independent watchdog's: it restarts the processor, which
  watches itself as every unit does (see [Porjadok](../porjadok/SOFTWARE.md#watchdogs)).
- **SWD pads** for each processor take a programmer on the bench, should the update itself ever
  go wrong. They cost no header pin, so nothing on the header resets the processors.

## Open questions

- the ring's size against Baťa's real gaps: how long Linux keeps him from "data ready", measured
  under load,
- the I2S slave with a dummy codec, tried on the board,
- the first *start* across the START wire, tried: the trunk's first DRDY against a limb's, on a
  scope,
- processor 2's SPIs as slaves at 11.1 MHz through the ROCK's UM3204s, on a kernel clock of
  12.288 MHz, tried,
- the BMS's byte order and its SOC registers, on a sample.
