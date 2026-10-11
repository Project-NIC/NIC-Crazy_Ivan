<div align="center">

# Terem: construction

**The board:** its shape and its layers, the PCIe pairs, where the converters go, the heights
under the ROCK, and what to watch when it is drawn.

↑ [Terem](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## The board

- **Shape:** one rectangle, 80 mm long and 45.5 mm wide, the slots' 23.5 mm spacing plus a
  card's 22 mm, with a 2280 card edge for each slot cut into one short side and the two standoff
  holes at the other. The edges copy a 2280 module: the Key M notch, the finger pads on both
  faces, hard gold on the fingers and a bevelled edge, so that they go into the sockets as a
  module does. The edges' spacing and the holes are the ROCK's (see
  [HARDWARE](HARDWARE.md#the-two-slots)).
- **The holes are slots,** a few tenths wider than the screw along the board's length: the
  drawing places the sockets and the standoffs to a few hundredths, but the sockets as soldered
  on the ROCK sit to some tenths (an estimate), so the edges set the board's place and the
  screws only hold it.
- **Thickness 0.8 mm.** An M.2 socket takes a card of 0.8 mm; the figure is the M.2
  specification's as the socket makers quote it, the specification itself not read here, so it
  is to be checked once more in the chosen socket's drawing. The whole board is 0.8 mm, there
  is no stepping.
- **Four layers:** signal, ground, power with ground, signal. Both the converters' guide and
  the PCIe pairs want an unbroken ground plane right under the top layer (SNAS877 8.4.1: *use at
  least one ground plane in one of the middle layers*), and only a thin prepreg under the pairs
  lets 85 Ω fit into the 0.5 mm pitch of the fingers. Copper 2 oz outside, 1 oz inside, the
  stack TI names for the converter (SNAS877 8.4.1.1). A prototype house makes a 0.8 mm
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
  around the slots, and the gap under a card is only the socket's height. Under the strip
  between the two cards the drawing has only small passives, 0201 by their outlines
  (0.3 × 0.8 mm); past the cards' end, from ~2 mm beyond the standoffs, the ROCK carries parts
  on its underside, so Terem ends where a 2280 card does. Every part of Terem sits on the
  face away from the ROCK: the two sockets, the modules under their heatsink, the converters,
  the capacitors and the connectors.

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
  the pad. The plane is the return of the pairs and the return of the module's up to 2.5 A at once,
  so it is whole under the sockets and the edges.

## The converters

One LMR60440 beside each socket, past the module's far end, so that the modules' heatsink has
nothing under it and the converter's heat spreads into its own copper. TI's rules for the cell
(SNAS877 8.4.1), in the order that matters:

- **The input loop first:** the 4.7 µF and the 100 nF right at VIN and GND, the loop they make
  with the pins as small as it can be; this loop carries the switching edges and sets the EMI.
- **SW small:** the SW pad to the inductor short and wide and nothing else on that copper; the
  inductor's outer end to the output capacitors, ~20 µF rated, and from them a wide trace to
  the socket's 3.3 V pins, a few millimetres at most.
- **FB straight to the output** at the capacitors, the fixed-3.3 V variant needing no divider,
  that trace led away from SW; RT's 16.5 kΩ close to its pin; 100 nF between BOOT and SW on
  short, wide traces.
- **Thermal copper:** thermal vias spread under PGND into the plane, the main path of the heat,
  and as much ground copper on the outer layers as the board leaves (SNAS877 8.4.1.1). The part's
  own loss at 2.5 A from 16 V is to be read from the sheet's efficiency curves; the ROCK's underside
  above it is likely the warmer neighbour.
- **EN** as a trace from the connector with 100 kΩ to ground at the pin, nothing else.

The battery's copper runs along the board's outer long edge, the edge away from the card edges,
and never under or beside the pairs. The 2.2 MHz of the converters is their own business: each
converter's loop is closed in its own input capacitors, and the plane carries nothing of it to
the pairs when the loops are small. There is no common-mode choke and no bead on Terem; the
suit's lines are filtered on Mamka, and the battery cable here is 10 cm inside a shell.

## The connectors and the mounting

- **The XT30** on the far short edge, its pads wide, the chip fuse right behind it, the input bank,
  2 × EEHZA1H470P with 10 µF and 100 nF, beside it and the converters' VIN fed from the same copper.
  The ROCK's board reaches ~13 mm past Terem's end there (the 2D drawing), so the battery cable
  comes in from below the ROCK, not past its edge.
- **To Mamka:** a 2 × 5 IDC box header on the same edge, ~20 mm, the wires in the order of
  [HARDWARE](HARDWARE.md#the-converters), a few centimetres of flat cable up to Mamka. The
  EN and PGOOD lines are plain traces between the connector and the converters, with the 100 kΩ
  pull-downs at the EN pins.
- **The modules** screw to their own 2242 standoffs on Terem, as on any carrier; the sockets
  are the standard M.2 Key M type at the standard height, so that the standoff is the standard
  one.
- **The Hailos' heatsink:** a Fischer Elektronik **ICK S 45 × 45 × 20**, aluminium pins on a
  3.5 mm base, 36 g, 4.4 K/W in still air down to 0.75 K/W in forced air, 17 W (DAU Components'
  listing; Fischer's own sheet not read). Its 45 × 45 mm covers both modules side by side,
  45.5 × 42 mm, and its pins take the air from any side. It lies on thermal pads over the
  modules' parts, 1.5 mm tall on top (Hailo's datasheet Rev. 1.0, 2.1), and is held by two M2.5
  screws with springs through two holes drilled in its base, into two holes on Terem's centre
  line: one ahead of the sockets between the two slots' pairs, one past the modules' standoffs.
  No fan of its own; the backpack's air passes its pins.
- **The heat:** two modules at their typical 2.5 W, 5 W in all, warm it ~22 K over the
  channel's air at the 4.4 K/W of still air; both at the datasheet's 8.25 W, 16.5 W, would be
  ~73 K, which wants the backpack's fan or a lighter load: the computer runs the fan by the
  Hailos' temperature and lowers their load if it stops (see
  [Babuška](../babuska/CONSTRUCTION.md#heat)).
- **The height:** ~30 mm under the ROCK's board with the heatsink, an estimate until the sockets
  are chosen: the ROCK's sockets 4.2 mm, Terem 0.8 mm, Terem's socket, the module and the pad
  ~5 mm, the heatsink 20 mm. The stack grows to ~68 mm (see
  [Mamka](../mamka/CONSTRUCTION.md#the-stack)). The 45 × 45 × 10 of the same series would save
  10 mm; its thermal resistance is not read.
- **Terem itself** is held by the ROCK's two 2280 standoff screws, one a slot, with its edges in
  the sockets; the two screws are at the end where the connectors sit, and the modules'
  heatsink hangs between the sockets and the screws. With the ROCK face-up the whole chamber
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

## Open questions

- the chosen sockets' and the ROCK's socket drawings: the card thickness and the finger
  numbering, the socket height and what may stand on Terem's face towards the ROCK,
- the board house's stack and its impedance figures for the pairs,
- the XT30's direction: a vertical one mated from below, or a horizontal one with its cable
  bent along the board, under the ROCK's overhang,
- the heatsink on a sample: the holes in its base and in Terem, the pads' thickness over the
  modules, its temperature at both modules' full load in the channel,
- the trained speed and width of both links on the first board, read from the ROCK.
