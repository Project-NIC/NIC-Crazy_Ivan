# Body

**Bogatyr's layout drawn on an average body:** every place of
[Bogatyr](../../bogatyr/CONSTRUCTION.md) put on MakeHuman's base mesh by the bones' landmarks,
the pictures in [`bogatyr/`](../../bogatyr/README.md#on-an-average-body): the 256 electrodes (P
red, N blue), the 128 channels as lines from a P to its N, the 16 reference electrodes (green),
the 16 bias electrodes (yellow) and the 48 IMUs (violet), from the front, the back and the side,
and the hand, the foot and the neck with the upper back up close. The modules are not drawn,
their places on the trunk not being set.

| file | what is in it |
|---|---|
| `load.py` | reads MakeHuman's base mesh (OBJ): the skin and the joints' centres |
| `skin.py` | the tools: a joint's centre, a ray from inside the body to the skin, a limb's girth |
| `layout.py` | the layout: the spine's levels and the other landmarks, every module's P, N, reference and bias, the IMUs, each place commented with its muscle or bone; it counts what it placed against Bogatyr's table and stops if a count differs |
| `view.html`, `shot.mjs` | draw it with three.js in a headless Chromium and save the pictures; `only=` shows some modules alone |

The body is MakeHuman's base mesh `hm08`, released as CC0 in September 2020 (the file's own
header); it is not kept here. Units are decimetres, +x the body's left, +y up, +z front.

```
curl -sLO https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/3dobjs/base.obj
python3 layout.py base.obj layout.json
npm i three@0.169.0 playwright-core@1.56.1
python3 -m http.server 8765 --bind 127.0.0.1 &   # serves view.html and the JSON
mkdir -p out && node shot.mjs "sheet:2100:1500::layout.json:legend=1" \
  "hand:1000:1000::layout.json:only=forearm l" "foot:1000:1000::layout.json:only=calf l" \
  "neck:1000:1000::layout.json:only=neck and upper back,shoulder l,shoulder r"
```

`shot.mjs` points at Chromium in `/opt/pw-browsers`; change `executablePath` for another.

**A first draft, an estimate, not measured.** The body is an average one, and its landmarks are read
off the mesh's joints: the spinous processes C7 by its neck joint and the others spread evenly down
to the sacrum, the anterior superior iliac spine, the iliac crest and the trochanter at heights set
by eye, a limb's places at fractions of its bone and angles round it. Where every electrode really
sits is found on a body, with a physiotherapist (see
[Bogatyr](../../bogatyr/CONSTRUCTION.md#open-questions)).
