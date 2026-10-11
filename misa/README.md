<div align="center">

# Míša

**The watchdog:** a radar and ultrasound watch for obstacles and warn through the headphones and
the headband.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

## What it does

Míša is a unit of its own on the forehead: a 60 GHz radar, an ultrasonic sensor and an IMU on
one board, with its own processor. It plugs into [Nataša](../natasa/HARDWARE.md#míšas-socket)
with four wires, builds a map of what is around the head and sends the whole map with every
frame. When an obstacle comes near, the headband buzzes on that side and Baťa beeps or speaks.

It serves two kinds of people:

- **the blind,**
- **anyone in VR glasses,** who does not see the room around them. The suit needs the sensors
  for this anyway.

Not every name has a board of its own: Soňa, Taťána and Nikita are software on Baťa only. Míša
has one because its sensors need it, and it keeps them off Nataša, who stays with the sound,
the buttons and the vibration.

## How much it helps

A blind person finds their way by hearing very well. When the people around behave normally
and talk, they need very little help. Míša is meant for the start, while a person learns, and
for critical situations, not as a constant guide.

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | the radar and the ultrasound, the board, the parts, the processor's pins, the radar beside the EMG |
| [SOFTWARE.md](SOFTWARE.md) | the sphere around the head, the errors and the ghosts, the data |
| [WHY.md](WHY.md) | what is not used, and why |
