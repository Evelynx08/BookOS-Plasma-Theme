# BookOS Plasma Theme

Color schemes for KDE Plasma with the BookOS aesthetic (inspired by Apple system colors). Available in **Dark** and **Light** modes, with 6 accents: **blue, red, green, purple, orange, pink**.

## Contents

- `color-schemes/` — 12 `.colors` files (6 colors × 2 modes)
- `color-schemes/_generate.py` — script that regenerates variants from the baseline `BookOSDark.colors` / `BookOSLight.colors`
- `install.sh` — installer with flags
- `theme-plasma/` — Python scripts to regenerate the full Plasma desktoptheme (not required to use the color schemes)

## Quick install

```bash
git clone https://github.com/Evelynx08/BookOS-Plasma-Theme.git
cd BookOS-Plasma-Theme
./install.sh --all
```

Then activate from **System Settings → Colors**.

## Installer usage

```bash
./install.sh [options]
```

### Color flags
Pick one or more. Default: `--blue`.

| Flag | Color |
|------|-------|
| `--blue` | Blue (default) |
| `--red` | Red |
| `--green` | Green |
| `--purple` | Purple |
| `--orange` | Orange |
| `--pink` | Pink |

### Mode flags
Pick one or both. Default: both.

| Flag | Mode |
|------|------|
| `--dark` | Dark only |
| `--light` | Light only |

### Other flags

| Flag | Description |
|------|-------------|
| `--all` | Install all 12 schemes (every color, both modes) |
| `--system` | Install system-wide to `/usr/share/color-schemes` (requires `sudo`) |
| `--force` | Overwrite without asking |
| `-h`, `--help` | Show help |

### Examples

```bash
./install.sh --blue --dark              # only BookOS Dark Blue
./install.sh --red --green              # red and green, both modes
./install.sh --purple --orange --light  # purple and orange, light only
./install.sh --all                      # all 12 schemes
./install.sh --all --force              # all, no prompts
sudo ./install.sh --all --system        # system-wide for all users
```

## Activation

1. Open **System Settings → Colors**
2. Find the scheme (e.g. `BookOS Dark Blue`)
3. Click to apply

## Regenerate variants

If you modify the baseline (`~/.local/share/color-schemes/BookOSDark.colors` or `BookOSLight.colors`):

```bash
python3 color-schemes/_generate.py
```

This regenerates the 12 `.colors` files in `color-schemes/`.

## Uninstall

```bash
rm ~/.local/share/color-schemes/BookOS*.colors
# or with sudo if installed system-wide:
sudo rm /usr/share/color-schemes/BookOS*.colors
```

## Requirements

- KDE Plasma 5 or 6
- Bash
- Python 3 (only to regenerate variants)

## License

GPL-3.0
