<div align="center">

# Míša: software

**What Míša works out:** the sphere around the head, the errors and the ghosts, and the data it
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

With a header of 4 B, the frame's number, a status byte, the head's turn and its pitch, the
whole sphere is 112 B; byte by byte it is under [Nataša](../natasa/SOFTWARE.md#míšas-wire).

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
  62–125 ms at 16 frames a second, 9–18 cm at a walking pace. A fast approach is reported from
  its first frame:
  better a false alarm than a missed car.

## Data

- **The whole sphere in every frame,** 16 times a second, ~1.8 kB/s. Every frame stands alone:
  whoever reads it takes the latest, and a lost frame does not matter.
- **Up the line:** Nataša passes it up the head line in her frame's rotation, and Mamka's
  processor 2 hands it to Baťa over the I2C as a container of type 10 (see
  [Mamka](../mamka/SOFTWARE.md#the-control-channel)), ~5% of what the I2C carries at 400 kHz.
- **Its readers:** Míša's program on Baťa beeps by direction and speaks, Deduška draws it in the
  glasses, and the recordings keep it.
- **Safety without Linux:** the sphere passes through Nataša, and she buzzes by herself when
  something in the middle row ahead is nearer than ~1 m or coming fast. If Baťa hangs, Míša and
  Nataša still keep watch.

## Open questions

- the radar's firmware: TI's, which sends the points, or our own on its M4F,
- the wearer's own speed from the radar, the field margins and the 2-of-3 confidence, on the
  bench; the radar's view of the wearer's own arms and chest in the down row,
- the floor, holes and steps from the tilt,
- the chirps for a car faster than ~72 km/h.
