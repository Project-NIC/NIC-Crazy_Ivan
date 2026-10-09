<div align="center">

# Mamka: construction

**The strip and the wing:** how the board sits over the computer, where its connectors and
tall parts go, and what it must keep clear of.

↑ [Mamka](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## The strip and the wing

Mamka sits straight on the 40-pin header of a ROCK 5T, or on top of Kormilica on a Raspberry Pi
(see [Kormilica](../kormilica/CONSTRUCTION.md#on-the-header)), a socket on her underside. Over the
computer she is only a strip with that socket; the rest reaches out past the computer's edge on
the header's side. That wing carries the converters, the connectors and the tall parts: the
hybrid polymers stand 10.2 mm. Nothing lies over the Raspberry Pi's Active Cooler, and nothing
over Mamka (see [Babuška](../babuska/CONSTRUCTION.md#the-backpack)).

- **Screws:** the strip screws to the computer's two holes on the header's side, the wing's
  outer edge to the insert on two spacers of its own; the ROCK 5T's holes come from its 2D
  drawing, and the strip takes both pairs if they do not collide.
- **The ROCK 5T's USB-C** sits on the same edge beside the header (Radxa's photo), the port for
  the glasses, so the wing leaves it free.
- **The lines' connectors:** five 2 × 5 IDC box headers, ~20 mm each, take ~100 mm of edge, more
  than the Raspberry Pi's 85 mm. Inside the backpack a short harness joins them to the PT 24-61
  in the shell, the one connector of the whole suit (see
  [Babuška](../babuska/CONSTRUCTION.md#the-backpack)).
- **The converters** sit on one side of the wing with copper poured under them, away from the
  clock and the processors (see [hardware](HARDWARE.md#filtering)).
- **The fan header** and the short cables to Kormilica (EN, PGOOD) or Terem (eight wires, see
  [hardware](HARDWARE.md#the-computers-supply)) and to the battery's terminals come off the wing
  too.

## Open questions

- the layout: the strip over the Raspberry Pi, on Kormilica, against the Active Cooler's
  outline and height, measured on the part (a taller socket if needed); over the ROCK 5T, the
  wing clear of its USB-C; the wing's size.
