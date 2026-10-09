<div align="center">

# Rubaška: construction

**The electrodes and their leads,** the fabric, the harness and the washing, where the IMUs sit,
and the glove and the foot on the body.

↑ [Rubaška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## Electrodes

The electrodes are not tied to one common point. Within each block, the electrodes of
different channels cross one another, so every channel measures a mix of signals. The
[project README](../README.md#tomography) explains why.

Two electrodes of the whole suit go to the right leg (see
[Right-leg drive](HARDWARE.md#right-leg-drive)).
That is why there are two fewer measuring electrodes than inputs.

**The heart and the breath.** The heart's ECG shows in the EMG, strongest on the torso and
weaker on the limbs. Cleaning the EMG means estimating the ECG and subtracting it, and the ECG
so removed gives the heart rate and its rhythm for free. Breathing shows the same way, in the
diaphragm and the lower abdominal muscles. What has to be compensated anyway, because it
disturbs the signals we want, is kept once it is separated.

**Material.** The electrodes are stainless-steel studs, kept moist.

- The grade is **316L**, the steel of body jewellery. 316Ti is not needed: its titanium protects
  the steel at high temperatures (welding), not on the skin.
- A cheap source is marine press studs in 316 (A4), made for boat covers and sold in kits with a
  hand tool for pressing them into fabric; the polished cap is the electrode. Cheap "stainless"
  studs are often 304 or plated brass, so the grade has to be 316/A4.
- Medical silver (Ag/AgCl) or titanium electrodes are out on price.
- Stainless steel has more low-frequency noise and drift than Ag/AgCl, which is acceptable for
  EMG. The ADS1299's input itself would cope even with dry contacts (datasheet SBAS499C):
  1000 MΩ input impedance and ±300 pA bias current, so a 1 MΩ contact shifts the input by
  0.3 mV, and the input range is ±VREF / gain, ±187.5 mV even at a gain of 24. The input filter
  would not: with 1 MΩ contacts its corner falls to ~360 Hz, inside the band.
- **Moist, not dry.** A ring around each electrode holds the skin's moisture under it, so the
  contact sits far below the ~1 MΩ of a dry one; tens of kilohms are taken as the working
  figure, to be measured. The ring is of dissipative material, not plain plastic, which would
  charge by friction. Moisture also lets charge from friction decay faster.
- 316L contains nickel; anyone allergic to nickel tries it on the skin first.

**Leads and the triboelectric effect.** Leads and fabric that move against each other build up
charge, which shows as artifacts in the signal.

- The leads are short: the module sits in the piece, close to its electrodes.
- Where the positive and negative lead of a channel can run together, they are twisted and sewn
  down. Charge from movement then lands on both alike and the ADS1299 rejects it as common mode
  (CMRR −110 dB).
- Leads are fixed so they do not rub.
- **The moist contact eases the rest.** Charge from friction is a small current, and the
  voltage it makes is that current times the contact; at tens of kilohms instead of a
  megohm it is some twenty times smaller, and so is the mains that unequal contacts turn into a
  difference. An ordinary shielded cable therefore does; a low-noise cable with a graphite
  layer, as for piezo sensors, stays in reserve.

**The lead: 3M 3517,** a shielded and jacketed flat cable (3M TS-0069), one per module for its
eight channels:

- 16 conductors at 1.27 mm (3517/16, 23.6 mm wide, 2.8 mm thick); 28 AWG of 7 × 0.127 mm
  tinned stranded copper; PVC insulation and jacket; a shield of expanded copper all round,
  20 dB on average; as an option two drain wires, which join the shield to the module's ground.
- Insulation over 10¹⁰ Ω per 3 m; 70.5 pF/m unbalanced (ground-signal-ground, the shield on
  ground) and 41.7 pF/m within a pair (TS-0069). A 30 cm lead adds ~13–21 pF across the pair,
  by which of the two figures applies, to the input filter's 220 pF, which moves its corner down
  by 5–10%.
- The inner cable can be zipped apart, so its end fans out to the crossed electrodes; that last
  stretch is unshielded and kept short.
- It fits an ordinary IDC socket with two rows at 2.54 mm: 2 × 8 positions, ~25–28 mm long.

**Fabric.** The base is cotton, no synthetics or plastic; cotton sits near the middle of the
triboelectric series, synthetics at its ends.

- A conductive suit would short the electrodes or carry crosstalk between them. A
  **static-dissipative** fabric is used instead. ANSI/ESD S541 calls a material conductive
  below 10⁴ Ω, dissipative from 10⁴ to below 10¹¹ Ω and insulative above. A dissipative layer
  drains the charge slowly without shorting the signals.
- **From the top of that range,** gigaohms between neighbouring electrodes. It may then lie on
  the skin and touch the electrodes: against even a dry 1 MΩ contact, 1 GΩ makes ~0.1% of
  crosstalk, and against a moist one far less.
- **No wire:** the charge from friction drains through the fabric into the skin, and the body
  is held by the right-leg drive; currents of nanoamperes do not trouble it.
- Carbon, not silver: silver is too expensive, and fabric with a grid of carbon fibres is sold
  for antistatic workwear.

## Harness and washing

The electrodes, the leads and the line cables ride on a simple strap harness worn under the
clothes. The harness is rinsed in clean water; the clothes go into the washing machine. Taking
the cables off and putting them back for every wash would wear them out sooner than wearing the
suit does.

- The units unplug before rinsing. Rinsing washes the sweat salt off the IDC contacts; they then
  dry thoroughly.
- The cable bundles lie in the straps along the main axes of bending. That has to be drawn,
  tried and sewn as a prototype.
- The units sit in 3D-printed enclosures, each with a red star.

The cable and its connectors are described under
[Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit).

## IMU placement

Up to 64 IMUs go on the suit, one on every body segment and more where a segment twists: two on
each long bone, one near each end, and up to three on the palm. The foot and the glove are below.

- Each IMU measures the orientation of its own segment. Sensor fusion keeps it as a quaternion,
  which has no singularity, and a joint's rotation is the difference between two neighbouring
  IMUs, again a quaternion. A singularity can only appear when a result is turned into three
  angles at the output; see [Porjadok](../porjadok/SOFTWARE.md#output).
- **No magnetometer.** Indoors the steel in a building bends the Earth's field, differently from
  place to place, so no calibration takes it out. Gravity shows an IMU's tilt but not its turn about
  the vertical, and the gyro alone drifts in that. Across a joint the turn is pinned anyway: both
  bones share the joint's centre, and an IMU off the joint's axis runs round a circle, so the
  centre's acceleration worked out from the IMU on either side must agree. Every movement corrects
  the drift. Standing still, a gyro reads nothing but its own offset, which is measured and taken
  off; silent EMG confirms the stillness, since a slow movement that the accelerometers barely see
  still shows in the muscles. With an IMU near each end of every long bone, every joint has one
  close by on each side. Seel, Schauer and Raisch find a joint's axis and centre from such
  constraints (IEEE CCA 2012); Weygers et al. remove the drift using only what the IMUs on two
  connected segments measure in common, and put knee angles 2–4° RMS over 7 minutes of walking (IEEE
  Sensors Journal, 2020; both from the abstracts). What stays unseen is which way the whole body
  faces in the room, and joint angles do not need it.
- Twist shows as a gradient along the segment. Turning the palm over is the radius rolling
  round the ulna: the forearm IMU by the wrist turns through almost the whole range, the one by
  the elbow a little, the one on the shoulder hardly at all.
- Skin slides over bone, so an IMU on the skin does not turn exactly with the bone. It is worst
  for the upper arm turning round its own axis, where the muscle moves under the sensor.
  Several IMUs per bone and the EMG of the muscles doing the turning give the model enough to
  tell the two apart.
- The suit never sits the same way twice, for the IMUs as for the electrodes. A calibration
  pose at the start, a few seconds standing with the arms down or out to the sides, gives the
  model its starting point. IMU motion-capture suits do the same.

## The glove and the foot

- **The glove** carries four IMUs a finger, twenty a hand, on one Vnučka per finger (see
  [hardware](HARDWARE.md#the-glove-and-the-foot)): the distal and the middle phalanx on the outer
  side, the proximal phalanx and the metacarpal on the back of the hand on the inner.
- **The cables** run along the sides of the fingers, never across their backs, five wires each:
  SCL, SDA, +3.3 V, ground and CLKIN. Across the wrist go Interconnect, CLKIN, +3.7 V and ground.
- **The foot** has three or four IMUs below the calf's module: the heel, the instep and the toes,
  and a fourth where it is wanted, on one Vnučka on the instep.

## Open questions

- the leads: the 3M 3517 bent, tapped and rubbed on a sample, against a low-noise cable,
- the ring around the electrode: its dissipative material and shape, and the contact it gives,
  measured,
- a test of 316/A4 marine press studs as electrodes: contact, noise, skin,
- a prototype of the strap harness,
- the glove's and the foot's cables on the body: the tinsel wire and its connectors, tried.

## Ideas for later

- buttons on the gloves.
