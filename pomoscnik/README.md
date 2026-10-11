<div align="center">

# Pomoščnik

**The helper at your elbow:** looks at what you look at, reads its marking and finds it for you.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

*Pomoščnik* is Russian for a helper. You hold a part in front of you, a chip, a bearing, a fuse,
and say "find it"; Pomoščnik reads the number on it, looks it up and shows what it found in the
glasses or reads it into your ears. It is software only: everything it needs is in the suit
already.

## What it uses

- **The eyes:** Ďaďa Sem's two cameras, on the glasses or the headband (see
  [Baťa](../bata/HARDWARE.md#ďaďa-sem)).
- **The ears and the voice:** Nataša's microphones and headphones (see
  [Nataša](../natasa/README.md)), or the glasses' own; the speech recognition and the voice are
  Taťána's (see [Taťána](../tatana/README.md)).
- **The hands:** the gloves point and confirm, so nothing has to follow your eyes (see
  [Rubaška](../rubaska/HARDWARE.md#the-glove-and-the-foot)).
- **The picture:** the glasses on Deduška's USB-C, or on Baťa's while the suit is not a keyboard
  for another computer, the two using the same port (see
  [Baťa](../bata/SOFTWARE.md#output-modes)).

## How it goes

1. **The request:** "find it", heard by Taťána's recognition, or a gesture of the gloves.
2. **The marking:** the text in one still found and read (OCR) by PaddleOCR's **PP-OCRv5
   mobile**, its detection and its recognition (the recognition ~16 MB, PaddleOCR's
   documentation), on Baťa's processor: one picture at a request needs no NPU. For small
   markings Pomoščnik takes the still at the camera's full resolution instead of the 640 × 480
   stream. Should it be slow, the detection, all convolutions, goes to the RK3588's NPU through
   Teflon.
3. **The search:** the number looked up on the internet, through a connection the backpack does
   not have of its own: a phone's hotspot, over USB or Wi-Fi.
4. **The answer:** in the glasses, or read aloud.

**"What is it"** goes further than a marking: a thing in front of the camera, named and
explained. That wants a model that understands a picture and speech together (a VLM): on the
second Umnica in the brutal fitting, where Hailo lists Qwen2-VL-2B and Qwen3-VL-2B for the
Hailo-10H (see [Baťa](../bata/HARDWARE.md#umnica)), or online through the same connection.

## A lighter build

If anyone wants Pomoščnik without the suit, the core stays the same and the rest is left off:
the backpack with Mamka and Baťa, two sleeves with the gloves on IMUs only, a sensing module's
board without its ADS1299 (no new board), markers on the gloves that the cameras see to correct
the IMUs' drift, and the head's turn from an IMU on the headband, or the glasses' own if it can
be read over USB. Nothing of it is drawn; it is only an option.

## Open questions

- how long PP-OCRv5 mobile takes for one still on the A76 cores: PaddleOCR gives ~1.75 s an
  image on a server's Xeon, so a few seconds here (an estimate),
- whether the camera's full resolution reads a chip's marking at arm's length,
- the internet connection, and what the search uses,
- what the glasses show, which waits on DisplayPort over the ROCK 5T's USB-C in mainline.
