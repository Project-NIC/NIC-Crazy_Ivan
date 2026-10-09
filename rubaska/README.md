<div align="center">

# Rubaška

**The suit itself:** the pieces with their sensing modules, 126 to 254 electrodes and 16 to 64
IMUs.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

*Rubaška*, Russian for a shirt. In Russian, as in Czech, a child born in a shirt is born lucky:
the "shirt" is the caul, a second skin around the newborn. The suit is a second skin too.

## Pieces

A piece is a sleeve, a trouser leg, the torso, a headband around the head and so on. Pieces
join in any combination. Each piece carries one or two sensing modules, depending on how the
suit is populated.

## Sensing module

The sensing module is the suit's basic block; a suit has 8 to 16 of them. Together they are the
*Rebjata*, Russian for the kids: Mamka's own children, on the end of her
[Pupovina](../porjadok/HARDWARE.md#links-between-boards). A module is one board
in its piece, as small as it can be: fewer and smaller parts, fewer pads, smaller connectors.
Its IMUs sit along the bones, each on a small board of its own, joined to the module by I3C,
two IMUs to a bus. No SPI runs over a cable anywhere.

What the module is made of, pin by pin, is under [hardware](HARDWARE.md); what its firmware does
under [software](SOFTWARE.md); the electrodes, the fabric and where everything sits on the body
under [construction](CONSTRUCTION.md); and what was tried and dropped under [why not](WHY.md).

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | the sensing module's board: parts, pins, the IMUs on I3C, the input circuit, connectors; the IMU; the right-leg drive; the power; the Vnučata of the glove and the foot |
| [SOFTWARE.md](SOFTWARE.md) | the ADS1299's and the IMUs' settings, an electrode coming off, the glove and the foot on the line, the rules from the errata |
| [CONSTRUCTION.md](CONSTRUCTION.md) | the electrodes, the leads, the fabric, the harness and washing, IMU placement, the glove and the foot on the body |
| [WHY.md](WHY.md) | what is not used, and why |

## Scale

| | smallest | largest |
|---|---|---|
| sensing modules, one ADS1299 each | 8 | 16 |
| electrode inputs, 16 per ADS1299 (8 differential channels) | 128 | 256 |
| of which go to the right leg (right-leg drive) | 2 | 2 |
| **measuring electrodes** | **126** | **254** |
| IMUs, 2 to 4 per sensing module | 16 | 64 |

ADS1299 sampling: **3,840 SPS** as the target, **960 SPS** at the least. The IMUs sample at
1,200 Hz and give one step per 32 ADS samples (120 Hz), interleaved into the ADS frames; see
[Porjadok](../porjadok/SOFTWARE.md#the-frame).
