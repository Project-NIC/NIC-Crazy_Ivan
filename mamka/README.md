<div align="center">

# Mamka

**The base board:** she sits on Baťa's header and carries the clock for the whole suit, the
sound bridge, the drivers for the five lines and the suit's power.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

Russian slang calls a motherboard *mamka*, and so does this one. She runs the suit and feeds her
own children, its modules. [Kormilica](../kormilica/README.md), the wet nurse, feeds the
Raspberry Pi, and [Baťa](../bata/README.md), the computer, does the thinking.

Mamka rides in the backpack with [Babuška](../babuska/CONSTRUCTION.md#the-backpack), the
battery. The same Mamka sits on either computer, a Radxa ROCK 5T or a Raspberry Pi 5, with no
variants and no jumpers.

**Two processors, one board.** She does two things at once, as mums do: processor 1 runs the
body, processor 2 the head and the household. Each has its own job and its own path to Baťa, and
they do not talk to each other; they share only a clock wire and the power.

| | processor 1: the body | processor 2: the head and the household |
|---|---|---|
| to the suit | the four body lines; the clock for all five lines | the head line: Nataša and what else sits on the head |
| to Baťa | two SPIs with the suit's data, "data ready", the UART for diagnostics, firmware and the blocks' chip settings | the I2S with the sound, the I2C with the head's buttons, vibration and settings, Míša's sphere and the battery's state, "a message waiting" |
| the rest | | the BMS, the converters, Kormilica or Terem, Budilnik (the start button and the latch), the fan, the GPS if fitted |
| DMA | 12 of 16: the lines 8, the SPIs 2, the UART 2 | 8 of 16: the head line 2, the SAI 2, the BMS 2, the I2C 2; with the GPS 9 |

What is on the board, pin by pin, is under [hardware](HARDWARE.md); what the two processors do
under [software](SOFTWARE.md); how the board sits over the computer under
[construction](CONSTRUCTION.md); and what was tried and dropped under [why not](WHY.md).

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | the parts, both processors' pins, Baťa's header, the lines, the clock, the helper functions, Mamka's own supply, the converters, the filtering |
| [SOFTWARE.md](SOFTWARE.md) | the control channel and the UART to Baťa, the sound and the clock on Baťa's side, the BMS's protocol, the memory, the firmware and its update |
| [CONSTRUCTION.md](CONSTRUCTION.md) | the strip and the wing over the computer, the connectors' edge, what to keep clear of |
| [WHY.md](WHY.md) | what is not used, and why |
