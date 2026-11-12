# The signals

**Baťa's signal chain, the first version tried on recordings** ([Baťa](../../bata/SIGNALS.md)):
the EMG's band, the mains tracked and taken out, the envelopes a step; the QRS, the ECG out and the
heart taken out of the EMG. Every filter causal, block by block, as the live chain will run it.
Python 3 with numpy and scipy (Debian's `python3-numpy`, `python3-scipy`); the recordings read are
the [recorder](../recorder/README.md)'s.

| file | what is in it |
|---|---|
| `signals/emg.py` | the high-pass at 10 Hz (20 to try), the adaptive mains canceller at 50 Hz and two harmonics, its frequency followed; variant A's log-RMS envelope a step, absent past 2 held samples; variant B's conditioned samples, i16 of 0.25 µV |
| `signals/ecg.py` | Pan–Tompkins's QRS detector, the ECG out at 480 SPS (0.5–40 Hz, 1 µV a step), the heart taken out by a template a channel, RMSSD |
| `signals/imu.py` | the IMUs' orientations by a complementary filter of Mahony's kind, the gyros' offsets when still, the bones' mounting from the calibration pose, the joints as angles or as a swing and a twist, into bytes by their ranges |
| `signals/run.py` | a recording's BDF+ files read with numpy and run through the chain, the EMG and the IMUs |
| `tests/` | the band, the mains tracked and taken out, no wandering without it, the envelope and absence, the QRS, the heart taken out and no noise added, the ECG's scale, the simulator through the recorder; the tilt found and the offset learnt, a turn followed, tilting while turning, a hinge's flexion, the swing and twist, the bytes, the offset when still |

```
python3 -m signals /tmp/rec.bdf /tmp/rec-2.bdf --out /tmp/rec.npz      # --highpass 20, --no-heart
python3 -m unittest discover -s tests -t .
```

- **The band:** a Butterworth high-pass of the second order, its state carried from block to
  block and started settled on the first sample, so an electrode's offset does not ring.
- **The mains:** every channel its own amplitude and phase at 50, 100 and 150 Hz, learnt by
  block LMS once a step (16 samples) against one oscillator, the notch ~0.5 Hz wide. The
  oscillator follows the mains from the turning of the fundamental's weights, within ±0.2 Hz,
  and only while half the channels or more hear the mains ten times over the noise their
  estimate carries: the mains comes in on every lead, the heart mostly on the trunk's. On 280
  channels with a mains of 5–30 µV at 50.3 Hz (tried with the range opened) it found 50.30 Hz and
  left 0.08 µV, the EMG's power kept to 99 %.
- **Two variants of the model's input,** both made here and trained side by side (the owner, 11
  Nov 2026; [Baťa](../../bata/SIGNALS.md#the-model)): A the envelopes, B the cleaned samples
  themselves as i16 of 0.25 µV, ±8.2 mV, the heart left in and nothing late (`--raw`).
- **The envelope:** ln of the RMS of each step, NaN where more than 2 samples of the step were
  held, the model's "absent".
- **The QRS** on the trunk channel whose 5–15 Hz band swings the most: band-pass, the five-point
  derivative, squaring, a window of 150 ms, the adaptive thresholds, 200 ms refractory from the
  window's peak, a search back at half the threshold; the R the largest swing above 5 Hz in the
  window before the peak. The first 2 s set the levels.
- **The heart taken out** of the trunk's channels: each channel's beat from 0.15 s before the R
  to 0.45 s after it, a plain mean of the first beats, then each new one weighing 1/16, every beat
  moved by up to ±5 ms to where it matches best, the template shrunk where it is mostly the EMG
  averaged in, by T² / (T² + its noise), so the QRS goes and nothing is added between beats; from
  the eighth beat. On the simulator's chest the QRS's steps came down ~4×, ~12 dB; on noise alone
  the output grew by 1 %. **The trunk's envelopes are then 1 s late,** the beat's window and the
  detector's lag; the others are held back with them.
- **The ECG out:** the trunk modules' first channels from the raw samples, band-passed 0.5–40
  Hz, every fourth sample, 1 µV a step in an i16, the packet of type 3.
- **The IMUs:** a quaternion an IMU, each step's turn integrated and the tilt pulled towards
  gravity (proportional 1.0, integral 0.02 a second), the force trusted only within 0.1 g of
  1 g; a unit's gyros' offsets taken from any second all its IMUs stay under 2 °/s. A joint is the
  relative turn of its two bones, each IMU turned into its bone by the calibration pose; out as
  angles about x, y, z (flexion, abduction, rotation) or, for the shoulder and the hip, as a swing
  across the bone's axis and a twist about it from a rest; each into a byte by its range. Not
  yet: the joint list (which two IMUs a joint), to be written with Baťa's map, and the joints'
  own constraints on the turn about the vertical, for the recordings.
- **Speed:** the whole suit's 280 channels, 12 s of the simulator, in ~0.6 s with the reading of
  the files, the chain alone ~0.25 s; the 108 IMUs' 6 s ~1 s with their files; one core.
