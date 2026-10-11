<div align="center">

# Porjadok: why not

**The graveyard:** what was considered for the household's rules and why it is not used.

↑ [Porjadok](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Each entry says what it was and why it went, so that nobody digs it up without knowing. Where a
thing waits in reserve, it says so.

## The lines

- **M-LVDS** for the lines. Considered for its speed; classic RS-422/485 stayed because of what
  the drivers and the parts around them consume, and the THVD145x reach 50 Mbit/s anyway.
- **The RP1's UARTs for the lines,** on the Raspberry Pi of 0.1. They reach 6.25 Mbit/s at most,
  without DMA; the lines end at Mamka's STM32H562 at 19.66 Mbaud, and Baťa gets whole cycles over
  SPI.
- **The Raspberry Pi as the SPI slave,** in 0.1. The Linux driver did not support it; the
  computer is the master and Mamka raises "data ready" when a cycle waits.
- **Category 5e or 6 Ethernet cable** for the lines, with 100 Ω terminations. It would do; the
  3M 1785 flat cable takes IDC sockets anywhere on a flat stretch, so a block taps in without a
  connector of its own. The Ethernet cable stays as the fallback.
- **The lines twisted or untwisted.** Not decided: the untwisted 3M 3517 is a variant to try,
  held to two tests (see [hardware](HARDWARE.md#cable-and-connectors-in-the-suit)); until they
  pass, the twisted 1785 is the design.
- **The digital rail at 3.7 V,** in 0.1 and 0.2. It saved ~0.3 W across the suit against 4 V, but at
  the worst corner the cable, the filters and the connectors left the modules' TPS7A2033 ~3.35 V,
  under the 3.44 V its dropout (at most 140 mV) needs and the 3.6 V its ±1.5% asks (SBVS338H, 5.5),
  and the head's motors ~3.5–3.6 V, short of the 3.55 V their overdrive needs (SLOS754C). 4 V gives
  both room for ~0.3 W. The analog rail stays at 6 V: 5.5 V would save only ~0.06 W, and the
  headroom helps the TPS7A47 reject ripple.

## The frame and the output

- **A short START pulse.** Conversions run only while START is high; a pulse would stop the
  measurement after the first conversion (SBAS499C, 9.4.1 and 9.4.5). START stays high.
- **More than one byte per joint axis** on the output. Over 120° a byte's step is 0.47° and its
  rounding 0.14° RMS, under what IMUs and EMG deliver; more bits would carry noise, and the
  Hailo hands out UINT8 as it is.
- **Three angles for the shoulder and the hip.** Any three angles in a row have a pose where the
  first and third axes line up, and for the shoulder in the ISB convention it is the arm hanging
  at the side. They go out as a swing and a twist instead, with the unreachable pose put behind
  the head or the back.
- **A second number in the output frame.** RTP carries a sequence number and a timestamp, the
  one to see a loss, the other to place the data in time. CI-BTP carries the sample number
  alone, at the owner's wish: a lost snapshot frame shows as a jump in it, a lost event is caught
  by the event packet's own counter, and a meta packet comes again within a second.
- **Signing the firmware.** MCUboot checks a SHA-256 and a signature on every image. The suit
  takes images from Baťa alone, and whoever has Baťa has the suit with or without a signature,
  so the CRC-32 guards against a bad transfer and nothing more; a signature would cost a key and
  a verification in every unit.
- **Framing on the lines.** Byte stuffing or a sync word, as HDLC or COBS do, is not needed: the
  slots and the cycle say where a frame begins, the master sends nothing after its message until
  the next cycle, and every container has its own CRC, so a bad one costs the rest of that
  message and no more.
- **Labelling the contact points by hand.** The rule that marks them, a limb that neither hangs
  nor is held must rest on something, marks the recordings as well, so nobody labels.
