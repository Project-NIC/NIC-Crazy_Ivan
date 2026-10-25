<div align="center">

# Nikita

**Rhythm you can feel:** the beat of the music as vibration, for dancing and learning to dance.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

## What it does

A deaf person does not hear the music, and someone leading them has to keep giving the beat by
hand. Nikita gives it instead: [Nataša](../natasa/README.md)'s headband vibrates on the beat.

- **On the beat, not after it.** Finding the beats in music is a classic task with open
  libraries, and it runs on the processor in real time. Nikita predicts the next beat and
  vibrates on it; a pulse that only reacts would come late.
- **The one.** The first beat of the bar, the "one" of a waltz, gets a stronger or longer
  pulse. Standard dances are counted from it.
- **By the style of the music.** Nikita follows the instrument that carries the beat in that
  style: the bass drum low down, the hi-hat high up.

**BeatNet** does the tracking (Heydari, Cwitkowitz and Duan, ISMIR 2021, arXiv 2108.03576):
convolutional and recurrent layers that look only at what has sounded already, and two particle
filters that follow the beat, the downbeat and the metre together, with no time signature given
in advance. It has a mode that listens to a microphone. The downbeat is the "one". It runs on
Baťa's processor, with no NPU and no Hailo.

Nikita is in Russian a man's name, which suits dancing: it can lead and follow.

## Open questions

- BeatNet in real time on one A76 core, beside the other assistants,
- the delay from the music to the pulse, and how far ahead to predict,
- the music from Baťa himself, or from the room through the microphones.
