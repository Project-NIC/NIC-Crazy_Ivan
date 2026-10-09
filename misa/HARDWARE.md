<div align="center">

# Míša: hardware

**The unit on the forehead:** the radar and the ultrasound, the board, the parts, the processor's
pins, and the radar beside the EMG.

↑ [Míša](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## Radar and ultrasound

| | radar | ultrasound |
|---|---|---|
| tells | distance, angle and speed | distance only |
| angle | ~30° across, ~60° up and down | none: anywhere in its beam |
| speed | measured directly (Doppler) | from two readings in a row |
| glass | only part of 60 GHz comes back from it | comes back, the reason it is here |
| hides | behind fabric and plastic | needs a hole and a horn |

- **The radar is the main sensor:** it sees where things are and how fast they come, a car at
  the roadside included, and it hides in the headband.
- **The ultrasound is the safety net:** it sees glass doors and shop windows, which give the
  radar only a weak echo.
- **No camera in Míša:** a camera brings a model of its own, with its power and computing on
  top of the muscles' model. Ďaďa Sem, the cameras on Baťa's second Umnica (see
  [Baťa](../bata/README.md)), can add one where the backpack allows it.

## The board

| part | package | count | what it does |
|---|---|---|---|
| STM32H523 | UFQFPN48 or LQFP64 | 1 | the processor, as in every module |
| SiTime SiT8008BI-21-33N-9.830400D | 3.2 × 2.5 mm | 1 | 9.8304 MHz, the suit's oscillator as on Mamka: ±20 ppm in all over −40…+85 °C |
| Jorjin MT5C01-03 | module 15.5 × 7.0 mm, on a Hirose BM23PF0.8-14DS-0.35V | 1 | the radar, see below |
| ICM-42688-P | LGA-14, 2.5 × 3 × 0.91 mm | 1 | the IMU: the head's tilt from gravity, short turns from the gyro |
| ICU-20201 | LGA-14, 3.5 × 3.5 × 1.26 mm | 1 | the ultrasound ahead, in a 45° horn |
| TPS62850x | SOT583, 2.1 × 1.6 mm | 3 | 3.7 V to 3.3 V, 1.8 V and 1.2 V for the radar module, after Jorjin's reference design (2.7–6 V in, 2 A) |
| TPS7A2018 | X2SON, 1 × 1 mm | 1 | 3.3 → 1.8 V for the ultrasonic sensor's core |
| 6TPE220MI | case D2E, 7.3 × 4.3 × 1.8 mm | 1 | the polymer bulk at the 3.7 V input: 220 µF, 18 mΩ, 105 °C, which bridges the converters' loops during a chirp |
| socket | to choose | 3 | more ultrasonic sensors, on boards of their own: the temples and the nape |

- **The radar to the processor:** its UART, and its reset and SOP0, so the processor can put it
  into flashing mode and load new radar firmware; the radar can be updated through the suit.
- **The ultrasonic sensors:** one SPI with a chip select each and no interrupt lines, as below.
- **To Nataša:** a UART both ways, 3.7 V and ground, four wires. The UART runs at exactly
  1,228,800 Bd, an exact division on both sides: the PLL's 196.608 MHz ÷ 160, since the USART's
  kernel clock comes from the PLL or the bus, not from the HSE (RM0481, RCC_CCIPR1); it is the
  9.8304 MHz ÷ 8.
- **Its own oscillator of the suit's frequency:** Míša needs no clock wire. Its 9.8304 MHz and
  the suit's are at most 40 ppm apart, ±20 ppm each, so the UART's rates differ by 0.004%, far
  inside the few percent a UART tolerates. Its frames still keep to the suit's clock: Nataša
  sends a *measure* container with the sample number every 240 cycles of the suit, 16 times a
  second (see [Radar and the EMG](#radar-and-the-emg) and
  [Nataša](../natasa/SOFTWARE.md#míšas-wire)).

## The processor's pins

Míša's STM32H523 is the block's **STM32H523CCU6** in UFQFPN48, 35 I/Os, and keeps the block's
pins wherever the job is the same, so the numbers below are the block's (DS14540, figure 6 and
tables 14 and 15; see [Rubaška](../rubaska/HARDWARE.md#sensing-module), *The processor's pins*).
She needs 23:

| what | pins | where |
|---|---|---|
| her own oscillator | 1 | PH0-OSC_IN (5), the HSE in bypass, as the suit clock on a block |
| the radar: its UART, NRESET, SOP0, its host interrupt | 5 | USART1_TX PA9 (30), USART1_RX PA10 (31), AF7; NRESET PA11 (32) and SOP0 PA12 (33), outputs; the interrupt PA15 (38), an input on EXTI15 |
| the radar's supplies: EN of its three converters together | 1 | PB10 (21), an output, so the processor can power the module down and up |
| the ultrasonic sensors: one SPI and a chip select each | 7 | SPI1 (AF5): SCK PA5 (15), MISO PA6 (16), MOSI PA7 (17), mode 3, at most 13 MHz (DS-000478), 78.6432 MHz ÷ 8 = 9.83 MHz; CS as outputs: the sensor on the board PA4 (14), the three sockets PB0, PB1, PB2 (18–20) |
| the IMU: one I3C bus and CLKIN | 3 | I3C1_SCL PB6 (42), I3C1_SDA PB7 (43), AF3; CLKIN from TIM1_CH1 on PA8 (29), AF1, 38,400 Hz from her own 9.8304 MHz ÷ 256 |
| the wire to Nataša | 2 | USART2_TX PA2 (12), USART2_RX PA3 (13), AF7, 1,228,800 Bd |
| SWD and SWO | 3 | PA13 (34), PA14 (37), PB3 (39), AF0 |
| status LED | 1 | PB12 (25), as on a block |
| **total** | **23** | 12 I/Os free |

- **The block's pins where the job is the same:** the oscillator, SPI1, I3C1, CLKIN, SWD and the
  LED sit where the block has them, so the IMU and clock code carry over unchanged. SPI1 serves
  the ultrasonic sensors instead of an ADS1299; the sensors have no interrupt lines, so a
  measurement is started by a write and its end read or waited for (see
  [the ultrasonic sensor](#the-ultrasonic-sensor)).
- **The radar** talks over USART1 with the suit's line pins free, since Míša hangs on no line;
  TI's UART rates are the firmware's business. NRESET and SOP0 let the processor put the module
  into its flashing mode (see [the board](#the-board)); the exact pin names on the MT5C01-03's
  connector are to be read in Jorjin's sheet. Its host interrupt says when a frame of points is
  ready.
- **The IMU** runs at 1,200 Hz as in a block, from the CLKIN that Míša makes herself, and the
  processor sums its steps the same way; its 12 B a step go into the sphere's header as the
  head's turn and pitch, not up the line.
- BOOT0 to ground through 10 kΩ, NRST to the SWD pads, 2.2 µF on each VCAP (DS14540, table 21),
  PC13 to PC15 left free (table 13, note 2), as on a block. Should LQFP64 be chosen for the
  layout, the pins keep their names and only their numbers change.

## The radar

The **Jorjin MT5C01-03** carries a TI **IWRL6432AOP** with its antennas in the package, a 40 MHz
crystal and a 16 Mbit flash (Jorjin's datasheet MT5C01-03-DTS-R01; TI's SWRS323B).

| | MT5C01-03 |
|---|---|
| field of view | 140° across, 120° up and down |
| range | 15 m ahead and 7 m at the edges, for detecting motion |
| antennas | 2 transmit and 3 receive, a 2 × 4 virtual array |
| power | 11 mW on average at 10 frames a second, 2 Tx and 3 Rx, deep sleep between frames; ~0.96 W while chirping, so ~1 ms of chirping a frame; at Míša's 16 frames a second ~18 mW |
| peaks | 1.1 A on 1.2 V, 270 mA on 1.8 V, 90 mA on 3.3 V at most |
| processor | Arm Cortex-M4F at 160 MHz, ours to program, and a hardware accelerator for the FFTs |
| interfaces | UART, SPI whose clock and select double as I2C, a host interrupt, one GPIO |
| supply | 1.2 V, 1.8 V and the I/O at 3.3 V or 1.8 V |
| cover | polycarbonate 1.5 mm thick over a 2.5 mm air gap; PP, PE and PTFE lose less |

- **It sends points:** each a distance, an angle and a speed. Míša's processor sorts them into
  the map.
- **Resolution:** ~30° across from four virtual antennas and ~60° up and down from two, by the
  rule of thumb of 2 / N radians; Mistral's module with the IWR6843AOP states 29° for four. The
  distance resolves to ~7.5 cm over a 2 GHz sweep.
- **Speed:** with two transmitters taking turns and ~31 µs chirps the unambiguous speed is
  about ±20 m/s (72 km/h) towards the wearer, by the physics. A faster car folds over; the
  chirps are to be tuned.

## The ultrasonic sensor

The **TDK ICU-20201** (datasheet DS-000478): a MEMS ultrasonic transducer and a processor of its
own in one 3.5 × 3.5 × 1.26 mm package. It sends the pulse, listens and works out the distance
itself.

| | ICU-20201 |
|---|---|
| range | 20 cm to 5 m to a wall and 2.7 m to a 58 mm post, both with a 45° horn; people at 3–4 m |
| reports | up to five echoes a measurement, each a distance and an amplitude, no angle (AN-000329) |
| sees | glass and clear plastic too |
| frequency | ~85 kHz, 70–95 kHz from part to part |
| one measurement | 6.5 ms to 1 m, 30 ms to 5 m |
| current | 26 µA at one measurement a second to 5 m, 296 µA at 25; 9 µA idle |
| supply | the core 1.71–1.89 V, the I/O 1.71–3.63 V, so 3.3 V and no translators |
| bus | SPI up to 13 MHz, mode 3 |
| firmware | loaded at every power-on, 5,882 B of code and 566 B of initial data in TDK's SonicLib (BSD licence) |

- **No interrupt lines:** a measurement starts with an SPI write (software-triggered mode,
  DS-000478 section 4.4.3), the sensor's clock takes its calibration from the factory
  (SonicLib), and the end of a measurement is read over SPI or simply waited for.
- **The horns:** the bare sensor sends into nearly half a sphere, and against intuition a wider
  horn gives a narrower beam (DS-000478, section 3.1.1). TDK offers 3D models of horns for the
  CH201, which has the same package and frequency: 45° × 45°, 160° × 40° and 180° × 180°
  (PB-000084, PB-000086, PB-000092). The datasheet's ranges were measured with the 45° one and
  a particle ingress filter, against dust and sweat.
- **Ahead, 45°:** from a forehead ~1.65 m above the floor, the beam's lower edge reaches the
  floor ~4 m ahead, past the 2–3 m that Míša watches.
- **The nape, 160° × 40°, if wanted:** one sensor watches the whole back half, a bumper for
  stepping back in VR glasses; its 40° keep the floor out to ~4.4 m.
- **They hear each other** at under 10 m when their frequencies are close (DS-000478, section
  4.5): sensors on one head, and two people in suits side by side. They take turns, started at a
  precise rate from Míša's oscillator; a foreign pulse then comes at the same moment every time and
  the stationary-target filter drops it.

## Radar and the EMG

The radar draws ~1 W while it chirps, about a millisecond a frame. At 10 frames a second those
bursts have harmonics at 10, 20, 30 … Hz, right in the EMG band up to ~500 Hz.

- **The head line has a converter of its own** on Mamka and its own π filter, so the bursts do
  not share a supply with the body; each module's analog side has its own TPS7A47. What is left
  is the common ground at Mamka and the field around the current loop, worst with a module of
  electrodes in the headband next to Míša.
- **The frames keep to the suit's clock:** 16 Hz is 3,840 / 240, so every frame starts on the
  same ADS sample. Whatever reaches the EMG is then a fixed pattern on exact multiples of 16 Hz,
  which Baťa averages and takes away; Baťa knows when the radar chirped.
- **The radar's 60 GHz itself** hardly reaches the leads: at a 5 mm wavelength they are poor
  antennas, and it sends +15 dBm EIRP. The ADS1299's datasheet advises small common-mode
  capacitors at the inputs, 10–20 times smaller than the differential one, where a system meets
  high-frequency interference; they are added if a measurement asks for them.
- **Bulk capacitors** on Míša's board soften the bursts' edges, the higher harmonics.

## Open questions

- first a trial: Jorjin's evaluation board MT5C01E02R1, or TI's IWRL6432AOPEVM, on Baťa: glass
  doors, a post, a car at the roadside, the fields and the two conditions, before a board is
  drawn,
- whether the MT5C01-03 can be bought in small numbers, and its price,
- the EMG beside the radar: a module next to the evaluation board, its noise with the radar
  off, free at 10 Hz and locked at 16 Hz,
- whether the CH201's horns fit the ICU-20201,
- the ultrasound without INT1: the end of a measurement over SPI (only some sensor firmware) or
  waited for, and whether an unused INT1, an open drain, wants a pull-up,
- Míša's current peaks against the head line's converter, measured: on paper a chirp is ~0.63 A
  from the 3.7 V for ~1 ms (2.1 W at ~90%), ~1.05 A with Nataša's two motors, under the
  converter's limit of at least 1.13 A (see [Nataša](../natasa/HARDWARE.md#power)).
