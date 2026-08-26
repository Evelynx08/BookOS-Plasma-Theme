#!/usr/bin/env python3
"""
Create BookOS Dark Plasma Desktop Theme from cachyos-emerald.
Handles both real .svgz (gzip) and plain .svg files with .svgz extension.
"""
import gzip
import os
import re
import shutil

SRC = "/usr/share/plasma/desktoptheme/cachyos-emerald"
DST = os.path.expanduser("~/.local/share/plasma/desktoptheme/bookos-dark")

# cachyos-emerald → BookOS Dark
COLOR_MAP = {
    # Backgrounds
    "#232629": "#000000",   # main bg
    "#1a1a1a": "#000000",   # very dark bg
    "#31363b": "#1c1c1e",   # card/surface
    "#2e2e2e": "#1c1c1e",   # alt surface
    "#313338": "#1c1c1e",   # discord-style bg
    "#36393e": "#1c1c1e",
    "#14171f": "#000000",
    "#161a23": "#000000",
    "#212329": "#0d0d0f",
    # Accent blue
    "#3daee9": "#0a84ff",
    "#3DAEE6": "#0a84ff",
    "#3daee6": "#0a84ff",
    "#1E92FF": "#0a84ff",
    "#1a73e8": "#0a84ff",
    "#1a92ff": "#0a84ff",
    "#93cee9": "#47a1ff",   # lighter blue
    "#71dbff": "#64d2ff",   # sky
    "#82afe6": "#5e9fff",
    # Text / light
    "#eff0f1": "#ffffff",
    "#EFF0F1": "#ffffff",
    "#fcfcfc": "#ffffff",
    "#FCFCFC": "#ffffff",
    "#dfdfdf": "#ebebf0",
    "#d4d4d4": "#c7c7cc",
    "#c8c8c8": "#aeaeb2",
    "#cbcbcb": "#aeaeb2",
    "#a8a8a8": "#8e8e93",
    "#a9a9a9": "#8e8e93",
    "#818181": "#636366",
    "#666666": "#48484a",
    "#565656": "#3a3a3c",
    "#505050": "#2c2c2e",
    "#3a3a3a": "#2c2c2e",
    "#363636": "#2c2c2e",
    "#5e5e5e": "#48484a",
    "#8b8b8b": "#636366",
    "#7B7C7E": "#636366",
    # Red
    "#da4453": "#ff453a",
    "#ff2a2a": "#ff453a",
    "#ef5350": "#ff453a",
    # Green
    "#27ae60": "#30d158",
    "#27ad60": "#30d158",
    "#26ad5f": "#30d158",
    "#2ecc71": "#32d74b",
    "#4caf50": "#30d158",
    # Orange / Yellow
    "#f67400": "#ff9f0a",
    "#ff6600": "#ff9f0a",
    "#ff9800": "#ff9f0a",
    "#ffca28": "#ffd60a",
    "#ffb54d": "#ff9f0a",
}

# Sort by length desc so longer patterns match first
_SORTED = sorted(COLOR_MAP.items(), key=lambda x: len(x[0]), reverse=True)

# After general recoloring, fix ColorScheme CSS classes to correct BookOS Dark values.
# These are used by Plasma as fallback/hint colors for SVG colorization.
COLORSCHEME_CLASSES = {
    "ColorScheme-Text":              "#ffffff",
    "ColorScheme-Background":        "#000000",
    "ColorScheme-Highlight":         "#0a84ff",
    "ColorScheme-HighlightedText":   "#ffffff",
    "ColorScheme-PositiveText":      "#30d158",
    "ColorScheme-NeutralText":       "#ffd60a",
    "ColorScheme-NegativeText":      "#ff453a",
    "ColorScheme-ActiveText":        "#0a84ff",
    "ColorScheme-LinkText":          "#0a84ff",
    "ColorScheme-VisitedText":       "#5a9fff",
    "ColorScheme-ViewText":          "#ffffff",
    "ColorScheme-ViewBackground":    "#000000",
    "ColorScheme-ViewHover":         "#47a1ff",
    "ColorScheme-ViewFocus":         "#0a84ff",
    "ColorScheme-ButtonText":        "#ffffff",
    "ColorScheme-ButtonBackground":  "#1c1c1e",
    "ColorScheme-ButtonHover":       "#47a1ff",
    "ColorScheme-ButtonFocus":       "#0a84ff",
    "ColorScheme-ComplementaryText": "#ffffff",
    "ColorScheme-ComplementaryBackground": "#0d0d0f",
    "ColorScheme-HeaderText":        "#ffffff",
    "ColorScheme-HeaderBackground":  "#1c1c1e",
}

_CS_PATTERN = re.compile(
    r'(\.' + r'|\.'.join(re.escape(k) for k in COLORSCHEME_CLASSES) + r')\s*\{([^}]+)\}',
    re.DOTALL
)

def fix_colorscheme_classes(text: str) -> str:
    def replacer(m):
        cls = m.group(1).lstrip('.')
        body = m.group(2)
        color = COLORSCHEME_CLASSES.get(cls)
        if not color:
            return m.group(0)
        body = re.sub(r'(?<=color:)#[0-9a-fA-F]{3,8}', color, body)
        body = re.sub(r'(?<=stop-color:)#[0-9a-fA-F]{3,8}', color, body)
        return f'.{cls} {{{body}}}'
    return _CS_PATTERN.sub(replacer, text)

def recolor(data: bytes) -> bytes:
    text = data.decode("utf-8", errors="replace")
    for src_color, dst_color in _SORTED:
        text = re.sub(re.escape(src_color), dst_color, text, flags=re.IGNORECASE)
    text = fix_colorscheme_classes(text)
    return text.encode("utf-8")

def copy_file(src_path: str, dst_path: str):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    ext = os.path.splitext(src_path)[1].lower()

    if ext in (".svg", ".svgz"):
        # Try gzip first, fall back to plain text
        try:
            with gzip.open(src_path, "rb") as f:
                data = f.read()
            data = recolor(data)
            with gzip.open(dst_path, "wb") as f:
                f.write(data)
        except (gzip.BadGzipFile, OSError):
            with open(src_path, "rb") as f:
                data = f.read()
            # Check if it's actually XML/SVG despite .svgz extension
            if data[:2] == b'\x1f\x8b':
                # Real gzip after all — re-raise shouldn't happen, but handle
                import io
                with gzip.open(io.BytesIO(data), "rb") as f:
                    data = f.read()
                data = recolor(data)
                with gzip.open(dst_path, "wb") as f:
                    f.write(data)
            else:
                data = recolor(data)
                with open(dst_path, "wb") as f:
                    f.write(data)
    else:
        shutil.copy2(src_path, dst_path)

COLORS_FILE = """\
[ColorEffects:Disabled]
Color=56,56,56
ColorAmount=0
ColorEffect=0
ContrastAmount=0.65
ContrastEffect=1
IntensityAmount=0.1
IntensityEffect=2

[ColorEffects:Inactive]
ChangeSelectionColor=true
Color=112,111,110
ColorAmount=0.025
ColorEffect=2
ContrastAmount=0.1
ContrastEffect=2
Enable=false
IntensityAmount=0
IntensityEffect=0

[Colors:Button]
BackgroundAlternate=28,28,30
BackgroundNormal=28,28,30
ForegroundInactive=142,142,147
ForegroundLink=10,132,255
ForegroundNegative=255,69,58
ForegroundNeutral=255,214,10
ForegroundNormal=255,255,255
ForegroundPositive=48,209,88
ForegroundVisited=90,159,255
DecorationFocus=10,132,255
DecorationHover=10,132,255

[Colors:Complementary]
BackgroundAlternate=28,28,30
BackgroundNormal=13,13,15
ForegroundInactive=142,142,147
ForegroundLink=10,132,255
ForegroundNegative=255,69,58
ForegroundNeutral=255,214,10
ForegroundNormal=255,255,255
ForegroundPositive=48,209,88
ForegroundVisited=90,159,255
DecorationFocus=10,132,255
DecorationHover=10,132,255

[Colors:Header]
BackgroundAlternate=13,13,15
BackgroundNormal=13,13,15
ForegroundInactive=142,142,147
ForegroundLink=10,132,255
ForegroundNegative=255,69,58
ForegroundNeutral=255,214,10
ForegroundNormal=255,255,255
ForegroundPositive=48,209,88
ForegroundVisited=90,159,255
DecorationFocus=10,132,255
DecorationHover=10,132,255

[Colors:Selection]
BackgroundAlternate=10,132,255
BackgroundNormal=10,132,255
ForegroundActive=255,255,255
ForegroundInactive=200,200,200
ForegroundLink=255,255,255
ForegroundNegative=255,69,58
ForegroundNeutral=255,214,10
ForegroundNormal=255,255,255
ForegroundPositive=48,209,88
ForegroundVisited=90,159,255

[Colors:Tooltip]
BackgroundAlternate=28,28,30
BackgroundNormal=28,28,30
ForegroundInactive=142,142,147
ForegroundLink=10,132,255
ForegroundNegative=255,69,58
ForegroundNeutral=255,214,10
ForegroundNormal=255,255,255
ForegroundPositive=48,209,88
ForegroundVisited=90,159,255

[Colors:View]
BackgroundAlternate=13,13,15
BackgroundNormal=0,0,0
ForegroundInactive=142,142,147
ForegroundLink=10,132,255
ForegroundNegative=255,69,58
ForegroundNeutral=255,214,10
ForegroundNormal=255,255,255
ForegroundPositive=48,209,88
ForegroundVisited=90,159,255
DecorationFocus=10,132,255
DecorationHover=10,132,255

[Colors:Window]
BackgroundAlternate=28,28,30
BackgroundNormal=0,0,0
ForegroundInactive=142,142,147
ForegroundLink=10,132,255
ForegroundNegative=255,69,58
ForegroundNeutral=255,214,10
ForegroundNormal=255,255,255
ForegroundPositive=48,209,88
ForegroundVisited=90,159,255
DecorationFocus=10,132,255
DecorationHover=10,132,255

[General]
ColorScheme=BookOS Dark
Name=BookOS Dark
shadeSortColumn=true

[KDE]
contrast=4

[WM]
activeBackground=0,0,0
activeBlend=10,132,255
activeForeground=255,255,255
inactiveBackground=13,13,15
inactiveBlend=142,142,147
inactiveForeground=142,142,147
"""

def make_metadata():
    return """\
[AdaptiveTransparency]
enabled=true

[ContrastEffect]
contrast=0.9
enabled=true
intensity=0.35
saturation=1.2

[Desktop Entry]
Comment=BookOS Dark - AMOLED black theme for Plasma
Name=BookOS Dark
X-KDE-PluginInfo-Author=BookOS
X-KDE-PluginInfo-Category=Plasma Theme
X-KDE-PluginInfo-Email=
X-KDE-PluginInfo-License=GPL3.0
X-KDE-PluginInfo-Name=bookos-dark
X-KDE-PluginInfo-Version=1.0.0
X-Plasma-API=5.0
"""

def main():
    if os.path.exists(DST):
        shutil.rmtree(DST)

    processed = 0
    skipped = 0
    for root, dirs, files in os.walk(SRC):
        for name in files:
            src_path = os.path.join(root, name)
            rel = os.path.relpath(src_path, SRC)
            dst_path = os.path.join(DST, rel)

            if name == "metadata.desktop":
                # Write our own
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                continue

            try:
                copy_file(src_path, dst_path)
                processed += 1
            except Exception as e:
                print(f"  SKIP {rel}: {e}")
                skipped += 1

    # Write metadata and colors
    with open(os.path.join(DST, "metadata.desktop"), "w") as f:
        f.write(make_metadata())
    with open(os.path.join(DST, "colors"), "w") as f:
        f.write(COLORS_FILE)

    print(f"Done. {processed} files processed, {skipped} skipped.")
    print(f"Theme at: {DST}")

if __name__ == "__main__":
    main()
