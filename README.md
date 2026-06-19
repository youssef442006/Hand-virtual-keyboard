# Virtual Hand-Gesture Keyboard (AR/EN)

A computer-vision based virtual keyboard that lets you type using **hand gestures** captured from your webcam. It uses **MediaPipe Hands** for finger tracking, a **pinch gesture** (or dwell/hover) to "press" keys, and **pynput** to send the actual keystrokes to whatever application currently has focus on your system. It supports both **English (QWERTY)** and **Arabic** keyboard layouts, with right-to-left text rendering and a built-in **word-suggestion** system for both languages.

---

## Features

- **Real-time hand tracking** using MediaPipe Hands (supports both hands simultaneously).
- **Two click modes**:
  - `PINCH` — tap a key by pinching your thumb and index finger together over it.
  - `DWELL` — hover over a key for a short period of time to select it.
- **Bilingual layouts**:
  - English QWERTY (lowercase / uppercase / numbers & symbols).
  - Arabic layout with its own numbers/symbols layout.
  - One-tap switching between `AR` ⇄ `EN` and `123` ⇄ `ABC`.
- **Shift & Caps Lock** support, including correct character mapping between the lower/upper/Arabic layouts.
- **Smart word suggestions**:
  - Matches the word you're currently typing against local English/Arabic dictionaries using Levenshtein (edit) distance.
  - Arabic matching normalizes common letter variants (e.g. `أ/إ/آ → ا`, `ى → ي`, `ة → ه`) and handles the `ال` (definite article) prefix.
  - Tap a suggestion to auto-complete the current word.
- **Right-to-left Arabic rendering** using `arabic-reshaper` + `python-bidi`, drawn with Pillow for proper glyph shaping.
- **On-screen text preview** showing what has been typed so far.
- **Audio click feedback** (Windows only, via `winsound`).
- **Real OS-level typing**: keystrokes are sent through `pynput`, so the virtual keyboard types into any focused window (text editor, browser, chat app, etc.), not just inside the camera preview.

---

## Requirements

- Python 3.8+
- A working webcam
- Windows is recommended (the default font path and the click-sound feature are Windows-specific — see [Platform Notes](#platform-notes))

### Python packages

```bash
pip install opencv-python mediapipe pynput numpy Pillow arabic-reshaper python-bidi
```

---

## Setup

Before running the script, you need to provide two things it expects on disk:

### 1. Word dictionaries (for suggestions)

The script loads two plain-text dictionary files:

```python
AR_WORDS = load_dictionary("D:/hand keyboard/arabic_words.txt")
EN_WORDS = load_dictionary("D:/hand keyboard/english_words.txt")
```

- Each file should contain one word per line (multiple words on the same line can also be separated by commas `,` or the Arabic comma `،`).
- **Update these two paths** to point to wherever you keep your dictionary files on your machine.
- If a file is missing, suggestions for that language simply won't appear — the script will keep running.

### 2. Font path

Arabic and Latin text is rendered with Pillow using this font:

```python
ARABIC_FONT_PATH = "C:/Windows/Fonts/tahoma.ttf"
DEFAULT_FONT_PATH = "C:/Windows/Fonts/tahoma.ttf"
```

Tahoma is used because it has solid Arabic glyph coverage. If you're not on Windows, or want a different font, point these constants to a `.ttf`/`.otf` font file that supports Arabic, on your system.

---

## Usage

```bash
python virtual_keyboard.py
```

1. A window opens showing your webcam feed with the virtual keyboard overlaid near the bottom.
2. **Click into the text field/app you actually want to type in first** (e.g. Notepad, a browser, a chat window) — the keyboard sends real keystrokes via `pynput`, so whatever window has OS focus is what receives the typed text.
3. Raise your hand(s) in front of the camera. Bring your **thumb and index finger together** (pinch) directly over a key to "press" it.
4. Word suggestions (if any match your dictionaries) appear in a row above the keyboard — pinch one to insert it and replace the current word fragment.
5. Press **`Esc`** or **`q`** (with the camera window focused) to quit.

### Gesture controls

| Action | Gesture |
|---|---|
| Press a key / suggestion | Pinch thumb + index finger over it (`PINCH` mode) |
| Press a key / suggestion | Hover over it for ~0.5s (`DWELL` mode) |
| Switch hands | Both left and right hands are tracked independently and can each interact with the keyboard |

### Special keys

| Key | Function |
|---|---|
| `Bksp` | Backspace |
| `Tab` | Tab |
| `Caps` | Toggle Caps Lock (switches between lower/upper layout) |
| `Shift` | One-shot Shift (capitalizes/maps the next key, then turns off) |
| `Enter` | Enter / new line |
| `Space` | Space bar |
| `123` / `ABC` | Toggle between letters and numbers/symbols layout |
| `AR` / `EN` | Switch between Arabic and English layouts |

---

## Configuration

Most behavior can be tuned by editing the constants near the top of the script:

| Constant | Purpose |
|---|---|
| `CLICK_MODE` | `'PINCH'` or `'DWELL'` selection method |
| `PINCH_DISTANCE_THRESHOLD` | Pixel distance below which fingers count as "pinching" |
| `DWELL_TIME_THRESHOLD` | Seconds of hovering required to trigger a dwell click |
| `COOLDOWN_TIME` | Minimum time between repeated presses of the same key |
| `HAND_MODEL_COMPLEXITY` | `0` (faster) or `1` (more accurate) MediaPipe model |
| `KEY_WIDTH_DEFAULT`, `KEY_HEIGHT`, `KEY_SPACING`, `KEYBOARD_START_X/Y` | Keyboard layout geometry |
| `FONT_SIZE_KEYS`, `FONT_SIZE_TEXT`, `FONT_SIZE_SUGGESTIONS` | Font sizes for keys, typed text, and suggestions |
| `SUGGESTIONS_MAX` | Maximum number of word suggestions shown at once |
| `USE_CLICK_SOUND`, `USE_HOVER_SOUND` | Enable/disable audio feedback |

---

## How the suggestion engine works

1. As you type, the script tracks the current "word fragment" (text since the last space/newline).
2. It detects whether that fragment is Arabic or Latin script.
3. It scores every word in the matching dictionary by **Levenshtein distance** to your fragment (with Arabic letters normalized first), keeping close matches (distance ≤ 1 for Arabic, ≤ 2 for English).
4. The closest matches are shown as tappable suggestion chips; selecting one deletes the current fragment (via simulated backspaces, if needed) and types the full word instead.

---

## Platform Notes

This project was originally written for **Windows**:

- `winsound` (used for the click sound) is Windows-only — sound is automatically disabled on macOS/Linux.
- The default Arabic/Latin font path points to `C:/Windows/Fonts/tahoma.ttf`.
- Dictionary file paths default to `D:/hand keyboard/...`.

To run on macOS/Linux:
- Remove or guard the `winsound` import/usage (already conditionally handled by `platform.system()`).
- Point `ARABIC_FONT_PATH` / `DEFAULT_FONT_PATH` to a font available on your system (e.g. `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf`, though it has limited Arabic support — a font like `Amiri` or `Noto Naskh Arabic` is recommended for Arabic text).
- Update the dictionary file paths accordingly.

---

## Known Limitations

- Hand-tracking accuracy depends on lighting, camera quality, and hand visibility.
- Since keystrokes are sent at the OS level via `pynput`, typing will go to **whatever window currently has focus** — make sure the right window is active before pinching.
- File paths for dictionaries and fonts are hardcoded and need to be adjusted per machine.
- The on-screen keyboard does not currently support resizing or repositioning at runtime.
- Designed and tested primarily for a single-monitor, single-webcam Windows setup.

---

## Project Structure

```
virtual_keyboard.py     # Main script (camera loop, hand tracking, keyboard UI, typing logic)
arabic_words.txt         # Arabic dictionary used for suggestions (user-provided)
english_words.txt        # English dictionary used for suggestions (user-provided)
```

---
