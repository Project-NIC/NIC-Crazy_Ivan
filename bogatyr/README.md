<div align="center">

# Bogatyr

**The meat on Kaščej's bones:** where every electrode and every IMU sits on the body, and why.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

*Bogatyr*, the strongman of the Russian byliny. Kaščej, the harness, is bone and skin (see
[Rubaška](../rubaska/CONSTRUCTION.md#harness-and-washing)); dressed in the electrodes on the
muscles and the IMUs on the bones, he is a bogatyr.

**A proposal, not yet tried on a body.** The layout is put together from several studies and anatomy
books, named where a place has one, and is to be gone through with someone who knows the body, a
physiotherapist, before any strip is drawn. Where a place is an estimate, it says so.

## What it lays out

- **The EMG of 16 modules,** each with 16 electrodes, a bias electrode and a reference electrode,
  288 in all, for both ways of measuring on one suit: differential, a channel P against N, and
  against the reference, eight P against one point (see
  [Rubaška](../rubaska/HARDWARE.md#right-leg-drive)). A channel's two electrodes lie 4–8 cm apart
  where the muscle allows, 2–3 cm on small muscles and near the heart, along the fibres and across
  them by turns, and across the spine only diagonally.
- **The IMUs,** 48 on the body of 64 places, two or more on each segment of a limb and more where
  the skin slides most, and the gloves' 2 × 20.
- **What was left out,** the muscles surface EMG cannot reach and the places the body presses
  on, and the layouts before this one.

## On an average body

**A first draft,** drawn to see the layout whole, to be looked at with the layout by someone who
knows the body (see [construction](CONSTRUCTION.md#open-questions)).

![Bogatyr on an average body, a first draft: from the front, the back and the side](body.png)

Every place of [construction](CONSTRUCTION.md) put on MakeHuman's average body by the bones'
landmarks: P red, N blue, each channel a line between them, the reference green, the bias yellow,
the IMUs violet. The landmarks are estimates on that body, not measured (see
[software/body](../software/body/README.md)); the modules are not drawn, their places on the
trunk not being set. Up close, each with its own modules alone:

| the hand and the forearm | the foot and the calf | the neck, the upper back and the shoulders |
|---|---|---|
| ![the left forearm's module](hand.png) | ![the left calf's module](foot.png) | ![the neck's module and the shoulders'](neck.png) |

The hand is drawn with no glove, its two IMUs on the back of the hand; with the glove they are the
glove's (see [construction](CONSTRUCTION.md#the-imus)).

| file | what is in it |
|---|---|
| [CONSTRUCTION.md](CONSTRUCTION.md) | the electrodes' rules; the modules one by one, every muscle with its P and N, the reference and the bias; the IMUs' rules and places; the glove's |
| [WHY.md](WHY.md) | what was left out, and why; the layouts before this one |
| `body.png`, `hand.png`, `foot.png`, `neck.png` | the layout on an average body, a first draft, drawn by [software/body](../software/body/README.md) |

What the electrodes, the strips and the harness are made of is under
[Rubaška](../rubaska/CONSTRUCTION.md); the modules and the glove under
[Rubaška's hardware](../rubaska/HARDWARE.md).

## Scale

| | modules | electrodes | IMUs |
|---|---|---|---|
| the body | 16: the head, the neck with the upper back, the two shoulders, the chest with the abdomen, the lower back, the two hips, and two on each limb | 256, a bias and a reference electrode on each module, 288 | 48 of 64 places |
| the gloves | — | — | 2 × 20 |
