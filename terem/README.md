<div align="center">

# Terem

**The chamber under the ROCK 5T:** one board in both of its M.2 slots, with the two Umnicas and
a supply for each.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

*Terem* is Russian for the upper chamber of an old house, where the daughters lived. Umnica,
the clever daughter, has hers here: a Hailo-10H in each of its two sockets, each with a
converter of its own, so neither leans on the ROCK's one 3.3 V. The board plugs into both M.2
slots on the ROCK 5T's underside at once and takes the battery through one connector. The ROCK
itself is fed through its eFuse on [Mamka](../mamka/HARDWARE.md#the-computers-supply), so a suit
without the Hailos, which runs its model on the RK3588's own NPU, has no Terem at all, and
Borovičok, who has no Umnica, has none either.

Nothing bought does the ROCK's part: the adapters sold for a short module in a long slot are
passive brackets or boards that pass the slot's own 3.3 V on, and the powered adapters all go the
other way, from an M.2 slot to a PCIe card with a power plug. An M.2 slot always has 3.3 V, so
nobody has needed a powered one (see [WHY.md](WHY.md)).

| file | what is in it |
|---|---|
| [HARDWARE.md](HARDWARE.md) | the board in the two slots, the sockets and the converters, what goes to Mamka |
| [CONSTRUCTION.md](CONSTRUCTION.md) | the board: four layers at 0.8 mm, the pairs, the converters' layout, the heights, what to watch |
| [WHY.md](WHY.md) | what is not used, and why |
