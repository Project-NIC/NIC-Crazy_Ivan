<div align="center">

# Mamka: why not

**The graveyard:** what was considered for the base board and why it is not used.

↑ [Mamka](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Each entry says what it was and why it went, so that nobody digs it up without knowing.

## The processors and the header

- **SPI2 on PB13 and PB14 for Baťa.** With MISO on PB14 a slave transmits at 6 MHz at most, with
  SCK on PB13 a master at 3 MHz (DS14258, table 115, notes 2 and 3). SPI1 and SPI3 transmit at
  up to 43 MHz as a slave, above the ROCK 5T's 37.5 MHz.
- **Jumpers for the second SPI,** one set of header pins for the ROCK 5T and
  another for the Raspberry Pi. The lines went to both sets through 33 Ω, the other set a stub
  of a few centimetres that 37.5 MHz bears; with the Pi gone only the ROCK's is left.
- **A strip over the header and a wing past the computer's edge,** the first layout.
  The wing stuck out of the computer's outline and made the backpack's insert wider; one board
  over the whole ROCK on an extra-tall header keeps the stack inside its 110 × 82 mm, over the SoC
  (see [construction](CONSTRUCTION.md#the-stack)).
- **Taking 5 V or 3.3 V from the header.** Mamka runs from the battery and feeds herself, and
  she could feed a switched-off computer back through its pins' protection diodes; so she takes
  only the data pins and the grounds, and pin 1's 3.3 V as the signal "Baťa is up".
- **Header pin 22 for "data ready".** It is a 1.8 V ADC input on the ROCK 5T; pin 36 is a plain
  GPIO.
- **An STM32H523 for processor 1.** Its 272 KB would spare ~192 KB for the ring, ~0.08 s of
  cycles for Baťa; the STM32H562's 640 KB give a ring of 512 KB, ~0.22 s. For processor 2 the
  STM32H523 might still do (no SAI, so the sound through an SPI in I2S mode); both are the
  STM32H562VG or the STM32H563VG, one footprint and one firmware base.
- **The LQFP64** (to 24 Oct 2026). Processor 2 needs 48 I/Os of its 49, and it lacks PB9 and
  PB11, pins 62 and 30–32 being VCAP and the supply (ST's pin data); both processors are in
  LQFP100, 80 I/Os.
- **The STM32H563 in its SMPS version,** the ...Q, its core fed by a converter of its own: a
  2.2 µH inductor, 4.7 µF of at most 10 mΩ, 10 µF on VCAP and 220 pF on VLXSMPS (DS14258 Rev 6,
  table 23), a converter switching beside the clock's buffers to save a fraction of a watt, and
  JLCPCB stocks none (31 Oct 2026). The LDO version, the STM32H563VGT6, takes the STM32H562VG's
  place as it is.
- **The RP1's UARTs for the lines,** on the Raspberry Pi. They reach 6.25 Mbit/s at most,
  without DMA; the lines run at 19.66 Mbaud into the STM32H562.
- **Processor 1's UART to Baťa,** on header pins 8 and 10 until 22 Oct 2026, for the modules'
  chip settings and firmware, a leftover of the Raspberry Pi. The SPIs are full duplex and carry
  those down in places of their own, ~2.9 MB/s against the UART's ~150 kB/s; the UART went to
  processor 2 instead of the I2C.
- **The I2C control channel,** I2C7_M3 on header pins 3 and 5 with processor 2 as the slave at
  0x5C, until 22 Oct 2026. It needed an overlay of our own with the ROCK's audio codec, the ES8316,
  turned off, which Radxa offers for the Industrial only, ran at 40–100 kB/s and needed a pin for
  "a message waiting". Processor 2's UART on pins 8 and 10 carried the same at ~150 kB/s with no
  overlay and no pin, until it went too (below).
- **The ROCK's console as processor 2's channel,** UART2_M0 on header pins 8 and 10, from 22 to
  24 Oct 2026. It is the ROCK 5T's debug console at 1.5 Mbaud, ~150 kB/s, and needed three rules
  to keep it apart from the boot loader and the kernel: processor 2 silent until Baťa spoke, a
  boot loader that never stops on a key, no console in Linux. A SPI of her own, SPI3_M0 on pins
  18, 27 and 28, carries half of processor 2's stripe at 11.1 MHz and leaves the console to the
  ROCK.
- **The ROCK 5T Industrial V2.01.** It has GPIO2_B2 and B3 on header pins 27 and 28, where the V1.2
  has SPI3_M0 (the schematics V1.2 and V2.01, sheets 13 and 36), so it gives Mamka two SPIs, not
  three. Besides, its RK3588J runs its big cores to 1.6 GHz and its small to 1.29 GHz, where the
  RK3588 runs them to 2.4 and 1.8 GHz (Radxa Docs, ROCK 5T Introduction), so the assistants on
  cpu4–5 would run ~1.5 times slower; its board is rated −40 to 85 °C, the V1.2's 0 to 60 °C
  (radxa.com, the ROCK 5T's page). Neither states a coating or a humidity. The V1.2 was chosen for
  the third SPI, at the cost of the narrower range (24 Oct 2026): a start below 0 °C is not
  guaranteed, and the backpack worn on the body is to keep it above.
- **Processor 2 through processor 1,** her frames over the link into processor 1's two SPIs,
  weighed on 24 Oct 2026: no third SPI was needed then, but processor 2 could reach Baťa only
  through processor 1, and processor 1 would carry DMA channels for both. Each has her own SPIs.
- **SPI0_M2 at 37.5 MHz for processor 1,** striped with SPI1_M1 (to 24 Oct 2026). Its pins
  pass a UM3204 on the ROCK's board, 24 Mbps at most (UM3204 Rev.16), so ~11 MHz. SPI1_M1, the
  one SPI straight from a 3.3 V bank, carries the limbs alone at 50 %; SPI0_M2 and SPI3_M0, both
  behind translators, are processor 2's, striped.
- **A sender for each line,** until 24 Oct 2026, a DMA channel each. One sender drives a
  processor's lines' drivers at once, since little goes down and every unit takes only what its
  address names; each line keeps a receiver and a channel of its own, all of them sending up at
  once (see [Porjadok](../porjadok/WHY.md)).
- **A link at 19.66 Mbaud between the processors,** LPUART1 with frames of 37 B both ways (24 Oct
  2026, the same day): the limbs' power by a register, the first *start* timed by a mark byte
  polled with the interrupts masked. Four wires do it more simply: the START edge into a timer
  that triggers the DMA, the limbs' PGOOD read by both, and a UART at 115,200 Bd for a frame of
  34 B a second.
- **Data in the I2S,** in the 16 spare bits of each 32-bit slot, ~192 kB/s each way, as DoP
  carries DSD inside PCM. The ROCK's I2S2 is a two-channel one (`i2s2_2ch`, `rk3588-base.dtsi`),
  the sound stays bit-exact only straight from ALSA's hardware device and not through PipeWire,
  and the sound should stay sound; the head's data go on the SPIs.
- **A tunnel through Mamka between two computers,** a UART between them, or a Mamka with a
  processor for each. Baťa and Borovičok talk over UDP on Ethernet; Mamka stays out of it.

## The clock

- **The computer on the suit's clock.** The RK3588 takes no outside clock and runs from its
  24 MHz, as the retired Raspberry Pi's RP1 ran its PLLs from its own 50 MHz crystal.
  The samples are taken on the suit's clock in the units, and the sound comes over I2S with the
  computer as the slave, so it does not matter.
- **The family of 44.1 kHz,** an oscillator of 11.2896 MHz (256 × 44.1 kHz) instead of
  9.8304 MHz, weighed on 22 Oct 2026. It holds together: one PLL (× 30, ÷ 2: 169.344 MHz), the
  ADS1299 at ÷ 6 (1.8816 MHz) and 3,675 SPS, the lines at 18.816 Mbaud with 512 B a cycle as
  now, the sound straight from the HSE with exactly 12 samples a cycle. But no IMU step comes
  out at 120 Hz, only 75, 105 or 147 Hz, so the snapshots no longer fall on a screen's rates,
  and the speech models' 16 kHz is no longer a whole division of the sound; the family of 120
  stays, and music in 44.1 kHz is PipeWire's to convert.
- **Dividing the clock on Mamka** before it goes down the lines. The buffers hand the 9.8304 MHz
  out undivided, and every block divides it itself; one frequency on every line, one driver per
  line.
- **The clock through processor 1,** until 11 Oct 2026: the oscillator into its HSE, its MCO1 to
  the lines' buffers and MCO2 to processor 2, the buffers gated by one pin. A reset or a fault
  in processor 1 stopped the clock of the whole suit. The oscillator now feeds the buffers
  itself.
- **A line's clock by its driver's DE,** a processor pin each, from 11 to 24 Oct 2026, **or the
  DE tied on** (24 Oct, afternoon). Each processor switches her own lines' clock drivers on one
  pin: the clock runs from her start until the suit is off, and ~0.3 A of the eight drivers comes
  off while her lines are off or asleep.

## The power

- **Processor 2 always alive on the battery,** waiting for the power button. Mamka's own 3.3 V
  with two processors and the drivers' receivers would draw ~0.3 W or more with the suit off,
  and the 256 Wh pack would be flat in a month. Budilnik holds the converter off instead: the
  button wakes it, processor 2 holds it, and the suit switches itself off completely.
- **A polymer bulk at Mamka's outputs.** The lines' inputs are damped at the modules, where the
  cables arrive; one here would only add to what each converter charges at start.
- **A polymer bulk wherever a cable arrives,** the house rule to 31 Oct 2026: a POSCAP at every
  unit's input, ~110 µF on 4 V for a converter to charge at start. An RC, 22 µF behind 0.5 Ω,
  damps a module plugged into a live line under its parts' ratings and leaves ~26 µF (see
  [hardware](HARDWARE.md#filtering); the POSCAPs themselves in [Rubaška](../rubaska/WHY.md)).
  Polymers stay only where a ceramic cannot do it: the battery input, Míša's input, Nataša's
  motors.
- **The LMR43610R3, the RT version at 2.2 MHz** (to 31 Oct 2026). With RT on ground it ran at
  2.2 MHz with no part and no trace, but it costs four times the MB3 version fixed at 1 MHz,
  $10.26 against $2.12 at JLCPCB, ~$75 more a suit by the thousand; at 1 MHz the chain of filters
  still takes ~59 dB a stage, and the MB3's pin 1 gives the forced PWM the 6 V converter wants.
- **A sync to the suit's clock** for the converters. At 983.04 kHz, the suit clock ÷ 10, they
  would switch at twice the ADS1298's modulator, and their ripple would fold to DC; free running
  near 1 MHz it lands ~17 kHz away, which the filters and the decimation take.
- **One 4 V converter for the whole suit.** One per line: a short or a faulty module takes down
  only its line, the lines come up one after another, and the battery takes one line's inrush
  at a time.
- **A MOSFET and a diode for the fan.** A 4-pin PWM fan has its own driver inside; Mamka gives it
  5 V, a PWM and reads its speed.
- **A converter for the ROCK 5T.** Its DC jack takes 9–20 V, and the pack gives 10–14.6 V; it
  runs straight from the battery through its eFuse here.
- **A bare P-MOSFET as the ROCK 5T's switch.** At 14.6 V its gate needs a level shifter and a
  slow turn-on anyway, three or four parts with no current limit; an eFuse brings the limit, the
  soft start, the under- and overvoltage cutoffs and an enable in one part, and the branch is
  protected like every other.
- **The TPS26630 as the ROCK's eFuse** (to 31 Oct 2026): 4.5–60 V, 6 A, 31 mΩ, in VQFN-24 of
  4 × 4 mm (SLVSE94G), at $13.26 against the TPS259474L's $1.29 at JLCPCB, ~$10 more a ROCK by
  the thousand. The pack gives at most 14.6 V, and its ring on plugging in, 15.1–23.8 V by an
  estimate, stays under the TPS259474L's 28 V (see
  [hardware](HARDWARE.md#the-computers-supply)). Tokmas's and Maxinmicro's copies of the
  TPS26630, $1.16 and $0.77, lost to TI's own part at that price.
- **CAN to the BMS.** The JK BMS speaks RS485 Modbus too, and the THVD1450 is already on the
  board for the lines' clock.
- **A GPS in a box of its own, or on USB.** The module sits on Mamka with a UART to processor 2,
  its antenna on the shoulder strap; its PPS goes into a timer that counts the suit clock.

## The stack

- **Radxa's Heatsink 6240B on the SoC** (to 31 Oct 2026): 62 × 40 × 9 mm of aluminium with its
  own 5 V fan, pressed by two pegs into the ROCK's board, ~13.5 mm of air between it and Mamka.
  Inside Mrazík, the closed block round the stack, its fan would only stir the air shut in with
  it; a boss of the block's top wall through a window in Mamka takes the SoC's heat to the fins
  outside (see [construction](CONSTRUCTION.md#the-stack)).
