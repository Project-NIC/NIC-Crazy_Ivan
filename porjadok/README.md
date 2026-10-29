<div align="center">

# Porjadok

**What holds for every module:** processor, firmware and the links between boards.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

*Porjadok*, Russian for order, as in the order a household keeps: the rules every member lives
by.

## Processor

The units in the suit each have an **STM32H523** processor: the sensing modules, the glove's
Staršaja, Nataša and Míša; the glove's and the sock's Bratiški are the smaller **STM32H503**.
[Mamka](../mamka/README.md) has two of the more capable **STM32H562**, one for the limbs' lines 1–4
and one for the head's and the trunk's lines 5–8 and the household, next to Baťa, the computer in
the backpack, a Radxa ROCK 5T. The packages: UFQFPN48 on a module, on the glove's Staršaja and on
Míša, LQFP64 for Nataša, UFQFPN32 for a Bratiška, LQFP100 on Mamka.

## Firmware

Every module: C, hard-coded, with no operating system.

## Files

The rules themselves are in two files: what every module shares in copper and what it shares in
firmware. The graveyard holds what was considered and dropped.

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | the power rails and the budget, the lines, the cable and its connectors, the drivers on a unit, the boards |
| [SOFTWARE.md](SOFTWARE.md) | the modes, the frames and their slots, the commands and the registers, the bring-up, the start, the errors, the way into Baťa, the firmware, the output of the whole suit |
| [WHY.md](WHY.md) | what is not used, and why |
