<div align="center">

# Baťa: signals

**What happens to the data between the record and the output:** the EMG channel, the ECG and the
breath, the electrodes' quality, the IMUs and the joints, what the model gets and gives, fatigue,
and where it all runs.

↑ [Baťa](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Everything on this page runs on Baťa in software, and every step of it can change later:
recordings, made when asked, keep the samples as the ADS1298s gave them, in BDF (see
[Porjadok](../porjadok/SOFTWARE.md#ci-btp)), so the chain below is a first version to be tried on
recordings, not a part of the suit. What has
to hold now is only the interfaces: what the model takes, what goes out, and in what packets.

## The EMG channel

280 channels at 1,920 SPS, 24 bits, 39.74 nV a step at a gain of 12 on every ADS1298 (±333 mV
over 24 bits).

- **A lost frame,** its place on the SPI zeros and its kind 0: the unit's last sample is held
  before any filter, a flat step rather than a jump of the electrodes' offset, tens of mV, into
  the 10 Hz high-pass, which would ring ~50–100 ms; past ~2 samples running the unit's envelopes
  are marked absent, and the IMU step its frame carried (the frame's number mod 16) absent, so
  the model takes nothing made up (see [Porjadok](../porjadok/SOFTWARE.md#errors)).
- **The band:** a high-pass at ~10 Hz takes the electrodes' drift and most of the movement
  artefact; the upper edge is the chips' own, ~503 Hz at 1,920 SPS, 0.262 of the rate (SBAS459K,
  Electrical Characteristics), the 10–500 Hz band SENIAM recommends for surface EMG. The movement
  artefact of the electrode on the skin, larger than the cables', lies at 0–20 Hz, and De Luca
  filters from 20 Hz (*Surface Electromyography: Detection and Recording*, Delsys 2002); 10 Hz
  stays, and 20 Hz is tried on the first recordings, one number here.
- **The mains at 50 Hz** is not notched: a fixed notch takes EMG with it. The right-leg drive and
  the chips' CMRR, −105 dB at least on the ADS1298 (SBAS459K), leave little, and what is left is
  tracked by an adaptive notch, a PLL ~0.5 Hz wide that follows the mains' frequency too, at 50 Hz
  and its first harmonics, and subtracted. Whether it is needed at all the first recordings will
  show.
- **No lead-off tone** under the recording: the chips' AC lead-off, a tone at 480 Hz, runs only
  as a check Baťa asks for, at putting-on and between two recordings, never while recording (see
  [Rubaška](../rubaska/SOFTWARE.md#an-electrode-coming-off)); the samples of a check's 32
  cycles are not recorded.
- **The radar's pattern** on the head's electrodes, aligned to each radar frame by the cycle's
  number Míša stamps on it from the module's end-of-frame pin, not by a sphere's arrival, 10
  frames a second, is averaged over
  hundreds of frames and subtracted (see [Míša](../misa/HARDWARE.md#radar-and-the-emg)).
- **The envelope:** for every channel the log of the RMS over each step of 16 samples (1/120 s),
  so the EMG arrives at the model at the IMUs' rate. Log, because muscle activity spans two
  decades and the model should see a quiet muscle as well as a straining one.

## The ECG and the breath

The heart shows on every channel of the trunk and weaker on the limbs. It is taken out of the
EMG and kept as a measurement of its own.

- **The QRS** is found on the trunk channel with the strongest R wave by the classic
  Pan–Tompkins detector (band-pass, derivative, squaring, moving window, adaptive thresholds;
  Pan and Tompkins, IEEE Trans. Biomed. Eng. 1985). The beats give the heart rate and its
  variability.
- **The template:** the waveform around each beat, averaged over the last beats, one template
  per channel with its own amplitude and delay, since every electrode sees the heart from
  somewhere else. The template is subtracted at every beat; what is left is EMG, what was taken
  is the ECG.
- **Out:** the ECG of the three trunk modules' first channels, the chest's, the neck's and the lower
  back's, made from the raw samples band-passed at 0.5–40 Hz, the template used only for the
  subtraction, so that the P and T waves and an ectopic beat stay, 2 B a sample, 1 µV a step, at 480
  SPS, the packet of type 3 with a decimation of 4. A doctor reads a rhythm from that; the picture
  of the current through the chest is for later, from a recording with all channels.
- **The breath:** from the slow envelope of the diaphragm's and the lower abdomen's channels,
  which rise and fall with every breath, and from the trunk IMUs, which tilt a little with it.
  The two agree or the breath is marked unsure.
- **Vitals,** the packet of type 6, 8 B once a second: the heart rate (u8, beats a minute), its
  variability (u8, the RMS of successive differences in ms, RMSSD), the breathing rate (u8, breaths
  a minute, 0 unsure), the module temperature from the trunk modules' processors, their dies, not
  the skin (i8, °C), the ECG's quality 0–15 in bits 7–4 and the breath's source in bits 3–0 (0 none,
  1 the EMG, 2 the trunk IMUs, 3 both agreeing, 4 unsure), 3 B zeros.

## The electrodes' quality

- **Off:** the pairs on the skin come in the diagnostics as the last lead-off check left them,
  at putting-on and whenever Baťa asks one between two recordings (see
  [Rubaška](../rubaska/SOFTWARE.md#an-electrode-coming-off)). While the suit runs an electrode
  that comes off shows in its channel: the input floats, the channel runs to a rail or carries
  the mains at full swing, so a channel with a sample at the rails or with 50 Hz over a threshold
  found on the first recordings is marked absent by Baťa, for its envelope (set to a value the
  model learns as "absent") and an event.
- **Quality 0–15** in the meta packet of the electrodes: from the channel's noise floor in the
  quietest stretches of the last seconds against the chip's own noise at this rate, 0.8 µVrms on
  the ADS1298 at a gain of 12 (SBAS459K, its noise table), and from how
  much mains and movement artefact the channel shows
  compared with its neighbours. A channel of quality 0 is as good as off.

## The IMUs and the joints

Each IMU's step is its turn Δθ over 1/120 s with the coning term and its mean specific force
(see [Rubaška](../rubaska/SOFTWARE.md#the-imus-settings)).

- **Orientation** is kept per IMU as a quaternion, the turn integrated step by step and the tilt
  pulled towards gravity by a complementary filter of the Mahony or Madgwick kind (Madgwick,
  2010; Mahony et al., IEEE Trans. Autom. Control 2008), without a magnetometer, so the turn
  about the vertical is free.
- **A joint** is the relative quaternion of the two IMUs that share it. Their free turn about the
  vertical is pinned by the joint itself: both bones share the joint's centre, so the centre's
  acceleration worked out from either IMU must agree, and a hinge like the knee or the elbow
  has one axis (Seel, Schauer and Raisch, IEEE CCA 2012; Weygers et al., IEEE Sensors J. 2020,
  from the abstracts). Every movement corrects the drift; standing still, the gyro's offset is
  measured and taken off, and silent EMG confirms the stillness.
- **The calibration pose** at the start, a few seconds with the arms down or out, gives each
  IMU's turn against its bone; the bones' lengths come from the meta packet.
- **Out:** the joints' angles into the 127 bytes by the joint table, each axis to its range, the
  shoulder and the hip as a swing and a twist (see [Porjadok](../porjadok/SOFTWARE.md#output)).

## The model

Two variants are built and trained on the same recordings, and the better one is kept (the
owner, 11 Nov 2026): nobody knows yet whether the Hailo carries the raw EMG. Both share the body
and the output below; they differ in what the EMG is when it reaches the model. Its output is
its own, not the snapshot's joints, which are the pose the IMUs measure; its input is normalised
channel by channel, it is trained with dropout over the channels, and the IMU steps are turned into
each bone's frame.

- **Variant A, the envelopes:** every step of 1/120 s, 280 EMG envelopes (log-RMS of the step)
  and 108 IMU steps of 6 values, **928 values a step**; a window of **32 steps**, 267 ms, 29,696
  values. Baťa's core makes the envelopes; the heart is taken out of the trunk's channels first,
  which makes them 1 s late (open questions). Small and certain; it runs on the RK3588's NPU
  too, so the small fitting keeps it whatever is chosen.
- **Variant B, the raw EMG** (the suit's first idea): every channel at 1,920 SPS into the Hailo,
  280 × 16 samples a step and the same IMU steps beside them; the window the same 267 ms, 512
  samples a channel. Baťa's core only conditions the samples, what a network does badly: the lost
  ones held, the electrode's offset taken off by the high-pass, the mains by the adaptive canceller,
  each sample then an i16 of 0.25 µV (±8.2 mV, the chip's 0.8 µVrms ~3 steps). The heart stays in;
  the network learns it, so nothing waits. The model's first layers learn the filters and the
  spread of activity over neighbouring electrodes, the map of the muscles over the body, and see
  the spectrum the fatigue lives in, which an envelope throws away. ~1.1 MB/s of samples, ~34 MB/s
  of whole windows into the Hailo, little on its PCIe; the first layers ~1 GOP/s at 120 windows a
  second (a filter of 33 taps a channel at a stride of 4, one of 9 after it, then the channels
  mixed into 256; an estimate). To be checked in Hailo's tools first: the input and the first
  layer at 16 bits, since at 8 bits the quiet muscles are lost; if only 8 bits go, each channel
  scaled by its own slow RMS before, the scale a second input.
- **The choice** by the scoring the layouts get (below): the same task, the same fresh putting-on,
  the EMG alone and with the IMUs, then the latency and the Hailo's power. Absent IMUs and masked
  channels take their "absent" value in both.
- **Out, every step:** the joint values (up to 127), the 32 contact bits and, from longer
  windows, the fatigue below. Neural networks learn rotations better in a six-number form than as
  angles or quaternions (Zhou et al., CVPR 2019), so the model may put that out and the output
  step turns it into the bytes.
- **The split:** the large fixed part on the Hailo, a small last part on a core of Baťa that
  learns this person and this fit of the suit (see [learning](SOFTWARE.md#learning)). The IMUs'
  joints are the targets the EMG part learns from.
- **How the EMG is judged** (an answer on OpenBCI's forum, *How would you lay out a whole-body
  sEMG suit?*, 4 Nov 2026): with the IMU steps among the inputs and the IMUs' joints as the
  targets, a good joint score says little of the electrodes, the IMUs alone being able to give
  it. So a layout is scored on the same task three ways, the IMUs alone, the EMG alone and both,
  and ranked by the EMG alone and by what it adds to the IMUs; trained on earlier fittings and
  tested on a wholly new putting-on of the suit, whole repetitions on one side of the split, never
  neighbouring windows across it; a short recalibration, if allowed, held out before the scoring,
  the same time for every layout.
- **What the EMG must show beyond the joints** (the same answer's follow-up): the joints stay the
  baseline, and one task needs the EMG, a held contraction against a fixed load cell, the force
  measured apart and varied at one posture, relaxed trials among them, lest the model learn the
  posture or the instruction instead of the force. A look-ahead fixes its horizon before training,
  every input only what is there at the prediction's moment, the filters and the envelope included,
  and is compared at the same horizon with a predictor from the IMUs' own history, a smooth movement
  being predictable from its trajectory; the fresh putting-on for both. Never the EMG's amplitude as
  the force's label, nor its lead over the movement as one fixed delay.
- **Contacts** come from the model, trained by the rule that a limb that neither hangs nor is
  held must rest on something, which marks the recordings without anyone labelling.

## Fatigue

Surface EMG shows fatigue as the spectrum sliding down and the amplitude rising for the same
effort (the myoelectric manifestations of fatigue, De Luca, J. Appl. Biomech. 1997). For each
muscle group the median frequency of its channels' spectrum and their RMS are taken over 1 s
windows and compared with the first minutes of the day; the drop goes out as a byte per group in
the meta packet of fatigue. Surface EMG hears the neighbouring muscles too, so groups, not muscles.

## Where it runs and what it costs

- **The envelopes, the filters, the ECG and the quaternions** are ~10 MFLOP/s for the whole suit:
  one core of Baťa, the input core, in the gaps between SPI reads; variant B's conditioning less
  (no envelopes, no heart taken out). The model runs on the Hailo, variant B's first layers with
  it; the personal part on a free core. The chain in Python on recordings: the whole suit's 12 s
  in ~0.25 s on one core ([software/signals](../software/signals/README.md)).
- **Latency:** the step's window adds 8.3 ms; the model's window of 267 ms is history, not delay,
  the newest step is in it. The rest is under [latency](SOFTWARE.md#latency).
- **In code:** Python on recordings first, the same code that the simulator's files run through
  ([software/signals](../software/signals/README.md)); then the live chain in C or Rust on Baťa.

## Open questions

- the heart taken out of the trunk's EMG waits for a beat's whole window and the detector, which
  makes the envelopes 1 s late: live, either every envelope waits, or the trunk's go out at once
  with the QRS's steps marked; for the first recordings,
- the first recordings decide: the high-pass at 10 or 20 Hz, whether the mains needs taking out
  at all, how far the ECG
  template reaches on the limbs, the breath from the EMG against a belt,
- the complementary filter's gains and the joint constraints' weights, on a recorded walk against
  a camera,
- the model's window and features: 32 steps of 928 values is variant A's first guess, to be
  tuned; variant B's 16-bit input on the Hailo, and which variant stays,
- the load cell and the look-ahead's horizon for the first arm's recordings,
- the fatigue index against a known effort, on a recording with a dynamometer.
