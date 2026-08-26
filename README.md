# BookOS Plasma Theme

KDE Plasma theme with the BookOS aesthetic (inspired by Apple system colors). Pre-built and ready to install — works on any KDE distro (Fedora, Ubuntu, Arch, etc.) with no build dependencies.

Available in **Dark** and **Light** modes, with 6 accents: **blue, red, green, purple, orange, pink** (12 variants total).

## What gets installed

1. **Color schemes** — window/button/widget colors (`.colors` files)
2. **Plasma desktopthemes** — panel, system tray, dialogs, widgets

Both are independent — you can install one or the other.

## Contents

- `color-schemes/` — 12 `.colors` files
- `desktoptheme/` — 12 pre-built Plasma desktopthemes
- `install.sh` — installer
- `theme-plasma/_generate_all.py` — regenerates all 12 desktopthemes from `cachyos-emerald` (only needed by maintainers)

## Quick install

```bash
git clone https://github.com/Evelynx08/BookOS-Plasma-Theme.git
cd BookOS-Plasma-Theme
./install.sh --all
```

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

### Component flags
By default both are installed.

| Flag | Description |
|------|-------------|
| `--schemes-only` | Install only color schemes |
| `--desktoptheme-only` | Install only Plasma desktopthemes |

### Other flags

| Flag | Description |
|------|-------------|
| `--all` | Install every color and mode (12 of each component) |
| `--system` | Install system-wide to `/usr/share` (requires `sudo`) |
| `--force` | Overwrite without asking |
| `-h`, `--help` | Show help |

### Examples

```bash
./install.sh --blue --dark              # Dark Blue only
./install.sh --red --green              # red and green, both modes
./install.sh --all                      # all 12 variants of both components
./install.sh --all --schemes-only       # all color schemes, no desktoptheme
./install.sh --purple --orange --light  # purple and orange, light mode
sudo ./install.sh --all --system        # system-wide for all users
```

## Activation

- **Colors:** System Settings → Colors → pick `BookOS Dark Blue` (or whichever)
- **Desktoptheme:** System Settings → Plasma Style → pick `BookOS Dark Blue` (or whichever)

## Uninstall

```bash
# user-level
rm ~/.local/share/color-schemes/BookOS*.colors
rm -rf ~/.local/share/plasma/desktoptheme/BookOS-*

# system-wide
sudo rm /usr/share/color-schemes/BookOS*.colors
sudo rm -rf /usr/share/plasma/desktoptheme/BookOS-*
```

## Requirements

- KDE Plasma 5 or 6
- Bash

## Regenerate (maintainers only)

Requires `/usr/share/plasma/desktoptheme/cachyos-emerald` as source:

```bash
python3 theme-plasma/_generate_all.py
```

Output goes to `desktoptheme/`.

## License

GPL-3.0
