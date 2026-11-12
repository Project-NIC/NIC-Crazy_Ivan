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
| angle | ~19° across, ~60° up and down | none: anywhere in its beam |
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
| STM32H523 | UFQFPN48 | 1 | the processor, as in every module |
| THVD1450 | VSSOP-8, or SOIC-8 | 3 | line 8's pair from Mamka and the suit's clock, receive only, and its return pair with the echo, as on a module (see [Porjadok](../porjadok/HARDWARE.md#drivers-on-a-unit)) |
| IWRL6432WMOD (TI) | QFM, 30 pads of a land grid, 31 × 15.5 mm | 1 | the radar, see below |
| LSM6DSV16X | LGA-14L, 2.5 × 3 × 0.83 mm | 1 | the IMU, the suit's: the head's tilt from gravity, short turns from the gyro; 100 nF at each supply pin and 10 kΩ in series with INT2, as on the IMU board (see [Rubaška](../rubaska/HARDWARE.md#the-imu)) |
| ICU-20201 | LGA-14, 3.5 × 3.5 × 1.26 mm | 1 | the ultrasound ahead, in a 45° horn; ending at TDK, open (see [the ultrasonic sensor](#the-ultrasonic-sensor)) |
| TPS73733 | SOT-223-6, 6.5 × 7.06 mm | 1 | 4 V to the radar's 3.3 V, its only supply: a linear regulator of 1 A, nothing switching beside the EMG (SBVS067W) |
| TPS7A2018 | X2SON, 1 × 1 mm | 1 | 3.3 → 1.8 V for the ultrasonic sensor's core |
| 6TPE220MI | case D2E, 7.3 × 4.3 × 1.8 mm | 1 place | the polymer bulk at the 4 V input, 220 µF, 18 mΩ, 105 °C; not fitted at first: with the cable it softens only a chirp's edges, and plugged into a live line 8 it would take the line down and reset Nataša; fitted if the bursts want it |
| socket | to choose | 3 | more ultrasonic sensors, on boards of their own: the temples and the nape |

- **The radar to the processor:** its SPI with a chip select, its busy and end-of-frame outputs,
  its wake-up input, its NRESET and SOP0, and its UART, which carries TI's patches for its
  firmware, so the radar can be updated through the suit. With the radar's 3.3 V off, the
  processor holds every line to it low: the module's pins other than NRESET are not failsafe
  (SWRS350B, 4.2).
- **The ultrasonic sensors:** one SPI with a chip select each and no interrupt lines, as below.
- **On line 8,** a unit of his own, 0x82, with a tap, the Picoflex PF-50 header 90814-0816 where
  the line's cable passes (see
  [Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit)), and a module's three
  drivers, as the glove's Staršaja has: the line's pairs, its 4 V and ground, and the suit's clock
  from its pair (see [Porjadok](../porjadok/HARDWARE.md#links-between-boards)). Nataša beside him
  may be missing. The forehead's vibration motor sits in Míša's housing off the skin but is
  Nataša's, its two wires from her board (see [Nataša](../natasa/HARDWARE.md#míša-beside-her)).
- **The suit's clock** comes off the line as to every unit, so his slot keeps in step and the
  radar's rhythm is as precise as the suit's clock.
  He counts the suit's cycles himself, so the suit's time is his own (see
  [Radar and the EMG](#radar-and-the-emg)).

## The processor's pins

Míša's STM32H523 is the module's **STM32H523CCU6** in UFQFPN48, 35 I/Os, and keeps the module's
pins wherever the job is the same, so the numbers below are the module's (DS14540, figure 6 and
tables 14 and 15; see [Rubaška](../rubaska/HARDWARE.md#sensing-module), *The processor's pins*).
He needs 31:

| what | pins | where |
|---|---|---|
| the suit clock in | 1 | PH0-OSC_IN (5), the HSE in bypass, as on a module |
| the radar: its SPI, a chip select, busy, the end of a frame, wake-up | 7 | SPI2 (AF5): SCK PB13 (26), MISO PB14 (27), MOSI PB15 (28); the end of a frame on PC13 (2), an input on EXTI13; CS on PA0 (10) and wake-up on PB8 (45), outputs, wake-up on a pull-down under 10 kΩ (SWRS350B, 6.3.1.1); busy on PC14 (3), an input |
| the radar: NRESET, SOP0 and the UART for its patches | 4 | NRESET PA11 (32) and SOP0 PA12 (33), outputs; USART1_TX PA9 (30), USART1_RX PA10 (31), AF7 |
| the radar's supply: EN of its regulator | 1 | PB10 (21), an output, so the processor can power the module down and up |
| the ultrasonic sensors: one SPI and a chip select each | 7 | SPI1 (AF5): SCK PA5 (15), MISO PA6 (16), MOSI PA7 (17), mode 3, at most 13 MHz (DS-000478), 78.6432 MHz ÷ 8 = 9.83 MHz; CS as outputs: the sensor on the board PA4 (14), the three sockets PB0, PB1, PB2 (18–20) |
| the IMU: one I3C bus and REF | 3 | I3C1_SCL PB6 (42), I3C1_SDA PB7 (43), AF3; REF from TIM1_CH1 on PA8 (29), AF1, to the IMU's INT2, 24 or 15 Hz from the suit's 9.8304 MHz ÷ 409,600 or ÷ 655,360 |
| line 8: transmit, the echo, DE, receive from Mamka | 4 | USART2_TX PA2 (12), the echo on USART2_RX PA3 (13), USART2_DE PA1 (11), AF7; Mamka's frames on UART5_RX PB5 (41), AF14 (tables 14 and 15), the radar keeping USART1, NRESET and SOP0 on PA9–PA12 |
| SWD and SWO | 3 | PA13 (34), PA14 (37), PB3 (39), AF0 |
| status LED | 1 | PB12 (25), as on a module |
| **total** | **31** | 4 I/Os free |

- **The module's pins where the job is the same:** the clock in, SPI1, I3C1, REF, SWD and the
  LED sit where the module has them, so the IMU and clock code carry over unchanged. SPI1 serves
  the ultrasonic sensors instead of an ADS1298; the sensors have no interrupt lines, so a
  measurement is started by a write and its end read or waited for (see
  [the ultrasonic sensor](#the-ultrasonic-sensor)).
- **The radar** is SPI2's only device, as TI asks (SWRS350B, 5.11.2.3): mode 0, 16-bit words,
  MSB first, at most 15 MHz; Míša runs it at 4.92 MHz, plenty for a frame of points ten times a
  second. He raises wake-up before a transaction and drops it after, waits while busy is high,
  and reads a frame when the end-of-frame pin toggles (6.3.1.1). USART1 carries only TI's patches
  for the module's firmware, at its 115,200 Bd (5.11.4.1), NRESET and SOP0 putting it into that
  mode, so Míša's line takes other pins.
- **PA15 and PB4 stay free:** they come up as JTDI and NJTRST with their pull-ups on (DS14540,
  table 13, note 5), which would feed the radar's pins while its 3.3 V is off (SWRS350B, 4.2).
  PC13 and PC14, limited as outputs on the backup domain's switch (table 13, note 2), serve as
  inputs.
- **The IMU** runs at 960 Hz as in a module: its 800 Hz setting is held to the REF that Míša
  makes from the suit's clock on his own timer, the ODR-triggered mode (DS13510 Rev 4, 6.6; AN5763
  Rev 4, 3.3, table 15). REF stays low until the IMU is set, its INT2 being an output forced to
  ground from power-on (DS13510 Rev 4, table 23); should the IMU reset while REF runs, the 10 kΩ
  holds the current to 0.33 mA. The processor sums its steps the same way; its 12 B a step go into
  the sphere's header as the head's turn and pitch, not up the line.
- BOOT0 to ground through 10 kΩ, NRST to the SWD pads, 2.2 µF on each VCAP (DS14540, table 21),
  PC13 to PC15 left free (table 13, note 2), as on a module.

## The radar

**TI's IWRL6432WMOD** (datasheet SWRS350B, rev. B, September 2026): TI's own module with the
IWRL6432 radar chip, its antennas etched on the module's board, its 40 MHz crystal, flash and
power, certified for FCC, RED and MIC, on 30 pads of a land grid, 31 × 15.5 mm. Its datasheet and
pinout are public, so it goes into an open design as it is.

| | IWRL6432WMOD |
|---|---|
| field of view | ±60° across, ±60° up and down (5.7) |
| resolution across | 19°, for two like objects near the axis (5.7) |
| range | a person at 15 m ahead and 8 m at ±60° (5.7) |
| antennas | 2 transmit and 3 receive, a virtual array of 6 across and 2 up and down (5.8.1) |
| sweep | 57–61.5 GHz, 4.5 GHz continuous (features) |
| power | 54–59 mW on average for 15 m at 5 updates a second, 8.7 mW for 4 m at one (5.5) |
| peaks | at most 1 A on VCC and 90 mA on VIO (table 5-2) |
| supply | 3.3 V for VCC and the I/O; the 1.8 V made on the module |
| interfaces | SPI to the host, busy, the end of a frame or presence, wake-up, NRESET, SOP0; a UART for patches only (table 4-1) |

- **Its firmware is TI's,** presence and motion detection in the module's flash, set over SPI by
  TI's mmWaveULink library on the host (the package MMWAVE-UDFP-APPSW): the range, the
  sensitivity, the region of interest, the update rate. Míša runs it in its Verbose mode, which
  hands the points to the host and toggles the end-of-frame pin every frame; the mode is chosen
  when the firmware loads (SWRS350B, 6.3.1.2, 6.3.2). The firmware is not ours to change. What a
  point holds (the antennas give the range, both angles and the speed, 5.8.1), whether still
  objects are kept, and whether it runs 10 frames a second (its power table goes to 5) are to be
  read in TI's interface document and seen in the trial.
- **The points to the map:** Míša's processor turns x, y, z into a distance and two angles and
  sorts them into the sphere.
- **Resolution:** ~19° across (5.7) and ~60° up and down from two rows, by the rule of thumb of
  2 / N radians.

## The ultrasonic sensor

**TDK is ending its SmartSonic sensors** (TDK's pages, 10 Nov 2026: the ICU-20201 and the ICU-30201
"EOL Announced", no last buy or successor named), so the ultrasound is open: nothing is drawn on a
part that ends, and the radar's trial on glass decides whether Míša keeps one (see the
[open questions](#open-questions)). What follows is the ICU-20201 as chosen.

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
  stepping back in VR glasses; its 40° keep the floor out to ~4.5 m (1.65 m / tan 20°).
- **They hear each other** at under 10 m when their frequencies are close (DS-000478, section
  4.5): sensors on one head, and two people in suits side by side. They take turns, started at a
  precise rate from the suit's clock; a foreign pulse then comes at the same moment every time and
  the stationary-target filter drops it.

## Radar and the EMG

The radar draws its current in short bursts while it chirps, up to 1 A on its 3.3 V (SWRS350B,
table 5-2), a burst a frame. At Míša's 10 frames a second
those bursts have harmonics at 10, 20, 30 … Hz, right in the EMG band up to ~500 Hz.

- **Line 8 has a converter of its own** on Mamka and its own π filter, so the bursts do
  not share a supply with the body; each module's analog side has its own LP2985. What is left
  is the common ground at Mamka and the field around the current loop, worst with a module of
  electrodes in the headband next to Míša.
- **When the radar chirped:** the module's firmware runs its frames on its own timer and has no
  trigger to lock them to the suit. Its end-of-frame pin tells Míša when a frame ended; he stamps
  the sphere made from it with the cycle's number from his own count of the suit's cycles, and
  Baťa aligns the pattern that reaches the EMG to each frame by it, averages it and takes it away.
  How much that stamp wanders against the chirps is for the trial.
- **The radar's 60 GHz itself** hardly reaches the leads: at a 5 mm wavelength they are poor
  antennas, and it sends at most +19 dBm EIRP a transmitter (SWRS350B, 5.7). The ADS1298 has an RC
  filter at every input, ~3 MHz (SBAS459K, 9.3.1.1), and a module's inputs keep empty places for
  small common-mode capacitors (see [Rubaška](../rubaska/HARDWARE.md#sensing-module)), filled if a
  measurement asks for them.
- **The polymer's place** at Míša's input softens the bursts' edges, the higher harmonics, if
  fitted; a chirp of milliseconds comes through the cable all the same.

## Open questions

- the ultrasound, TDK's ending: the radar on glass doors, head-on and at an angle, decides
  whether the front needs one at all; glass reflects 60 GHz and ultrasound alike as a mirror,
  seen head-on and lost at a slant. If it does, a sensor current then, TI's TUSS4470 one candidate
  (SLDS251A: it drives a transducer from its own H-bridge, 40 kHz to 1 MHz, the echo's envelope
  out to the processor's ADC, but VPWR 5–36 V, more than the line's 4 V). The sides and the nape
  stay optional and later, a second radar or ultrasound; the headband without Baťa's cameras
  needs them more than the suit does,

- the module's firmware, from TI's interface document (MMWAVE-UDFP-APPSW): what a point holds,
  still objects kept or dropped, 10 frames a second or 16, the speeds it reports, a car's
  included; how its patches are loaded, with NRESET and SOP0,
- first a trial: TI's module on a small adapter, or on an evaluation board if TI sells one, on
  Baťa: glass doors, a post, a car at the roadside, the fields and the two conditions, before a
  board is drawn,
- the EMG beside the radar: a module next to it, its noise with the radar off, and at 10 Hz,
- whether the CH201's horns fit the ICU-20201,
- the ultrasound without INT1: the end of a measurement over SPI (only some sensor firmware) or
  waited for, and whether an unused INT1, an open drain, wants a pull-up,
- Míša's current peaks against line 8's converter, measured: the module's VCC takes up to 1 A at 3.3
  V (table 5-2), the same from the 4 V through the linear regulator, near the limit of at least 1.13
  A with Nataša's motors on top; the bursts' real current measured, and the bulk at Míša's input
  sized by it (see [Nataša](../natasa/HARDWARE.md#power)).
