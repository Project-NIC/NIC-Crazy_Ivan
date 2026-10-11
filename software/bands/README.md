# The bands

**Which pairs of a band's sixteen electrodes to measure,** worked out on a cross-section of a
limb before a band is sewn. Python 3 with NumPy.

| file | what is in it |
|---|---|
| `chords.py` | every pairing of the eight P electrodes with the eight N electrodes, 8! = 40,320, scored on random cross-sections: how well seven superficial muscles are told apart, how much the deep ones show, and how much the channels change when the band sits ~1 cm round; the same against the reference |
| `test_chords.py` | the pairings are whole, and the ring's mean is a quiet reference |

```
python3 chords.py 200
python3 -m unittest test_chords
```

The model is a sketch, not anatomy: a homogeneous disk with an insulating skin and line sources
whose field falls as −ln r. It says which way a choice leans, not what a real arm will show;
the arm decides (see [Rubaška](../../rubaska/CONSTRUCTION.md#electrodes)).
