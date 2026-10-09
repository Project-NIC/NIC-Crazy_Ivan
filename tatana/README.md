<div align="center">

# Taťána

**Writes and reads:** types what you dictate and reads text aloud, books included.

↑ [NIC-Crazy_Ivan](../README.md)

</div>

---

Like Tatiana in *Eugene Onegin*, Taťána writes letters.

## Dictation

- You click where the text should go. Once the cursor blinks, you speak.
- Speech recognition runs on Baťa: whisper.cpp, a version of OpenAI's Whisper,
  runs on the ROCK 5T and the Raspberry Pi alike. How well small models take Czech has to be
  tried. Czech will likely need at least the small model, and whether it keeps up in real time
  on the cores the assistants share is to be tried too.
- The text goes out in the suit's HID mode (see [Baťa](../bata/SOFTWARE.md#output-modes)): into
  Deduška over the cable, or into any other computer as a USB keyboard, wherever the cursor is,
  in a word processor or anywhere else. Nothing is installed on the other computer.
- **The keyboard layout:** a USB keyboard sends the codes of keys, not letters; the other
  computer turns them into letters by its own layout. Czech letters (ě, š, č, ř, ž, ů…) come out
  right only when it has the Czech layout set, and Taťána types for that layout.

## Reading aloud

- Text to speech runs on Baťa with no internet: Piper, a neural speech synthesizer
  that runs in real time even on a Raspberry Pi 4, has a Czech voice (Jirka).
- **Books:** a book in plain text takes hundreds of kilobytes, a few megabytes at most, so a
  library of thousands fits on the card. You choose a folder and start a book by voice, and
  Taťána carries on where it stopped.
- **The computer's screen:** a keyboard can only write, so the HID mode cannot read the screen.
  That needs the computer's side: its own screen reader, or, with the whole suit, the glasses and
  a second computer, the two systems linked, so the suit both controls the computer and reads
  from it.

## Open questions

- the recognition model, and how well it takes Czech,
- voice commands for the library,
- the link to a second computer for reading its screen.
