#!/usr/bin/env python3
"""Create BookOS Light Plasma Desktop Theme from cachyos-emerald-light."""
import gzip, os, re, shutil

SRC = "/usr/share/plasma/desktoptheme/cachyos-emerald-light"
DST = os.path.expanduser("~/.local/share/plasma/desktoptheme/bookos-light")

COLOR_MAP = {
    # Backgrounds
    "#232629": "#f2f2f7",
    "#1a1a1a": "#e5e5ea",
    "#31363b": "#1c1c1e",   # text/dark elements
    "#2e2e2e": "#1c1c1e",
    "#fcfcfc": "#ffffff",   # card bg
    "#eff0f1": "#f2f2f7",   # main bg
    "#dfdfdf": "#e5e5ea",
    "#d4d4d4": "#d1d1d6",
    "#c8c8c8": "#c7c7cc",
    "#a8a8a8": "#aeaeb2",
    "#666666": "#8e8e93",
    "#565656": "#636366",
    "#505050": "#48484a",
    # Accent
    "#3daee9": "#007aff",
    "#3DAEE6": "#007aff",
    "#3daee6": "#007aff",
    "#1E92FF": "#007aff",
    "#1a73e8": "#007aff",
    "#93cee9": "#5ac8fa",
    "#71dbff": "#32ade6",
    # Red / Green / Orange
    "#da4453": "#ff3b30",
    "#ef5350": "#ff3b30",
    "#27ae60": "#34c759",
    "#27ad60": "#34c759",
    "#f67400": "#ff9500",
    "#ffca28": "#ffcc00",
}
_SORTED = sorted(COLOR_MAP.items(), key=lambda x: len(x[0]), reverse=True)

COLORSCHEME_CLASSES = {
    "ColorScheme-Text":              "#000000",
    "ColorScheme-Background":        "#f2f2f7",
    "ColorScheme-Highlight":         "#007aff",
    "ColorScheme-HighlightedText":   "#ffffff",
    "ColorScheme-PositiveText":      "#34c759",
    "ColorScheme-NeutralText":       "#ffcc00",
    "ColorScheme-NegativeText":      "#ff3b30",
    "ColorScheme-ActiveText":        "#007aff",
    "ColorScheme-LinkText":          "#007aff",
    "ColorScheme-VisitedText":       "#5856d6",
    "ColorScheme-ViewText":          "#000000",
    "ColorScheme-ViewBackground":    "#ffffff",
    "ColorScheme-ViewHover":         "#5ac8fa",
    "ColorScheme-ViewFocus":         "#007aff",
    "ColorScheme-ButtonText":        "#000000",
    "ColorScheme-ButtonBackground":  "#e5e5ea",
    "ColorScheme-ButtonHover":       "#5ac8fa",
    "ColorScheme-ButtonFocus":       "#007aff",
    "ColorScheme-ComplementaryText": "#000000",
    "ColorScheme-ComplementaryBackground": "#e5e5ea",
    "ColorScheme-HeaderText":        "#000000",
    "ColorScheme-HeaderBackground":  "#f2f2f7",
}

_CS_PATTERN = re.compile(
    r'(\.' + r'|\.'.join(re.escape(k) for k in COLORSCHEME_CLASSES) + r')\s*\{([^}]+)\}',
    re.DOTALL
)

def fix_colorscheme_classes(text):
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

def recolor(data):
    text = data.decode("utf-8", errors="replace")
    for src, dst in _SORTED:
        text = re.sub(re.escape(src), dst, text, flags=re.IGNORECASE)
    text = fix_colorscheme_classes(text)
    return text.encode("utf-8")

def copy_file(src_path, dst_path):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    ext = os.path.splitext(src_path)[1].lower()
    if ext in (".svg", ".svgz"):
        try:
            with gzip.open(src_path, "rb") as f: data = f.read()
            data = recolor(data)
            with gzip.open(dst_path, "wb") as f: f.write(data)
        except (gzip.BadGzipFile, OSError):
            with open(src_path, "rb") as f: data = f.read()
            if data[:2] == b'\x1f\x8b':
                import io
                with gzip.open(io.BytesIO(data), "rb") as f: data = f.read()
                data = recolor(data)
                with gzip.open(dst_path, "wb") as f: f.write(data)
            else:
                data = recolor(data)
                with open(dst_path, "wb") as f: f.write(data)
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
BackgroundAlternate=229,229,234
BackgroundNormal=229,229,234
ForegroundInactive=142,142,147
ForegroundLink=0,122,255
ForegroundNegative=255,59,48
ForegroundNeutral=255,204,0
ForegroundNormal=0,0,0
ForegroundPositive=52,199,89
ForegroundVisited=88,86,214
DecorationFocus=0,122,255
DecorationHover=0,122,255

[Colors:Complementary]
BackgroundAlternate=229,229,234
BackgroundNormal=242,242,247
ForegroundInactive=142,142,147
ForegroundLink=0,122,255
ForegroundNegative=255,59,48
ForegroundNeutral=255,204,0
ForegroundNormal=0,0,0
ForegroundPositive=52,199,89
ForegroundVisited=88,86,214
DecorationFocus=0,122,255
DecorationHover=0,122,255

[Colors:Header]
BackgroundAlternate=229,229,234
BackgroundNormal=242,242,247
ForegroundInactive=142,142,147
ForegroundLink=0,122,255
ForegroundNegative=255,59,48
ForegroundNeutral=255,204,0
ForegroundNormal=0,0,0
ForegroundPositive=52,199,89
ForegroundVisited=88,86,214
DecorationFocus=0,122,255
DecorationHover=0,122,255

[Colors:Selection]
BackgroundAlternate=0,122,255
BackgroundNormal=0,122,255
ForegroundActive=255,255,255
ForegroundInactive=200,200,200
ForegroundLink=255,255,255
ForegroundNegative=255,59,48
ForegroundNeutral=255,204,0
ForegroundNormal=255,255,255
ForegroundPositive=52,199,89
ForegroundVisited=88,86,214

[Colors:Tooltip]
BackgroundAlternate=229,229,234
BackgroundNormal=242,242,247
ForegroundInactive=142,142,147
ForegroundLink=0,122,255
ForegroundNegative=255,59,48
ForegroundNeutral=255,204,0
ForegroundNormal=0,0,0
ForegroundPositive=52,199,89
ForegroundVisited=88,86,214

[Colors:View]
BackgroundAlternate=242,242,247
BackgroundNormal=255,255,255
ForegroundInactive=142,142,147
ForegroundLink=0,122,255
ForegroundNegative=255,59,48
ForegroundNeutral=255,204,0
ForegroundNormal=0,0,0
ForegroundPositive=52,199,89
ForegroundVisited=88,86,214
DecorationFocus=0,122,255
DecorationHover=0,122,255

[Colors:Window]
BackgroundAlternate=229,229,234
BackgroundNormal=242,242,247
ForegroundInactive=142,142,147
ForegroundLink=0,122,255
ForegroundNegative=255,59,48
ForegroundNeutral=255,204,0
ForegroundNormal=0,0,0
ForegroundPositive=52,199,89
ForegroundVisited=88,86,214
DecorationFocus=0,122,255
DecorationHover=0,122,255

[General]
ColorScheme=BookOS Light
Name=BookOS Light
shadeSortColumn=true

[KDE]
contrast=4

[WM]
activeBackground=242,242,247
activeBlend=0,122,255
activeForeground=0,0,0
inactiveBackground=229,229,234
inactiveBlend=142,142,147
inactiveForeground=142,142,147
"""

METADATA = """\
[AdaptiveTransparency]
enabled=true

[ContrastEffect]
contrast=0.9
enabled=true
intensity=0.35
saturation=1.2

[Desktop Entry]
Comment=BookOS Light - iOS-inspired light theme for Plasma
Name=BookOS Light
X-KDE-PluginInfo-Author=BookOS
X-KDE-PluginInfo-Category=Plasma Theme
X-KDE-PluginInfo-License=GPL3.0
X-KDE-PluginInfo-Name=bookos-light
X-KDE-PluginInfo-Version=1.0.0
X-Plasma-API=5.0
"""

def main():
    if os.path.exists(DST): shutil.rmtree(DST)
    processed = 0
    for root, dirs, files in os.walk(SRC):
        for name in files:
            src_path = os.path.join(root, name)
            dst_path = os.path.join(DST, os.path.relpath(src_path, SRC))
            if name == "metadata.desktop": continue
            try:
                copy_file(src_path, dst_path)
                processed += 1
            except Exception as e:
                print(f"  SKIP {os.path.relpath(src_path, SRC)}: {e}")
    with open(os.path.join(DST, "metadata.desktop"), "w") as f:
        f.write(METADATA)
    with open(os.path.join(DST, "colors"), "w") as f:
        f.write(COLORS_FILE)
    print(f"Done. {processed} files processed.")
    print(f"Theme: {DST}")

if __name__ == "__main__":
    main()
