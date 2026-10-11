<div align="center">

# Soňa

**For the deaf:** listens all the time and tells by vibration what is happening around.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

## What it does

Soňa, as in sound, listens to the surroundings through the microphones in
[Nataša](../natasa/README.md). When a sound that matters comes up, a siren or a doorbell,
Nataša's headband vibrates. Soňa is only software on Baťa.

## Recognising the sounds

Recognising sounds is a solved task with ready models. YAMNet, for one, recognises 521 of the
527 classes of Google's AudioSet and is built on MobileNet v1, a network made for phones. Its
classes include:

| kind | AudioSet classes |
|---|---|
| danger | Police car (siren), Ambulance (siren), Fire engine, fire truck (siren), Civil defense siren, Smoke detector, smoke alarm, Fire alarm, Car alarm |
| attention | Vehicle horn, car horn, honking, Doorbell, Baby cry, infant cry |

The list of classes is in the
[YAMNet repository](https://github.com/tensorflow/models/tree/master/research/audioset/yamnet).

**YAMNet as it is, on the processor.** It takes 16 kHz mono and has 3.7 million weights, 69.2
million multiplies for each 0.96 s of sound (its repository), a small part of one of the A76
cores Baťa keeps for the assistants (see [Baťa](../bata/SOFTWARE.md#cores-on-the-rock-5t)). It
needs no NPU and no Hailo, so a smaller model trained for the classes above is not needed; each
class gets a threshold of its own.

Each kind of sound gets its own vibration pattern, set by the user: a long vibration for danger
and a short one for attention, for example. The motors and the patterns are described under
[Nataša](../natasa/HARDWARE.md#vibration).

## Open questions

- each class's threshold, set on recordings of real sirens, bells and alarms,
- the time from the sound to the vibration: a frame is 0.96 s, so about a second (an estimate),
- the patterns: which tell apart best on the head.
