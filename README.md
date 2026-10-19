# Pokémon Box Patcher

A Python script that patches your own copy of **Pokémon Box: Ruby & Sapphire** (GameCube, NTSC-U and PAL) so that:

- **Adventure Mode** works with **Pokémon FireRed, LeafGreen and Emerald**, with saving that works, as well as Ruby and Sapphire
- the **Universal Version** changes are built in (see below)

The script contains only patch data. It includes no game files or ROMs: you supply your own Pokémon Box disc image and your own ROM dumps.

---

## Features

- **Universal Patch:** the Box-side changes from WindyPrairie's Universal Version are always applied:
  - You can withdraw Pokémon without having 100 Pokédex entries.
  - The story-progress restriction is removed.
  - USA only: Ruby and Sapphire in any language are accepted.

  USA discs can be the original or ones that already have the Universal Version applied. The result is the same either way.

- **Adventure Mode support** *(optional)* adds FireRed, LeafGreen and/or Emerald to Adventure Mode:
  - The game runs from the ROM stored on the disc, and your progress is saved to the cartridge connected by GBA link, just like Ruby and Sapphire.
  - Add only the games you want; each ROM is optional.
  - Emerald is stored in a packed form, so it uses less disc space and memory.
  - PAL only: the GBA frame textures are compressed. This frees enough memory for Emerald to run, and the frame looks slightly less sharp.

- **Your original ISO is never changed.** The patcher writes a new, full-size ISO.

---

## Requirements

- **Python 3.8 or newer.**
  - Windows: install it from [python.org](https://www.python.org/downloads/), or with `winget install Python.Python.3.12`.
  - macOS and Linux: Python 3 is usually already installed.
- **A Pokémon Box Ruby & Sapphire disc image** (`.iso`) dumped from your own disc:

  | Region | Game ID | Accepted |
  |---|---|---|
  | NTSC-U (USA) | `GPXE01` | Original, or with the Universal Version patch applied |
  | PAL (Europe/Australia) | `GPXP01` | Original |

- **For Adventure Mode** *(optional)*: your own **full 16 MB ROM dumps** of FireRed, LeafGreen and/or Emerald, in the right language for your disc:

  | Disc | Accepted ROM languages | Game codes |
  |---|---|---|
  | USA | English | `BPRE` (FireRed), `BPGE` (LeafGreen), `BPEE` (Emerald) |
  | PAL | English, French, Italian, German, Spanish | `BPRx`, `BPGx`, `BPEx`, where `x` is `E`, `F`, `I`, `D` or `S` |

- **To play Adventure Mode:** the matching **GBA cartridge** connected with a GBA link cable, as with Ruby and Sapphire. Your save is read from and written to that cartridge. In Dolphin, use its emulated GBA loaded with the same game and save.
- **About 1.5 GB of free disk space** for the new ISO.

---

## How to use it

1. Download `box_frlg_e_patcher.py`.
2. Double-click it, or run `py box_frlg_e_patcher.py` (`python3 box_frlg_e_patcher.py` on macOS or Linux).
3. Drag each file onto the window when asked and press Enter. Press Enter on a ROM question to skip that game.

   ```
   Pokemon Box ISO (USA or PAL):
   FireRed ROM   (optional, Enter to skip):
   LeafGreen ROM (optional, Enter to skip):
   Emerald ROM   (optional, Enter to skip):
   Output ISO [<name> (FRLGE).iso]:
   ```

4. Wait for `Done`, then load the new ISO in your loader or in Dolphin.

### Command line

```
py box_frlg_e_patcher.py BOX.iso OUT.iso [--firered FR.gba] [--leafgreen LG.gba] [--emerald E.gba]
```

Examples:

```
py box_frlg_e_patcher.py "Pokemon Box.iso" "Pokemon Box (FRLGE).iso" --firered FireRed.gba --leafgreen LeafGreen.gba --emerald Emerald.gba
py box_frlg_e_patcher.py "Pokemon Box.iso" "Pokemon Box (Universal).iso"
```

The second example adds no ROMs, so it only applies the Universal changes.

---

### Not yet confirmed

- **Emerald's clock:** time-based events in Emerald (berry growth, daily events, tides) haven't been tested during Adventure Mode.
- **Trainer Tower and Trainer Hill records:** FireRed and LeafGreen's Trainer Tower records, and Emerald's Trainer Hill and recorded battles, are kept in a separate part of the save. They're left untouched on the cartridge, but haven't been tested with saves that contain them.

---

## Troubleshooting

| Message | What to do |
|---|---|
| `Not a supported Pokemon Box disc (game ID …)` | Use an image of Pokémon Box Ruby & Sapphire, `GPXE01` (USA) or `GPXP01` (PAL). |
| `gbarom.arc doesn't match a supported … disc` | Your disc has been changed by another mod, or it's a PAL disc with the Universal patch applied. Start from a clean dump. |
| `game code is '…'; the … disc needs one of: …` | The ROM is the wrong game or the wrong language for your disc's region. |
| `ROM too small … expected a full 16 MB dump` | The ROM is trimmed or incomplete. Use a full dump. |
| `Warning: this Emerald needs … KB of extra memory` | PAL only: that Emerald dump may not run. Try a clean, unmodified Emerald dump. |
| `Note: your Start.dol/gbarom.arc differ from the author's elsewhere` | Something else has changed your disc files. Patching continued, but if anything misbehaves, start from a clean dump. |

---

## Credits

- **[WindyPrairie](https://projectpokemon.org/home/files/file/4950-pokemon-box-ruby-sapphire-universal-version/)**, creator of the Pokémon Box Universal Version patch. The Universal changes included here are their work.

---

## Important

**Always back up your save files** before using Adventure Mode. Copy your cartridge's save with a save backup device, or keep a copy of your `.sav` if you're using Dolphin.

Use your own legally obtained game dumps. This tool is only for patching your own copies of the games, and it is not affiliated with Nintendo, The Pokémon Company or Game Freak.
