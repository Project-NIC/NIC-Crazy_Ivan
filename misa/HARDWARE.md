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
  top of the muscles' model. Ďaďa Sem, the cameras on Baťa's NPUs (see
  [Baťa](../bata/README.md)), can add one where the backpack allows it.

## The board

| part | package | count | what it does |
|---|---|---|---|
| STM32H523 | UFQFPN48 or LQFP64 | 1 | the processor, as in every module |
| THVD1452 | VSSOP-10, or SOIC-14 | 1 | line 8's return pair (see [Porjadok](../porjadok/HARDWARE.md#drivers-on-a-unit)) |
| AM26LV32E | VQFN-16, 3.5 × 4 mm | 1 | line 8's pair from Mamka, the echo and the suit's clock |
| Jorjin MT5C01-03 | module 15.5 × 7.0 mm, on a Hirose BM23PF0.8-14DS-0.35V | 1 | the radar, see below |
| LSM6DSV16X | LGA-14L, 2.5 × 3 × 0.83 mm | 1 | the IMU, the suit's: the head's tilt from gravity, short turns from the gyro; 100 nF at each supply pin and 1 kΩ in series with INT2, as on the IMU board (see [Rubaška](../rubaska/HARDWARE.md#the-imu)) |
| ICU-20201 | LGA-14, 3.5 × 3.5 × 1.26 mm | 1 | the ultrasound ahead, in a 45° horn |
| TPS62850x | SOT583, 2.1 × 1.6 mm | 3 | 4 V to 3.3 V, 1.8 V and 1.2 V for the radar module, after Jorjin's reference design (2.7–6 V in, 2 A) |
| TPS7A2018 | X2SON, 1 × 1 mm | 1 | 3.3 → 1.8 V for the ultrasonic sensor's core |
| 6TPE220MI | case D2E, 7.3 × 4.3 × 1.8 mm | 1 | the polymer bulk at the 4 V input: 220 µF, 18 mΩ, 105 °C, which bridges the converters' loops during a chirp |
| socket | to choose | 3 | more ultrasonic sensors, on boards of their own: the temples and the nape |

- **The radar to the processor:** its UART, and its reset and SOP0, so the processor can put it
  into flashing mode and load new radar firmware; the radar can be updated through the suit.
- **The ultrasonic sensors:** one SPI with a chip select each and no interrupt lines, as below.
- **On line 8,** a unit of his own, 0x82, with a tap, the Picoflex PF-50 header 90814-0816 where the
  line's cable passes (see [Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit)),
  and two packages of drivers as the glove's Staršaja: the line's pairs, its 4 V and ground, and the
  suit's clock from its pair (see [Porjadok](../porjadok/HARDWARE.md#links-between-boards)). Nataša
  beside him may be missing. The forehead's vibration motor sits in Míša's housing off the skin but
  is Nataša's, its two wires from her board (see [Nataša](../natasa/HARDWARE.md#míša-beside-her)).
- **The suit's clock** comes off the line as to every unit, so his slot keeps in step and the
  radar's rhythm is as precise as the suit's clock, a SiT8008 of ±20 ppm.
  He counts the suit's cycles himself, so the suit's time is his own (see
  [Radar and the EMG](#radar-and-the-emg)).

## The processor's pins

Míša's STM32H523 is the module's **STM32H523CCU6** in UFQFPN48, 35 I/Os, and keeps the module's
pins wherever the job is the same, so the numbers below are the module's (DS14540, figure 6 and
tables 14 and 15; see [Rubaška](../rubaska/HARDWARE.md#sensing-module), *The processor's pins*).
He needs 25:

| what | pins | where |
|---|---|---|
| the suit clock in | 1 | PH0-OSC_IN (5), the HSE in bypass, as on a module |
| the radar: its UART, NRESET, SOP0, its host interrupt | 5 | USART1_TX PA9 (30), USART1_RX PA10 (31), AF7; NRESET PA11 (32) and SOP0 PA12 (33), outputs; the interrupt PA15 (38), an input on EXTI15 |
| the radar's supplies: EN of its three converters together | 1 | PB10 (21), an output, so the processor can power the module down and up |
| the ultrasonic sensors: one SPI and a chip select each | 7 | SPI1 (AF5): SCK PA5 (15), MISO PA6 (16), MOSI PA7 (17), mode 3, at most 13 MHz (DS-000478), 78.6432 MHz ÷ 8 = 9.83 MHz; CS as outputs: the sensor on the board PA4 (14), the three sockets PB0, PB1, PB2 (18–20) |
| the IMU: one I3C bus and REF | 3 | I3C1_SCL PB6 (42), I3C1_SDA PB7 (43), AF3; REF from TIM1_CH1 on PA8 (29), AF1, to the IMU's INT2, 24 or 15 Hz from the suit's 9.8304 MHz ÷ 409,600 or ÷ 655,360 |
| line 8: transmit, the echo, DE, receive from Mamka | 4 | USART2_TX PA2 (12), the echo on USART2_RX PA3 (13), USART2_DE PA1 (11), AF7; Mamka's frames on UART5_RX PB5 (41), AF14 (tables 14 and 15), the radar keeping USART1, NRESET and SOP0 on PA9–PA12 |
| SWD and SWO | 3 | PA13 (34), PA14 (37), PB3 (39), AF0 |
| status LED | 1 | PB12 (25), as on a module |
| **total** | **25** | 10 I/Os free |

- **The module's pins where the job is the same:** the clock in, SPI1, I3C1, REF, SWD and the
  LED sit where the module has them, so the IMU and clock code carry over unchanged. SPI1 serves
  the ultrasonic sensors instead of an ADS1298; the sensors have no interrupt lines, so a
  measurement is started by a write and its end read or waited for (see
  [the ultrasonic sensor](#the-ultrasonic-sensor)).
- **The radar** talks over USART1 at 1,250,000 Bd, the one rate TI's demo takes (below), on the
  module's line pins, so Míša's line takes other pins: 196.608 MHz ÷ 157, 0.18% off, inside
  what a UART tolerates. NRESET and SOP0 let the processor put the module
  into its flashing mode (see [the board](#the-board)); the exact pin names on the MT5C01-03's
  connector are to be read in Jorjin's sheet. Its host interrupt says when a frame of points is
  ready.
- **The IMU** runs at 1,920 Hz as in a module: its 1.6 kHz setting is held to the REF that Míša
  makes from the suit's clock on his own timer, the ODR-triggered mode (DS13510 Rev 4, 6.6; AN5763
  Rev 4, 3.3, table 15). REF stays low until the IMU is set, its INT2 being an output forced to
  ground from power-on (DS13510 Rev 4, table 23); should the IMU reset while REF runs, the 1 kΩ
  holds the current to 3.3 mA. The processor sums its steps the same way; its 12 B a step go into
  the sphere's header as the head's turn and pitch, not up the line.
- BOOT0 to ground through 10 kΩ, NRST to the SWD pads, 2.2 µF on each VCAP (DS14540, table 21),
  PC13 to PC15 left free (table 13, note 2), as on a module. Should LQFP64 be chosen for the
  layout, the pins keep their names and only their numbers change.

## The radar

The **Jorjin MT5C01-03** carries a TI **IWRL6432AOP** with its antennas in the package, a 40 MHz
crystal and a 16 Mbit flash (Jorjin's datasheet MT5C01-03-DTS-R01; TI's SWRS323B).

| | MT5C01-03 |
|---|---|
| field of view | 140° across, 120° up and down |
| range | 15 m ahead and 7 m at the edges, for detecting motion |
| antennas | 2 transmit and 3 receive, a 2 × 4 virtual array |
| power | 11 mW on average at 10 frames a second, 2 Tx and 3 Rx, deep sleep between frames; ~0.96 W while chirping, so ~1 ms of chirping a frame; Míša runs 10 frames a second |
| peaks | 1.1 A on 1.2 V, 270 mA on 1.8 V, 90 mA on 3.3 V at most |
| processor | Arm Cortex-M4F at 160 MHz, ours to program, and a hardware accelerator for the FFTs |
| interfaces | UART, SPI whose clock and select double as I2C, a host interrupt, one GPIO |
| supply | 1.2 V, 1.8 V and the I/O at 3.3 V or 1.8 V |
| cover | polycarbonate 1.5 mm thick over a 2.5 mm air gap; PP, PE and PTFE lose less |

- **Its firmware is TI's,** the Motion and Presence Detection demo of the MMWAVE-L-SDK 05.05
  (TI's demo page), not our own. Míša's processor sends it its settings as CLI commands at start
  (`channelCfg`, `chirpComnCfg`, `chirpTimingCfg`, `frameCfg` …, two transmitters taking turns,
  TDMA_2TX) and reads one TLV packet a frame: the points as x, y, z and the radial speed, in
  floats or in int16, and the stats. With `lowPowerCfg` 1 the radar sleeps deeply between
  frames; TI measured 31.9 mW on average for its motion-detection profile. Its frame period is
  at least 100 ms, so **10 frames a second**, and it starts frames only by software, on its
  own timer. The source is in the SDK, so it can be changed if the trial asks for it.
- **The points to the map:** Míša's processor turns x, y, z into a distance and two angles and
  sorts them into the sphere.
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
  precise rate from the suit's clock; a foreign pulse then comes at the same moment every time and
  the stationary-target filter drops it.

## Radar and the EMG

The radar draws ~1 W while it chirps (Jorjin's ~0.96 W; 2.1 W at the sum of its rails' peaks),
about a millisecond a frame. At Míša's 10 frames a second
those bursts have harmonics at 10, 20, 30 … Hz, right in the EMG band up to ~500 Hz.

- **Line 8 has a converter of its own** on Mamka and its own π filter, so the bursts do
  not share a supply with the body; each module's analog side has its own LP2985. What is left
  is the common ground at Mamka and the field around the current loop, worst with a module of
  electrodes in the headband next to Míša.
- **When the radar chirped:** with TI's demo the frames run on the radar's own timer, not
  locked to the suit. Baťa then aligns the pattern that reaches the EMG to each frame by the
  cycle's number a sphere made with the radar carries, which Míša stamps from his own count of
  the suit's cycles, averages it and takes it away; how much that stamp wanders against the
  chirps is for the trial. Locked frames, each started on the same ADS sample (10 Hz is
  1,920 / 192), want a hardware trigger: the chip has one, SYNC_IN, ~160 ns from the pulse to the
  frame (its datasheet), but TI's SDK 05.05 does not use it yet, and Jorjin's pinout must bring
  it out.
- **The radar's 60 GHz itself** hardly reaches the leads: at a 5 mm wavelength they are poor
  antennas, and it sends +15 dBm EIRP. The ADS1298 has an RC filter at every input, ~3 MHz
  (SBAS459K, 9.3.1.1), and a module's inputs keep empty places for small common-mode capacitors
  (see [Rubaška](../rubaska/HARDWARE.md#sensing-module)), filled if a measurement asks for them.
- **Bulk capacitors** on Míša's board soften the bursts' edges, the higher harmonics.

## Open questions

- first a trial: Jorjin's evaluation board MT5C01E02R1, or TI's IWRL6432AOPEVM, on Baťa: glass
  doors, a post, a car at the roadside, the fields and the two conditions, before a board is
  drawn,
- whether the MT5C01-03 can be bought in small numbers, and its price,
- the EMG beside the radar: a module next to the evaluation board, its noise with the radar
  off, and at 10 Hz,
- 16 frames a second: TI's demo's processing time a frame (its stats) against 62.5 ms and a
  frame period under 100 ms; SYNC_IN on Jorjin's connector and a hardware trigger in the demo,
- whether the CH201's horns fit the ICU-20201,
- the ultrasound without INT1: the end of a measurement over SPI (only some sensor firmware) or
  waited for, and whether an unused INT1, an open drain, wants a pull-up,
- Míša's current peaks against line 8's converter, measured: on paper a chirp is ~0.58 A
  from the 4 V for ~1 ms (2.1 W at ~90%), ~1.0 A with Nataša's two motors, under the
  converter's limit of at least 1.13 A (see [Nataša](../natasa/HARDWARE.md#power)).
