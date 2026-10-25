<div align="center">

# Nataša

**The unit in the headband:** headphones, two microphones, vibration and buttons.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

## What it does

Nataša sits on the head as part of the headband. Like every module it has an STM32H523 (see
[Porjadok](../porjadok/README.md)), here the **STM32H523RE** in LQFP64, 10 × 10 mm, with 49 I/Os and
512 KB of flash (DS14540, table 2). The 64-pin part lays out more easily around the sound, the
motors and the buttons, and leaves pins to spare. Everything runs over wires:

- **headphones:** any wired headphones plug into its jack,
- **two microphones:** they send what they hear to Baťa, for
  [Soňa](../sona/README.md) and [Taťána](../tatana/README.md),
- **vibration:** four motors in the headband, for [Soňa](../sona/README.md),
  [Míša](../misa/README.md) and [Nikita](../nikita/README.md),
- **buttons:** eight, four behind each ear, for what is quicker by hand than by voice,
- **Míša** beside her: [Míša](../misa/README.md), the radar unit on the forehead, is a unit of
  his own on line 8, with his own tap.

**Nataša is optional:** any Bluetooth headphones or hands-free take her place, paired with Baťa,
who then sends the sound there (see [Bluetooth headphones](SOFTWARE.md#bluetooth-headphones));
Míša keeps his own place on line 8 either way.

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | line 8, the processor's pins, the microphones, the headphones, the buttons, the motors, Míša beside her, the power |
| [SOFTWARE.md](SOFTWARE.md) | the sound across the suit, line 8, her frames, Bluetooth headphones, the buttons' bits and their assignment, the vibration commands, Míša beside her, the clocks, the DMA and the interrupts |
| [CONSTRUCTION.md](CONSTRUCTION.md) | where things sit on the head |
| [WHY.md](WHY.md) | what is not used, and why |
