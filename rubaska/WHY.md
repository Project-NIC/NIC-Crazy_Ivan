<div align="center">

# Rubaška: why not

**The graveyard: what was considered for the suit and why it is not used.**

↑ [Rubaška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Each entry says what it was and why it went, so that nobody digs it up without knowing. Where a
thing waits in reserve, it says so.

## The sensing module

- **1,920 SPS as the suit's rate** (proposed 23 Oct 2026, after the professionals' ~2 kHz, Meta's
  2,000 Hz and OT Bioelettronica's 2,048 Hz, and SENIAM's band of 10–500 Hz): half the data, and
  0.46 against 0.65 µVrms. The rate is set by what the suit must catch: fast movements in sport,
  and the twitches of a nervous system that does not work as it should, which cannot even be seen
  from outside; the cost, the data, the design bears. 1,920 SPS stays a setting to try, with the
  IMUs' step at 60 Hz.
- **The module's firmware in two versions,** one adding the foot to its frame, the other
  sending the glove's as a second unit. One image for each kind of unit, the firmware split into
  parts only in its source.
- **The glove's calls and answers in containers,** types 0x20 and 0xA0. The containers are
  gone; what the glove's wires carry is set on the first board.
- **SPI to the IMUs over a cable.** Every IMU would want its own chip select and five or six
  wires, eight or nine into a finger with the drivers. I3C puts two IMUs on five wires, SCL,
  SDA, power and CLKIN, at a rate far below its 12.5 MHz. No SPI runs over a cable anywhere.
- **The IMU clock over I3C** (synchronous timing control, SETXTIME) instead of the CLKIN wire.
  ST's documents disagree on whether the STM32H5's controller has it, and the ICM-42688-P
  documents its sample rates only from CLKIN (DS-000347, 12.5). The wire stays.
- **SPI4 for the ADS1299.** It takes frames of 4 to 16 bits only (DS14540, table 10); the
  ADS1299's 24-bit words want SPI1 to SPI3, which take up to 32.
- **PC13 to PC15 for the LED.** They hang on the backup domain's power switch, 2 MHz and 30 pF at
  most and no current to source (DS14540, table 13, note 2).
- **PB3 or PA8 for I3C2's SCL.** PB3 is the only pin with SWO, PA8 the only one with TIM1_CH1
  for CLKIN, so I3C2 takes PB5 and PB4, which have no Fm+ drive; I3C carries 12 B per IMU 1,200
  times a second with ease, and as I2C at 400 kHz the IMUs run the chip's own 120 Hz.
- **An LDO for every branch.** Earlier drafts had one; the π filters of the house rule do the job
  behind two LDOs, one for the 5 V analog side and one for the 3.3 V rest.
- **Microamp lead-off currents** (6 or 24 µA). Through a 50 kΩ contact they make 0.3 or 1.2 V,
  most of the ±375 mV input range at a gain of 12 or far beyond it. Only 6 or 24 nA are usable.
- **The bias through channel 8's multiplexer** (MUX = BIAS_DRN, IN8N the bias electrode, IN8P
  its spare). It kept the electrode connector at 16 positions, but cost the driving module two
  of its inputs and put the drive through the ADS1299. Reopened on 10 Oct 2026: the bias
  electrode has a lead of its own through 4.99 kΩ and a TMUX1101, every input measures, and the
  connector has 20 positions; what changed is under [hardware](HARDWARE.md#right-leg-drive).
- **Measuring the bias drive's voltage** with BIAS_MEAS (MUX = 010). A channel so set measures
  BIASIN against the mid-supply with its own inputs cut off, and must not be in the bias sum
  (SBAS499C, 9.3.2.4.2); TI gives it for debugging. The differential channels do not
  need a zero: a difference does not change when a constant is added to every potential.
- **A jumper for the reference electrode.** The suit is washed and its boards potted, so nobody
  will move a jumper; the SRB1 bit in MISC1 is the switch, set by the firmware.
- **The BIASINV wire between the ADS1299s** that the datasheet's figure 39 draws. A
  high-impedance node on a metre of cable would pick up the mains; one module's channels sense
  the body's common voltage well enough, since the body is one conductor.
- **The glove's board on the back of the hand,** Staršaja and four Vnučata, five STM32H523CCU6 on
  the suit clock, joined by Interconnect, one half-duplex wire on the board (10–24 Oct 2026).
  Vešč puts Staršaja on the sleeve before the wrist, an STM32H523 in LQFP64 with six U(S)ARTs,
  and a small Bratiška on each finger's wire; Interconnect, its pull-up and the four processors'
  oscillator inputs go.
- **The STM32H523CCU6 for the small processors, for its suit clock** (to 24 Oct 2026). The
  STM32H503KB in UFQFPN32, 5 × 5 mm, has no PH0-OSC_IN, and needs none: Staršaja makes the IMUs'
  CLKIN from the suit clock and sends it on one wire, so the IMUs sample in step with the suit and
  a Bratiška only reads them, on its own HSI. Its bank holds an image of 64 KB (DS14053 Rev 4).
- **The Vnučata at the module's then 196.608 MHz in VOS1.** 21–47 mA each typical and 72 mA at most
  (DS14540, table 26), more than one TPS7A2033 can give five of them at worst. A Bratiška at
  32 MHz in VOS3 does the work at ~5 mA.
- **An oscillator on the glove's boards.** The line brings the suit clock to Staršaja, as to every
  unit, and the glove runs in step with the suit.
- **The whole glove behind the forearm's module,** on its UART across the wrist, in the line's
  fifth slot that the module sent for it, until 24 Oct 2026. The glove is the arm's fourth unit
  with drivers of its own (see [Porjadok](../porjadok/WHY.md)).
- **A simple glove,** Staršaja alone behind the forearm's module with three or four IMUs, in its
  frame as an extension (to 24 Oct 2026). It was a second way of doing the hand, with a
  firmware path of its own; the whole glove is now part of every suit with arms, and a hand that
  takes no glove has the forearm's module's two IMUs beyond the wrist (see
  [Bogatyr](../bogatyr/CONSTRUCTION.md#the-imus)).
- **BGA and WLCSP packages for the small processors.** The STM32H523's WLCSP39 would take the
  clock in 2.8 × 2.8 mm (DS14540), but at a 0.4 mm pitch it wants a dearer board and, on a hand
  that bends, an underfill.

## The IMU

- **A magnetometer.** Indoors the steel of a building bends the Earth's field differently from
  place to place, so no calibration takes it out. The joints do not need it: across a joint the
  turn about the vertical is pinned by the two IMUs sharing the joint's centre. Only which way
  the whole body faces in the room stays unseen, and if that ever matters, one magnetometer on
  the trunk comes back, not one per IMU.
- **The chip's own 120 Hz as the only mode.** It was the first choice: the 100 Hz setting under
  CLKIN, filtered and decimated in the chip, nothing to compute. In noise it equals the sum of
  ten samples at 1,200 Hz, but a step of 8.3 ms taken as one rotation misses the coning term
  when a piece turns about two axes at once, a few degrees by the end of a fast swing; Movella's
  MTw integrates at 1,000 Hz on the sensor for that reason. The block now sums at 1,200 Hz, and
  the chip's 120 Hz stays a mode for the I2C fallback and for comparison.
- **Bosch BMI570.** Lower noise on paper, but we found no external clock input, and the suit
  runs every sensor from one clock.
- **ICM-45686.** The same family's newer part; it would reach 120 Hz too, but its gyro is noisier
  (3.8 against 2.8 mdps/√Hz) and its CLKIN takes 20–40 kHz. The noise decided for the
  ICM-42688-P.

## The electrodes and the suit

- **Ag/AgCl or titanium electrodes, for now.** Sintered Ag/AgCl comes to ~$2,000–3,700 for 288
  of them, and titanium press studs are not sold off the shelf (the prices in
  [Construction](CONSTRUCTION.md#electrodes)). Stainless steel has more low-frequency noise and
  drift, which EMG bears; the three are compared on a sample, and Ag/AgCl goes in only if the
  steel drifts too far.
- **A gain of 24.** It leaves ±187.5 mV, which an offset of 176 mV between metal electrodes, seen
  on dry ones, nearly fills. A gain of 12 holds ±375 mV for 0.65 against 0.56 µVrms of noise
  ([Software](SOFTWARE.md#the-ads1299s-settings)).
- **316Ti steel.** Its titanium protects the steel at welding temperatures, not on the skin;
  316L, the steel of body jewellery, does.
- **Dry electrodes.** A dry contact is ~1 MΩ, which the ADS1299's input would bear but the input
  filter would not: its corner falls to ~360 Hz, inside the band. A moist ring keeps the
  contact at tens of kilohms.
- **A low-noise cable with a graphite layer** for the leads, as for piezo sensors. The band's
  strip has no cable: its layers are bonded and do not rub, and a moist contact makes the charge
  from friction ten to twenty times less voltage.
- **The 3M 3517 flat cable and leads fanned out by hand.** A shielded cable needs its drain
  wires twisted, sleeved and pressed into the connector, and every lead joined to its stud by
  crimp or solder: hours of hand work on every suit, and a price that rises with it. Its bare
  fan-out also ran up to half the girth unshielded. The band's strip carries the studs itself.
- **Meanders in the polyimide** to stretch the band. Horseshoe meanders hold 40,000 stretches of
  30% only when moulded in an elastomer (Vanfleteren et al., MRS Bulletin 2012); a free one sewn
  in fabric has no such data, and a bend across its plane tears it. The strip does not stretch;
  an elastic gap in the fabric does.
- **A harmonica of polyimide,** folds out of the plane to take the stretch. Flexing again and
  again wants a bend radius of ~100 times the thickness, ~150 for two layers (flex makers' rule,
  after IPC-2223, not read here): 11–17 mm for 0.11 mm, a bulge on every fold.
- **The IMU boards soldered onto the glove's circuit.** One failed IMU would cost the whole
  insert; in a locking connector it is changed alone.
- **A conductive fabric.** It would short the electrodes or carry crosstalk between them. A
  static-dissipative one, gigaohms between neighbouring electrodes, drains charge without
  shorting signals.
- **Synthetics and plastic in the fabric.** They sit at the ends of the triboelectric series;
  cotton sits near its middle.
- **Silver in the fabric.** Too expensive; carbon-fibre grids are sold for antistatic workwear.
- **Taking the cables off for every wash.** It would wear them out sooner than wearing the suit
  does. The harness is rinsed with the cables on; only the units unplug.
- **Pressure insoles in the shoes** as a part of the suit. The contact points come out of the
  model from the EMG and the IMUs; a bought insole may serve once, at recording time, as the
  truth about heel and toe for the model to learn from, then goes back in the drawer.
- **Cables across the backs of the fingers.** They would bend with every grip; the cables run
  along the sides of the fingers.
- **Tinsel wire and silicone wire for the fingers.** Tinsel, copper ribbon round a textile core,
  is not sold as a thin multi-core and its IDC termination is unproven; silicone wears through
  at the sides of the fingers. PTFE of 28 AWG fits the 9175-700 IDC and does not; it stays the
  fallback to the stretchable circuit.
- **A switch on the reference electrode.** It was there in case the ADS1299's own switching
  behaved otherwise than its register table says; the SRB1 bit in MISC1 is that switch (figure
  18), and an unused SRB1 may float (10.1.1). The bias keeps its switch: how a powered-down bias
  amplifier's output behaves with an electrode on it, the datasheet does not say.
- **Polyimide on the limbs.** A working biceps or calf swells more than a fixed ring takes; the
  limbs' rings are stretchable.
- **Glued and suction electrodes.** They hold through a grip, but a glued one must be torn off
  with the suit, and suction, as the owner tried, left bruises that took a month to fade, and
  skin that conducts unlike the rest.
- **A coaxial lead per electrode,** as professional EMG has it. It is made to order and does not
  live long under constant bending; one strip per band, with the reference on it, does.
