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
- **Jumpers for the second SPI,** in version 0.1, one set of header pins for the ROCK 5T and
  another for the Raspberry Pi. The lines went to both sets through 33 Ω, the other set a stub
  of a few centimetres that 37.5 MHz bears; with the Pi retired in 0.2 only the ROCK's is left.
- **A strip over the header and a wing past the computer's edge,** the layout of version 0.1.
  The wing stuck out of the computer's outline and made the backpack's insert wider; one board
  over the whole ROCK on an extra-tall header keeps the stack inside its 110 × 82 mm, over the SoC's
  heatsink (see [construction](CONSTRUCTION.md#the-stack)).
- **Taking 5 V or 3.3 V from the header.** Mamka runs from the battery and feeds herself, and
  she could feed a switched-off computer back through its pins' protection diodes; so she takes
  only the data pins and the grounds, and pin 1's 3.3 V as the signal "Baťa is up".
- **Header pin 22 for "data ready".** It is a 1.8 V ADC input on the ROCK 5T; pin 36 is a plain
  GPIO.
- **An STM32H523 for processor 1.** Its 272 KB would spare ~192 KB for the ring, ~65 ms of
  cycles for Baťa; the STM32H562's 640 KB give a ring of 512 KB, ~178 ms. For processor 2 the
  STM32H523 might still do (no SAI, so the sound through an SPI in I2S mode); for now both are
  STM32H562, one part and one firmware base.
- **The STM32H563.** The same memory plus Ethernet and a second SDMMC, which Mamka does not
  need: the network is Baťa's.
- **The RP1's UARTs for the lines,** on the Raspberry Pi of 0.1. They reach 6.25 Mbit/s at most,
  without DMA; the lines run at 19.66 Mbaud into the STM32H562.
- **A tunnel through Mamka between two computers,** a UART between them, or a Mamka with a
  processor for each. Baťa and Deduška talk over UDP on Ethernet; Mamka stays out of it.

## The clock

- **The computer on the suit's clock.** The RK3588 takes no outside clock and runs from its
  24 MHz, as the retired Raspberry Pi's RP1 ran its PLLs from its own 50 MHz crystal.
  The samples are taken on the suit's clock in the blocks, and the sound comes over I2S with the
  computer as the slave, so it does not matter.
- **Dividing the clock on Mamka** before it goes down the lines. The buffers hand the 9.8304 MHz
  out undivided, and every block divides it itself; one frequency on every line, one driver per
  line.
- **The clock through processor 1,** until 11 Oct 2026: the oscillator into its HSE, its MCO1 to
  the lines' buffers and MCO2 to processor 2, the buffers gated by one pin. A reset or a fault
  in processor 1 stopped the clock of the whole suit. The oscillator now feeds the buffers
  itself, and a line's clock goes by its driver's DE.

## The power

- **Processor 2 always alive on the battery,** waiting for the power button. Mamka's own 3.3 V
  with two processors and the drivers' receivers would draw ~0.3 W or more with the suit off,
  and the 244 Wh pack would be flat in a month. Budilnik holds the converter off instead: the
  button wakes it, processor 2 holds it, and the suit switches itself off completely.
- **A polymer bulk at Mamka's outputs.** The lines' bulks sit at the modules, where the cables
  arrive; one here would only add to what each converter charges at start.
- **A resistor on RT, a sync to the suit's clock, or forced PWM** for the converters. With RT on
  ground the LMR43610 runs at 2.2 MHz with no part and no trace; the chain of filters takes 2 MHz
  down by ~70 dB a stage, so neither the exact frequency nor the light-load pulse mode matters.
- **One 4 V converter for the whole suit.** One per line: a short or a faulty module takes down
  only its line, the lines come up one after another, and the battery takes one line's inrush
  at a time.
- **A MOSFET and a diode for the fan.** A 4-pin PWM fan has its own driver inside; Mamka gives it
  5 V, a PWM and reads its speed.
- **A converter for the ROCK 5T.** Its DC jack takes 9–20 V, and the pack gives ~11.5–16 V; it
  runs straight from the battery through its eFuse here.
- **A bare P-MOSFET as the ROCK 5T's switch.** At 16 V its gate needs a level shifter and a
  slow turn-on anyway, three or four parts with no current limit; the TPS26630 eFuse brings the
  limit, the soft start, the under- and overvoltage cutoffs and a shutdown pin in one part, and
  the branch is protected like every other.
- **CAN to the BMS.** The JK BMS speaks RS485 Modbus too, and the THVD1450 is already on the
  board for the lines' clock.
- **A GPS in a box of its own, or on USB.** The module sits on Mamka with a UART to processor 2,
  its antenna on the shoulder strap; its PPS goes into a timer that counts the suit clock.
