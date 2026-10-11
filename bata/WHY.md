<div align="center">

# Baťa: why not

**The graveyard:** what was considered for the computers and why it is not used.

↑ [Baťa](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Each entry says what it was and why it went, so that nobody digs it up without knowing. Where a
thing waits in reserve, it says so.

## The computers

- **An x86 board in the backpack** for learning. The Hailo Dataflow Compiler runs only on x86
  Linux, but it is needed once, at home, to compile the general model; the learning that happens
  in the suit is the small last part of the model, on one of Baťa's cores.
- **Orange Pi 5 Plus, ROCK 5B+ and other RK3588 boards.** The ROCK 5T won on its two M.2 slots
  for two Hailos, its DC input that takes the battery as it is, and DisplayPort on its USB-C.
  The ROCK 5B+ shares the header but takes its power over USB-C.
- **The Raspberry Pi 5,** Baťa's other computer until version 0.2, on Kormilica, the board that
  fed it and carried its one Hailo. With no NPU of its own it needs a Hailo for any model, and its
  one PCIe lane takes only one; Kormilica's stack over its Active Cooler made the layering awkward
  and the distances long; and it saves no battery, ~6.6–11 h against the ROCK 5T's ~7–10 h in
  the *normal* profile (Babuška's budget of version 0.1). The ROCK's mainline support keeps
  growing: the GPU since Linux 6.10, the NPU's own driver `accel/rocket`, the video decoders in
  2026. Kormilica's pages stay as they were under [retired](../retired/kormilica/README.md), for
  whoever wants a smaller suit on a Pi.
- **The AI HAT+ 2 on the Raspberry Pi.** The same chip; the M.2 module sat on Kormilica's wing
  instead, with its own 3.3 V, so the stack over the Raspberry Pi stayed Kormilica and Mamka.
- **A third computer for the cameras.** Ďaďa Sem was first a computer of his own on Ethernet;
  Baťa's NPUs look at the pictures instead (see [hardware](HARDWARE.md#ďaďa-sem)).
- **The cameras into Deduška,** on his NPU. Deduška is an add-on and the suit must see without
  him: Míša's warnings take Ďaďa Sem's results.
- **A UART or a tunnel through Mamka between Baťa and Deduška.** They talk over UDP on a short
  Ethernet cable; the ROCK 5T has two 2.5GbE ports.
- **USB between Baťa and Deduška.** Inside the backpack both run from Babuška, so no isolator is
  needed and Ethernet does; USB with the ISOUSB211 isolator is for a computer outside.

## The cameras

- **MIPI CSI cameras on the head.** The metre or two to the backpack needs serializers; USB 2
  reaches 5 m.
- **Network cameras.** They compress the picture, which delays it by hundreds of ms, and bring a
  switch with them.
- **MJPEG.** It would cost decoding, estimated at tens of percent of one core a camera; 640 × 480
  YUYV at 30 frames a second fits a USB 2 host uncompressed.
- **Cameras by radio,** Wi-Fi or other. A radio link needs pairing and a supply of its own on
  the head and shares the air with the Bluetooth headphones; a cable does none of that.
- **USB 3 cameras.** USB 3 puts broadband noise into the 2.4 GHz band (Intel's white paper of
  2012, read in summary), and on the head it would sit beside the Bluetooth headphones; USB 2
  carries 640 × 480 uncompressed.
- **Endoscope cameras.** Their fixed focus is close, ~3–8 cm by the sellers, and the picture is
  blurred beyond it.
- **A board module in a box of our own.** A ready bullet of Ø20 mm fits a clip on the headband or
  on the glasses as it is.
- **A stereo camera.** Two cheap cameras are not in step, up to one frame apart, which does not
  matter for naming things; should depth from two pictures be wanted, a stereo camera with both
  pictures in one frame on one USB 3 port is the way.

## The software

- **An image built from nothing,** Buildroot or the like. The smallest, but with no package
  manager, and the board's boot loader and support all to be done by hand; Armbian's minimal
  Debian brings them ready.
- **Fedora.** It works on arm64, but a release lasts about a year; Debian's stable one is kept
  for years, which suits a machine that should only run.
- **Raw EMG straight into the model,** Baťa only moving data. 2.46 MB/s of samples into a
  network cost what it does not need; the model takes 128 log-RMS envelopes and 64 IMU steps
  every 1/120 s instead, which one core computes in the gaps (see [signals](SIGNALS.md)).
- **A fixed 50 Hz notch** on the EMG. It takes EMG with it; the mains, if any is left behind
  the right-leg drive and −110 dB of CMRR, is tracked as a sinusoid and subtracted.
- **A driver of our own** to save the one copy from spidev's buffer into the Hailo's. 768 B per
  cycle cost next to nothing; the copy stays.
- **Training on the Hailo.** HailoRT has no functions for training; the Hailo only runs models.
- **An SSD on Baťa's PCIe** in the normal and brutal fittings. PCIe goes to the Hailos;
  recordings go to Deduška's NVMe SSD, or only the features are kept. In the small fitting his
  slots are free (see [Software](SOFTWARE.md#open-questions)).
- **An Umnica in Deduška.** He runs the applications and the glasses, not the suit's model, and
  the RK3588 has an NPU of its own; his slots take an NVMe SSD instead, and his eFuse on Mamka
  switches him.
- **HDMI for the glasses.** Glasses that take DisplayPort over USB-C carry the picture, their
  power and their head sensors on one cable, and the ROCK 5T's USB-C is wired for it; HDMI
  through a powered adapter stays the fallback.
- **Forcing an Umnica's EN pin from a process.** The pin is a plain GPIO, and a root process can
  write the controller's register through `/dev/mem` under the driver's feet. It works once, and
  leaves the regulator framework believing the rail is on, the port believing its device is
  there, and the way back, the pin high again, powers the module with PERST# already high and no
  100 ms, outside the M.2 sequence. The patched driver's `unbind` and `bind` do the same thing
  in order, so the hack is not used.
