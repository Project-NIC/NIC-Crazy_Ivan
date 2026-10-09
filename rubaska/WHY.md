<div align="center">

# Rubaška: why not

**The graveyard: what was considered for the suit and why it is not used.**

↑ [Rubaška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Each entry says what it was and why it went, so that nobody digs it up without knowing. Where a
thing waits in reserve, it says so.

## The sensing module

- **SPI to the IMUs over a cable.** Every IMU would want its own chip select and five or six
  wires, eight or nine into a finger with the drivers. I3C puts two IMUs on five wires, SCL,
  SDA, power and CLKIN, at a rate far below its 12.5 MHz. No SPI runs over a cable anywhere.
- **The IMU clock over I3C** (synchronous timing control, SETXTIME) instead of the CLKIN wire.
  ST's documents disagree on whether the STM32H5's controller has it, and the ICM-42688-P
  documents its sample rates only from CLKIN (DS-000347, 12.5). The wire stays.
- **SPI4 for the ADS1299.** It takes frames of 4 to 16 bits only (DS14540, table 10); the
  ADS1299's 24-bit words want SPI1 to SPI3, which take up to 32.
- **PC13 to PC15 for the LED.** They hang on the backup domain's power switch, 2 MHz and 30 pF at
  most and no current to source (DS14540, table 13, note 2).
- **PB3 or PA8 for I3C2's SCL.** PB3 is the only pin with SWO, PA8 the only one with TIM1_CH1
  for CLKIN, so I3C2 takes PB5 and PB4, which have no Fm+ drive; I3C carries 12 B per IMU 1,200
  times a second with ease, and as I2C at 400 kHz the IMUs run the chip's own 120 Hz.
- **An LDO for every branch.** Earlier drafts had one; the π filters of the house rule do the job
  behind two LDOs, one for the 5 V analog side and one for the 3.3 V rest.
- **Microamp lead-off currents** (6 or 24 µA). Through a 50 kΩ contact they make 0.3 or 1.2 V,
  beyond the ±187.5 mV input range at a gain of 24. Only 6 or 24 nA are usable.
- **A lead of its own for the bias electrode.** Channel 8's multiplexer routes BIASIN to IN8N
  instead (MUX = BIAS_DRN), so the electrode connector keeps its 16 positions and the input's
  4.99 kΩ protects the bias path.
- **The BIASINV wire between the ADS1299s** that the datasheet's figure 39 draws. A
  high-impedance node on a metre of cable would pick up the mains; one module's channels sense
  the body's common voltage well enough, since the body is one conductor.
- **Line drivers on Interconnect** between the forearm's module and the Vnučata. The distances
  are centimetres; a half-duplex open-drain UART wire does.

## The IMU

- **A magnetometer.** Indoors the steel of a building bends the Earth's field differently from
  place to place, so no calibration takes it out. The joints do not need it: across a joint the
  turn about the vertical is pinned by the two IMUs sharing the joint's centre. Only which way
  the whole body faces in the room stays unseen, and if that ever matters, one magnetometer on
  the trunk comes back, not one per IMU.
- **The chip's own 120 Hz as the only mode.** It was the first choice: the 100 Hz setting under
  CLKIN, filtered and decimated in the chip, nothing to compute. In noise it equals the sum of
  ten samples at 1,200 Hz, but a step of 8.3 ms taken as one rotation misses the coning term
  when a piece turns about two axes at once, a few degrees by the end of a fast swing; Movella's
  MTw integrates at 1,000 Hz on the sensor for that reason. The block now sums at 1,200 Hz, and
  the chip's 120 Hz stays a mode for the I2C fallback and for comparison.
- **Bosch BMI570.** Lower noise on paper, but we found no external clock input, and the suit
  runs every sensor from one clock.
- **ICM-45686.** The same family's newer part; it would reach 120 Hz too, but its gyro is noisier
  (3.8 against 2.8 mdps/√Hz) and its CLKIN takes 20–40 kHz. The noise decided for the
  ICM-42688-P.

## The electrodes and the suit

- **Ag/AgCl or titanium electrodes.** Out on price for 254 of them. Stainless steel has more
  low-frequency noise and drift, which EMG bears.
- **316Ti steel.** Its titanium protects the steel at welding temperatures, not on the skin;
  316L, the steel of body jewellery, does.
- **Dry electrodes.** A dry contact is ~1 MΩ, which the ADS1299's input would bear but the input
  filter would not: its corner falls to ~360 Hz, inside the band. A moist ring keeps the
  contact at tens of kilohms.
- **A low-noise cable with a graphite layer** for the leads, as for piezo sensors. With a moist
  contact the charge from friction makes some twenty times less voltage, so an ordinary shielded
  flat cable does; the graphite cable stays in reserve should the sample tests say otherwise.
- **A conductive fabric.** It would short the electrodes or carry crosstalk between them. A
  static-dissipative one, gigaohms between neighbouring electrodes, drains charge without
  shorting signals.
- **Synthetics and plastic in the fabric.** They sit at the ends of the triboelectric series;
  cotton sits near its middle.
- **Silver in the fabric.** Too expensive; carbon-fibre grids are sold for antistatic workwear.
- **Taking the cables off for every wash.** It would wear them out sooner than wearing the suit
  does. The harness is rinsed with the cables on; only the units unplug.
- **Pressure insoles in the shoes** as a part of the suit. The contact points come out of the
  model from the EMG and the IMUs; a bought insole may serve once, at recording time, as the
  truth about heel and toe for the model to learn from, then goes back in the drawer.
- **Cables across the backs of the fingers.** They would bend with every grip; the cables run
  along the sides of the fingers.
