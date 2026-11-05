<div align="center">

# Bogatyr

**The meat on Kaščej's bones:** where the electrodes and the IMUs go on the body, and why.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

*Bogatyr*, the strongman of the Russian byliny. Kaščej, the harness, is bone and skin (see
[Rubaška](../rubaska/CONSTRUCTION.md#harness-and-washing)); dressed in the electrodes on the
muscles and the IMUs on the bones, he is a bogatyr.

**The electrodes' places are not laid out yet.** We do not know how to lay them out well, and we
are asking professionals for advice; the pictures will come with the layout. What is settled is
how many there are, the rules any layout keeps, and the IMUs. Where a place is an estimate, it
says so.

## What it lays out

- **The EMG of 16 modules,** every chip an ADS1298: fifteen with two, 32 electrodes and a bias
  electrode each, the neck's with one, 16 and a bias; every channel differential, P against N, no
  reference: 512 electrodes on the modules, and the hand's and the foot's sixteen with a bias on
  the glove's and the sock's own ADS1298, 580 in all.
- **The rules** any layout keeps: on small muscles and near the heart short pairs, none across the
  sternum, across the spine only diagonally, nothing in the hair, nothing where the body is
  pressed, no two electrodes closer than 1.5 cm (see
  [construction](CONSTRUCTION.md#the-electrodes-rules)).
- **The IMUs,** 44 on the body of 64 places, two or more on each segment of a limb, more where
  the skin slides most, four in a square on the head and four down the neck and the upper back;
  the gloves' 2 × 24 and the socks' 2 × 8, 108 in all.
- **What was left out,** the muscles surface EMG cannot reach and the places the body presses
  on, and the layouts tried.

| file | what is in it |
|---|---|
| [CONSTRUCTION.md](CONSTRUCTION.md) | the electrodes' rules; the modules and their counts; the IMUs' rules and places; the glove's and the sock's |
| [WHY.md](WHY.md) | what was left out, and why; the layouts tried |

What the electrodes, the strips and the harness are made of is under
[Rubaška](../rubaska/CONSTRUCTION.md); the modules and the glove under
[Rubaška's hardware](../rubaska/HARDWARE.md).

## Scale

| | modules | electrodes | IMUs |
|---|---|---|---|
| the body | 16: the head, the neck with the upper back, the two shoulders, the chest with the abdomen, the lower back, the two hips, and two on each limb | 496, 32 on a module of the body and on the head's, 16 on the neck's; a bias electrode on every module, 512 | 44 of 64 places |
| the gloves | one unit each, the hand's: an ADS1298 on the board | 2 × 17: sixteen and a bias | 2 × 24 |
| the socks | one each, the foot's | 2 × 17 | 2 × 8 |
