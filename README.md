# Ayo

A Python/Tkinter prank script. Opens 30 small image windows across the screen, shakes the active window (Linux/X11), and finally shows the image fullscreen.

**This is a prank. Run it only on your own machine or with the owner's permission.**

## What it does

1. Finds an image in the script's folder (`image.*` or the first file with a supported extension).
2. Tries to shake the active window via `xdotool`, if available and running X11.
3. Over 12 seconds, opens 30 small windows at random screen positions. Each lives for 1 second.
4. When all are closed, shows the image fullscreen.
5. Exit with Esc or by clicking the fullscreen image.

## Requirements

- Python 3.8+
- Tkinter
- Pillow (optional — for proper resizing)
- xdotool (optional, Linux/X11 only — for window shaking)

Install on Ubuntu/Debian:

sudo apt install python3-tk xdotool
pip install Pillow
text


On Arch:

sudo pacman -S tk xdotool python-pillow
text


On Fedora:

sudo dnf install python3-tkinter xdotool python3-pillow
text


On Windows and macOS it works, but without window shaking — `xdotool` isn't available there.

## Running

1. Put an image next to the script named `image.png` (or `.jpg`, `.gif`, `.bmp`, `.webp`).
2. `python3 ayo.py`
3. Esc to exit.

For testing, lower `WINDOWS_COUNT` to 3 and `LIFETIME_MS` to 300 first.

## Settings

All at the top of the file:

| Parameter | Default | Meaning |
|---|---|---|
| `WINDOWS_COUNT` | 30 | How many windows to open |
| `SMALL_SIZE` | 220 | Window size in pixels |
| `LIFETIME_MS` | 1000 | Window lifetime |
| `SPREAD_MS` | 12000 | Time over which to open them all |
| `SHAKE_POWER` | 30 | Shake amplitude |
| `SHAKE_INTERVAL_MS` | 30 | Shake interval |

## Compatibility

| System | Windows | Fullscreen | Shake |
|---|---|---|---|
| Linux X11 | yes | yes | yes, with xdotool |
| Linux Wayland | yes | yes | no |
| Windows | yes | yes | no |
| macOS | yes | yes | no |

On Wayland the script prints a warning and disables shaking on its own.

## How it works

- `find_image()` — locates the image.
- `load_photo()` — resizes via Pillow if available, otherwise via `PhotoImage.subsample`.
- `WindowShaker` — wrapper around `xdotool`: gets the active window and its coordinates, then every `SHAKE_INTERVAL_MS` shifts it by a random offset.
- `App` — creates a hidden root window, schedules window appearances via `root.after()`, and finally shows the fullscreen image.

Everything runs on a single Tkinter thread, no `threading`.

## License

MIT.

## Disclaimer

The script collects nothing, makes no network calls, and touches no files. At worst it annoys the user for a few seconds and gives them a jump scare with an image. Don't run it on people who aren't in on the joke.
