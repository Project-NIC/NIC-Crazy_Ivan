<div align="center">

# Terem: hardware

**The board in the ROCK 5T's two M.2 slots:** the sockets and their converters, the eFuse for
the ROCK, the battery in, and the lines to Mamka.

↑ [Terem](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## What is on it

| part | package | count | what it does |
|---|---|---|---|
| two M.2 Key M card edges | 2280 | 2 | into the ROCK 5T's two slots at once, the board as long as the slots, held by their standoffs at 80 mm |
| M.2 socket, Key M | 2242 | 2 | one Hailo-10H 2242 module each (see [Baťa](../bata/HARDWARE.md#umnica)), right behind its edge |
| LMR43620 | VQFN-HR, 2 × 2 mm | 2 | a 3.3 V converter for each module, 2 A, the 2 A member of Mamka's LMR436x0 family (SNVSBY5B) |
| TPS26630 | VQFN-24, 4 × 4 mm | 1 | the eFuse: the battery to the ROCK's DC jack, a current limit, a soft start, under- and overvoltage cutoffs, SHDN and PGOOD (SLVSE94G) |
| DC cable with a 5.5 × 2.5 mm plug | | 1 | from the eFuse to the ROCK's jack |
| EEHZA1H470P | SMD 8 × 10.2 mm | 2 | the bulk on the battery input: 47 µF 50 V hybrid polymer, NIC-Heimdall's house part |
| Amass XT30 | | 1 | the battery in, ~2.5 A at most |
| JST GH, 8-pin | | 1 | to Mamka: the eFuse's SHDN and PGOOD, each converter's EN and PGOOD, two grounds |

## The two slots

The ROCK 5T's two M.2 Key M slots lie side by side on its underside with standoffs for 2280
(Radxa). Terem is one board with a card edge for each, so it goes in as one piece: an M.2 card
goes into its connector at an angle and is pressed down, so both edges must meet their
connectors together, which asks the two slots to be coplanar, of one height and orientation, at a
spacing the board copies. That spacing and height come from Radxa's 2D drawing (dl.radxa.com),
not read yet; should the slots not allow it, Terem becomes two boards, one a slot, with the eFuse
on one of them, and nothing else changes.

- **Each socket sits right behind its edge.** A 2242 module lies over the board's middle, and the
  converters, the eFuse and the connectors take the far end around the standoff holes. The PCIe
  pairs run ~10–20 mm from an edge to its socket, 85 Ω differential and matched within 0.1 mm
  in a pair, far inside what Gen 3 allows; CLKREQ#, PERST#, PEWAKE# and the rest pass straight
  through. Each slot gives its module the two lanes the ROCK wires to it (the board itself in
  [CONSTRUCTION.md](CONSTRUCTION.md)).
- **The edges' 3.3 V pins are not connected** at all: the ROCK's one SY8113B feeds nothing
  here (see [Baťa](../bata/HARDWARE.md#umnica)). Each converter is enabled by a pin of the ROCK
  instead, below.
- **Height:** the sockets' and the modules' height under the ROCK, in the insert's channel, with
  a small heatsink on each module (see [Babuška](../babuska/CONSTRUCTION.md#the-backpack)).

## The converters

A **TI LMR43620** for each module, fixed by a divider at 3.3 V, 2 A: a module takes up to 5 W,
~1.5 A, so each has 6.6 W to itself. The cell is Mamka's (see
[Mamka](../mamka/HARDWARE.md#converters)): the RT pin on ground for 2.2 MHz, a 2.2 µH shielded
inductor, the divider 28.0 kΩ over 12.1 kΩ → 3.31 V with 22 pF across the top resistor, C_IN
4.7 µF 50 V + 100 nF, C_OUT 3 × 10 µF 50 V + 100 nF, 1 µF on VCC and 100 nF on BOOT. From 16 V
at 2.2 MHz the on-time is 94 ns against the 75 ns minimum, as for Mamka's own 3.3 V.

- **EN from the ROCK, straight.** Each converter's EN is a trace from a GPIO of the ROCK, **EN A**
  from header pin 16 (GPIO3_A4) and **EN B** from pin 32 (GPIO3_C2), across Mamka and the cable
  (see [Mamka](../mamka/HARDWARE.md#on-baťas-header)), with 100 kΩ to ground at the pin and
  nothing else: no transistor, no divider. EN takes up to 42 V and switches at 1.23 V (SNVSBY5B),
  so a 3.3 V high is on and a low or a floating pin is off. Both GPIOs rest at a pull-down out of
  reset (`GPIO3_A4_d`, `GPIO3_C2_d`, the ROCK 5T schematic V1.2), so the modules are off until
  Linux says otherwise; pin 33 is the other way (`GPIO3_A7_u`), so it carries a PGOOD, not an EN.
- **The PCIe driver does the switching,** not a script. In the device tree each EN is a
  `regulator-fixed` with `enable-active-high` and `vin-supply = <&vcc3v3_pcie30>`, the ROCK's
  own slot rail on GPIO1_A4, and each port names it as its `vpcie3v3-supply`: `pcie3x4` for
  slot A, `pcie3x2` for slot B (mainline `rk3588-rock-5t.dts` and its `rk3588-rock-5b-5bp-5t.dtsi`;
  the ROCK's rail is such a regulator already). The driver, `pcie-dw-rockchip.c`, enables the
  regulator before it touches the PHY, holds PERST# low, waits `PCIE_T_PVPERL_MS`, 100 ms, and
  lets it go; so the module gets the slot rail, its own 3.3 V (soft start 3.5 ms, t_SS,
  SNVSBY5B), and the reset in the order the M.2 sequence asks, with `startup-delay-us` set to
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
  Mamka's traces onto the ROCK's header pins 18 and 33, with 10 kΩ pull-ups from header pin 1,
  the ROCK's own 3.3 V, so nothing drives an unpowered RK3588. The ROCK reads them on an edge
  interrupt and knows at once which Umnica lost her supply; the link itself tells it first
  (a dead module drops the link and its driver reads all ones), PGOOD says why. A converter in
  hiccup, after a short, retries every 30–75 ms (SNVSBY5B, t_HICCUP), so its PGOOD flaps until
  its EN goes low.
- **What the module sees** is only this 3.3 V; it makes its own 1.8 V and core voltages from it,
  so the two converters, the ROCK's and Terem's, share no node and no frequency.
- **Current:** two modules at 5 W and the ROCK at up to 17 W are ~2.5 A from the battery at
  11.5 V; the XT30 carries 15 A continuous by its distributors (Amass's sheet to be read).

## The eFuse for the ROCK

The ROCK 5T takes 9–20 V on its DC jack, 5.5 × 2.5 mm, and Radxa recommends 12 V; its USB-C
does not power it (Radxa's FAQ). The pack gives ~11.5–15.6 V between 20 and 80% (an estimate
until the cell is measured, see [Babuška](../babuska/HARDWARE.md#the-battery)), 16 V at most, so
it runs straight from the battery, with no converter, through an eFuse here.

- **TI TPS26630** (SLVSE94G): 4.5–60 V, up to 6 A through its own 31 mΩ FET, the current limit
  set by a resistor, the output's rise by a capacitor, an undervoltage and an overvoltage cutoff
  set by a divider, a shutdown pin and PGOOD. The protection chain of the suit is then the
  battery's fuse, the BMS, and in every branch its own limit: Mamka's converters have theirs,
  Terem's and Kormilica's theirs, and the ROCK, which has no converter, gets the eFuse.
- **Its values:** R(ILIM) 6.04 kΩ for a limit of ~3 A (the sheet's table runs 30 kΩ for 0.6 A
  to 3 kΩ for 6 A, ~18 kΩ·A); C(dVdT) 22 nF for an output ramp of ~5–7 ms over 11.5–16 V
  (t = 20.8 × 10³ × V(IN) × C, equation 2), so the ROCK's input capacitors charge gently and the
  cable from the battery does not ring; the divider from IN_SYS, 866 kΩ, 75 kΩ and 66.5 kΩ to
  ground, puts the undervoltage cutoff at ~8.5 V and the overvoltage cutoff at ~18 V against
  the 1.2 V thresholds of UVLO and OVP (equations 9 and 10). The divider is a must: with UVLO
  at ground the part's own default of 15.5 V would never let the battery through. MODE open:
  a fault latches off, and Mamka clears it by cycling SHDN.
- **To Mamka** on the short cable: SHDN, which she drives (the eFuse sleeps at ~21 µA with it
  low), and PGOOD, an open drain pulled up to her 3.3 V; FLT is not wired, a ROCK that does not
  come up shows on PGOOD and on header pin 1 (see [Budilnik](../mamka/HARDWARE.md#budilnik)).
  The same 8-wire cable carries the converters' EN A, EN B, PGOOD A and PGOOD B, which only pass
  across Mamka to the header, and two grounds.
- Under 9 V, 2.25 V a cell, the ROCK 5T would go out; the suit shuts down at 20% long before,
  and the eFuse's 8.5 V is only the backstop.
- The battery input carries the house input bank, two 47 µF hybrid polymers with 10 µF 50 V and
  100 nF, as on Mamka; the converters and the eFuse take their peaks from it.

## Open questions

- the ROCK 5T's 2D drawing: the two slots' spacing, height and orientation, which decide whether
  Terem is one board or two,
- the Hailo-10H 2242 module's order code and its sheet: current, heat, and whether it carries a
  heatsink of its own,
- a module with its EN low in a live slot: the host's pull-ups and the reference clock into an
  unpowered Hailo-10H, from its sheet; the Hailo driver's own low-power states as the way to
  rest a module while running,
- the TPS26630's current limit against the ROCK 5T's real peaks with the glasses on its USB-C,
  measured; the XT30's rating from Amass's own sheet.
