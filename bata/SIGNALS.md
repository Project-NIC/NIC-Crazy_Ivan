<div align="center">

# Baťa: signals

**What happens to the data between the record and the output:** the EMG channel, the ECG and the
breath, the electrodes' quality, the IMUs and the joints, what the model gets and gives, fatigue,
and where it all runs.

↑ [Baťa](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Everything on this page runs on Baťa in software, and every step of it can change later: the raw
data are recorded as they came (packets 16 and 17, see [Porjadok](../porjadok/SOFTWARE.md#output)),
so the chain below is a first version to be tried on recordings, not a part of the suit. What has
to hold now is only the interfaces: what the model takes, what goes out, and in what packets.

## The EMG channel

128 channels at 3,840 SPS, 24 bits, 22.35 nV a step at a gain of 24 (±187.5 mV over 24 bits).

- **The band:** a high-pass at ~10 Hz takes the electrodes' drift and most of the movement
  artefact; the upper edge is the ADS1299's own, ~1 kHz at 3,840 SPS (SBAS499C, table 1). That
  is the 10–500 Hz band SENIAM recommends for surface EMG, with room above it.
- **The mains at 50 Hz** is not notched: a fixed notch takes EMG with it. The right-leg drive and
  the ADS1299's −110 dB of CMRR leave little, and what is left is estimated as a slowly varying
  sinusoid at 50 Hz and its first harmonics, tracked from quiet stretches, and subtracted. Whether
  it is needed at all the first recordings will show.
- **The radar's pattern** on the head's electrodes, locked to 16 Hz, is averaged over hundreds of
  its periods and subtracted (see [Míša](../misa/HARDWARE.md#radar-and-the-emg)).
- **The envelope:** for every channel the log of the RMS over each step of 32 samples (1/120 s),
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
- **Out:** the ECG of the four trunk blocks' first channels, 1 B a sample at 480 SPS, the
  packet of type 3 with a decimation of 8. A doctor reads a rhythm from that; the picture of the
  current through the chest is for later, from the raw recording with all channels.
- **The breath:** from the slow envelope of the diaphragm's and the lower abdomen's channels,
  which rise and fall with every breath, and from the trunk IMUs, which tilt a little with it.
  The two agree or the breath is marked unsure.
- **Vitals,** the packet of type 6, 8 B once a second: the heart rate (u8, beats a minute), its
  variability (u8, the RMS of successive differences in ms, RMSSD), the breathing rate (u8,
  breaths a minute, 0 unsure), the skin temperature from the trunk blocks' processors (i8, °C),
  the ECG's quality 0–15 and the breath's source (u8), 3 B zeros.

## The electrodes' quality

- **Off:** LOFF_STATP and LOFF_STATN come in every frame; an electrode that has come off masks
  its channel for the model (the channel's envelope is set to a value the model learns as
  "absent") and raises an event.
- **Quality 0–15** in the meta packet of the electrodes: from the channel's noise floor in the
  quietest stretches of the last seconds against the ADS1299's own 0.56 µVrms at this rate
  (SBAS499C, the noise table), and from how much mains and movement artefact the channel shows
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

The model takes features at the IMUs' rate, not the raw EMG: 2.46 MB/s of raw samples into a
network would cost what it does not need, and the envelopes carry the muscles' activity.

- **In, every step of 1/120 s:** 128 EMG envelopes (log-RMS of the step) and 64 IMU steps of 6
  values, **512 values a step**; a window of **32 steps**, 267 ms, 16,384 values. Absent IMUs and
  masked channels take their "absent" value.
- **Out, every step:** the 127 joint values, the 32 contact bits and, from longer windows, the
  fatigue below. Neural networks learn rotations better in a six-number form than as angles or
  quaternions (Zhou et al., CVPR 2019), so the model may put that out and the output step turns
  it into the bytes.
- **The split:** the large fixed part on the Hailo, a small last part on a core of Baťa that
  learns this person and this fit of the suit (see [learning](SOFTWARE.md#learning)). The IMUs'
  joints are the targets the EMG part learns from.
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
  one core of Baťa, the input core, in the gaps between SPI reads. The model runs on the Hailo;
  the personal part on a free core.
- **Latency:** the step's window adds 8.3 ms; the model's window of 267 ms is history, not delay,
  the newest step is in it. The rest is under [latency](SOFTWARE.md#latency).
- **In code:** Python on recordings first, the same code that the simulator's files run through;
  then the live chain in C or Rust on Baťa.

## Open questions

- the first recordings decide: whether the mains needs taking out at all, how far the ECG
  template reaches on the limbs, the breath from the EMG against a belt,
- the complementary filter's gains and the joint constraints' weights, on a recorded walk against
  a camera,
- the model's window and features: 32 steps of 512 values is the first guess, to be tuned,
- the fatigue index against a known effort, on a recording with a dynamometer.
