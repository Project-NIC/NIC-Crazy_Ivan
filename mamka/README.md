<div align="center">

# Mamka

**The base board:** she sits on Baťa's header and carries the clock for the whole suit, the
sound bridge, the drivers for the eight lines and the suit's power.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

Russian slang calls a motherboard *mamka*, and so does this one. She runs the suit and feeds her
own children, its modules, and the computers too, and [Baťa](../bata/README.md), the
computer, does the thinking.

Mamka rides in the backpack with [Babuška](../babuska/CONSTRUCTION.md#the-backpack), the
battery, on the header of Baťa's Radxa ROCK 5T, and feeds him and Borovičok, if he is fitted,
through an eFuse each.

**Two processors, one board.** She does two things at once, as mums do: processor 1 runs the
limbs, lines 1–4, processor 2 the head and the trunk, lines 5–8, and the household. Each has her
own path to Baťa; they share four wires, for the first *start*, the limbs' power and a frame of
34 B a second, and the clock buffers and the power. A Mamka for the head and the trunk alone leaves
processor 1 and the limbs' lines off the board.

| | processor 1: the limbs | processor 2: the head, the trunk and the household |
|---|---|---|
| to the suit | lines 1–4, the arms with their shoulders and the legs, one sender for all four | lines 5–7, the head, the chest and the back, one sender for all three; line 8, Nataša and Míša |
| to Baťa | SPI1_M1 at 37.5 MHz both ways: the frames up as they came, the settings and firmware down; "data ready" | SPI0_M2 and SPI3_M0 at 11.1 MHz, one transfer striped over both: the frames, Míša's sphere, her own registers (the battery, the power, the GPS, the events), the firmware; "data ready"; the I2S with the sound |
| to each other | START, the limbs' PGOOD, a UART at 115,200 Bd | the same |
| the rest | | the BMS, the converters, the computers' eFuses, Budilnik (the start button and the latch), the fan, the GPS if fitted |
| DMA | 7 of 16: the lines 5, the SPI 2 | 12 of 16: the lines 6, the SPIs 4, the SAI 2 |

What is on the board, pin by pin, is under [hardware](HARDWARE.md); what the two processors do
under [software](SOFTWARE.md); how the board sits over the computer under
[construction](CONSTRUCTION.md); and what was tried and dropped under [why not](WHY.md).

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | the parts, both processors' pins, Baťa's header, the lines, the clock, the helper functions, Mamka's own supply, the converters, the filtering |
| [SOFTWARE.md](SOFTWARE.md) | processor 1's SPI, processor 2's two, the wires between them, Mamka's own registers, the sound and the clock on Baťa's side, the BMS's protocol, the memory, the firmware and its update |
| [CONSTRUCTION.md](CONSTRUCTION.md) | the stack of the ROCK, Terem and Mamka in Mrazík, the window for the SoC's boss, the connectors, what to keep clear of |
| [WHY.md](WHY.md) | what is not used, and why |
