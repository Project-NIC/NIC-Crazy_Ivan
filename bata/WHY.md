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
- **The AI HAT+ 2 on the Raspberry Pi.** The same chip; the M.2 module sits on Kormilica's wing
  instead, with its own 3.3 V, so the stack over the Raspberry Pi stays Kormilica and Mamka.
- **A third computer for the cameras.** Ďaďa Sem was first a computer of his own on Ethernet;
  Baťa's second Umnica looks at the pictures instead, and only on a Raspberry Pi, which has one
  Umnica, the cameras go into Deduška.
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
- **A stereo camera.** Two cheap cameras are not in step, up to one frame apart, which does not
  matter for naming things; should depth from two pictures be wanted, a stereo camera with both
  pictures in one frame on one USB 3 port is the way.

## The software

- **Raw EMG straight into the model,** Baťa only moving data. 2.46 MB/s of samples into a
  network cost what it does not need; the model takes 128 log-RMS envelopes and 64 IMU steps
  every 1/120 s instead, which one core computes in the gaps (see [signals](SIGNALS.md)).
- **A fixed 50 Hz notch** on the EMG. It takes EMG with it; the mains, if any is left behind
  the right-leg drive and −110 dB of CMRR, is tracked as a sinusoid and subtracted.
- **A driver of our own** to save the one copy from spidev's buffer into the Hailo's. 768 B per
  cycle cost next to nothing; the copy stays.
- **Training on the Hailo.** HailoRT has no functions for training; the Hailo only runs models.
- **An SSD on Baťa's PCIe.** PCIe goes to the Hailos on both computers; recordings go to
  Deduška's disk, or to an SSD on USB 3, or only the features are kept.
- **HDMI for the glasses.** Glasses that take DisplayPort over USB-C carry the picture, their
  power and their head sensors on one cable; HDMI stays the fallback while mainline has not
  switched the ROCK 5T's USB-C DisplayPort on.
- **Forcing an Umnica's EN pin from a process.** The pin is a plain GPIO, and a root process can
  write the controller's register through `/dev/mem` under the driver's feet. It works once, and
  leaves the regulator framework believing the rail is on, the port believing its device is
  there, and the way back, the pin high again, powers the module with PERST# already high and no
  100 ms, outside the M.2 sequence. The patched driver's `unbind` and `bind` do the same thing
  in order, so the hack is not used.
