<div align="center">

# Rubaška: construction

**The electrodes and their leads,** the fabric, the harness and the washing, and the glove; where
everything sits on the body is under [Bogatyr](../bogatyr/README.md).

↑ [Rubaška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

## Electrodes

Where each electrode sits on the body, muscle by muscle, is under
[Bogatyr](../bogatyr/CONSTRUCTION.md); here is what the electrodes and their strips are made of and
how they ride the body. A module of the body has its 32 electrodes and a bias electrode, 33; the
head's 32, a bias and a reference electrode, 34; the neck's 16, a bias and a reference, 18; 514 on a
suit of 16, 582 with the gloves' and the socks' 17 each (see [Right-leg
drive](HARDWARE.md#right-leg-drive)).

- **The head and the neck are joined like a turtleneck,** two pieces of the suit: the headband
  above, the neck's unit below, fabric between them over the back of the head and behind the ears.
  The face, the chin and the throat stay free. The fabric holds the band and the neck's unit in
  place without a strap; hair cut short, ~3 mm, helps the electrodes above the ears, to be tried.
- **The glove is tight,** elastic in the middle, its seams sitting in the spaces between the
  fingers so that it hardly moves.

**Material.** The electrodes are stainless-steel studs, kept moist.

- The grade is **316L**, the steel of body jewellery. 316Ti is not needed: its titanium protects
  the steel at high temperatures (welding), not on the skin.
- **The source is body jewellery:** flat discs of 316L in ASTM F138, the implant grade, 3 to 8 mm
  across with a 1.2 mm internal thread, and the 14g posts of the same steel that fit them, sold
  by the piece (Painful Pleasures, $0.99 a disc, $0.39 from 100, October 2026): a polished
  electrode of exactly 6 or 8 mm for about a dollar with its post, the post through the strip and
  the ring where a pressed stud would be, cut to length or a short screw, chosen when the strip is
  drawn. Marine press studs in 316 are too large for it, and cheap "stainless" snaps are 304 or
  plated brass (see [why not](WHY.md#the-electrodes-and-the-suit)).
- Stainless steel has more low-frequency noise and drift than Ag/AgCl, which is acceptable for
  EMG. The chips' inputs themselves would cope even with dry contacts (SBAS459K, Electrical
  Characteristics): 1,000 MΩ of input impedance, 500 MΩ with the lead-off current on, and a bias
  current of ±1 nA from 0 to 70 °C, so a 1 MΩ contact shifts the input by 1 mV, and the input
  range is ±VREF / gain, ±333 mV at our gain of 12 on the 4 V reference. The input filter would
  not: with 1 MΩ contacts its corner falls to ~360 Hz, inside the band.
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
- **Conductive silicone is the third candidate,** carbon-filled, ~5 Ω·cm: nothing in it
  corrodes and it is washed with the suit; its few ohms are nothing against the skin's tens of
  kilohms. Carbon rubber on the skin has a higher contact impedance than Ag/AgCl at the same EMG
  amplitude (a study of carbon electrodes on 20 subjects, 2016), the EMS suits that wear it wet
  it, and its resistance drifts with temperature, time and stretch. The form is a moulded plug of
  a push-in silicone foot's shape, PINGOOD's GMC-3RF-SFB as the pattern: a domed face Ø 12 × 3 mm
  on a stem Ø 8 × 2 mm with a 1.1 mm shoulder, 55 Shore A, pushed through the fabric into a
  stainless eyelet on the strip, the dissipative ring round it holding the moisture; a moulder
  runs such a tool in the conductive compound, so no tool is paid for. Tried on the first arm
  beside the steel.

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
- The gain is 12 for this, ±333 mV on the ADS1298 (see
  [Software](SOFTWARE.md#the-ads129xs-settings)).
- The offset needs no instrument: the chips' inputs are DC-coupled, an AC coupling being the
  datasheet's other way, not ours (SBAS459K, 10.1.2), so the mean of a raw channel is the
  offset, and a few minutes recorded on Baťa show its drift.

**The price** of the electrodes, as listed in October 2026, for 582 of them:

| electrode | apiece | for 582 | where listed |
|---|---|---|---|
| 316L discs, ASTM F138, 6 and 8 mm, with their posts | $0.99 a disc, $0.39 from 100; a post about the same | ~$600 | Painful Pleasures (US) |
| titanium discs, ASTM F136, mostly 2–5 mm | $10–14 at retail; $1–2 at Alibaba from 10 pieces | for samples | Pierced Owl, Urban Body Jewelry; Right Grand |
| sintered Ag/AgCl pellets and discs | $7–15 from 500 pieces; $8–12 with a lead, from 100 | ~$4,000–9,000 | Greentek (Wuhan), its Alibaba store |
| sintered Ag/AgCl, 12 mm | €0.17–0.21 from 5,000 pieces | the least order ~€850–1,050 | Alibaba |
| sintered Ag/AgCl discs of 6–8 mm, and a snap with a 4 or 8 mm cavity, by the piece | €23–30, the snap €33.20; from $10.93; $18 | for samples | Medcat (NL); Neurospec; BioMed Electrodes |
| sintered Ag/AgCl cups, single use | $19.95 for 24 | ~$480 a set | Compumedics (Neuromedical Supplies) |
| plated AgCl snap studs for ECG, 3.9 mm | $0.04–0.09 | ~$50 | Alibaba, Honsung: disposable grade, the plating wears |
| conductive silicone, carbon-filled, ~5 Ω·cm | a sheet 500 × 500 × 1 mm $1.2–40; a moulded part $0.30–0.60 from 1,000 | ~$400 moulded | Alibaba; Milesun, Better Silicone (Xiamen); Wave Company's ElecSil (Korea) |
| dry comb electrodes coated with Ag/AgCl, for the hair | $5–8 from 5–10 pieces; €125 for 10 | for the head's trials | Alibaba; Neurospec |

The titanium discs take the same post as the steel ones. The sintered Ag/AgCl pieces are EEG
discs, pellets and a snap, not studs: how they would sit in the strip is not known. A sintered
electrode is Ag/AgCl right through and is renewed by rubbing its face; the makers tie its DC
stability to a chloride gel, and how it fares on sweat alone was not found.

**The band's strip.** The electrodes do not hang on wires: each band is a flexible printed
circuit that carries the studs and runs to the module, polyimide made by JLCPCB, four layers,
on the torso and on the limbs alike.

- **A piece of a cone's mantle.** A flat flexible circuit can be bent to a cylinder or a cone,
  but not to a sphere or an irregular surface (Vanfleteren et al., *Printed circuit board
  technology inspired stretchable circuits*, MRS Bulletin 37, 2012). A limb under its band is
  near a cone, and the trunk too, so a strip that wraps round is cut as a sector of a ring, the
  cone unrolled: its angle is the difference of the girths at its two edges over its width, its
  outer radius the larger girth over that angle; it then lies on the body without wrinkling or
  pulling sideways.
- **The polyimide does not stretch; an elastic gap in the fabric does.** The strip only wraps
  round the body, a static bend, which polyimide bears well. A band of it is **two or three short
  strips** a module, ~20 cm at most (the owner), meeting at a gap of elastic fabric that takes
  the wearer's size and the swell of a working muscle: after contractions an arm measured
  0.4–1.0 cm more (Journal of Sports Science and Medicine 2008, 7, table 2), and the arm flexed
  against relaxed 33.4 → 35.3 cm in men and 29.3 → 29.8 cm in women (Frontiers in Nutrition
  2025, DOI 10.3389/fnut.2025.1534453, 139 players; flexed at the biceps' peak, so an upper
  figure). On the limbs the gap lies over the ulna's edge on the forearm, over the tibia on the
  calf, on the outer side of the upper arm and over the iliotibial tract on the thigh, so that
  the inner side carries electrodes too; by anatomy, to be checked against the atlas. Where a
  gap wants another place, the module moves, settled when the band is drawn. The module sits on
  the outer side, where nothing rubs it. The torso's areas, over the shoulder above all, which
  turns in three axes, take what their layout asks for.
- **The pads** at their places (see [Bogatyr](../bogatyr/CONSTRUCTION.md)). The strip ends in a
  stiffened tail, in the module's lever connector of 36 ways on the first arm and soldered to the
  board in a series (see [hardware](HARDWARE.md#sensing-module)); JLCPCB makes flexible circuits
  up to 234 × 490 mm in regular orders, with stiffeners of polyimide, FR4 or steel (JLCPCB, *Flex
  PCB capabilities*).
- **Ground on both faces:** JLCPCB's four-layer flex, 0.2 mm at the thinnest, ground on both
  outer layers and the leads between them, vias along both edges every few centimetres that make
  the two grounds one node, no fence of them, the leads a few tenths of a millimetre in from the
  edge (our estimate), a clearance round every stud. It is about six times stiffer than a
  two-layer flex of 0.11 mm, the thickness cubed, still inside JLCPCB's ten times the thickness
  for a wrap, 2 mm; worse for any fold. A hatch would shield little, its openings far wider than
  the trace's distance from it (our inference, to be measured). The cheaper alternative is two
  layers and JLCPCB's 18 µm shielding film on the skin's side, joined to ground through
  openings; copper inside polyimide is taken to bear washing better (our judgment). The layers
  are driven at the body's common mode by default, or put on the module's ground, and every stud
  has a follower's place beside it under a 0 Ω part, with a +5 V trace by the edge, fitted only
  if the strip's own noise asks (see [hardware](HARDWARE.md#the-strips-ground-layer)). A
  channel's P and N run side by side from where they meet, on thin leads, 3 mil.
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

The electrodes, the leads, the units and the line cables ride on a simple strap harness worn
under the clothes. The harness is rinsed in clean water with everything on it; the clothes go
into the washing machine. Taking the cables and the units off and putting them back for every
wash would wear them out sooner than wearing the suit does.

- **The units stay on.** Each sits in a 3D-printed shell with a red star, potted whole in Dow
  SYLGARD 527, a silicone dielectric gel, its connectors mated, so a connector opens only at
  assembly and repair. For a repair the gel comes out, Dow's OS fluids helping, and the place is
  cleaned, dried and patched with more gel (Dow, SYLGARD 527). The gel is soft, so the shell
  holds it (our inference); Dow gives it no IP rating.
- **Contact spray** goes only where there is no gel, on the Weipu connectors in their shells and
  Mamka's IDC: sulfur, amines, tin compounds and oils can stop a platinum-cured silicone from
  curing (general knowledge; Dow's list not read).
- The cable bundles lie in the straps along the main axes of bending. That has to be drawn,
  tried and sewn as a prototype.
- **The harness, Kaščej (Venom), is cut from an overall.** A whole close-fitting overall, gloves
  included, is sewn, the bands' places are marked on the wearer, and the rest is cut away: the bands
  stay, joined by strips of fabric. The strips hold the bands to one another, so a band shifts and
  turns less than one on its own, the shift the pairs must bear. Nothing is left over the groin or
  the larynx. A bought compression overall serves as the pattern only, being synthetic; the harness
  is of the suit's cotton with some stretch.
- **It zips at the back,** with a long cord on the zip's pull, as on a wetsuit, so the wearer
  closes it alone.
- **Over it goes Strejda Al** (after South Park's Big Gay Al and his tight outfits), a tight
  compression overall, one of the clothes: it presses the bands to the body, keeps the
  electrodes' pressure and moisture, and goes into the washing machine with the rest.

The cable and its connectors are described under
[Porjadok](../porjadok/HARDWARE.md#cable-and-connectors-in-the-suit).

## The glove

Vešč's board sits on the back of the hand, over the bases of the second and third metacarpals,
in a low enclosure of its own (see [hardware](HARDWARE.md#the-glove)); its 16 electrodes and
its IMUs are laid out under [Bogatyr](../bogatyr/CONSTRUCTION.md#the-gloves).

- **The hand's strip** carries the sixteen electrodes and the bias in its studs, as a band's
  strip does (see [electrodes](#electrodes)), polyimide like the bands', round the hand's edges
  and over its back under the board, its tail in the board's 20-way lever connector on the first
  glove and soldered in a series.
- **The finger strips are bare polyimide flex** from JLCPCB, cut as a meander, one a finger and
  one for the thumb, five, in the glove's inner layer. Each has seven leads, SCL1, SDA1, SCL2,
  SDA2, REF, +3.3 V and ground, its Bratiška's two I3C buses with two IMUs on each, and runs
  along the side of the finger, never across its back, where the skin stretches least; up to
  ~10 cm a finger, ~6 cm to its last phalanx. The IMU boards are small rigid islands soldered to
  it through plated holes, as LED strips are joined, the joint widened, stiffened and potted
  (see [the IMU board](HARDWARE.md#the-imu-board)); a repair is heat, lift, a new piece. The
  strip's tail goes into a seven-way lever connector on the board on the first glove and is
  soldered in a series. A torn strip is replaced alone. Its shape and its life are left to a
  bending test.
- **A glove of two layers** with a hook-and-loop closure: the outer one comes off, and the inner
  one with the strips can be changed, its strips unplugged from the board on the first glove and
  unsoldered in a series.
- **The fallback** is the IMU boards on Kyocera AVX IDCs with PTFE wires of 28 AWG along the
  sides of the fingers (see [the IMU board](HARDWARE.md#the-imu-board)), should the meander
  fail its bending test.
- **Across the wrist** goes the arm's line alone, its flat cable sewn in meanders over the wrist's
  back to the board's Picoflex header; the glove comes off the cable and its strips only for a
  repair, as a module does. The glove is cut with the sleeve, one piece of the harness (see
  [Harness and washing](#harness-and-washing)).

## The sock

Nosok, the glove's unit on the foot (see [hardware](HARDWARE.md#the-sock)), is made as the glove
is: a sock of two layers with a hook-and-loop closure at the ankle, the inner one carrying the
foot's strip of sixteen electrodes and one or two IMU strips, the outer one over it; the strips
run along the foot's sides and over the instep, never under the sole, which is stood on. The board
sits on the calf above the ankle in its enclosure, where the calf's module's strip crosses too,
and the foot's strips come up to it across the ankle, in meanders, as the line's cable crosses the
wrist. Where its electrodes and its IMUs sit is under
[Bogatyr](../bogatyr/CONSTRUCTION.md#the-socks); it is drawn after the hand's layout is settled,
since each version is a circuit made and thrown away.

## Open questions

- the band's strip on a sample: bent, tapped and rubbed while recording, on a dummy body of
  resistors first, its fit on the limb as a piece of a cone, the elastic gap over the bone, and
  the girths that set two or three short strips; the swell of a working muscle on the first arm,
  and meanders moulded in silicone only if it wants them,
- the strip's ground layers: the four-layer strip against two layers with the shielding film,
  driven and on ground, its stiffness on the limb, and what the strip generates by itself (see
  [hardware](HARDWARE.md#the-strips-ground-layer)),
- the units potted in the gel: rinsed with the harness again and again, and a potted module in
  the washing test beside the materials; a repair, the gel dug out and patched,
- the sock: its strips on the foot, gripping the floor and washing; the foot's strip across the
  ankle,
- the stud on the strip: the disc spring, the sealant, washed again and again; the contact
  through it and the offset, against a stud on a wire,
- the ring around the electrode: its dissipative material and shape, and the contact it gives,
  measured,
- the electrodes on a sample: 316L discs, titanium discs, sintered Ag/AgCl and conductive
  silicone side by side on one arm: the contact, the noise, the skin, and the offset with its
  drift, and the washing, at 60 °C in a bag with the laundry, fifty times; Ag/AgCl goes in only
  if the steel drifts too far,
- the girths under each band, and the studs' and rings' sizes they allow,
- the backpack's straps over the shoulders' units: they must run beside the electrodes or be
  padded,
- a prototype of the harness, cut from an overall; how much stretch the cotton may carry,
- the glove: the finger strips' meanders in a bending test, their shape and life, gripping and
  washing; the risk the soldered islands carry, one IMU lost costing a piece of strip; the
  joints widened, stiffened and potted; the tails in the lever connectors on the first glove;
  the board on the back of the hand in a grip and a fall; the hand's electrodes under the board
  and at the thumb's edge as the thumb turns to the palm,
- the headband's electrodes above the ears, in the hair; the layout itself is under
  [Bogatyr](../bogatyr/CONSTRUCTION.md#open-questions).

## Ideas for later

- buttons on the gloves.
