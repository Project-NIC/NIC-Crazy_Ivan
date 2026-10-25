<div align="center">

# Rubaška: construction

**The electrodes and their leads,** the fabric, the harness and the washing, and the glove; where
everything sits on the body is under [Bogatyr](../bogatyr/README.md).

↑ [Rubaška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## Electrodes

Where each electrode sits on the body, muscle by muscle, is under
[Bogatyr](../bogatyr/CONSTRUCTION.md); here is what the electrodes and their strips are made of
and how they ride the body. Every module has its sixteen electrodes, a bias electrode and a
reference electrode, 18 a module, 288 on a suit of 16 (see
[Right-leg drive](HARDWARE.md#right-leg-drive)).

- **The head and the neck are joined like a turtleneck,** two pieces of the suit: the headband
  above, the neck's unit below, fabric between them over the back of the head and behind the ears.
  The face, the chin and the throat stay free. The fabric holds the band and the neck's unit in
  place without a strap; hair cut short, ~3 mm, helps the electrodes above the ears, to be tried.
- **The glove is tight,** elastic in the middle, its seams sitting in the spaces between the
  fingers so that it hardly moves.

**Material.** The electrodes are stainless-steel studs, kept moist.

- The grade is **316L**, the steel of body jewellery. 316Ti is not needed: its titanium protects
  the steel at high temperatures (welding), not on the skin.
- A cheap source is marine press studs in 316 (A4), made for boat covers and sold in kits with a
  hand tool for pressing them into fabric; the polished cap is the electrode. Cheap "stainless"
  studs are often 304 or plated brass, so the grade has to be 316/A4.
- Stainless steel has more low-frequency noise and drift than Ag/AgCl, which is acceptable for
  EMG. The ADS1299's input itself would cope even with dry contacts (datasheet SBAS499C):
  1000 MΩ input impedance and ±300 pA bias current, so a 1 MΩ contact shifts the input by
  0.3 mV, and the input range is ±VREF / gain, ±375 mV at our gain of 12. The input filter
  would not: with 1 MΩ contacts its corner falls to ~360 Hz, inside the band.
- **Moist, not dry.** A ring around each electrode holds the skin's moisture under it, so the
  contact sits far below the ~1 MΩ of a dry one; tens of kilohms are taken as the working
  figure, to be measured. The ring is of dissipative material, not plain plastic, which would
  charge by friction. Moisture also lets charge from friction decay faster.
- **8 mm studs where there is room, 6 mm on the forearm and the hand,** each in a ring at least
  5 mm wide. The ring keeps even a small stud moist, but its contact and its noise still grow as
  it shrinks (see [The noise](HARDWARE.md#the-noise)). On a limb's ring the P sit an eighth or a
  fifth of the girth apart and the N 4 cm above or below (see
  [Bogatyr](../bogatyr/CONSTRUCTION.md)), so the rings fit with room; the hand's pairs, 2 cm
  apart, are the tightest and find their rings' width on the body.
- 316L contains nickel; anyone allergic to nickel tries it on the skin first.

**The offset.** Two metal electrodes on the skin differ by a DC voltage that adds to the channel
and wanders. Steel polarises; Ag/AgCl hardly does, which makes it the reference electrode of the
field.

- Wet Ag/AgCl ECG electrodes: a median offset of 0.5–4 mV (*The electrical characteristics of
  some commercial ECG electrodes*, PubMed 621452).
- Dry metal electrodes in the ear: a spread of 46 mV, from −108 to +176 mV over 122 measurements
  (*Dry Electrodes for Human Bioelectrical Signal Monitoring*, Sensors 2020, PMC7374322).
- Stainless steel on the skin: no figure found.
- ECG amplifiers are commonly required to work with ±300 mV of offset (IEC 60601-2-25, read only
  second hand, not in the standard itself).
- Titanium films on steel come close to Ag/AgCl in the quality of surface EMG (Rodrigues et al.,
  Materials 2020, PMC7254203; Ti–Au films, Sensors 2021, 21, 8143); their offset was not
  measured. Titanium is covered by its oxide and so polarises like steel; that is our inference.
- The gain is 12 for this, ±375 mV (see [Software](SOFTWARE.md#the-ads1299s-settings)).
- The offset needs no instrument: the ADS1299's input is DC-coupled (SBAS499C, 10.1), so the
  mean of a raw channel is the offset, and a few minutes recorded on Baťa show its drift.

**The price** of other electrodes, as listed in October 2026, for 288 of them:

| electrode | apiece | for 288 | where listed |
|---|---|---|---|
| sintered Ag/AgCl | $7–13 from 500 pieces; $8–12 with a lead, from 100 | ~$2,000–3,700 | Greentek (Wuhan), its Alibaba store |
| sintered Ag/AgCl, 12 mm | €0.17–0.21 from 5,000 pieces | the least order ~€850–1,050 | Alibaba |
| sintered Ag/AgCl cups, single use | $19.95 for 24 | ~$240 a set | Compumedics (Neuromedical Supplies) |
| sintered Ag/AgCl DC-EEG disc | $37.95 | ~$10,900 | bio-medical.com |
| titanium press studs | not sold off the shelf; made to order | — | — |

The cheap Ag/AgCl pieces are EEG discs and cups, not press studs: how they would sit in the
fabric is not known. A sintered electrode is Ag/AgCl right through and is renewed by rubbing its
face; the makers tie its DC stability to a chloride gel, and how it fares on sweat alone was not
found.

**The band's strip.** The electrodes do not hang on wires: each band is a flexible printed
circuit that carries the studs and runs to the module, on the torso polyimide of two layers
made by JLCPCB, on the limbs copper on TPU (below).

- **A piece of a cone's mantle.** A flat flexible circuit can be bent to a cylinder or a cone,
  but not to a sphere or an irregular surface (Vanfleteren et al., *Printed circuit board
  technology inspired stretchable circuits*, MRS Bulletin 37, 2012). A limb under its band is
  near a cone, and the trunk too, so a strip that wraps round is cut as a sector of a ring, the
  cone unrolled: its angle is the difference of the girths at its two edges over its width, its
  outer radius the larger girth over that angle; it then lies on the body without wrinkling or
  pulling sideways.
- **The polyimide does not stretch.** It only wraps round the body, a static bend, which polyimide
  bears well; a band of it closes with a stretch of elastic fabric, which takes the wearer's size
  and the swell of a working muscle: after contractions an arm measured 0.4–1.0 cm more (Journal of
  Sports Science and Medicine 2008, 7, table 2). Two or three lengths of strip for each band.
- **The limbs' rings stretch:** a working biceps or calf swells more than a fixed ring takes,
  and the forearm's and the calf's cross the wrist and the ankle, so all eight limb units are
  the glove's stretchable circuit, copper on TPU, two layers for the ground (Würth's
  STRETCH.flex is made single- and double-sided), one piece each into the module's one connector,
  with a small elastic gap: over the ulna's edge on the forearm, over the tibia on the calf, on
  the outer side of the upper arm and over the iliotibial tract on the thigh, so that the inner
  side carries electrodes too; by anatomy, to be checked against the atlas. The module sits on
  the outer side, where nothing rubs it. The torso's areas, over the shoulder above all, which
  turns in three axes, take what their layout asks for, polyimide where the skin does not
  stretch, TPU where it does.
- **The pads** at their places (see [Bogatyr](../bogatyr/CONSTRUCTION.md)). The strip ends in a
  stiffened tail in the module's locking flexible-circuit connector (see
  [hardware](HARDWARE.md#sensing-module)); JLCPCB makes flexible circuits up to 234 × 490 mm in
  regular orders, with stiffeners of polyimide, FR4 or steel (JLCPCB, *Flex PCB capabilities*).
- **The second layer is ground,** the shield, hatched by our choice so that the strip stays
  supple, or JLCPCB's shielding film of 18 µm. A channel's P and N run under the same ground.
- **Less charge from friction.** In a cable the charge is made where the insulation rubs the
  shield as it bends (US patent 6,232,789); the low-noise cables put a graphite layer there
  (PCB Piezotronics, *WPL 43, Accelerometer Signals*). In a printed circuit the layers are bonded
  and do not rub, so it should make less; that is our inference, and no source gives the charge
  in figures (makers of cables state only ratios, such as ~1,000 times less than RG58, FEMTO,
  CAB-LN1), so it is measured on a sample.
- **The moist contact eases the rest.** Charge from friction is a small current, and the
  voltage it makes is that current times the contact; at tens of kilohms instead of a megohm
  it is ten to twenty times smaller, and so is the mains that unequal contacts turn into a
  difference.
- The strip is sewn into the band under the dissipative layer, so that nothing rubs it.

**The stud on the strip.** The stud is pressed through the strip at its pad and holds it by
pressure; a rivet through a flexible circuit's pads, held by its clamping force, is used in
wearables (a wearable neurostimulator, US patent application 2024/0039190).

- The pad is gold (ENIG), stiffened under the stud, so that the press does not tear the
  polyimide.
- A soft disc spring under the stud keeps the pressure as the materials move with heat.
- A non-curing, elastic sealant on the pad before the press: the press squeezes it out, the
  metals meet directly, and the sealant round them shuts out sweat and water. Gold against
  steel in sweat would make a cell; sealed, it stays dry and the strip can be washed. Which
  sealant, and how many washes it bears, the sample shows.

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
- **The harness, Kaščej (Venom), is cut from an overall.** A whole close-fitting overall, gloves
  included, is sewn, the bands' places are marked on the wearer, and the rest is cut away: the bands
  stay, joined by strips of fabric. The strips hold the bands to one another, so a band shifts and
  turns less than one on its own, the shift the pairs must bear. Nothing is left over the groin or
  the larynx. A bought compression overall serves as the pattern only, being synthetic; the harness
  is of the suit's cotton with some stretch.
- **It zips at the back,** with a long cord on the zip's pull, as on a wetsuit, so the wearer
  closes it alone.

The cable and its connectors are described under
[Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit).

## The glove

Vešč's Staršaja sits before the wrist, on the sleeve, and its five Bratiški on the hand (see
[hardware](HARDWARE.md#the-glove)); where its IMUs sit is under
[Bogatyr](../bogatyr/CONSTRUCTION.md#the-gloves).

- **The wiring is a stretchable printed circuit,** copper on TPU with meanders, laminated into
  the glove's inner layer: 5–20% of repeated stretch by its layout, turned round and round
  without harm, gentle on the skin, softening at 155–185 °C, soldered with SnBi; samples on
  request (Würth Elektronik, *STRETCH.flex*, webinar 2021; Murata makes the like). It runs along
  the sides of the fingers, never across their backs, where the skin stretches least. Each
  branch ends in a tail stiffened over ~4 mm and goes into its IMU board's five-way locking
  connector: SCL, SDA, +3.3 V, ground and CLKIN (see [the IMU board](HARDWARE.md#the-imu-board)).
  Up to ~10 cm a finger, ~6 cm to its last phalanx.
- **One spider or five noodles,** whichever proves cheaper and lasts better and is easier to
  mend: one circuit for the whole hand, a leg a finger, across the wrist into one larger
  connector at Staršaja; or five strips, one a finger, each into a small connector of its own. The
  spider is one part and one connector; a noodle is a simple shape, and a torn one is replaced
  alone.
- **A glove of two layers** with a hook-and-loop closure: the outer one comes off, the inner one
  with the circuit is pulled out and a new one goes in.
- **The fallback** is PTFE wires of 28 AWG along the sides of the fingers, as the IMU board was
  first drawn, should the stretchable circuit fail on a sample.
- **Across the wrist** go eight wires, the five Bratiški's, CLKIN, the supply and ground, and the
  glove comes off at a connector there; the arm's line ends at Staršaja on the sleeve.

## Open questions

- the band's strip on a sample: bent, tapped and rubbed while recording, its fit on the limb as a
  piece of a cone, the elastic gap over the bone, and the girths that set two or three lengths,
- the stud on the strip: the disc spring, the sealant, washed again and again; the contact
  through it and the offset, against a stud on a wire,
- the ring around the electrode: its dissipative material and shape, and the contact it gives,
  measured,
- the electrodes on a sample: 316/A4 marine press studs, titanium and sintered Ag/AgCl side by
  side on one arm: the contact, the noise, the skin, and the offset with its drift; Ag/AgCl goes
  in only if the steel drifts too far,
- the girths under each band, and the studs' and rings' sizes they allow,
- the backpack's straps over the shoulders' units: they must run beside the electrodes or be
  padded,
- a prototype of the harness, cut from an overall; how much stretch the cotton may carry,
- the glove: the stretchable circuit along the fingers, gripping and washing; the spider against
  five noodles in price, life and mending; the stiffened tails in the locking connectors; the
  hand's three channels on the thumb's edge as the thumb turns to the palm,
- the headband's electrodes above the ears, in the hair; the layout itself is under
  [Bogatyr](../bogatyr/CONSTRUCTION.md#open-questions).

## Ideas for later

- buttons on the gloves.
