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
- **Jumpers for the second SPI,** one set of header pins for the ROCK 5T and another for the
  Raspberry Pi. The lines go to both sets through 33 Ω; on each computer the other set is a
  plain GPIO left as an input, a stub of a few centimetres that 37.5 MHz bears.
- **Taking 5 V or 3.3 V from the header.** Mamka runs from the battery and feeds herself, and
  she could feed a switched-off computer back through its pins' protection diodes; so she takes
  only the data pins and the grounds, and pin 1's 3.3 V as the signal "Baťa is up".
- **Header pin 22 for "data ready".** It is a 1.8 V ADC input on the ROCK 5T; pin 36 is a plain
  GPIO on both computers.
- **An STM32H523 for processor 1.** Its 272 KB would spare ~192 KB for the ring, ~65 ms of
  cycles for Baťa; the STM32H562's 640 KB give a ring of 512 KB, ~178 ms. For processor 2 the
  STM32H523 might still do (no SAI, so the sound through an SPI in I2S mode); for now both are
  STM32H562, one part and one firmware base.
- **The STM32H563.** The same memory plus Ethernet and a second SDMMC, which Mamka does not
  need: the network is Baťa's.
- **The RP1's UARTs for the lines.** They reach 6.25 Mbit/s at most, without DMA; the lines run
  at 19.66 Mbaud into the STM32H562.
- **A tunnel through Mamka between two computers,** a UART between them, or a Mamka with a
  processor for each. Baťa and Deduška talk over UDP on Ethernet; Mamka stays out of it.

## The clock

- **The computers on the suit's clock.** Neither takes an outside clock: the RP1's PLLs run from
  its own 50 MHz crystal and none of its clock sources is a GPIO; the RK3588 runs from its 24 MHz.
  The samples are taken on the suit's clock in the blocks, and the sound comes over I2S with the
  computer as the slave, so it does not matter.
- **Dividing the clock on Mamka** before it goes down the lines. MCO1 hands the 9.8304 MHz out
  undivided, and every block divides it itself; one frequency on every line, one driver per line.

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
- **One 3.7 V converter for the whole suit.** One per line: a short or a faulty module takes down
  only its line, the lines come up one after another, and the battery takes one line's inrush
  at a time.
- **A MOSFET and a diode for the fan.** A 4-pin PWM fan has its own driver inside; Mamka gives it
  5 V, a PWM and reads its speed.
- **CAN to the BMS.** The JK BMS speaks RS485 Modbus too, and the THVD1450 is already on the
  board for the lines' clock.
- **A GPS in a box of its own, or on USB.** The module sits on Mamka with a UART to processor 2,
  its antenna on the shoulder strap; its PPS goes into a timer that counts the suit clock.
