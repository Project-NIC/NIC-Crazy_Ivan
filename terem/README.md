<div align="center">

# Terem

**The chamber under the ROCK 5T:** one board in both of its M.2 slots, with the two Umnicas,
a supply for each, and the eFuse that feeds the ROCK itself.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

*Terem* is Russian for the upper chamber of an old house, where the daughters lived. Umnica,
the clever daughter, has hers here: a Hailo-10H in each of its two sockets, each with a
converter of its own, so neither leans on the ROCK's one 3.3 V. The board plugs into both M.2
slots on the ROCK 5T's underside at once, takes the battery through one connector, and carries
the eFuse for the ROCK's DC jack, so that with a ROCK there is no
[Kormilica](../kormilica/README.md) and no cable but the battery's and the DC jack's. Deduška,
a second ROCK, gets a Terem of his own.

Umnica's chamber has two forms, by the computer:

| computer | Terem | where it is described |
|---|---|---|
| ROCK 5T | the board here, in both M.2 slots, with two 2242 modules, a converter each and the eFuse | [HARDWARE.md](HARDWARE.md) |
| Raspberry Pi 5 | the M.2 socket, its 3.3 V and the PCIe FFC on Kormilica's wing, one 2280 module | [Kormilica](../kormilica/HARDWARE.md#the-hailo-10h) |

Nothing bought does the ROCK's part: the adapters sold for a short module in a long slot are
passive brackets or boards that pass the slot's own 3.3 V on, and the powered adapters all go the
other way, from an M.2 slot to a PCIe card with a power plug. An M.2 slot always has 3.3 V, so
nobody has needed a powered one (see [WHY.md](WHY.md)).

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | the board in the two slots, the sockets and the converters, the eFuse, what goes to Mamka |
| [CONSTRUCTION.md](CONSTRUCTION.md) | the board: four layers at 0.8 mm, the pairs, the converters' and the eFuse's layout, the heights, what to watch |
| [WHY.md](WHY.md) | what is not used, and why |
