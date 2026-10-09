<div align="center">

# Porjadok

**What holds for every module:** processor, firmware and the links between boards.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

*Porjadok*, Russian for order, as in the order a household keeps: the rules every member lives
by.

## Processor

The modules in the suit each have an **STM32H523** processor: the sensing modules and Nataša.
[Mamka](../mamka/README.md) has two of the more capable **STM32H562**, one for the body and one for
the head, next to Baťa, the computer in the
backpack, a Radxa ROCK 5T or a Raspberry Pi 5. The package is chosen with each module's board
design.

## Firmware

Every module: C, hard-coded, with no operating system.

## Files

The rules themselves are in two files: what every module shares in copper and what it shares in
firmware. The graveyard holds what was considered and dropped.

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | the power rails and the budget, the lines, the cable and its connectors, the drivers on a block |
| [SOFTWARE.md](SOFTWARE.md) | the frame, the cycle and its slots, the channel from the master, the way into Baťa, the errors, the output of the whole suit, the start of a measurement |
| [WHY.md](WHY.md) | what is not used, and why |
