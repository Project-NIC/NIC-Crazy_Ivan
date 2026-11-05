<div align="center">

# Rubaška

**The suit itself:** the pieces with their sensing modules, up to 580 electrodes and 108 IMUs, 64
of them in the two gloves and the two socks.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

*Rubaška*, Russian for a shirt. In Russian, as in Czech, a child born in a shirt is born lucky:
the "shirt" is the caul, a second skin around the newborn. The suit is a second skin too.

## Pieces

A piece is what one line serves (see [Porjadok](../porjadok/HARDWARE.md#links-between-boards)): a
sleeve with its shoulder, three modules and the glove; a trouser leg with its hip, three and the
sock; the headband; the torso's front, one; its back with the neck, two. Pieces join in any
combination, and a piece carries its modules as the suit is populated; where each sits on the body
is under [Bogatyr](../bogatyr/README.md).

## Sensing module

The sensing module is the suit's basic block; a suit has 8 to 16 of them. Together they are the
*Rebjata*, Russian for the kids: Mamka's own children, on the end of her
[Pupovina](../porjadok/HARDWARE.md#links-between-boards). A module is one board
in its piece, as small as it can be: fewer and smaller parts, fewer pads, smaller connectors.
Its IMUs sit along the bones, each on a small board of its own, joined to the module by I3C,
two IMUs to a bus. No SPI runs over a cable anywhere. Every module carries the ADS1298: a module
of the body two, 16 channels on 32 electrodes; the head's two; the neck's one; the same board
fitted otherwise, every channel differential.

What the module is made of, pin by pin, is under [hardware](HARDWARE.md); what its firmware does
under [software](SOFTWARE.md); the electrodes, the fabric and the harness under
[construction](CONSTRUCTION.md); and what was tried and dropped under [why not](WHY.md).

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | the sensing module's board: parts, pins, the IMUs on I3C, the input circuit, connectors; the IMU and its board; the right-leg drive and the reference; the strip's ground layer; the power; the glove, Vešč, one board for the hand's EMG and IMUs, its Staršaja reading every IMU on switched branches, and the sock, Nosok |
| [SOFTWARE.md](SOFTWARE.md) | the ADS1298's and the IMUs' settings, an electrode coming off, the glove and the sock on the line and their IMUs on switched branches, the rules from the errata |
| [CONSTRUCTION.md](CONSTRUCTION.md) | the electrodes and their strips, the fabric, the harness, the overall over it and the washing, the glove's strips and layers |
| [WHY.md](WHY.md) | what is not used, and why |

## Scale

| | a module of the body | the head's | the neck's | the glove or the sock | the suit of 16, with two gloves and two socks |
|---|---|---|---|---|---|
| ADS1298 | two | two | one | one | 35 |
| **measuring electrodes**, 16 a chip (8 differential channels) | **32** | **32** | **16** | **16** | **560** |
| the bias electrode | 1 | 1 | 1 | 1 | 20 |
| electrodes in all | 33 | 33 | 17 | 17 | **580** |
| IMUs | up to 4 | 4 | 4 | 24 places; 24 on the glove, 8 on the sock to start | 64 places on the modules, 44 fitted; 64 on the gloves and the socks, **108** |

The ADS1298 sample at **1,920 SPS**, 3,840 SPS a setting to try (see
[software](SOFTWARE.md#the-ads129xs-settings)). The IMUs sample at 960 Hz and give one step of
eight samples per 16 ADS samples (120 Hz), interleaved into the frames; see
[Porjadok](../porjadok/SOFTWARE.md#the-frames).
