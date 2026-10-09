<div align="center">

# Babuška

**The battery and its BMS, the backpack, and the power variants.**

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

*Babuška*, Russian for grandma, keeps the pantry, and everyone in the backpack eats from her.

The suit runs from a sodium-ion battery of **12 V** nominal.
[Mamka](../mamka/HARDWARE.md#converters) makes the suit's rails from it, **3.7 V** for the digital
parts and **6 V** for the analog parts, and each module brings them down itself; see
[Porjadok](../porjadok/HARDWARE.md#power), which also has the budget.
[Kormilica](../kormilica/README.md) feeds a Raspberry Pi its 5.1 V; [Terem](../terem/README.md)
feeds a ROCK 5T the battery as it is through an eFuse, and its Umnicas (see
[Baťa](../bata/README.md)).
Mamka also reads the BMS.

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | the energy the suit needs, the chemistry, the pack, the cells' limits, the BMS, the charging, the two power variants |
| [SOFTWARE.md](SOFTWARE.md) | what is written into the BMS: thresholds, the state of charge, the currents, the temperatures |
| [CONSTRUCTION.md](CONSTRUCTION.md) | the backpack: the shell, the insert, the one connector of the suit, the heat and the air |
| [WHY.md](WHY.md) | what is not used, and why |
