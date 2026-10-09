<div align="center">

# Kormilica: why not

**The graveyard:** what was considered for the computers' power and why it is not used.

↑ [Kormilica](README.md) · [NIC-Crazy_Ivan](../README.md)

</div>

---

Each entry says what it was and why it went, so that nobody digs it up without knowing.

- **The Raspberry Pi on its USB-C.** It takes 5.1 V on the header's pins 2 and 4 instead, from
  the LM61460 right at the header; without a USB-C supply that announces 5 A it holds its USB
  ports to 600 mA, which `usb_max_current_enable=1` lifts. The USB-C stays free for the HID
  gadget.
- **One of Mamka's rails for the Raspberry Pi.** None gives 5.1 V, and Mamka feeds her own
  children; Kormilica feeds the other boards from the battery.
- **The Hailo from the Raspberry Pi's PCIe connector.** It gives only ~1 A at 5 V; the module has
  a second LM61460 of its own at 3.3 V.
- **A pin of Mamka's for the Hailo's EN.** The Raspberry Pi's PCIE_PWR_EN says when a board on
  its PCIe connector may power up, so the module's 3.3 V follows that and nothing else.
- **Kormilica for a ROCK 5T,** with the eFuse for its DC jack and adapters for its Hailos. With
  a ROCK there is no header for her to sit on; [Terem](../terem/README.md), the board in the
  ROCK's two M.2 slots, carries the Hailos, their converters and the eFuse, and Kormilica stays
  the Raspberry Pi's.
