<div align="center">

# Mamka: construction

**Over the ROCK:** the stack of the ROCK 5T, Terem and Mamka, where her connectors and tall
parts go, and what she must keep clear of.

↑ [Mamka](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## The stack

The ROCK 5T, Terem under it and Mamka over it make one stack of ~110 × 82 × 68 mm, held by four
screws. Its heights come from Radxa's 3D model of the ROCK 5T V1.2 (read for the bounds of every
face): the ports along the board's far edge stand up to 16.4 mm over its top, the 40-pin header
7.5 mm, the SoC 1.75 mm, the tallest other part 8.5 mm; under the board the M.2 sockets reach
4.225 mm and nothing over Terem more than ~2 mm but two inductors of 2.8 mm, under windows in
Terem; Terem with the Hailos' heatsink hangs ~30 mm under it (see
[Terem](../terem/CONSTRUCTION.md#the-board)).

- **The SoC's cooler** is Radxa's Heatsink 6240B, made for the ROCK 5B, 5B+ and 5T: 62 × 40 ×
  9 mm of aluminium with its own 5 V fan on the board's fan connector, pressed by two pegs into
  the board's holes beside the SoC, Ø3.2 mm on a diagonal (Radxa's page; the drawing's holes).
  With the SoC and the pad its top stands ~11.75 mm over the board, and it lies at x −29.6…32.4,
  y −26.6…13.4 in Radxa's drawing, clear of the header at y −37.6…−35. That its 9 mm include the
  fan is the page's figure; no drawing of it was found.
- **Mamka is one board over the whole ROCK,** ~110 × 65 mm: everything that was a wing past the
  computer's edge lies over it, and the band of ports along the far edge stays uncovered, so
  their cables plug in under her edge. She sits on the 40-pin header on one extra-tall 2 × 20 female
  header, its body 23 mm tall, soldered to her underside: Adafruit's 1979, made for stacking
  boards over a Raspberry Pi's header, 2.54 mm, 0.6 mm square pins 10 mm long (Adafruit's page),
  the pins trimmed flush on her top. On the ROCK's header, whose plastic stands ~2.5 mm (the
  common height; the model gives its pins' tops at 7.5 mm), her underside comes ~25.5 mm over
  the ROCK's board: clear of the ports by ~9 mm and ~13.5 mm over the heatsink's fan. One part,
  no loose riser between two sockets; spacers of the same height carry the screws.
- **Her parts sit on her top face only;** her underside faces the fan and stays bare. The hybrid
  polymers stand 10.2 mm, so the stack's top is ~37 mm over the ROCK's board.
- **The ROCK's USB-C,** the port for the glasses, sits on the header's edge beside the header
  (Radxa's photo), so Mamka's edge leaves it free.
- **Screws:** four M2.5 through the stack at the ROCK's four corner holes, Ø2.7 mm, which are not
  a rectangle: 57 mm apart on the left, 49 mm on the right (Radxa's 2D drawing V1.2); Mamka
  copies them, and takes the fifth hole beside the header too, the Raspberry Pi's place, 58 mm
  from the corner hole on that edge, so that the socket is held where it carries. Under the ROCK
  each screw ends in a nut; at the corner past the slots' standoffs on the side away from the
  header, Terem passes 2.5 mm under the board, so that nut is at most 2 mm thick, the screw cut
  flush with it.
- **The box:** none, the stack bare in the backpack's insert, or a perforated metal box of the
  stack's outer size; the sides stay open to the ports and the air either way.
- **The lines' connectors:** eight 2 × 5 IDC box headers, ~20 mm each, on her top face along
  the header's side, their flat cables leaving over that edge. In one row they do not fit,
  ~162 mm against her ~110 mm, Terem's not counted: two rows of four, ~81 mm a row, the inner
  row's cables over the outer row's sockets, at ~20 mm of the board's depth; or a smaller IDC at
  1.27 mm, whose size and wire are not yet read, likely on a thinner cable than the harness's
  28 AWG (see [Porjadok](../porjadok/HARDWARE.md#end-to-end)). Decided when she is drawn. Inside
  the backpack a short harness joins them to the connectors in the shell, one a piece of the suit
  (see [Babuška](../babuska/CONSTRUCTION.md#the-backpack)).
- **The processors,** two STM32H562VG in LQFP100, 14 × 14 mm each, side by side, so that the
  four wires between them stay a few millimetres long.
- **The converters** sit on one side of the board with copper poured under them, away from the
  clock and the processors (see [hardware](HARDWARE.md#filtering)).
- **The eFuses** sit beside the battery input and its bank, in the path battery → fuse → input bank
  → eFuse → DC cable, by TI's rules (SLVSE94G 9.6.1): 100 nF at IN_SYS and GND, the loop with the
  pins as small as a converter's input loop; R(ILIM), C(dVdT), the UVLO and OVP divider each at its
  pin, the other end straight to ground, the R(ILIM) trace short and away from the converters' SW
  nodes, since it sets the limit; the PowerPAD soldered to the ground plane through vias under the
  part. The power path, IN to OUT, is sized for the eFuse's 3 A limit: the ROCK's 17 W at the pack's
  10 V end is 1.7 A, so the pour carries 3 A with margin, at least 2 mm wide at 2 oz (IPC-2221's
  chart gives ~3 A for 1.5 mm at 1 oz and 10 K of rise; an estimate).
- **The fan header,** the DC cables to the ROCKs' jacks, the jack at the far corner from the
  header, Terem's flat cable down the side (see [hardware](HARDWARE.md#the-computers-supply))
  and the battery's terminals come off her edges too.

## Open questions

- the stack: the 23 mm header's seat on the ROCK's header and the stack's height checked on the
  parts; whether the 6240B's fan cools the SoC with ~13.5 mm of air under Mamka, measured; Mamka's
  outline against the ports and the USB-C; the eight IDC headers and Terem's: two rows of four,
  or a smaller IDC;
- the box: none, or a perforated metal one of the stack's size.
