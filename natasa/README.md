<div align="center">

# Nataša

**The unit in the headband:** headphones, two microphones, vibration and buttons.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

## What it does

Nataša sits on the head as part of the headband. Her processor is Mamka's family (see
[Porjadok](../porjadok/README.md)), the **STM32H562RG** in LQFP64, 10 × 10 mm, with 49 I/Os, 1 MB of
flash and 640 KB of RAM (DS14258, table 2). The 64-pin part lays out more easily around the sound,
the motors and the buttons, and leaves pins to spare. Everything runs over wires:

- **two microphones:** they send what they hear to Baťa, for
  [Soňa](../sona/README.md) and [Taťána](../tatana/README.md), each on the ear's board with its
  four buttons, one lead to a side,
- **vibration:** four motors in the headband, for [Soňa](../sona/README.md),
  [Míša](../misa/README.md) and [Nikita](../nikita/README.md),
- **buttons:** eight, four behind each ear, for what is quicker by hand than by voice,
- **headphones:** Bluetooth ones paired with Baťa as a rule; a 3.5 mm jack for wired ones is
  fitted on request, its DAC and amplifier with it,
- **Míša** beside her: [Míša](../misa/README.md), the radar unit on the forehead, is a unit of
  his own on line 8, with his own tap.

**The sound goes to Bluetooth headphones,** paired with Baťa, who sends it there himself (see
[Bluetooth headphones](SOFTWARE.md#bluetooth-headphones)). **Nataša is optional:** without her
the headphones' own microphone and buttons stand in; Míša keeps his own place on line 8 either way.

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | line 8, the processor's pins, the ear's boards, the microphones, the headphones' jack (fitted on request), the buttons, the motors, Míša beside her, the power |
| [SOFTWARE.md](SOFTWARE.md) | the sound across the suit, line 8, her frames, Bluetooth headphones, the buttons' bits and their assignment, the vibration commands, Míša beside her, the clocks, the DMA and the interrupts |
| [CONSTRUCTION.md](CONSTRUCTION.md) | where things sit on the head |
| [WHY.md](WHY.md) | what is not used, and why |
