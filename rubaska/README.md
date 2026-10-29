<div align="center">

# Rubaška

**The suit itself:** the pieces with their sensing modules, up to 582 electrodes and 98 IMUs, 56
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
two IMUs to a bus. No SPI runs over a cable anywhere. A module of the body carries two ADS1298,
16 channels on 32 electrodes; the head's two ADS1299 with one reference electrode, the neck's one,
the same board fitted otherwise.

What the module is made of, pin by pin, is under [hardware](HARDWARE.md); what its firmware does
under [software](SOFTWARE.md); the electrodes, the fabric and the harness under
[construction](CONSTRUCTION.md); and what was tried and dropped under [why not](WHY.md).

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | the sensing module's board: parts, pins, the IMUs on I3C, the input circuit, connectors; the IMU and its board; the right-leg drive and the reference; the strip's ground layer; the power; the glove, Vešč, one board for the hand's EMG and IMUs, its Staršaja and Bratiški, and the sock, Nosok |
| [SOFTWARE.md](SOFTWARE.md) | the ADS129x's and the IMUs' settings, an electrode coming off, the glove and the sock on the line and the Bratiški on their board, the rules from the errata |
| [CONSTRUCTION.md](CONSTRUCTION.md) | the electrodes and their strips, the fabric, the harness and washing, the glove's circuit and layers |
| [WHY.md](WHY.md) | what is not used, and why |

## Scale

| | a module of the body | the head's | the neck's | the glove or the sock | the suit of 16, with two gloves and two socks |
|---|---|---|---|---|---|
| ADS129x | two ADS1298 | two ADS1299 | one ADS1299 | one ADS1298 | 35 |
| **measuring electrodes**, 16 a chip (8 differential channels) | **32** | **32** | **16** | **16** | **560** |
| against the reference, on the head and the neck, 8 a chip | — | 16 | 8 | — | 24 |
| the bias electrode, and the reference on the head and the neck | 1 | 2 | 2 | 1 | 22 |
| electrodes in all | 33 | 34 | 18 | 17 | **582** |
| IMUs | up to 4 | 4 | 2 | 20 places on the glove, 8 to start on the sock | 64 places on the modules, 42 fitted; 56 on the gloves and the socks, **98** |

The ADS129x sample at **1,920 SPS**, 3,840 SPS a setting to try (see
[software](SOFTWARE.md#the-ads129xs-settings)). The IMUs sample at 1,920 Hz and give one step per
16 ADS samples (120 Hz), interleaved into the frames; see
[Porjadok](../porjadok/SOFTWARE.md#the-frames).
