#!/usr/bin/env python3
"""Generate BookOS-App Aurorae window decoration themes.

Mimics the titlebar buttons used in BookOS apps (Settings, Notepad, Clock):
- Square-ish rounded buttons (radius ~6)
- Monochrome glyphs (no macOS red/yellow/green circles)
- Translucent hover background
- Buttons on the RIGHT (LeftButtons empty, RightButtons=IAX)

Outputs to ../aurorae/themes/BookOS-App-{Dark,Light}/
"""
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.path.join(HERE, "themes")

MODES = {
    "Dark": {
        "fg":         "#ffffff",
        "fg_dim":     "rgba(255,255,255,0.55)",
        "hover_bg":   "rgba(255,255,255,0.12)",
        "pressed_bg": "rgba(255,255,255,0.20)",
        "active_text":   "255,255,255",
        "inactive_text": "142,142,147",
    },
    "Light": {
        "fg":         "#000000",
        "fg_dim":     "rgba(0,0,0,0.55)",
        "hover_bg":   "rgba(0,0,0,0.08)",
        "pressed_bg": "rgba(0,0,0,0.16)",
        "active_text":   "0,0,0",
        "inactive_text": "142,142,147",
    },
}

# 5-state Aurorae SVG layout: active, hover, pressed, inactive, deactivated.
# Each state is a 30x30 slot side by side -> 150x30 viewBox.
SLOT_W = 30
SLOTS = ["active", "hover", "pressed", "inactive", "deactivated"]
SVG_W = SLOT_W * len(SLOTS)

# Square button background centred in slot
BTN_SIZE = 22
BTN_RADIUS = 6
BTN_OFFSET = (SLOT_W - BTN_SIZE) // 2  # 4

def slot_x(i: int) -> int:
    return i * SLOT_W

def bg_rect(i: int, fill: str) -> str:
    x = slot_x(i) + BTN_OFFSET
    y = BTN_OFFSET
    return (f'<rect x="{x}" y="{y}" width="{BTN_SIZE}" height="{BTN_SIZE}" '
            f'rx="{BTN_RADIUS}" ry="{BTN_RADIUS}" fill="{fill}"/>')

def glyph_group(i: int, glyph: str, color: str, opacity: float) -> str:
    cx = slot_x(i) + SLOT_W // 2
    cy = SLOT_W // 2
    return (f'<g transform="translate({cx},{cy})" stroke="{color}" '
            f'stroke-width="1.4" stroke-linecap="round" fill="none" '
            f'opacity="{opacity}">{glyph}</g>')

# Glyphs (centred on 0,0)
GLYPH_CLOSE     = '<path d="M -3.5 -3.5 L 3.5 3.5 M 3.5 -3.5 L -3.5 3.5"/>'
GLYPH_MINIMIZE  = '<path d="M -4 0 L 4 0"/>'
GLYPH_MAXIMIZE  = '<rect x="-3.5" y="-3.5" width="7" height="7" rx="1" ry="1"/>'
GLYPH_RESTORE   = ('<rect x="-4" y="-2" width="6" height="6" rx="1" ry="1"/>'
                   '<rect x="-2" y="-4" width="6" height="6" rx="1" ry="1" fill="none"/>')
GLYPH_ABOVE     = '<path d="M -3.5 1.5 L 0 -2 L 3.5 1.5"/>'
GLYPH_BELOW     = '<path d="M -3.5 -1.5 L 0 2 L 3.5 -1.5"/>'
GLYPH_SHADE     = '<path d="M -4 -1 L 4 -1 M -3 2 L 3 2"/>'
GLYPH_ALLDESK   = ('<circle r="3" cx="0" cy="0" stroke-width="1.2"/>'
                   '<circle r="1" cx="0" cy="0" fill="currentColor" stroke="none"/>')

GLYPHS = {
    "close":       GLYPH_CLOSE,
    "minimize":    GLYPH_MINIMIZE,
    "maximize":    GLYPH_MAXIMIZE,
    "restore":     GLYPH_RESTORE,
    "keepabove":   GLYPH_ABOVE,
    "keepbelow":   GLYPH_BELOW,
    "shade":       GLYPH_SHADE,
    "alldesktops": GLYPH_ALLDESK,
}

def build_svg(name: str, theme: dict) -> str:
    glyph = GLYPHS[name]
    fg     = theme["fg"]
    fg_dim = theme["fg_dim"]
    hover  = theme["hover_bg"]
    press  = theme["pressed_bg"]

    parts = [
        f'<?xml version="1.0" encoding="UTF-8" standalone="no"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_W}" height="{SLOT_W}" viewBox="0 0 {SVG_W} {SLOT_W}">',
        # active: no bg, glyph at full color, opacity 0.6 (matches BookOS apps)
        f'<g id="active-center">{glyph_group(0, glyph, fg, 0.7)}</g>',
        # hover: translucent bg + glyph opacity 1
        f'<g id="hover-center">{bg_rect(1, hover)}{glyph_group(1, glyph, fg, 1.0)}</g>',
        # pressed: stronger bg + glyph opacity 1
        f'<g id="pressed-center">{bg_rect(2, press)}{glyph_group(2, glyph, fg, 1.0)}</g>',
        # inactive: dim glyph, no bg
        f'<g id="inactive-center">{glyph_group(3, glyph, fg, 0.35)}</g>',
        # deactivated (button disabled): very dim
        f'<g id="deactivated-center">{glyph_group(4, glyph, fg, 0.18)}</g>',
        '</svg>',
    ]
    return "\n".join(parts)

def build_rc(theme: dict) -> str:
    return f"""[General]
ActiveTextColor={theme['active_text']}
Animation=120
InactiveTextColor={theme['inactive_text']}
LeftButtons=M
RightButtons=IAX
Shadow=true
TextShadowOffsetX=0
TextShadowOffsetY=0
TitleAlignment=Center
TitleVerticalAlignment=Center
UseTextShadow=false
HaloActive=false
HaloInactive=false

[Layout]
ButtonHeight=22
ButtonWidth=22
ButtonMarginTop=7
ButtonSpacing=2
ExplicitButtonSpacer=8
PaddingBottom=8
PaddingLeft=8
PaddingRight=8
PaddingTop=8
TitleEdgeBottom=6
TitleEdgeBottomMaximized=4
TitleEdgeLeft=10
TitleEdgeLeftMaximized=6
TitleEdgeRight=10
TitleEdgeRightMaximized=6
TitleEdgeTop=6
TitleEdgeTopMaximized=4
TitleHeight=24
"""

def build_metadata_desktop(name: str, mode: str) -> str:
    plugin = name.lower().replace(" ", "-")
    return f"""[Desktop Entry]
Comment=BookOS App-style window decoration ({mode})
Encoding=UTF-8
Name={name}
Type=Service

[KDE]
ServiceTypes=KWin/AuroraeTheme
X-KDE-PluginInfo-Author=BookOS
X-KDE-PluginInfo-Category=
X-KDE-PluginInfo-Depends=
X-KDE-PluginInfo-Email=
X-KDE-PluginInfo-License=GPL3.0
X-KDE-PluginInfo-Name=__aurorae__svg__{name}
X-KDE-PluginInfo-Version=1.0
X-KDE-PluginInfo-Website=
X-KDE-ServiceTypes=KWin/AuroraeTheme
"""

def build_metadata_json(name: str, mode: str) -> str:
    data = {
        "KPlugin": {
            "Authors": [{"Email": "", "Name": "BookOS"}],
            "Category": "",
            "Description": f"BookOS App-style window decoration ({mode})",
            "Id": f"__aurorae__svg__{name}",
            "License": "GPL-3.0",
            "Name": name,
            "ServiceTypes": ["KWin/AuroraeTheme"],
            "Version": "1.0",
        },
    }
    return json.dumps(data, indent=4)

def build_theme(mode: str):
    theme = MODES[mode]
    name = f"BookOS-App-{mode}"
    dst = os.path.join(OUT_ROOT, name)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    os.makedirs(dst)

    for btn in GLYPHS:
        with open(os.path.join(dst, f"{btn}.svg"), "w") as f:
            f.write(build_svg(btn, theme))

    with open(os.path.join(dst, f"{name}rc"), "w") as f:
        f.write(build_rc(theme))
    with open(os.path.join(dst, "metadata.desktop"), "w") as f:
        f.write(build_metadata_desktop(name, mode))
    with open(os.path.join(dst, "metadata.json"), "w") as f:
        f.write(build_metadata_json(name, mode))

    print(f"[OK] {name}")

def main():
    os.makedirs(OUT_ROOT, exist_ok=True)
    for mode in MODES:
        build_theme(mode)
    print(f"\nDone. Output at {OUT_ROOT}")

if __name__ == "__main__":
    main()
