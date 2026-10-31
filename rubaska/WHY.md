<div align="center">

# Rubaška: why not

**The graveyard: what was considered for the suit and why it is not used.**

↑ [Rubaška](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Each entry says what it was and why it went, so that nobody digs it up without knowing. Where a
thing waits in reserve, it says so.

## The sensing module

- **3,840 SPS as the suit's rate** (to 29 Oct 2026), a band to ~1 kHz for fast movements in
  sport and the twitches of a nervous system that does not work as it should. With two chips a
  module it doubled the data, the lines at 46 % and processor 1's SPI at 84 %, for a band above
  the ~500 Hz surface EMG uses: SENIAM's 10–500 Hz, Delsys' Trigno at 1,926 SPS, Meta's band at
  2,000, OT Bioelettronica's at 2,048. 1,920 is the rate, its sinc filter's −3 dB at ~503 Hz and
  0.8 against 1.1 µVrms on the ADS1298; 3,840 stays a setting to try, a twitch of a few
  milliseconds seen at either, and the IMUs' step is 120 Hz at both, sixteen or thirty-two samples.
- **One ADS1299 a module** (to 29 Oct 2026): 8 channels on 16 electrodes, 128 in a suit of 16.
  Two ADS1298 in cascade give 16 channels a module at 0.8 against 0.46 µVrms, under the contacts'
  ~1 µVrms and the skin's 1–20, and cheaper, $40 against $62 a module at JLCPCB (29 Oct 2026);
  the head and the neck kept the ADS1299 two days more (below).
- **The ADS1299 on the head and the neck** (29 to 31 Oct 2026), for its SRB1, the switch to
  measure against the reference by MISC1, and its noise. That noise does not count against the
  contacts: 0.46 against the ADS1298's 0.8 µVrms at 2 kSPS and a gain of 12 (SBAS499C and
  SBAS459K, table 3), both under the contacts' ~1 µVrms, and it cost two chips, two boards and
  two firmwares, $59 against $20 a chip at JLCPCB. Every module carries the ADS1298; a strip that
  measures against a reference joins the N inputs to its electrode itself (see
  [hardware](HARDWARE.md#right-leg-drive)).
- **One ADS1299 on the head** (to 29 Oct 2026), 16 electrodes. The owner: 32 fit on the head; the
  module takes a second chip in the second chip's place, and line 5 keeps three slots free should
  the head ever split into two units, one a side.
- **Against the reference on the body** (to 29 Oct 2026), a reference electrode and SRB1 on
  every module. The ADS1298 has no SRB1, so the body measures differentially, the owner's layout
  from the start, and the reference stays on the head's and the neck's strips, wired; which way
  serves the model better is tried there.
- **A daisy chain of the two chips** (29 Oct 2026), DOUT into DAISY_IN, one read of 432 bits.
  The devices "cannot be programmed when sharing a common DIN" (SBAS499C, 10.1.4.2), and the two
  differ in their settings, the first's bias amplifier on and the second's off; the cascade
  shares DIN, DOUT and SCLK with a chip select each (10.1.4.1).
- **A hatched ground layer on the strip** (to 29 Oct 2026), hatched so that the strip stays
  supple. A mesh stops fields from sources far beyond its pitch, and the trace lies at a tenth of
  it (our inference); 12 µm of copper on the 25 µm core stays supple solid, so the layers are
  solid (see [hardware](HARDWARE.md#the-strips-ground-layer)).
- **One ground layer, on the strip's outer face,** the leads toward the skin, and on the module's
  ground by default (to 31 Oct 2026). The skin's side was left open to what friction and static
  make there. The strip is a four-layer flex with ground on both outer faces, driven at the
  common mode by default, so that what lands outside goes through the driver alike on P and N;
  the leads' capacitance to the shield about doubles, ~43 → ~86 pF on 20 cm, and thin leads and
  the pairs side by side win it back (see [hardware](HARDWARE.md#the-strips-ground-layer)).
- **A test board for the analog path** (29 Oct 2026), the strip's three levels tried on a board
  of its own first. A board made once, paid with the import's surcharge and its spare chips, and
  good for nothing after, is what the rules forbid (the owner); the module is drawn once so that
  all three levels are tried on it, and the first arm is the test.
- **TVS diodes on the inputs** (29 Oct 2026). The suit floats, so a wearer's discharge into a
  handle leaves ~0.5 mA for 50 ns in an input, which the 4.99 kΩ and the chips' own diodes take
  (computed on a simple model, see [hardware](HARDWARE.md#sensing-module)); a TVS would add
  capacitance and leakage to every input for a case that does not come.
- **Followers at every stud from the start,** BioSemi's active electrode (29 Oct 2026). They
  cost 32 op-amps a module, a potted strip and the chips' impedance check, for a current the
  bonded strip may not generate; their places wait under 0 Ω parts, fitted only if the dummy
  body shows the strip generating (see [hardware](HARDWARE.md#the-strips-ground-layer)).
- **The foot's and the hand's IMUs on their module's bus** (to 29 Oct 2026), two beyond the
  joint on the strip. The owner: losing the hand's and the foot's detail makes no sense; the
  sock, Nosok, a unit of the glove's kind in the limb's fourth slot, carries up to eight, the
  glove 20, and the modules keep four IMUs each (see [Porjadok](../porjadok/WHY.md)).
- **The glove as a unit of IMUs alone,** Staršaja on the sleeve with five Bratiški on the fingers
  (to 29 Oct 2026): 22 IMUs and no EMG, the hand's three channels going across the wrist to the
  forearm's module. The forearm's module got its sixteen channels for the forearm, and the hand
  its own eight on one board on the back of the hand with its IMUs, an ADS1298, Staršaja and
  four Bratiški, the frame 0x25 carrying both (see [hardware](HARDWARE.md#the-glove)).
- **Bratiški on the fingers, one wire each across the wrist** (to 29 Oct 2026): a processor on
  every finger, eight wires over the wrist, each an open-drain half-duplex wire at 4 MBd with a
  470 Ω pull-up, the step in halves of 4.17 ms and the finger in every step. On the board the
  four sit beside Staršaja, full duplex on traces, and the fingers carry passive strips of seven
  wires; nothing crosses the wrist but the line's cable.
- **Five Bratiški and 22 IMUs** (to 29 Oct 2026), one a finger with its metacarpal, and two of
  Staršaja's own. The thumb's three and the board's own sit on Staršaja's two buses, so four
  Bratiški read the four fingers, 20 places in all, the fourth place on each finger spare for the
  palm's arch and a second on the thumb's metacarpal.
- **SWD on the Bratiški** (to 29 Oct 2026): pads for four programmers on a board on the hand. An
  empty STM32H503 boots ST's bootloader, which listens on USART2 on the very pins to Staršaja; she
  programs them through it and recovers one by the shared BOOT0 line, and the pads stay for her
  alone.
- **A bank swap and a zero stage on a Bratiška** (29 Oct 2026): his image in frames through
  Staršaja into his second bank, with a trial and a swap back. With the bootloader there is
  nothing in him to update but the one image Staršaja writes; his 128 KB are one image.
- **Staršaja counting her cycles from *start* on a timer** (to 29 Oct 2026): with no ADS129x she
  had no DRDY. With one she keeps the cycle from DRDY as a module does.
- **The connector at the wrist** (to 29 Oct 2026), eight wires plugged into Staršaja on the
  sleeve. The line's cable runs on to the board on the hand, sewn in meanders over the wrist, and
  the board takes it on its Picoflex header as any unit.
- **One spider for the whole hand** against five strips (to 29 Oct 2026): with the board on the
  hand each finger's strip is a piece of its own, joined to the board alone, and a torn one is
  replaced alone.
- **LQFP64 for the glove's Staršaja** (to 29 Oct 2026), for six U(S)ARTs. The module's STM32H523CCU6
  in UFQFPN48 does it with the echo received on the LPUART and the master on USART1's RX, which
  frees UART4, and the ADS1298's CLK and START made by TIM2, which frees USART3's PB1: four Bratiški
  on USART2, USART3, UART4 and UART5, the echo kept, 33 of its 35 I/Os, so one processor serves the
  module and the glove (the owner's wish; see [hardware](HARDWARE.md#the-glove)).
- **The glove's line on one USART, no echo compared** (29 Oct 2026, for an hour), the fourth
  Bratiška on the LPUART instead. The owner: the line needs its two receivers. The echo went to
  the LPUART, which receives 19.66 MBd with room to spare, and nothing of a module's line was
  given up.
- **The module's firmware in two versions,** one adding the foot to its frame, the other
  sending the glove's as a second unit. One image for each kind of unit, the firmware split into
  parts only in its source.
- **The glove's calls and answers in containers,** types 0x20 and 0xA0. The containers are
  gone; what the glove's wires carry is set on the first board.
- **SPI to the IMUs over a cable.** Every IMU would want its own chip select and five or six
  wires, eight or nine into a finger with the drivers. I3C puts two IMUs on five wires, SCL,
  SDA, power and REF, at a rate far below its 12.5 MHz. No SPI runs over a cable anywhere.
- **The IMU clock over I3C** (synchronous timing control, SETXTIME) instead of a wire of its
  own. ST's documents disagree on whether the STM32H5's controller has it; the LSM6DSV16X lists
  SETXTIME (DS13510, table 17) but documents its rate held to an outside clock only from INT2
  (AN5763, 3.3). The wire stays, REF on it.
- **SPI4 for the ADS1298.** It takes frames of 4 to 16 bits only (DS14540, table 10); the
  chip's 24-bit words want SPI1 to SPI3, which take up to 32.
- **PC13 to PC15 for the LED.** They hang on the backup domain's power switch, 2 MHz and 30 pF at
  most and no current to source (DS14540, table 13, note 2).
- **PB3 or PA8 for I3C2's SCL.** PB3 is the only pin with SWO, PA8 the only one with TIM1_CH1
  for the IMUs' clock, so I3C2 takes PB5 and PB4, which have no Fm+ drive; I3C carries 12 B per
  IMU 1,920 times a second with ease, and as I2C at 400 kHz the IMUs run the chip's own 120 Hz.
- **An LDO for every branch.** Earlier drafts had one; the π filters of the house rule do the job
  behind two LDOs, one for the 5 V analog side and one for the 3.3 V rest.
- **The TPS7A47 for the analog side** (to 31 Oct 2026). Its ~4 µVrms bought nothing the chips
  can use, at $7.48 against the LP2985's $0.18 (JLCPCB); TI's own front-end boards feed these
  chips from ordinary low-noise LDOs (ADS1298ECG-FE, SBAU171D). It waits in reserve: should the
  first module's inputs, shorted inside the chip (MUX 001), read worse than SBAS459K's table 3,
  it comes back.
- **POSCAPs at the inputs,** Panasonic's 6TPE100M on 4 V and 10TPE47MAZB on 6 V (to 31 Oct 2026).
  A 22 µF ceramic behind 0.5 Ω damps the cable as well, its impedance at the peak 0.18–0.35 Ω
  against the polymers' 0.08–0.35 Ω (computed), for $0.15 against $1.09 a unit, two kinds of
  Extended part fewer, and ~26 µF an input for the line's converter to charge at start where
  they made ~110 (see [hardware](HARDWARE.md#power)).
- **Microamp lead-off currents** (6 or 24 µA, the ADS1299's). Through a 50 kΩ contact they make
  0.3 or 1.2 V, most of the input range at a gain of 12 or far beyond it. The ADS1298's are 6 to
  24 nA.
- **The bias through channel 8's multiplexer** (MUX = BIAS_DRN, IN8N the bias electrode, IN8P
  its spare). It kept the electrode connector at 16 positions, but cost the driving module two
  of its inputs and put the drive through the ADS1299. Reopened on 10 Oct 2026: the bias
  electrode has a lead of its own through 4.99 kΩ, every input measures, and the connector grew
  to 20 positions, 36 since 29 Oct 2026; what changed is under
  [hardware](HARDWARE.md#right-leg-drive).
- **The TMUX1101 on the bias electrode's lead** (10 to 29 Oct 2026). It parted a powered-down
  bias amplifier's output from the electrode, since nobody knew what that output does with an
  electrode on it. The datasheet's own bias lead-off check drives 6–24 nA through the pin with
  the amplifier powered down and reads the node with a comparator (SBAS499C, 9.3.2.4.4), which
  can only hold if the powered-down output leaks far less than that; so the switch went and the
  TLV9001S of the strip's ground layer took its place, the same count of parts. Confirmed on the
  first module by that very check.
- **Measuring the bias drive's voltage** with BIAS_MEAS (MUX = 010). A channel so set measures
  BIASIN against the mid-supply with its own inputs cut off, and must not be in the bias sum
  (SBAS499C, 9.3.2.4.2); TI gives it for debugging. The differential channels do not
  need a zero: a difference does not change when a constant is added to every potential.
- **A jumper for the reference electrode.** The suit is washed and its boards potted, so nobody
  will move a jumper; a strip that measures against the reference is wired so.
- **The BIASINV wire between the ADS1299s** that the datasheet's figure 39 draws. A
  high-impedance node on a metre of cable would pick up the mains; one module's channels sense
  the body's common voltage well enough, since the body is one conductor.
- **Several modules driving the bias at once,** each through its own electrode, a trial against
  one (to 28 Oct 2026). The datasheet asks for all but one bias amplifier to be powered down
  (SBAS499C, 9.3.2.4.5), and TI's answer on its E2E forum, *ADS1299: BIASOUT configuration*,
  says the same; two loops driving one body would pull its voltage against each other.
- **The glove's board on the back of the hand,** Staršaja and four Vnučata, five STM32H523CCU6 on
  the suit clock, joined by Interconnect, one half-duplex wire on the board (10–24 Oct 2026).
  Vešč came back to one board on the hand on 29 Oct 2026, with the hand's ADS1298 on it, small
  STM32H503 Bratiški on their HSI and a full-duplex U(S)ART to each; what died here is
  Interconnect, its pull-up, the five large processors and their oscillator inputs.
- **The STM32H523CCU6 for the small processors, for its suit clock** (to 24 Oct 2026). The
  STM32H503KB in UFQFPN32, 5 × 5 mm, has no PH0-OSC_IN, and needs none: Staršaja makes the IMUs'
  clock from the suit clock and sends it on one wire, so the IMUs sample in step with the suit and
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
  frame as an extension (to 24 Oct 2026). It was a second way of doing the hand, with a firmware
  path of its own; the whole glove is now part of every suit with arms, and a hand that takes no
  full glove wears the glove's board with fewer finger strips, 12 or 8 IMUs by its table (29 Oct
  2026; see [Bogatyr](../bogatyr/CONSTRUCTION.md#the-imus)).
- **BGA and WLCSP packages for the small processors.** The STM32H523's WLCSP39 would take the
  clock in 2.8 × 2.8 mm (DS14540), but at a 0.4 mm pitch it wants a dearer board and, on a hand
  that bends, an underfill. The STM32H503's WLCSP25, 2.33 × 2.24 mm at 0.40 mm, stays the
  Bratiška's fallback: USART2 on PA5 and PA15, the I3C pins, PA0, NRST and BOOT0 are all on it,
  with VDDIO2 to feed and via-in-pad to route (DS14053 Rev 4, figure 4).

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
  MTw integrates at 1,000 Hz on the sensor for that reason. The block sums at the IMU's rate,
  1,920 Hz, and the chip's own 120 Hz stays a mode for the I2C fallback and for comparison.
- **Bosch BMI570.** Lower noise on paper, but we found no external clock input, and the suit
  runs every sensor from one clock.
- **TDK's ICM-45686** (the suit's IMU from 28 to 31 Oct 2026). The ICM-42688-P's newer
  sibling; it would reach 120 Hz too, but its gyro is noisier (3.8 against 2.8 mdps/√Hz) and its
  CLKIN takes 20–40 kHz, so the noise decided for the ICM-42688-P at first. Taken on 28 Oct 2026,
  when the ICM-42688-P could not be had (DigiKey: none, 5,000 expected in August 2027) and the
  gyro's offset drift was weighed above its noise, ±5 mdps/°C, with CLKIN at 38,400 Hz. It went
  on 31 Oct 2026 for ST's LSM6DSV16X: $3.36 against $11.94 at JLCPCB, ~$840 a suit of 98, at
  ±6 mdps/°C and 2.8 mdps/√Hz (DS13510 Rev 4, table 3), and the LSM6DSV16X's rate held to a
  reference is documented (AN5763 Rev 4, 3.3), where the ICM-45686's 1,920 Hz under CLKIN was our
  inference, asked of TDK (see [hardware](HARDWARE.md#the-imu)).
- **The ICM-42688-P as the suit's IMU** (to 28 Oct 2026). The family's quietest gyro, but out of
  stock everywhere, and its zero no steadier than the ICM-45686's. It fitted the ICM-45686's
  board as a fallback until 31 Oct 2026; the LSM6DSV16X's pinout differs (DS13510, table 2).
- **The choke filter on the IMU board** (to 31 Oct 2026): 6.8 Ω and TDK's MLF1608A4R7KTA00,
  4.7 µH, into 2 × 1 µF and 100 nF. It answered the ICM-45686's sheet, a larger capacitor on VDD
  should the supply's ripple pass 50 mV pp (DS-000489, 4.5). ST asks 100 nF at each supply pin
  (DS13510, table 2), the IMUs' 3.3 V comes from the module's LDO behind its π filter, and the
  islands on the fingers want the room: one 1 µF at the input is all.
- **IMUs chained behind one on its sensor hub** (31 Oct 2026). The LSM6DSV16X's hub takes four
  sensors, but reads 18 B a trigger at up to 480 Hz (AN5763, 7.1 and 7.2.3), short of full IMUs
  at 1,920 Hz; each bus keeps its two IMUs, read by the processor itself.
- **IIM-42652** (28 Oct 2026, the same day). The ICM-42688's industrial twin (DS-000440), in
  stock and fitting without a change, but its offset drifts ±20 mdps/°C, four times the
  ICM-45686's at the same noise.
- **The rest of the ICM-426xx family.** The ICM-42686-P is noisier, 5.3 mdps/√Hz, for a
  ±4000 °/s the ICM-45686 has too; the ICM-42605 has no clock input; the ICM-42688-V is the
  ICM-42688-P again and as hard to get (the family's table on DS-000347 Rev 1.6's first page;
  DS-000439; DS-000292). An "ICM-42688-P" from TOKMAS at JLCPCB is another maker's chip under
  the name, 9 mdps/√Hz and 170 µg/√Hz by its own sheet.

## The electrodes and the suit

- **Ag/AgCl or titanium electrodes, for now.** Sintered Ag/AgCl comes to ~$4,000–9,000 for 582
  of them, and titanium discs cost $10 and more apiece at retail (the prices in
  [Construction](CONSTRUCTION.md#electrodes)). Stainless steel has more low-frequency noise and
  drift, which EMG bears; the four, with conductive silicone, are compared on a sample, and
  Ag/AgCl goes in only if the steel drifts too far.
- **Marine press studs in 316** (to 29 Oct 2026), the boat covers' snaps with their hand tool,
  the polished cap the electrode. Their caps are ~15 mm and their studs ~10 mm, DOT's line 24,
  and nothing smaller is made in 316; body jewellery's 316L discs come in 3 to 8 mm for the same
  money, implant grade (see [construction](CONSTRUCTION.md#electrodes)).
- **A gain of 24.** It leaves ±167 mV on the ADS1298, which an offset of 176 mV between metal
  electrodes, seen on dry ones, fills. A gain of 12 holds ±333 mV
  ([Software](SOFTWARE.md#the-ads129xs-settings)).
- **316Ti steel.** Its titanium protects the steel at welding temperatures, not on the skin;
  316L, the steel of body jewellery, does.
- **Dry electrodes.** A dry contact is ~1 MΩ, which the chips' input would bear but the input
  filter would not: its corner falls to ~360 Hz, inside the band. A moist ring keeps the
  contact at tens of kilohms.
- **A low-noise cable with a graphite layer** for the leads, as for piezo sensors. The band's
  strip has no cable: its layers are bonded and do not rub, and a moist contact makes the charge
  from friction ten to twenty times less voltage.
- **The 3M 3517 flat cable and leads fanned out by hand.** A shielded cable needs its drain
  wires twisted, sleeved and pressed into the connector, and every lead joined to its stud by
  crimp or solder: hours of hand work on every suit, and a price that rises with it. Its bare
  fan-out also ran up to half the girth unshielded. The band's strip carries the studs itself.
- **Free meanders in the polyimide** to stretch the band. Horseshoe meanders hold 40,000
  stretches of 30% only when moulded in an elastomer (Vanfleteren et al., MRS Bulletin 2012); a
  free one sewn in fabric has no such data, and a bend across its plane tears it. The strip does
  not stretch; an elastic gap in the fabric does. Moulded in silicone they come back only if the
  first arm shows the swell wants them. A finger's strip is cut as a meander all the same, its
  life left to a bending test (see [construction](CONSTRUCTION.md#the-glove)).
- **Stretchable circuits, copper on TPU,** for the limbs' strips and the fingers (Würth's
  STRETCH.flex, Murata's alike; to 31 Oct 2026). Set aside by the owner, made in China at German
  prices. The torso's rule holds on the limbs: the strip does not stretch, an elastic gap in the
  fabric does, two or three short polyimide strips a module meeting at it; the arm flexed against
  relaxed, 33.4 → 35.3 cm in men and 29.3 → 29.8 in women (Frontiers in Nutrition 2025, DOI
  10.3389/fnut.2025.1534453), is the swell the gap takes. Their meanders as a shield went with
  them (see [construction](CONSTRUCTION.md#electrodes)).
- **A harmonica of polyimide,** folds out of the plane to take the stretch. Flexing again and
  again wants a bend radius of ~100 times the thickness, ~150 for two layers (flex makers' rule,
  after IPC-2223, not read here): 11–17 mm for 0.11 mm, a bulge on every fold.
- **A conductive fabric.** It would short the electrodes or carry crosstalk between them. A
  static-dissipative one, gigaohms between neighbouring electrodes, drains charge without
  shorting signals.
- **Synthetics and plastic in the fabric.** They sit at the ends of the triboelectric series;
  cotton sits near its middle.
- **Silver in the fabric.** Too expensive; carbon-fibre grids are sold for antistatic workwear.
- **Taking the cables off for every wash.** It would wear them out sooner than wearing the suit
  does. The harness is rinsed with the cables on, and with the units on too (below).
- **The units unplugged for every rinse** (to 30 Oct 2026): the line on an IDC socket of 2 × 8,
  the strip's lever connector potted after its last mating or the tail soldered by hot bar, and
  for a day the board's own edge as the connector, a 3M card-edge IDC on the line and a Samtec
  MEC1 on the strip. The card-edge stood 18 mm high, the MEC1 34.5 mm long and not at JLCPCB.
  The units are potted whole in a gel that comes out for a repair and stay on the harness, so a
  connector opens only at assembly and repair; the line takes a Picoflex in tin, 30 cycles, $1.05
  a tap against $2.81 in gold, 100 cycles (see [construction](CONSTRUCTION.md#harness-and-washing)
  and [hardware](HARDWARE.md#sensing-module)).
- **Pressure insoles in the shoes** as a part of the suit. The contact points come out of the
  model from the EMG and the IMUs; a bought insole may serve once, at recording time, as the
  truth about heel and toe for the model to learn from, then goes back in the drawer.
- **Cables across the backs of the fingers.** They would bend with every grip; the cables run
  along the sides of the fingers.
- **Tinsel wire and silicone wire for the fingers.** Tinsel, copper ribbon round a textile core,
  is not sold as a thin multi-core and its IDC termination is unproven; silicone wears through
  at the sides of the fingers. PTFE of 28 AWG fits the 9175-700 IDC and does not; it stays the
  fallback to the finger strips.
- **A switch on the reference electrode.** It was there in case the ADS1299's own switching,
  SRB1 by MISC1, behaved otherwise than its register table says. The ADS1298 has no SRB1; a strip
  that measures against the reference joins the N inputs to its electrode itself (see
  [hardware](HARDWARE.md#right-leg-drive)). The bias lost its switch too, on 29 Oct 2026 (see
  [The sensing module](#the-sensing-module)).
- **Glued and suction electrodes.** They hold through a grip, but a glued one must be torn off
  with the suit, and suction, as the owner tried, left bruises that took a month to fade, and
  skin that conducts unlike the rest.
- **A coaxial lead per electrode,** as professional EMG has it. It is made to order and does not
  live long under constant bending; one strip per band, with the reference on it, does.
