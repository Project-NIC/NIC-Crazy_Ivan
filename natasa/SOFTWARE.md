<div align="center">

# Nataša: software

**What travels and what the buttons do:** the sound across the suit, line 8, Nataša's frames,
Bluetooth headphones, the buttons and the motors, Míša beside her.

↑ [Nataša](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Nataša is a unit like any other, 0x81, line 8's first: the same frames of 34 B and 8 B, the same
kinds and the same answers (see [Porjadok](../porjadok/SOFTWARE.md)). Her own chips are 0x02, the
sound, and 0x03, the motors. She is optional: any Bluetooth headphones or hands-free take her
place (see [Bluetooth headphones](#bluetooth-headphones)), and line 8 runs without her.

## Sound across the suit

Instead of overpriced I2S extenders, the sound travels like this:

1. Baťa sends his I2S into the SAI of the STM32H562 on Mamka. The SAI is the I2S
   master and runs from the suit's clock.
2. That processor sends the sound down line 8, in frames.
3. The STM32H523 in Nataša turns it back into I2S. The H523 has no SAI, so it uses an SPI in
   I2S mode, full duplex: the sound goes out to the DAC for the headphones, and the two
   microphones come in on the same bit clock.
4. The microphones' sound goes back the same way: up line 8 and through the SAI into
   the computer.

The sound is standard I2S: **48 kHz, 16 bits, stereo**, so neither the computer nor its
programs convert any rate. Mamka and Nataša both make the 48 kHz from the suit's clock with the
same PLL setting, ÷ 1, × 40, ÷ 32 = 12.288 MHz, 256 × 48 kHz (see
[Mamka](../mamka/HARDWARE.md#helper-functions)). The bit clock is 3.072 MHz, 64 bit clocks per
sample, as the microphones ask. Both ends run from one clock, so nothing drifts apart.

**A buffer at each end,** as network audio keeps one: Nataša holds ~10 ms of sound, 480 stereo
samples, 1,920 B of her 272 KB, and plays it out evenly; Mamka tops it up, so the sound need not
keep to the cycles. Both ends run from the suit clock, so the rates never part and the buffer's
level holds, with no resampling.

**The sound goes in packets of 198 B, 1 ms each,** the suit's fourth frame (see
[Porjadok](../porjadok/SOFTWARE.md#the-frames)): 0x22 down for the headphones, 0x23 up from the
microphones.

| B | a packet of sound |
|---|---|
| 0 | the unit's number, 0x81 |
| 1 | the kind, 0x22 or 0x23 |
| 2–3 | the packet's number |
| 4–195 | 192 B of sound: 48 stereo samples of 48 kHz, 16 bits, left then right |
| 196–197 | CRC-16 |

- **1,000 a second each way,** ~198 kB/s, ~10 % of line 8 each way. Its size is set by
  Nataša's slot up, 256 B a cycle at 19.66 Mbaud: her frame of data 34 B or her diagnostics 34 B,
  never both in one cycle, and the packet 198 B.
- **16 bits on the wire,** 32 in the slots: the SAI and Nataša's SPI in I2S mode put 16-bit
  samples into 32-bit slots and take them out in hardware (RM0481 Rev 5, 59.4.7 and figure 850;
  58.9.5); the slots are of 32 bits because the microphones want 64 bit clocks a frame
  (DS-000069 Rev 1.2), and nothing of the padding goes on the line. The microphones' 24 bits are
  cut to the upper 16: their signal-to-noise of 65 dBA fits in 16 bits.
- **A lost packet** is 1 ms of silence, known by its CRC and its number: Nataša asks it again
  with *repeat* (0x13, its number) in 8 B in her slot, and Mamka, who keeps the last ~10, sends it
  again within the 10 ms of the buffer: no click and no sample played twice. The microphones'
  packets are mended the same way the other round, Mamka asking. The sound comes 10 ms later;
  for the assistants' speech, reading and music that does not matter, and the vibration to the
  beat goes by the motors' own registers.
- **The microphones** go only while there are microphones and Baťa wants them, a packet in her
  slot every ~3.8 cycles; Mamka holds a buffer of her own on her side and feeds the SAI from it.
  The sound runs whether a measurement runs or not.

## Line 8

Line 8 runs by its slots always, measuring or not, since the sound runs always (see
[Porjadok](../porjadok/SOFTWARE.md#line-8)): two slots of 130.2 µs, 256 B each. Nataša counts
the cycle on her TIM2 from the suit clock, **3,840 a second,** and Mamka's *heartbeat*, once a
second at a cycle's start, corrects it; after power-on she finds the cycle's start by it and stays
silent until then.

| slot | whose | what goes in it |
|---|---|---|
| 1 | Nataša's | her frame of data in cycle 15 of 32 and her diagnostics in cycle 31; a packet of the microphones every ~3.8 cycles; *repeat* and an answer of 8 B; a 34 B answer waits for a cycle without a packet |
| 2 | Míša's, his own | his frame of data in cycle 15 of 32 and his diagnostics in cycle 31; his pieces of the sphere after every radar frame; his answers |

The pair down is Mamka's: the sound, 1,000 packets a second, the heartbeat, and whatever is for
Nataša or Míša. The rest of line 8's hardware is under [hardware](HARDWARE.md#line-8).

## Nataša's frames

**Her frame of data** goes in her slot once every 32 cycles, in the cycle whose number mod 32 is
15, half a round from the diagnostics, ~4 kB/s, whatever is plugged in, so
that nothing hangs on the microphones or the headphones, which are no must; a button is known
within ~8 ms.

| B | field |
|---|---|
| 0–3 | 0x81, 0x20, the frame's number |
| 4–5 | the buttons, a bit each, 1 pressed, debounced; 8 used, bits 0–3 behind the right ear, 4–7 the left |
| 6 | the state: bit 0 Míša present, 1 the warning sounding, 2 a motor running, 3 an unconfirmed firmware, 4 the last update failed |
| 7–31 | zeros |
| 32–33 | CRC-16 |

- **Her diagnostics** are a unit's with no ADS1299 (see
  [Porjadok](../porjadok/SOFTWARE.md#the-diagnostics)): the chips alive, her temperature and her
  lowest 3.3 V.
- **The buttons:** Mamka's processor 2 compares them with the frame before and sends Baťa an
  event for each change, with the cycle's number (see
  [Mamka](../mamka/SOFTWARE.md#mamkas-own-registers)). A hold is Baťa's to tell from the time.
- **The slow data,** her firmware's version and her table, Baťa reads when he wants, from her
  chip 0x00 (see [Porjadok](../porjadok/SOFTWARE.md#the-registers)).

## Bluetooth headphones

Whoever wants wireless headphones, bone conduction ones for instance, pairs them with
Baťa: the ROCK 5T has Bluetooth 5.2. PipeWire
sends the sound to them instead of down the line, and no stream runs down line 8; Nataša's
microphones keep listening.

Bluetooth adds delay: SBC, the codec that every A2DP device has, commonly takes 150–220 ms.
When the music plays from the computer, Nikita delays its pulses by as much, so the beat in
the ears and on the head stays together.

## Buttons and vibration

**Buttons:** up to 16, one bit each, in 2 B of her frame of data; Nataša debounces them herself
and confirms each press with a short pattern, which a setting can turn off.

**The motors are chip 0x03.** The four DRV2603 have no registers, only a PWM in, so the patterns,
the strength and the brake are Nataša's, and she answers to a map of registers of her own:

| register | what |
|---|---|
| 0x00–0x03 | the left motor: the pattern (0 stop, 1–15), the strength (0–100 %), the repeats (0 until stopped), a pulse (its length in 10 ms; writing it gives one pulse now) |
| 0x04–0x07 | the right, the same |
| 0x08–0x0B | the forehead, the same |
| 0x0C–0x0F | the nape, the same |
| 0x10–0x13 | the settings: the warning's distance (0.1 m, 0 off), its speed (0.2 m/s, 0 off), the press confirmation's pattern (0 off) and its strength |
| 0x20–0x5F | patterns 8–15, 8 B each: up to 8 steps, a step's length in 10 ms, on and off in turn from on, a 0 after the last |

Nataša carries out a frame whole, so one frame sets all four motors, 16 of its 25 values. A
pattern other than 0 starts its motor with its strength and repeats, 0 stops it; the pulse for
Nikita's beat is one byte written, in 8 B, for the least delay. The answer is the result, as for
every write.

- **Patterns 0–7 are built in,** in steps of on and off: 0 nothing; 1 a tap, 50 ms; 2 long,
  300 ms; 3 a double tap, 50 on, 100 off, 50 on; 4 a triple tap, the same with a third; 5 a
  slow pulse, 200 on, 800 off; 6 a fast pulse, 100 on, 150 off; 7 a ramp, 50, 100 and 200 ms
  on with 100 ms off between. Patterns 8–15 are Baťa's to define and are lost at power-off, so
  he writes them at start. Which pattern means what is set on Baťa, so it can change.
- **Strength** is the duty of the PWM above the 50% that means nothing, scaled to the ~94% of the
  motor's 3.0 V (see [hardware](HARDWARE.md#vibration)); the overdrive at a start and the brake
  at the end of every "on" are the firmware's and not in the registers.
- **Starts are spread:** when more than two motors are to run, Nataša starts them 50 ms apart,
  so their starting currents never add up on line 8's converter.
- **The warning** is Nataša's own, from the sphere as it passes (see [Míša](#míša-beside-her)):
  when a field of the middle row in the three columns ahead is nearer than the set distance or
  coming faster than the set speed, she plays pattern 5 on the forehead until it passes and sets
  bit 1 of her state, and processor 2 sends the event. It works with Baťa hung.
- **A short press and a hold** on each button. What they do is set on the computer, so it can
  change; a first assignment:

| side | button | short | hold |
|---|---|---|---|
| right | main | play / pause: a book, reading, music | dictation: speak while it is held, Taťána types it on release |
| right | volume + | louder | |
| right | volume − | quieter | |
| right | repeat | say the last message again | |
| left | mode | the next assistant on or off, said and confirmed by vibration | the state: the battery and what is on |
| left | forward | the next sentence | the next paragraph or chapter |
| left | back | the previous sentence | the previous paragraph or chapter |
| left | quiet | Soňa and Míša off or on together, for a social event or a companion | |

## Míša beside her

[Míša](../misa/README.md) is a unit of his own, 0x82, line 8's second, in slot 2, with his own tap
and drivers; Nataša does not pass his frames, and either may be missing. **She reads his
sphere as it passes** on the return pair, which every unit on the line hears: the middle row, for
the warning, so she warns by herself with Baťa hung. Without a sphere for 4 frames, 400 ms, she
clears bit 0 of her state. His sphere and his time are under
[Míša](../misa/SOFTWARE.md#the-sphere).

## Clocks

By the suit's clock tree (see [Porjadok](../porjadok/SOFTWARE.md#the-clock-tree)): the core at
49.152 MHz, the line's USARTs on PLL3 Q. She adds:

| what | setting |
|---|---|
| SPI3 in I2S, the sound | PLL1Q ÷ 32 (field 31): 12.288 MHz, SPI3SEL = 000 (RCC_CCIPR3, 11.8.42); I2SDIV = 2, ODD = 0, CHLEN = 1 (32-bit slots), MCKOE = 0: 12.288 MHz ÷ (32 × 2 × 4) = 48 kHz, a bit clock of 3.072 MHz (RM0481 Rev 5, 58.9.9) |
| USART1 and UART4, line 8 | PLL3 Q, 196.608 MHz (USART1SEL and UART4SEL = 010); OVER8 = 1, BRR = 0x0012: 19,660,800 Bd |
| TIM3, the motors | PSC = 0, ARR = 2,047: 24.0 kHz, inside the DRV2603's 10–250 kHz (SLOS754C), the duty in 2,048 steps |
| TIM2, the cycles | PSC = 4: a tick of the suit clock; ARR = 2,559, a cycle of 260.4 µs, set by Mamka's heartbeat |

## DMA

By the suit's rules (see [Porjadok](../porjadok/SOFTWARE.md#the-gpdma)), 5 channels:

| channel | request (REQSEL) | what | priority | how |
|---|---|---|---|---|
| GPDMA1 0 | 27, uart4_rx | UART4 RX: Mamka's frames, the sound among them | 3 | circular |
| GPDMA1 1 | 21, usart1_rx | USART1 RX: the return pair, her own sending as its echo and Míša's sphere as it passes | 3 | circular |
| GPDMA1 2 | 10, spi3_rx | SPI3 in I2S, RX: the microphones | 2 | circular |
| GPDMA2 0 | 22, usart1_tx | USART1 TX: her frames in her slot | 3 | one block a slot |
| GPDMA2 1 | 11, spi3_tx | SPI3 in I2S, TX: the DAC | 2 | circular |

## Interrupts

By the suit's levels (see [Porjadok](../porjadok/SOFTWARE.md#interrupts)); the numbers are the
vector table's (RM0481 Rev 5, table 153):

| level | interrupt | what it does |
|---|---|---|
| 0 | TIM2 (45) | her cycle, kept from the suit clock and set by the heartbeat, measurement or not: her slot's sending started |
| 2 | UART4 (61), USART1 (58) | Mamka's frames in; the return pair: the echo checked, Míša's sphere read |
| 4 | GPDMA1 channel 2, GPDMA2 channel 1 (29, 91) | the I2S's halves, both ways |
| 8 | ADC1 (37), FLASH (6) | her temperature and her 3.3 V, the firmware update; the DAC's error pin, PB10, is read with each frame, as the buttons are |

## Open questions

- the buttons' final assignment, tried with the people who will wear it,
- how Baťa says he wants the microphones' stream, and how he stops it: a register of the sound's
  chip, still to set,
- the radar's image through the suit: its kind's number, its size and TI's loading protocol, once
  the radar is on the bench.
