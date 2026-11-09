<div align="center">

# Terem: construction

**The board:** its shape and its layers, the PCIe pairs, where the converters go, the heights
under the ROCK, and what to watch when it is drawn.

↑ [Terem](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## The board

- **Shape:** ~90 × ~63 mm, an L, the figures estimates until it is drawn; the places below are read
  from Radxa's 3D model of the ROCK 5T V1.2. Along the slots it runs from a card edge for each slot,
  cut into one short side, past the ROCK's standoff holes at 80 mm to ~10 mm beyond them. Terem's
  own socket must start past the mouth of the ROCK's, whose lower half stands ~0.9 mm below Terem's
  far face, so a 2280 card on Terem has its screw ~7.5 mm past the ROCK's (the chosen socket's
  drawing decides). Across, the two cards lie 25.5 mm apart on their axes, 2 mm more than the ROCK's
  slots, with a gap of 3.5 mm between them, kept or closed to the slots' 23.5 mm when Mrazík is
  drawn; 48.5 mm in all. The L's foot is a strip ~14 mm wide along the cards' far half, on the long
  side away from the ROCK's 40-pin header, for the converters and the connectors.
- **A frame, not a plate** (the owner, 9 Nov 2026): Terem carries nothing under the cards but its
  plane, so it is solid only where something is: the front, with the edges, the pairs and the
  sockets; the strip; and a back plate ~10 mm deep with the ROCK's screws and the cards'
  standoffs. Rails ~5 mm wide join them along both long sides, and a middle leg ~5 mm wide runs
  back from the front between the cards. The rest is milled out. The middle leg ends ~15 mm
  before the ROCK's screws, where the ROCK's two inductors sit between the cards (below), and the
  back plate is notched round L5002, which ends ~2.7 mm before its screw's centre. The far
  converter's 3.3 V runs to its socket along the strip's rail and across the front, the power
  layer whole there. Air reaches the ROCK's underside through the openings.
- **A stiffener** screwed across the back plate and along the rails, an aluminium bar or a 1.6 mm
  FR4 one, chosen when Terem is drawn: the frame stays 0.8 mm, the edges' thickness, and the
  stiffener keeps it flat, so that both edges seat at once (*What to watch*).
- **The edges** copy a 2280 module: the Key M notch, the finger pads on both faces, hard gold on
  the fingers and a bevelled edge, so that they go into the sockets as a module does. Their
  spacing and the holes are the ROCK's (see [HARDWARE](HARDWARE.md#the-two-slots)); beside and
  between them the short side stays clear of the ROCK's sockets.
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
- **Sides:** the face towards the ROCK stays bare. It lies 2.5 mm under the ROCK's board, the
  height of the ROCK's standoffs, and the parts on the ROCK's underside over it stand up to
  ~2 mm, with these exceptions:
  - **two inductors,** L5001 and L5002 of two of the ROCK's own converters (the schematic: RXW
    SHC0630-1R5M and a 1.5 µH), 2.8 mm in the model, under the cards' far ends, from ~15 to ~3
    mm before the standoffs. They lie in the frame's opening (above), the back plate notched
    ~0.5 mm round L5002, so Terem never lies on them, whatever their real height: an inductor
    would have to stand 3.3 mm, the standoffs' 2.5 and Terem's 0.8, to reach past its far face,
    where the "0630" series is ~3.0 mm (an estimate by the name, the sheet not read), so nothing
    waits on a measurement;
  - **past the standoffs,** J2, the connector of the ROCK's clock battery, 3.5 mm, its leads
    ~10 mm beyond one standoff, and the stack's corner hole ~11.6 mm beyond the other, with its
    screw's nut (see [Mamka](../mamka/CONSTRUCTION.md#the-stack)). Terem ends ~0.5 mm before J2's
    leads and passes under the nut;
  - **the strip:** the pins of the ROCK's top-side connectors come through its board ~2.1 mm,
    so the strip begins only past the first half of the cards.

  Every part of Terem sits on the face away from the ROCK: the two sockets, the modules on their
  pads against Mrazík's wall, the converters, the capacitors and the connectors. A card on Terem
  lies ~2.5 mm under that face, the socket's height, so it may reach past Terem's end, over J2 and
  the nut.

## The pairs

Each slot carries two lanes, and the ROCK wires them to the socket's lane 0 and lane 1 pins:
PETp/n0 and PERp/n0 on pins 41–49, PETp/n1 and PERp/n1 on 29–37, the reference clock on 53 and
55 (the ROCK 5T schematic V1.2, the sheets of the two M.2 sockets). The module's socket on Terem
has the same numbering, so each pair goes from pin N of the edge to pin N of the socket.

- **Ten pairs,** five a slot, all on the top layer over the ground plane, with no via: the
  socket opens away from the edge, so the pairs run straight, 10–20 mm, and do not cross; each
  slot's pairs jog 1 mm outwards, the sockets being 2 mm further apart than the edges.
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

Both LMR60440s on the strip, side by side, with the input bank, so that the block's face over the
modules has nothing else under it and each converter's heat spreads into its own copper; each
converter's 3.3 V goes to its socket on the power layer, the far one's under the near card. TI's
rules for the cell (SNAS877 8.4.1), in the order that matters:

- **The input loop first:** the 4.7 µF and the 100 nF right at VIN and GND, the loop they make
  with the pins as small as it can be; this loop carries the switching edges and sets the EMI.
- **SW small:** the SW pad to the inductor short and wide and nothing else on that copper; the
  inductor's outer end to the output capacitors, ~20 µF rated, and from them into the power
  layer, a wide pour to the socket's 3.3 V pins, with its own 10 µF and 100 nF at the socket.
- **FB straight to the output** at the capacitors, the fixed-3.3 V variant needing no divider,
  that trace led away from SW; RT's 18 kΩ close to its pin; 100 nF between BOOT and SW on
  short, wide traces.
- **Thermal copper:** thermal vias spread under PGND into the plane, the main path of the heat, and
  as much ground copper on the outer layers as the board leaves (SNAS877 8.4.1.1). The part's own
  loss at 2.5 A from 14.6 V is to be read from the sheet's efficiency curves; the ROCK's underside
  above it is likely the warmer neighbour.
- **EN** as a trace from the connector with 100 kΩ to ground at the pin, nothing else.

The battery's copper stays on the strip, along the board's outer long edge, and never under or
beside the pairs. The ~1.9 MHz of the converters is their own business: each
converter's loop is closed in its own input capacitors, and the plane carries nothing of it to
the pairs when the loops are small. There is no common-mode choke and no bead on Terem; the
suit's lines are filtered on Mamka, and the battery cable here is 10 cm inside a shell.

## The connectors and the mounting

- **The XT30** on the strip, its pads wide, the chip fuse right behind it, the input bank,
  2 × EEHZA1H470P with 10 µF and 100 nF, beside it and the converters' VIN fed from the same copper:
  the strip, ~44 × 14 mm, takes them in two rows, the converters and the bank in one, the XT30,
  the fuse and the IDC in the other (an estimate until drawn). The ROCK's board reaches ~3 mm past
  the strip's edge, so the battery cable comes in from below the ROCK, not past its edge.
- **To Mamka:** a 2 × 5 IDC box header on the strip, ~20 mm, the wires in the order of
  [HARDWARE](HARDWARE.md#the-converters), a few centimetres of flat cable up to Mamka. The
  EN and PGOOD lines are plain traces between the connector and the converters, with the 100 kΩ
  pull-downs at the EN pins.
- **The modules** screw to their own 2280 standoffs on Terem, as on any carrier; the sockets
  are the standard M.2 Key M type at the standard height, so that the standoff is the standard
  one.
- **The Hailos' cooling** is Mrazík's wall (see [Babuška](../babuska/CONSTRUCTION.md#mrazík)):
  each module lies on a soft silicone thermal pad of ~1 mm against the block's aluminium, over the
  modules' parts, 1.5 mm tall on top (Hailo's datasheet Rev. 1.0, 2.1), the face's place along
  the cards from the module's drawing; no heatsink of their own and no fan.
- **The heat:** two modules at their typical 2.5 W, 5 W in all, 16.5 W at the datasheet's 8.25 W
  each, go through the pads into the block's wall and its fins; the computer runs the fan by the
  Hailos' temperature and lowers their load if it stops (see
  [Babuška](../babuska/CONSTRUCTION.md#heat)).
- **The height:** ~10 mm under the ROCK's board to the block's wall, an estimate until the
  sockets are chosen: the ROCK's sockets 4.2 mm, Terem 0.8 mm, Terem's socket, the module and the
  pad ~5 mm. The stack is ~48 mm (see [Mamka](../mamka/CONSTRUCTION.md#the-stack)).
- **Terem itself** is held by the ROCK's two 2280 standoff screws, one a slot, with its edges in
  the sockets. The screws' heads lie under the cards, ~7.5 mm before the cards' own screws, in
  the 2.5 mm between Terem and a card: a low head, under ~1.5 mm, under the module's own parts,
  0.5 mm on its underside (Hailo's datasheet Rev. 1.0, 2.1). With the ROCK face-up the whole
  chamber hangs below it, inside Mrazík (see [Babuška](../babuska/CONSTRUCTION.md#mrazík)).

## What to watch

- **The pin order of the fingers** is mirrored between a card and a socket: copy the card's
  numbering from the socket maker's drawing and check it against a 2280 SSD before the first
  board, not after. One swapped lane only trains at ×1; a swapped 3.3 V finger feeds the
  ROCK's rail onto an open pad, which is harmless, but a swapped ground is not.
- **PEDET** (pin 69): the module tells the host by it whether it is PCIe or SATA; it passes
  through, so the host reads the module's answer, as it should.
- **The two edges go in at once** at the socket's angle, so the board must be flat and the two
  slots coplanar; a bowed 0.8 mm board does not seat. Keep the heavy parts, the XT30, the bank
  and the inductors, on the strip's end by the standoffs.
- **The cards' screws ~7.5 mm past the ROCK's:** not more than ~0.5 mm further, or the standoff of
  the card on the header's side meets J2; the socket is chosen and placed with that in view, its
  drawing against the ROCK's model.
- **The two inductors** under Terem: the opening and the notch drawn from the model and Radxa's
  2D drawing, a little generous; a calliper on the first ROCK only confirms them.
- **The first board** is tried with one module, the link speed read from the ROCK (`lspci -vv`
  shows the trained width and speed), then with two. If a link trains at Gen 2 or ×1 with four
  layers, the fault is the stack or the pads, not the idea.

## Open questions

- the chosen sockets' and the ROCK's socket drawings: the card thickness and the finger
  numbering, the socket height and what may stand on Terem's face towards the ROCK,
- the board house's stack and its impedance figures for the pairs,
- the XT30's direction: a vertical one mated from below, or a horizontal one with its cable
  bent along the board, under the ROCK's overhang,
- the pads on a sample: their thickness over the modules and the modules' temperature at both
  modules' full load against Mrazík's wall, when the block is drawn,
- the trained speed and width of both links on the first board, read from the ROCK,
- the ROCK's inductors L5001 and L5002 as fitted, for an SSD in the ROCK's own slot (Borovičok):
  in the model a 2280 card lies 0.3 mm on them; Terem's frame does not wait on it,
- the Hailo-10H 2280's drawing: its chip's place for the block's face, its underside's parts over
  Terem's screw heads.
