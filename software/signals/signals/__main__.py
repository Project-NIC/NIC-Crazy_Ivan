"""python3 -m signals rec.bdf [rec-2.bdf] --out rec.npz: a recording through the chain.

The envelopes a step, the ECG at 480 SPS and the beats into one numpy file; the heart rate, its
variability and the mains' frequency printed."""
import argparse
import sys
import time

import numpy as np

from signals.run import load, orientations, process


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="the EMG and the ECG of a recording")
    ap.add_argument("files", nargs="+", help="the recorder's BDF+ files of one recording")
    ap.add_argument("--out", help="a .npz with the envelopes, the ECG and the beats")
    ap.add_argument("--highpass", type=float, default=10.0, help="Hz, 10 or 20 to try")
    ap.add_argument("--mains", type=float, default=50.0, help="Hz, 50 or 60")
    ap.add_argument("--no-heart", action="store_true", help="the heart left in the EMG")
    ap.add_argument("--raw", action="store_true", help="variant B's i16 samples into --out too")
    a = ap.parse_args(argv)
    t = time.time()
    emg = load(a.files)
    r = process(emg, highpass=a.highpass, heart=not a.no_heart, mains=a.mains, raw=a.raw)
    seconds = emg.uv.shape[1] / emg.fs
    print(f"{emg.uv.shape[0]} channels, {seconds:.0f} s in {time.time() - t:.2f} s; "
          f"{len(r.beats)} beats, {r.heart_rate:.1f} a minute, RMSSD {r.rmssd:.1f} ms; "
          f"the mains at {r.mains[-1]:.2f} Hz; the envelopes {r.delay / emg.fs:.2f} s late")
    imus, quats = orientations(a.files)
    if imus:
        print(f"{len(imus)} IMUs' orientations, {quats.shape[1]} steps")
    if a.out:
        np.savez_compressed(a.out, envelopes=r.envelopes.astype(np.float32), ecg=r.ecg,
                            ecg_labels=np.array(r.ecg_labels), beats=np.array(r.beats),
                            labels=np.array(emg.labels), mains=np.array(r.mains),
                            imus=np.array(imus), orientations=quats.astype(np.float32),
                            **({"raw": r.raw} if r.raw is not None else {}))
    if r.raw is not None:
        print(f"variant B: {r.raw.shape[1]} samples a channel, {r.clipped} at the ends")
    return 0


if __name__ == "__main__":
    sys.exit(main())
