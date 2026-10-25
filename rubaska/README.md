<div align="center">

# Rubaška

**The suit itself:** the pieces with their sensing modules, up to 288 electrodes and 84 IMUs, 40
of them in the two gloves.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

*Rubaška*, Russian for a shirt. In Russian, as in Czech, a child born in a shirt is born lucky:
the "shirt" is the caul, a second skin around the newborn. The suit is a second skin too.

## Pieces

A piece is what one line serves (see [Porjadok](../porjadok/HARDWARE.md#links-between-boards)):
a sleeve with its shoulder, three modules and the glove; a trouser leg with its hip, three; the
headband; the torso's front, one; its back with the neck, two. Pieces join in any combination,
and a piece carries its modules as the suit is populated; where each sits on the body is under
[Bogatyr](../bogatyr/README.md).

## Sensing module

The sensing module is the suit's basic block; a suit has 8 to 16 of them. Together they are the
*Rebjata*, Russian for the kids: Mamka's own children, on the end of her
[Pupovina](../porjadok/HARDWARE.md#links-between-boards). A module is one board
in its piece, as small as it can be: fewer and smaller parts, fewer pads, smaller connectors.
Its IMUs sit along the bones, each on a small board of its own, joined to the module by I3C,
two IMUs to a bus. No SPI runs over a cable anywhere.

What the module is made of, pin by pin, is under [hardware](HARDWARE.md); what its firmware does
under [software](SOFTWARE.md); the electrodes, the fabric and the harness under
[construction](CONSTRUCTION.md); and what was tried and dropped under [why not](WHY.md).

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | the sensing module's board: parts, pins, the IMUs on I3C, the input circuit, connectors; the IMU and its board; the right-leg drive and the reference; the power; the glove, Vešč, its Staršaja and Bratiški |
| [SOFTWARE.md](SOFTWARE.md) | the ADS1299's and the IMUs' settings, an electrode coming off, the glove on the line, the rules from the errata |
| [CONSTRUCTION.md](CONSTRUCTION.md) | the electrodes and their strips, the fabric, the harness and washing, the glove's circuit and layers |
| [WHY.md](WHY.md) | what is not used, and why |

## Scale

| | smallest | largest |
|---|---|---|
| sensing modules, one ADS1299 each | 8 | 16 |
| **measuring electrodes**, 16 per ADS1299 (8 differential channels) | **128** | **256** |
| against the reference, 8 per ADS1299 | 64 | 128 |
| a bias and a reference electrode per module | 16 | 32 |
| IMUs, 2 to 4 per sensing module | 16 | 64 |
| the gloves' IMUs, 20 each | — | 40 |

ADS1299 sampling: **3,840 SPS**, and 1,920 SPS a setting to try (see
[software](SOFTWARE.md#the-ads1299s-settings)). The IMUs sample at 1,200 Hz and give one step per
32 ADS samples (120 Hz), interleaved into the frames; see
[Porjadok](../porjadok/SOFTWARE.md#the-frames).
