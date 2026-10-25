<div align="center">

# Míša: software

**What Míša works out:** the sphere around the head, the errors and the ghosts, and the data he
sends.

↑ [Míša](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## The sphere

Míša keeps a map of what is around the head: a sphere of **36 fields**, 12 columns of 30° around
and 3 rows of 60°.

| row | angle | holds |
|---|---|---|
| up | +30° to +90° | what is right above the head |
| middle | −30° to +30° | what is ahead at head and chest height: a branch or a lorry's mirror, which a cane misses, lies here at any distance |
| down | −30° to −90° | what is below, around the feet |

- **Fixed to the head:** column 0 is where the nose points. The rows are levelled by gravity
  from the accelerometer, which does not drift.
- **Fields of 30° × 60° match what the radar resolves.** Smaller fields would only make ghosts:
  the radar merges two posts closer than ~30° into one point in the gap between them.
- **Two conditions in each field:** the nearest thing, and the one coming closest fastest.
- **The radar** fills the ~10 fields in its view sharply, from the angles of its points.
- **The ultrasound** knows only a distance, so it writes it into every field its beam touches,
  a blurred patch. The nearer of the two counts; the speed comes from the radar, or from two
  ultrasonic readings in a row where the radar has nothing, behind glass.
- **The floor:** Míša knows from the tilt how far the floor should be. As far is the floor,
  nearer is an obstacle, farther is a hole or a step down, as a cane finds it.

Each field is three bytes:

| byte | holds |
|---|---|
| 1 | the distance, logarithmic: 256 steps from 0.2 to 25 m, each ~1.9% |
| 2 | the speed, ±25 m/s in 0.2 m/s steps, positive coming closer |
| 3 | the confidence 0–15 (4 bits), the source: radar, ultrasound or both (2 bits), the kind: obstacle, floor or hole (2 bits) |

With a header of 4 B the whole sphere is 112 B:

| B | the sphere |
|---|---|
| 0 | the frame's number |
| 1 | the status: bit 0 the radar, 1 the ultrasound, 2 the IMU in order, 3 levelled |
| 2 | the head's turn since the last frame, signed, in steps of 2° |
| 3 | the pitch, signed, in degrees |
| 4–111 | the 36 fields of 3 B: the up row's 12 columns from column 0, then the middle, then the down |

It is a chip of its own, **0x05, registers 0x00–0x6F,** read only, and he sends it himself after
every radar frame in five answers of 34 B, 25 B of the sphere in each, unasked (see
[Porjadok](../porjadok/SOFTWARE.md#the-commands)), all five with the cycle's number at which it
was done, by which the pieces are put together.

**His time** is his own: he takes the suit's clock off line 8 and counts its cycles from the
heartbeat's numbers, so the sphere carries the suit's time with no one writing it to him.

## Errors and ghosts

- **Live, not from memory:** the sphere is built anew every frame from what the sensors see
  now. Nothing is tracked, no target numbers and no predicted paths; whether a thing moves or
  the head turns, the next frame simply finds it in its field.
- **A short memory only** for fields the head has turned away from, 1–2 s, shifted by the
  gyro's turn over that time. No absolute zero is needed: over seconds the gyro drifts a
  fraction of a degree against fields of 30°. It is zeroed again whenever the head is still.
- **A margin at the edges:** a thing moves to the next field only once it is ~5° over the edge,
  so it does not flicker between two.
- **The wearer's own walking:** everything standing still comes closer at the walking speed,
  and the radar sees it on the ground, the walls and the posts at once. Their common speed is
  the wearer's; taken away, what still moves really moves: a car, a bicycle, a person. To try.
- **Confidence:** a field counts as taken once 2 of the last 3 frames hit it, which costs
  100–200 ms at 10 frames a second, 14–28 cm at a walking pace. A fast approach is reported from
  its first frame:
  better a false alarm than a missed car.

## Data

- **The whole sphere in every frame,** 10 times a second, 112 B, in five answers of 34 B,
  1.7 kB/s. Every sphere stands alone: whoever reads it takes the latest, and a lost one does not
  matter.
- **Up the line:** he sends his pieces in his own slot on line 8, slot 2, and Mamka's processor 2
  passes them to Baťa over her own SPI as they came (see
  [Mamka](../mamka/SOFTWARE.md#processor-2s-two-spis)). His frame of data goes in cycle 15 of 32
  and his diagnostics in cycle 31, as Nataša's.
- **Its readers:** Míša's program on Baťa beeps by direction and speaks, Borovičok draws it in
  the glasses, and the recordings keep it.
- **Safety without Linux:** Nataša reads the sphere as it passes on the return pair and buzzes by
  herself when something in the middle row ahead is nearer than ~1 m or coming fast. If Baťa
  hangs, Míša and Nataša still keep watch.

## Clocks

By the suit's clock tree (see [Porjadok](../porjadok/SOFTWARE.md#the-clock-tree)), from the suit's
clock off line 8, his core at 196.608 MHz until his current is checked, set as Mamka's: P ÷ 2,
LATENCY 5 and WRHIGHFREQ 10, the ADC at the AHB clock ÷ 4 (RM0481, table 48; DS14540, table 89).
He adds:

| what | setting |
|---|---|
| SPI1, the ultrasonic sensors | PLL1Q ÷ 5: 78.6432 MHz, SPI1SEL = 000, the SPI's own ÷ 8: 9.83 MHz, under the sensors' 13 MHz (DS-000478) |
| USART1 to the radar | the APB clock, 16×, BRR = 0x009D: 196.608 MHz ÷ 157 = 1.2523 MBd, 0.18% from 1.25 MBd |
| USART2 and UART5, line 8 | the APB clock, OVER8 = 1, BRR = 0x0012: 19,660,800 Bd |
| I3C1, the IMU | the APB clock: 196.608 MHz |
| TIM1, the IMU | PSC = 0, ARR = 5,119, CH1 at CCR1 = 2,560: CLKIN at 38,400 Hz |
| TIM2, line 8's cycle | PSC = 19: a tick of the suit clock; ARR = 2,559, a cycle of 260.4 µs, set by Mamka's heartbeat |

## DMA

By the suit's rules (see [Porjadok](../porjadok/SOFTWARE.md#the-gpdma)), 8 channels. One IMU's two
control words fit the I3C's C-FIFO, so the core writes them and the RX alone is DMA:

| channel | request (REQSEL) | what | priority | how |
|---|---|---|---|---|
| GPDMA1 0 | 29, uart5_rx | UART5 RX: Mamka's frames | 3 | circular |
| GPDMA1 1 | 23, usart2_rx | USART2 RX: the return pair, the echo of his own sending | 3 | circular |
| GPDMA1 2 | 21, usart1_rx | USART1 RX: the radar's TLV packet, a frame | 1 | circular |
| GPDMA1 3 | 6, spi1_rx | SPI1 RX: the ultrasonic sensors' answers | 0 | one block a transfer |
| GPDMA1 4 | 120, i3c1_rx_dma | I3C1 RX: the IMU's 12 B | 1 | one block a sample |
| GPDMA2 0 | 24, usart2_tx | USART2 TX: his frames in his slot, the sphere's five pieces among them | 3 | one block a slot |
| GPDMA2 1 | 22, usart1_tx | USART1 TX: the radar's settings at start | 0 | one block a command |
| GPDMA2 2 | 7, spi1_tx | SPI1 TX: the sensors' commands and their firmware at power-on | 0 | one block a transfer |

## Interrupts

By the suit's levels (see [Porjadok](../porjadok/SOFTWARE.md#interrupts)); the numbers are the
vector table's (RM0481 Rev 5, table 153):

| level | interrupt | what it does |
|---|---|---|
| 0 | TIM2 (45) | line 8's cycle: his slot's sending started |
| 2 | UART5 (62), USART2 (59) | Mamka's frames in, the echo checked |
| 6 | EXTI15 (26), USART1 (58) | the radar's frame ready, its packet in |
| 6 | I3C1 (123, 124) | the IMU |
| 6 | SPI1 (55) | the ultrasonic sensors |
| 8 | ADC1 (37), FLASH (6) | the temperature and the 3.3 V, the firmware update |

## Open questions

- 16 frames a second instead of 10, once the trial shows the demo can (see
  [hardware](HARDWARE.md#open-questions)),
- the wearer's own speed from the radar, the field margins and the 2-of-3 confidence, on the
  bench; the radar's view of the wearer's own arms and chest in the down row,
- the floor, holes and steps from the tilt,
- the chirps for a car faster than ~72 km/h,
- what his frame of data carries, once in 32 cycles.
