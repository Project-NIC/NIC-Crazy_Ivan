# Body

**The suit drawn on an average body, a concept:** the picture
[`rubaska/concept.png`](../../rubaska/concept.png), front left and back right, with the 16 units'
256 electrodes (P red, N blue), the 128 channels as lines from a P to an N, the 16 bias
electrodes (yellow) and the 16 modules (grey), as
[Rubaška](../../rubaska/CONSTRUCTION.md#electrodes) lays them out.

| file | what is in it |
|---|---|
| `load.py` | reads MakeHuman's base mesh (OBJ): the skin and the joints' centres |
| `place.py` | the tools: rays from inside the body to the skin, a limb's girth cut by them; run on its own it places evenly spread rings, the first block layout |
| `detail.py` | the concept: the limbs' two rings with each P to the N half a turn round, the hand's and the foot's pairs, the torso's units by their muscles with each chord across, the bias electrodes and the modules; each channel drawn over the skin |
| `view.html`, `shot.mjs` | draw it with three.js in a headless Chromium and save the pictures |

The body is MakeHuman's base mesh `hm08`, released as CC0 in September 2020 (the file's own
header); it is not kept here. Units are decimetres, +x the body's left, +y up, +z front.

```
curl -sLO https://raw.githubusercontent.com/makehumancommunity/makehuman/master/makehuman/data/3dobjs/base.obj
python3 place.py base.obj suit.json             # the mesh, for detail.py too
python3 detail.py base.obj suit.json detail.json
npm i three@0.169.0 playwright-core@1.56.1
python3 -m http.server 8765 --bind 127.0.0.1 &   # serves view.html and the JSON
mkdir -p out && node shot.mjs "sheet:1900:1500:emg,bias,module:detail.json:iso=1"
```

`shot.mjs` points at Chromium in `/opt/pw-browsers`; change `executablePath` for another.

The body is an average one and the places are the pages' rules applied to it, not measured:
where every electrode really sits is found on a body (see
[Rubaška](../../rubaska/CONSTRUCTION.md#open-questions)).
