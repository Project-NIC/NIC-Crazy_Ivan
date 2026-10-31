<div align="center">

# Mamka: construction

**Over the ROCK:** the stack of the ROCK 5T, Terem and Mamka inside Mrazík, the window for the
SoC's boss, where her connectors and tall parts go, and what she must keep clear of.

↑ [Mamka](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## The stack

The ROCK 5T, Mamka over it and under it Terem, or a plain aluminium plate in Terem's place where
there are no Hailos, make one stack, ~110 × 82 × 68 mm with Terem, held by four screws, inside
Mrazík, the closed aluminium block that cools it (see
[Babuška](../babuska/CONSTRUCTION.md#mrazík)). Its heights come from Radxa's 3D model of the
ROCK 5T V1.2 (read for the bounds of every face): the ports along the board's far edge stand up
to 16.4 mm over its top, the 40-pin header 7.5 mm, the SoC 1.75 mm, the tallest other part
8.5 mm; under the board the M.2 sockets reach 4.225 mm and nothing over Terem more than ~2 mm but
two inductors of 2.8 mm, under windows in Terem; Terem with the Hailos' heatsink hangs ~30 mm
under it (see [Terem](../terem/CONSTRUCTION.md#the-board)). The plate's thickness is set when
Mrazík is drawn.

- **The SoC is cooled by a boss** of Mrazík's top wall through a window in Mamka over it,
  ~30 × 30 mm (the RK3588 is 23 × 23 mm), on a pad. The top wall clears Mamka's tallest parts,
  the hybrid polymers' 10.2 mm, so the boss is ~36 mm long: at 25 × 25 mm of aluminium
  (~200 W/m·K) ~0.3 K/W, ~5 K at the ROCK's 17 W, an estimate before the pads. The window's
  place over the SoC is taken from Radxa's drawing when she is drawn.
- **Mamka is one board over the whole ROCK,** ~110 × 65 mm: nothing of her reaches past the
  computer's edge, and the band of ports along the far edge stays uncovered, so their cables
  plug in under her edge. She sits on the 40-pin header on one extra-tall 2 × 20 female
  header, its body 23 mm tall, soldered to her underside: Adafruit's 1979, made for stacking
  boards over a Raspberry Pi's header, 2.54 mm, 0.6 mm square pins 10 mm long (Adafruit's page),
  the pins trimmed flush on her top. On the ROCK's header, whose plastic stands ~2.5 mm (the
  common height; the model gives its pins' tops at 7.5 mm), her underside comes ~25.5 mm over
  the ROCK's board: clear of the ports by ~9 mm and of his tallest other part by ~17 mm. One
  part, no loose riser between two sockets; spacers of the same height carry the screws.
- **Her parts sit on her top face only;** her underside faces the ROCK and stays bare. The hybrid
  polymers stand 10.2 mm, so the stack's top is ~37 mm over the ROCK's board, and Mrazík's top
  wall over it.
- **The ROCK's USB-C,** the port for the glasses, sits on the header's edge beside the header
  (Radxa's photo), so Mamka's edge leaves it free.
- **Screws:** four M2.5 through the stack at the ROCK's four corner holes, Ø2.7 mm, which are not
  a rectangle: 57 mm apart on the left, 49 mm on the right (Radxa's 2D drawing V1.2); Mamka
  copies them, and takes the fifth hole beside the header too, the Raspberry Pi's place, 58 mm
  from the corner hole on that edge, so that the socket is held where it carries. Under the ROCK
  each screw ends in a nut; at the corner past the slots' standoffs on the side away from the
  header, Terem passes 2.5 mm under the board, so that nut is at most 2 mm thick, the screw cut
  flush with it.
- **The case is Mrazík,** a closed aluminium block, IP55, round the stack: its walls' bosses
  reach the chips over pads, the boards sit on standoffs, and the cables leave through its
  plastic bottom with the ports facing it (see [Babuška](../babuska/CONSTRUCTION.md#mrazík)). One
  block serves every fitting, Terem or the plate under the ROCK.
- **The lines' connectors:** eight 2 × 5 IDC box headers, ~20 mm each, on her top face along
  the header's side, their flat cables leaving over that edge. In one row they do not fit,
  ~162 mm against her ~110 mm, Terem's not counted: two rows of four, ~81 mm a row, the inner
  row's cables over the outer row's sockets, at ~20 mm of the board's depth; or a smaller IDC at
  1.27 mm, whose size and wire are not yet read, likely on a thinner cable than the harness's
  28 AWG (see [Porjadok](../porjadok/HARDWARE.md#end-to-end)). Decided when she is drawn. Inside
  the backpack a short harness joins them to the connectors in the shell, one a piece of the suit
  (see [Babuška](../babuska/CONSTRUCTION.md#the-backpack)).
- **The processors,** two STM32H562VG or STM32H563VG in LQFP100, 14 × 14 mm each, side by side,
  so that the four wires between them stay a few millimetres long.
- **The converters** sit on one side of the board with copper poured under them, away from the
  clock and the processors (see [hardware](HARDWARE.md#filtering)).
- **The eFuses** sit beside the battery input and its bank, in the path battery → fuse → input bank
  → eFuse → DC cable, by TI's rules (SLVSFC9C 8.4.1): 100 nF or more from IN to GND at the pins,
  the loop as small as a converter's input loop; R(ILM), C(dVdt), C(ITIMER) and the dividers on
  EN/UVLO, OVLO and PGTH each at its pin, the other end straight to the eFuse's GND; the ILM trace
  short, under 50 pF and away from the converters' SW nodes, since it sets the breaker; the
  eFuse's ground an island of its own, joined to the power ground at one point; IN and OUT,
  which carry its heat, on wide copper on both outer layers with thermal vias; at least 1 µF at
  OUT. The power path, IN to OUT, carries at least twice the full load: the ROCK's 17 W at the
  pack's 10 V end is 1.7 A, so 3.4 A, at least 2 mm wide at 2 oz (IPC-2221's chart gives ~3 A for
  1.5 mm at 1 oz and 10 K of rise; an estimate).
- **The fan header,** the DC cables to the ROCKs' jacks, the jack at the far corner from the
  header, Terem's flat cable down the side (see [hardware](HARDWARE.md#the-computers-supply))
  and the battery's terminals come off her edges too.

## Open questions

- the stack: the 23 mm header's seat on the ROCK's header and the stack's height checked on the
  parts; Mamka's outline against the ports and the USB-C; the eight IDC headers and Terem's: two
  rows of four, or a smaller IDC;
- the window for Mrazík's boss, ~30 × 30 mm over the SoC: its place from Radxa's drawing and
  what of Mamka's parts it moves; the SoC's temperature through the boss and its pad at full
  load, measured;
- Mrazík round the stack, its walls, the plate in Terem's place and their dimensions: drawn at
  home from Radxa's 3D model V1.2 and Mamka's and Terem's boards once they are drawn in EasyEDA
  (see [Babuška](../babuska/CONSTRUCTION.md#open-questions)).
