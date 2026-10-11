<div align="center">

# Nataša: why not

**The graveyard:** what was considered for the headband unit and why it is not used.

↑ [Nataša](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Each entry says what it was and why it went, so that nobody digs it up without knowing. Where a
thing waits in reserve, it says so.

- **I2S extenders** between Baťa and the headband. Overpriced; the sound rides in the head line's
  frames, Mamka's SAI on one end and the STM32H523's SPI in I2S mode on the other, both on the
  suit's clock.
- **Analog microphones and an ADC.** Digital MEMS microphones with the converter inside go
  straight into the I2S, two on one data wire.
- **A DAC with registers** over I2C or SPI. The TAD5142 and the TPA6132A2 are set by their pins,
  so nothing has to be written and nothing can be left unwritten after a reset.
- **Output capacitors on the headphones.** The TPA6132A2's DirectPath outputs are centred on
  ground from its own charge pump; the jack's sleeve goes straight to ground.
- **Three-colour LEDs at eye level,** which Nataša started with. Vibration does their job better:
  it needs no looking, and it works for the deaf and the blind alike.
- **A linear actuator (LRA)** instead of the coin motors. It starts faster and fits the same
  board, LRA/ERM high and the driver finds its resonance itself; it waits in reserve.
- **Bluetooth as the only headphones.** It adds 150–220 ms through SBC; the wired jack stays,
  and Bluetooth is for whoever wants it, paired with Baťa.
- **Míša on the head line** as a unit of its own. It plugs into Nataša instead: one socket, a
  UART, its sphere rides in Nataša's frame, and Nataša buzzes by herself when something is near.
- **Four motors at once.** Two keep the current at ~0.2 A; four starting together with the rest
  of Nataša would come close to the head line's 1 A converter.
