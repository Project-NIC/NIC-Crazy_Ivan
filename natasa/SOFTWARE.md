<div align="center">

# Nataša: software

**What travels and what the buttons do:** the sound across the suit, Nataša's frame, Bluetooth
headphones, the buttons' bits and assignment, the vibration commands, Míša's wire.

↑ [Nataša](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## Sound across the suit

Instead of overpriced I2S extenders, the sound travels like this:

1. Baťa sends his I2S into the SAI of the STM32H562 on Mamka. The SAI is the I2S
   master and runs from the suit's clock.
2. That processor sends the sound down the head line.
3. The STM32H523 in Nataša turns it back into I2S. The H523 has no SAI, so it uses an SPI in
   I2S mode, full duplex: the sound goes out to the DAC for the headphones, and the two
   microphones come in on the same bit clock.
4. The microphones' sound goes back the same way: up the head line and through the SAI into
   the computer.

The sound is standard I2S: **48 kHz, 16 bits, stereo**, so neither the computer nor its
programs convert any rate. Mamka and Nataša both make the 48 kHz from the suit's clock with the
same PLL setting, ÷ 1, × 40, ÷ 32 = 12.288 MHz, 256 × 48 kHz (see
[Mamka](../mamka/HARDWARE.md#helper-functions)). The bit clock is 3.072 MHz, 64 bit clocks per
sample, as the microphones ask. Both ends run from one clock, so nothing drifts apart.

The head line keeps 3,840 cycles a second. 48,000 / 3,840 = 12.5 samples a cycle, so the cycles
carry 12 and 13 of them in turn, 25 in every two.

| direction | what | travels | per cycle |
|---|---|---|---|
| down | stereo, 16 bits | a container of type 8 in the master's channel (see [Porjadok](../porjadok/SOFTWARE.md#the-channel-from-the-master)) | 48–52 B |
| up | the two microphones, 16 bits | in [Nataša's frame](#natašas-frame), 13 places of 4 B | 48–52 B |

See [Porjadok](../porjadok/SOFTWARE.md#timing-of-one-cycle) for the channel and the slots. The
samples are not in step with the cycles, 25 come in every two, so each frame carries the 12 or
13 that arrived since the last one and says which in its state byte; processor 2 only appends
them to the SAI's stream. The sound runs whether a measurement runs or not.

## Nataša's frame

Nataša is unit 1 on the head line and sends in slot 1 of every cycle, like a block, but her
frame is her own: **68 B**, 34.6 µs at 19.66 MBd, with ~30 µs of the slot left for her answers,
which are all short. The sample number is the master's from the control frame.

| byte | field | meaning |
|---|---|---|
| 0 | `addr` | 1, the unit's number, as the block number in a block's frame |
| 1 | state | bit 0: 13 samples in this frame (0: 12, the last place zeros); bit 1: Míša present; bit 2: the warning is sounding; bit 3: a motor is running; bit 4: running an unconfirmed firmware; bit 5: the last update failed |
| 2–3 | `sample` | the master's sample number, little-endian |
| 4–5 | buttons | one bit each, 1 = pressed, debounced; 8 used, bits 0–3 the right temple, 4–7 the left |
| 6–13 | rotation | 8 B placed by `sample` mod 16: positions 0–13 Míša's sphere as she last sent it, 112 B, zeros without Míša; 14 Nataša's state: firmware version (2 B), the last container `seq` she took (1 B), her temperature (2 B, 0.1 °C), the sphere's age (2 B, cycles, 0xFFFF none), 1 B zero; 15 counters: CRC errors seen on the channel from the master (2 B), on Míša's wire (2 B), repeats asked of her (2 B), 2 B zeros |
| 14–65 | microphones | 13 places of 4 B: left then right, 16 bits each, oldest first |
| 66–67 | `crc` | CRC-16 over bytes 0–65 |

- **The rotation** brings the whole sphere every 16 cycles, 4.2 ms, many times over for each of
  Míša's frames at 16 Hz; processor 2 hands a sphere on to Baťa when position 13 completes it
  and its frame number has changed. A lost frame costs nothing: the next round brings it again.
- **The buttons** go every cycle; processor 2 compares them with the last frame's and sends an
  event (type 0x15) for each change, with the sample number, over the I2C (see
  [Mamka](../mamka/SOFTWARE.md#the-control-channel)). A hold is Baťa's to tell from the time.
- **Repeats:** as for a block, a bad frame is asked again with *repeat* and comes after the
  fresh one in the next slot, 136 B, 69 µs: longer than the slot, so on the head line a repeat
  runs into slot 2, which is free while Nataša is alone there. Should a second unit join the
  head line, it takes slot 3.

## Bluetooth headphones

Whoever wants wireless headphones, bone conduction ones for instance, pairs them with
Baťa: the ROCK 5T has Bluetooth 5.2, the Raspberry Pi 5 Bluetooth 5.0. PipeWire
sends the sound to them instead of down the line, and Nataša's microphones keep listening.

Bluetooth adds delay: SBC, the codec that every A2DP device has, commonly takes 150–220 ms.
When the music plays from the computer, Nikita delays its pulses by as much, so the beat in
the ears and on the head stays together.

## Buttons and vibration

Buttons and vibration are a few bytes and need nothing extra:

- **Buttons:** up to 16, one bit each, in 2 B of Nataša's frame; Nataša debounces them herself
  and confirms each press with a short pattern, which a setting can turn off.
- **Vibration:** the computer sends a container of type 9, which motors and which pattern. It
  goes to processor 2 over the I2C and down the head line, and Nataša plays the pattern herself.

**The containers of type 9,** data byte 0 the command:

| byte 0 | command | data after it |
|---|---|---|
| 1 | *vibrate* | motors (1 B, bit 0 left, 1 right, 2 forehead, 3 nape), pattern (1 B, 0–15), strength (1 B, 0–100%), repeats (1 B, 0 = until *stop*) |
| 2 | *pulse* | motors (1 B), length (1 B, in 10 ms), strength (1 B): one pulse now, for Nikita's beat |
| 3 | *stop* | motors (1 B) |
| 4 | *define* | pattern (1 B, 8–15), then up to 8 steps of on and off (1 B each, in 10 ms), a 0 after the last step unless all eight are given: 3–18 B |
| 5 | *settings* | the warning's distance (1 B, in 0.1 m, 0 off), the warning's speed (1 B, in 0.2 m/s, 0 off), the press confirmation's pattern (1 B, 0 off) and strength (1 B) |

The answer is the result byte alone: 0 done, 1 an unknown pattern or motor, 2 a bad length.

- **Patterns 0–7 are built in,** in steps of on and off: 0 nothing; 1 a tap, 50 ms; 2 long,
  300 ms; 3 a double tap, 50 on, 100 off, 50 on; 4 a triple tap, the same with a third; 5 a
  slow pulse, 200 on, 800 off; 6 a fast pulse, 100 on, 150 off; 7 a ramp, 50, 100 and 200 ms
  on with 100 ms off between. Patterns 8–15 are Baťa's to define and are lost at power-off, so
  he sends them at start. Which pattern means what is set on Baťa, so it can change.
- **Strength** is the duty of the PWM above the 50% that means nothing, scaled to the ~94% of the
  motor's 3.0 V (see [hardware](HARDWARE.md#vibration)); the overdrive at a start and the brake
  at the end of every "on" are the firmware's and not in the command.
- **Starts are spread:** when a command names more than two motors, Nataša starts them 50 ms
  apart, so their starting currents never add up on the head line's converter.
- **The warning** is Nataša's own, from the sphere as it passes (see [Míša's wire](#míšas-wire)):
  when a field of the middle row in the three columns ahead is nearer than the set distance or
  coming faster than the set speed, she plays pattern 5 on the forehead until it passes, sets
  bit 2 of her state and processor 2 sends the event. It works with Baťa hung.
- **A short press and a hold** on each button. What they do is set on the computer, so it can
  change; a first assignment:

| temple | button | short | hold |
|---|---|---|---|
| right | main | play / pause: a book, reading, music | dictation: speak while it is held, Taťána types it on release |
| right | volume + | louder | |
| right | volume − | quieter | |
| right | repeat | say the last message again | |
| left | mode | the next assistant on or off, said and confirmed by vibration | the state: the battery and what is on |
| left | forward | the next sentence | the next paragraph or chapter |
| left | back | the previous sentence | the previous paragraph or chapter |
| left | quiet | Soňa and Míša off or on together, for a social event or a companion | |

## Míša's wire

The UART to [Míša](../misa/README.md), 1,228,800 Bd, 8N1 (see
[hardware](HARDWARE.md#míšas-socket)), carries CI-STP containers both ways, with data up to
122 B as on the I2C. On the wire Míša is `addr` 1; seen from the head line she is **0x81**, the
unit behind Nataša, as a glove is the unit behind its block: a container for 0x81 Nataša puts on
the wire as it came, readdressed to 1, and Míša's answer she relays in her slot. So Míša's
settings and firmware (kind 4) come from Baťa like anyone's, through processor 2 and Nataša.

| `type` | from | data |
|---|---|---|
| 11 *measure* | Nataša, every 240 cycles | the sample number (4 B) at which Míša starts the radar's frame, 16 times a second; no answer |
| 10 the sphere | Míša, once a frame | 112 B: the frame number (1 B), status (1 B: bit 0 radar, 1 ultrasound, 2 IMU in order, 3 levelled), the head's turn since the last frame (1 B, signed, 2° steps), the pitch (1 B, signed, degrees), then the 36 fields of 3 B, the up row's 12 columns from column 0, then the middle, then the down; `seq` = the frame number; no answer |

- A sphere is 118 B on the wire, 0.96 ms of the 62.5 ms between frames. Nataša checks its CRC,
  keeps it as the current sphere for her frame's rotation and reads its middle row for the
  warning. Without a sphere for 4 frames, 250 ms, she clears bit 1 of her state and the
  rotation goes to zeros.
- The radar's own image, which Míša loads into the IWRL6432 over its UART and SOP0, would be a
  kind of its own, 7; how large it is and how Míša holds it is open.

## Open questions

- the buttons' final assignment, tried with the people who will wear it,
- the radar's image through the suit: its size and TI's loading protocol, once the radar is on
  the bench.
