<div align="center">

# Terem: hardware

**The board in the ROCK 5T's two M.2 slots:** the sockets and their converters, the battery in,
and the lines to Mamka.

↑ [Terem](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## What is on it

| part | package | count | what it does |
|---|---|---|---|
| two M.2 Key M card edges | 2280 | 2 | into the ROCK 5T's two slots at once, the board held by their standoffs at 80 mm and ~90 mm long |
| M.2 socket, Key M, and its standoff | 2280 | 2 | one Hailo-10H 2280 module each (see [Baťa](../bata/HARDWARE.md#umnica)), the socket right behind its edge, the standoff ~7.5 mm past the ROCK's |
| LMR60440, LMR604403SRAKR | WQFN-HR 9, 2.5 × 2 mm | 2 | a 3.3 V converter for each module, 4 A, the fixed-3.3 V variant (TI SNAS877, December 2024); pin compatible with the LMR60406, 10, 20 and 30 |
| EEHZA1H470P | SMD 8 × 10.2 mm | 2 | the bulk on the battery input: 47 µF 50 V hybrid polymer, the house part |
| Amass XT30 | | 1 | the battery in from Mamka, ~1.6 A with two Hailos at their most, ~2.6 A with two cards at a slot's full 13 W |
| chip fuse, 1206 or 1812 | SMD | 1 | right at the input, before the bank: fast-acting, ~2–5 A by the cards fitted, its value from the measured start (see [Babuška](../babuska/HARDWARE.md#power-variants)) |
| IDC box header, 2 × 5 | 2.54 mm grid | 1 | to Mamka on a 10-wire flat cable: each converter's EN and PGOOD, six grounds; Mamka's line part |

## The two slots

The ROCK 5T's two M.2 Key M slots lie side by side on its underside with standoffs for 2280
(Radxa). Terem is one board with a card edge for each, so it goes in as one piece: an M.2 card
goes into its connector at an angle and is pressed down, so both edges must meet their
connectors together, which asks the two slots to be coplanar, of one height and orientation, at a
spacing the board copies. Radxa's 2D drawing and 3D model (V1.2, dl.radxa.com) show they are:
both sockets on the underside, side by side and turned the same way, the cards' axes 23.5 mm
apart; the same socket body in the model, 8.15 × 21.85 mm and 4.225 mm below the board; the two
2280 standoff holes, Ø2.7 mm, on one line 77.4 mm from the sockets' pegs. Terem is one board.
The schematic draws both sockets as one symbol and names no part, so their exact type is not
known.

- **Each socket sits right behind its edge,** and a 2280 card in it reaches ~7.5 mm past the ROCK's
  standoffs, where Terem has a standoff of its own for the card's screw: two holes a slot, the
  ROCK's and the card's, none shared. The two cards cover the board from the sockets to its end, so
  the converters and the connectors take a strip along one long side (see
  [CONSTRUCTION](CONSTRUCTION.md#the-board)). The PCIe pairs run ~10–20 mm from an edge to its
  socket, 85 Ω differential and matched within 0.1 mm in a pair, far inside what Gen 3 allows;
  CLKREQ#, PERST#, PEWAKE# and the rest pass straight through. Each slot gives its module the two
  lanes the ROCK wires to it (the board itself in [CONSTRUCTION.md](CONSTRUCTION.md)).
- **The edges' 3.3 V pins are not connected** at all: the ROCK's one SY8113B feeds nothing
  here (see [Baťa](../bata/HARDWARE.md#umnica)). Each converter is enabled by a pin of the ROCK
  instead, below.
- **Any other card:** a socket is a plain M.2 Key M for 2280 with PCIe and its own 3.3 V, so
  another accelerator or any other card of that length goes in, with only the software changed,
  as long as it stays within what its converter gives, 4 A of 3.3 V, ~13 W a slot, and works on
  the slot's two lanes. A card that wants more wants a Terem of its own.
- **Height:** the sockets' and the modules' height under the ROCK, in the insert's channel, with
  one heatsink over both modules (see [Terem](CONSTRUCTION.md#the-connectors-and-the-mounting), and
  [Babuška](../babuska/CONSTRUCTION.md#the-backpack)).

## The converters

A **TI LMR60440** for each module, its fixed-3.3 V variant (LMR604403SRAKR, FB straight to the
output, no divider; 3.24–3.35 V), 4 A: a Hailo-10H takes up to 8.25 W, ~2.5 A (Hailo's datasheet
Rev. 1.0, 3.1), and a slot has ~13 W to give, room for a larger card (TI SNAS877, December 2024).
The cell is TI's for 2 MHz, 3.3 V and 4 A (table 8-1): 16.5 kΩ on RT, 1.5 µH, ~20 µF of rated output
capacitance, C_IN 4.7 µF 50 V + 100 nF, 100 nF on BOOT, MODE/SYNC to ground for PFM at light load
(its pin table); the inductor's saturation current at least the high-side limit, up to 8.2 A
(8.2.2.2, 6.5). From 14.6 V at 2 MHz the on-time is ~113 ns against the 30 ns minimum. The family is
pin compatible (LMR60406, 10, 20, 30, 40), so one board takes a smaller or a larger one.

- **EN from the ROCK, straight.** Each converter's EN is a trace from a GPIO of the ROCK, **EN A**
  from header pin 16 (GPIO3_A4) and **EN B** from pin 32 (GPIO3_C2), across Mamka and the cable
  (see [Mamka](../mamka/HARDWARE.md#on-baťas-header)), with 100 kΩ to ground at the pin and
  nothing else: no transistor, no divider. EN takes up to 42 V and switches on at 1.15–1.35 V,
  off at 0.9–1.1 V (SNAS877, 6.1 and 6.5),
  so a 3.3 V high is on and a low or a floating pin is off. Both GPIOs rest at a pull-down out of
  reset (`GPIO3_A4_d`, `GPIO3_C2_d`, the ROCK 5T schematic V1.2), so the modules are off until
  Linux says otherwise; a pin that rests pulled up, as pin 33 does (`GPIO3_A7_u`), suits a PGOOD,
  not an EN.
- **The PCIe driver does the switching,** not a script. In the device tree each EN is a
  `regulator-fixed` with `enable-active-high` and `vin-supply = <&vcc3v3_pcie30>`, the ROCK's
  own slot rail on GPIO1_A4, and each port names it as its `vpcie3v3-supply`: `pcie3x4` for
  slot A, `pcie3x2` for slot B (mainline `rk3588-rock-5t.dts` and its `rk3588-rock-5b-5bp-5t.dtsi`;
  the ROCK's rail is such a regulator already). The driver, `pcie-dw-rockchip.c`, enables the
  regulator before it touches the PHY, holds PERST# low, waits `PCIE_T_PVPERL_MS`, 100 ms, and
  lets it go; so the module gets the slot rail, its own 3.3 V (soft start 6 ms, t_SS,
  SNAS877), and the reset in the order the M.2 sequence asks, with `startup-delay-us` set to
  the converter's soft start. A module is never powered while its slot's rail is not, since the
  slot rail is the regulator's supply.
- **Off and on at runtime** go through the same driver, patched: the stock `pcie-dw-rockchip.c`
  has no `remove` and `suppress_bind_attrs`, so Baťa's kernel carries a small patch that adds
  the remove and allows unbind and bind (see [Baťa](../bata/SOFTWARE.md#the-kernel)). `unbind` of
  a port drops PERST#, the port and, through the devm cleanup, the regulator, so that module's
  3.3 V, with the other module untouched; `bind` runs the boot sequence again, regulator, 100 ms,
  PERST#. No script touches the EN pin itself, the driver owns it. An empty slot stays powered
  (the DWC core waits for a link and goes on without one), which costs nothing here. The
  *normal* profile disables one port in the overlay, so its EN never rises.
- **PGOOD to the ROCK.** Each converter's PGOOD, an open drain, goes over the same cable and
  Mamka's traces onto a free GPIO of the ROCK's header each, A's and B's, chosen when the boards
  are drawn and each pin's path checked on the ROCK's schematic, with 10 kΩ pull-ups from
  header pin 1,
  the ROCK's own 3.3 V, so nothing drives an unpowered RK3588. The ROCK reads them on an edge
  interrupt and knows at once which Umnica lost her supply; the link itself tells it first
  (a dead module drops the link and its driver reads all ones), PGOOD says why. A converter in
  hiccup, after a short, retries after ~85 ms (SNAS877, 7.3.7), so its PGOOD flaps until
  its EN goes low.
- **What the module sees** is only this 3.3 V; it makes its own 1.8 V and core voltages from it,
  so the two converters, the ROCK's and Terem's, share no node and no frequency.
- **Current:** two modules at their typical 2.5 W are ~0.4 A from the battery at its nominal
  12.8 V, at the datasheet's 8.25 W ~1.3 A, two cards at a slot's full ~13 W ~2.0 A, ~2.6 A near
  its 10 V end; the XT30 carries 15 A
  continuous by its distributors (Amass's sheet to be read).
- **Off with the suit:** with the ROCK down, both ENs rest at their pull-downs, at 0 V, under EN's
  low threshold, and each converter sleeps at 0.65 µA, 1 µA at most at 25 °C (SNAS877, 6.5), so
  Terem may hang on the battery unswitched, as Mamka's own converters do: it comes from Mamka's
  battery input, behind her fuse (see [Mamka](../mamka/HARDWARE.md#the-computers-supply)), through
  its own chip fuse. The ROCK itself is fed and switched by its eFuse on Mamka (see
  [Mamka](../mamka/HARDWARE.md#the-computers-supply)).
- **The chip fuse** sits right at the XT30, before the bank: the converters' limits guard their
  outputs, and the fuse takes Terem off alone should the bank or a converter's input fail short.
- **The battery input** carries the house input bank, two 47 µF hybrid polymers with 10 µF 50 V
  and 100 nF, as on Mamka; the converters take their peaks from it.
- **To Mamka** on a few centimetres of 10-wire flat cable in a 2 × 5 IDC box header, the part
  Mamka has for her lines. Wire by wire: 1 GND, 2 EN A, 3 PGOOD A, 4 GND, 5 EN B, 6 PGOOD B,
  7–10 GND. The four signals only pass across Mamka to the header.

## Open questions

- the Hailo-10H 2280's drawing: where its chip and its memory lie, for the heatsink's place,
- a module with its EN low in a live slot: the host's pull-ups and the reference clock into an
  unpowered Hailo-10H, from its sheet; the Hailo driver's own low-power states as the way to
  rest a module while running,
- the XT30's rating from Amass's own sheet.
