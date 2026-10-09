<div align="center">

# Terem: construction

**The board:** its shape and its layers, the PCIe pairs, where the converters and the eFuse
go, the heights under the ROCK, and what to watch when it is drawn.

↑ [Terem](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## The board

- **Shape:** one rectangle, 80 mm long, as wide as the two slots' spacing plus a card's 22 mm,
  with a 2280 card edge for each slot cut into one long side and the two standoff holes at the
  other. The edges copy a 2280 module: the Key M notch, the finger pads on both faces, hard gold
  on the fingers and a bevelled edge, so that they go into the sockets as a module does. The
  spacing between the two edges and the holes come from Radxa's 2D drawing (see
  [HARDWARE](HARDWARE.md#the-two-slots)).
- **Thickness 0.8 mm.** An M.2 socket takes a card of 0.8 mm; the figure is the M.2
  specification's as the socket makers quote it, the specification itself not read here, so it
  is to be checked once more in the chosen socket's drawing. The whole board is 0.8 mm, there
  is no stepping.
- **Four layers:** signal, ground, power with ground, signal. Both the converters' guide and
  the PCIe pairs want an unbroken ground plane right under the top layer (SNVSBY5B 9.5.1: *use at
  least one ground plane in one of the middle layers*), and only a thin prepreg under the pairs
  lets 85 Ω fit into the 0.5 mm pitch of the fingers. Copper 2 oz outside, 1 oz inside, the
  stack TI names for the converter (SNVSBY5B 9.5.1). A prototype house makes a 0.8 mm
  four-layer board as readily as a two-layer one, for a few euros more on a board this small (an
  estimate; the house's price list decides).
- **Why not two layers,** which the board's size invites: on a 0.8 mm two-layer board the
  ground is 0.8 mm away, and an 85 Ω pair there needs traces over a millimetre wide (an
  estimate from the usual microstrip figures), which cannot run between fingers and socket pins
  at 0.5 mm pitch; the pairs would run at whatever impedance they get. Over 10–20 mm the link
  might still train at Gen 3, or train down to Gen 2, or not at all: nobody can say without
  trying, and the ROCK's own traces to its sockets are controlled. Four layers take the gamble
  out for a few euros (see [WHY](WHY.md)).
- **Sides:** the face towards the ROCK stays bare. The ROCK's own underside has its parts
  around the slots, and the gap under a card is only the socket's height; what may stand there
  is read from the 2D drawing, and until then nothing does. Every part of Terem sits on the
  face away from the ROCK: the two sockets, the modules with their heatsinks, the converters,
  the eFuse, the capacitors and the connectors.

## The pairs

Each slot carries two lanes, and the ROCK wires them to the socket's lane 0 and lane 1 pins:
PETp/n0 and PERp/n0 on pins 41–49, PETp/n1 and PERp/n1 on 29–37, the reference clock on 53 and
55 (the ROCK 5T schematic V1.2, the sheets of the two M.2 sockets). The module's socket on Terem
has the same numbering, so each pair goes from pin N of the edge to pin N of the socket.

- **Ten pairs,** five a slot, all on the top layer over the ground plane, with no via: the
  socket opens away from the edge, so the pairs run straight, 10–20 mm, and do not cross.
- **85 Ω differential,** the width and gap from the board house's calculator for its stack,
  which comes out near 0.15 mm wide and 0.15 mm apart on a 0.1 mm prepreg (an estimate, the
  calculator decides). The two traces of a pair matched within 0.1 mm; the pairs of one lane
  need no matching to each other at this length. Other traces and the pours keep at least three
  gaps away from a pair, and no pair runs over a slit in the ground plane.
- **At the fingers and the socket pins** the pads are 0.5 mm apart and the pair is whatever the
  pads make it; that stretch is the same on every M.2 card and is counted in the standard.
  Between them the pair reaches its width within a millimetre of each pad.
- **No capacitors on the pairs.** The ROCK has 220 nF in its transmit pairs (the same sheets),
  the module has its own in its transmit pairs, and the receive side of each is bare, as the
  standard puts them: Terem passes all ten pairs straight through.
- **The sideband lines** PERST#, CLKREQ# and PEWAKE# (pins 50, 52, 54), PEDET (69), SUSCLK
  (68) and DAS/DSS# (10) go straight through too, as plain traces, also pin to pin; they carry
  no speed. The reference clock (53, 55) is a pair and is routed as one.
- **The 3.3 V pins** of each edge (2, 4, 12, 14, 16, 18, 70, 72, 74) are tied together and go
  nowhere, they are left open; the socket's 3.3 V pins are tied together and fed by
  that converter. The two 3.3 V nets, the ROCK's and Terem's, never meet (see
  [HARDWARE](HARDWARE.md#the-converters)).
- **Grounds:** every GND pin of each edge and each socket goes to the ground plane by a via at
  the pad. The plane is the return of the pairs and the return of the module's 1.5 A at once,
  so it is whole under the sockets and the edges.

## The converters

One LMR43620 beside each socket, past the module's far end, so that the module's heatsink has
nothing under it and the converter's heat spreads into its own copper. TI's rules for the cell
(SNVSBY5B 9.5.1), in the order that matters:

- **The input loop first:** the 4.7 µF and the 100 nF right at VIN and GND, the loop they make
  with the pins as small as it can be; this loop carries the switching edges and sets the EMI.
- **SW small:** the SW pad to the inductor short and wide and nothing else on that copper; the
  inductor's outer end to the output capacitors, the 3 × 10 µF, and from them a wide trace to
  the socket's 3.3 V pins, a few millimetres at most.
- **The feedback divider at FB,** its ground at the chip's GND, the tap from the output trace
  led away from SW; 1 µF at VCC and 100 nF between BOOT and SW close to their pins.
- **Thermal copper:** the GND pad into the plane through a few vias, and the pour around the
  chip on the top layer (SNVSBY5B 9.2.2.9 for the area against the load). The part's own loss
  at 1.5 A from 16 V is to be read from the sheet's efficiency curves; the ROCK's underside
  above it is likely the warmer neighbour.
- **EN** as a trace from the connector with 100 kΩ to ground at the pin, nothing else.

## The eFuse

The TPS26630 at the far end next to the XT30, in the path battery → input bank → eFuse → DC
cable. TI's rules (SLVSE94G 9.6.1):

- 100 nF at IN_SYS and GND, the loop with the pins as small as the converters' input loop;
- R(ILIM), C(dVdT), the UVLO and OVP divider each at its pin, the other end straight to ground;
  the R(ILIM) trace short and away from the converters' SW nodes, since it sets the limit;
- the PowerPAD soldered to the ground plane through vias under the part;
- the power path, IN to OUT, sized for twice the full load: the ROCK's 17 W at 11.5 V is 1.5 A,
  so the pour carries 3 A with margin, at least 2 mm wide at 2 oz (IPC-2221's chart gives
  ~3 A for 1.5 mm at 1 oz and 10 K of rise; an estimate);
- the input bank, 2 × EEHZA1H470P with 10 µF and 100 nF, between the XT30 and the eFuse's IN,
  the converters' VIN fed from the same copper; the eFuse's OUT to the DC cable with 10 µF and
  100 nF at the pads, the ROCK's own input capacitors behind the cable.

The battery's copper runs along the board's outer long edge, the edge away from the card edges,
and never under or beside the pairs. The 2.2 MHz of the converters is their own business: each
converter's loop is closed in its own input capacitors, and the plane carries nothing of it to
the pairs when the loops are small. There is no common-mode choke and no bead on Terem; the
suit's lines are filtered on Mamka, and the battery cable here is 10 cm inside a shell.

## The connectors and the mounting

- **The XT30** on the far short edge, its pads wide and its body outside the ROCK's outline, so
  that the battery cable comes straight in; the DC cable to the ROCK's jack on a 2-pin pad pair
  beside it, soldered, or a JST XH if it is to come off.
- **To Mamka:** an 8-pin JST GH on the same edge: GND, SHDN, PGOOD of the eFuse, PGOOD A,
  PGOOD B, EN A, EN B, GND. The EN and PGOOD lines are plain traces between the connector and
  the converters, with the 100 kΩ pull-downs at the EN pins.
- **The modules** screw to their own 2242 standoffs on Terem, as on any carrier; the sockets
  are the standard M.2 Key M type at the standard height, so that the standoff is the standard
  one.
- **Terem itself** is held by the ROCK's two 2280 standoff screws, one a slot, with its edges in
  the sockets; the two screws are at the end where the connectors sit, and the modules'
  heatsinks hang between the sockets and the screws. With the ROCK face-up the whole chamber
  hangs below it, in the insert's channel (see
  [Babuška](../babuska/CONSTRUCTION.md#the-backpack)).

## What to watch

- **The pin order of the fingers** is mirrored between a card and a socket: copy the card's
  numbering from the socket maker's drawing and check it against a 2280 SSD before the first
  board, not after. One swapped lane only trains at ×1; a swapped 3.3 V finger feeds the
  ROCK's rail onto an open pad, which is harmless, but a swapped ground is not.
- **PEDET** (pin 69): the module tells the host by it whether it is PCIe or SATA; it passes
  through, so the host reads the module's answer, as it should.
- **The two edges go in at once** at the socket's angle, so the board must be flat and the two
  slots coplanar; a bowed 0.8 mm board does not seat. Keep the heavy parts, the XT30 and the
  inductors, near the standoffs.
- **The first board** is tried with one module, the link speed read from the ROCK (`lspci -vv`
  shows the trained width and speed), then with two. If a link trains at Gen 2 or ×1 with four
  layers, the fault is the stack or the pads, not the idea.
- **The TPS26630 latches** on a fault with MODE open: on the bench, a short on the DC cable
  looks like a dead ROCK until SHDN is cycled (see [HARDWARE](HARDWARE.md#the-efuse-for-the-rock)).

## Open questions

- the chosen sockets' and the ROCK's socket drawings: the card thickness and the finger
  numbering, the socket height and what may stand on Terem's face towards the ROCK,
- the board house's stack and its impedance figures for the pairs,
- the trained speed and width of both links on the first board, read from the ROCK.
