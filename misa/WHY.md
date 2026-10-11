<div align="center">

# Míša: why not

**The graveyard:** what was considered for the obstacle sensors and why it is not used.

↑ [Míša](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Each entry says what it was and why it went, so that nobody digs it up without knowing.

| ruled out | why |
|---|---|
| HC-SR04 and other hobby modules | large, 5 V |
| CH201 | 1.8 V only and I2C: for four sensors 13 wires against 9, and translators |
| ICU-10201 | 1.25 m at most |
| a ring of ultrasonic sensors as the main sensor | a distance without an angle; a map hanging on the gyro; a wide beam sees the floor |
| an ultrasonic array of our own, angles from arrival times | the ICU-20201 does not listen to another's pulse; matching echoes between receivers makes ghosts; a research project |
| Toposens ECHO ONE, a 3D ultrasonic sensor | 2.2 W, a box for robots with a processing unit of its own |
| optical time of flight | glass |
| IWR6843AOP, and Mistral's module with it | 1.2–1.75 W on average and a heat plate; 15 × 15 mm; the module wants 5 V |
| Jorjin MT5C01-02R1 | 6 m: its transmitter is turned down 10 dB for certification |
| raw radar data: Acconeer A121, Infineon BGT60TR13C | ~10 MB/s and the FFTs on the host |
| a bare IWRL6432AOP on our own board | the RF layout, crystal and flash, which the module brings; kept as the fallback should the module not be sold in small numbers |
| fields of 5° | the radar resolves ~30°; smaller fields make ghosts |
| a compass against the gyro's drift | steel and cars upset it |
| a lidar with a 3D map (Livox Mid-360, Unitree L2) | SLAM wants a Raspberry Pi or a Jetson and a big battery |
| SAR, a 3D model of a hall | the antenna's size sets the resolution; the radar's position to tenths of a millimetre; a sheet-metal hall mirrors |
| recognising goods on a shelf | a phone app for the blind does it: Seeing AI, Be My Eyes |
