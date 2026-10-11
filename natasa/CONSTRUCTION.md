<div align="center">

# Nataša: construction

**The headband:** where the microphones, the motors, the buttons and the board sit.

↑ [Nataša](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## On the head

The headband is laid out round the glasses, the XREAL One Pro taken as the reference (its user
manual, *Hardware introduction*): a temple runs from the hinge by the eye straight to the top of the
ear and bends down behind it, the USB-C at the end of the left one, the buttons under the right one
and the speakers under both by the ear. **The headband runs above the glasses' temples** and presses
on them nowhere, above the ear and behind it least of all. Everything on it is as small as it can be
made.

| zone | what sits there | why |
|---|---|---|
| the forehead, middle | Míša: the radar, the ultrasound, the IMU, and the forehead's motor in its housing | it looks ahead; its IMU gives the head's turn |
| the forehead and the temples, round and under Míša | the 16 electrodes (see [Rubaška](../rubaska/CONSTRUCTION.md#electrodes)) | the front half |
| the temple, outside | a camera's snap mount (see [Baťa](../bata/HARDWARE.md#ďaďa-sem)) | near the eye, on the outside, pressing on no electrode |
| right behind the ear, both sides | four buttons, a microphone, a side motor | the back half begins; the ear guides the hand to the buttons |
| the back of the head | the board, the nape's motor, Míša's ultrasonic socket for the nape | the back half, no electrodes |
| down behind the neck | the glasses' cable from the left temple, the cameras' cables, the cable to the backpack | one way out, into the turtleneck |

- **The microphones,** one behind each ear, for stereo, where hearing aids sit: the head shades
  each from the other side. Their ports are at the bottom, so the sound comes through a hole in
  the board under each one, on a small board of its own on a lead from the main board; what
  covers the holes against sweat and wind is still open.
- **The motors,** four: left and right behind the ears, the nape, and the forehead's in Míša's
  housing, off the skin and off the electrodes, so an obstacle ahead buzzes from where the
  wearer looks. Without Míša there are three. They sit as far from the microphones as the
  headband allows and are held apart mechanically.
- **A motor and the electrodes, two ways.** Electrically a motor is quieted at the source: its
  two wires a twisted pair, its supply behind its own π filter (see
  [hardware](HARDWARE.md#power)); no capacitor across the motor, since the DRV2603's outputs,
  switched at ~20 kHz, have edge-rate control and need "no output filter or ferrites"
  (SLOS754C, 8.3.8).
  Mechanically no filter helps: the motor turns at 9,000 rpm, 150 Hz (see
  [hardware](HARDWARE.md#vibration)), inside the EMG's band, and an electrode it shakes on the
  skin makes a real signal at the contact. Hence the forehead's motor off the skin, and Baťa,
  who knows when a motor runs, marks that time in the data. If a sample shows the vibration
  does the electrodes no harm, the motor may sit among them.
- **The buttons,** four behind each ear, so that a blind wearer finds them by the ear, away from
  the temples' electrodes, which a press would show in; a cable of four lines and ground to each
  side.
- **Míša** plugs into one socket on the forehead side and works with the glasses on.
- **The board** lies flat in the headband: its polymers are 1.4–1.8 mm tall, where Mamka's 50 V
  hybrid polymer stands 10.2 mm. It sits on the back half, which has no electrodes: the
  headband is one piece with the head's band of 16 on its front half (see
  [Rubaška](../rubaska/CONSTRUCTION.md#electrodes)). Without electrodes it is Nataša's alone.
- **The headphones** are any wired pair in the 3.5 mm jack.

## Open questions

- where the microphones sit on the headband, and what covers their holes against sweat and
  wind: the hole in the board at least 0.5 mm (DS-000069, *PCB design and land pattern
  layout*), and InvenSense's AN-1124 on sealing bottom-port microphones still to read,
- the motors against the microphones: as far apart as the headband allows, and held apart
  mechanically; Soňa knows when the motors run and can leave that time out,
- the forehead's motor in Míša and Míša's socket among the head's electrodes: what a running
  motor shows in their EMG, which Baťa can mark as he knows when it runs, tried on a sample,
- the glasses' temple measured, and the gap the headband leaves above the ear and behind it.
