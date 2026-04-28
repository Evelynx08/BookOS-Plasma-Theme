#!/usr/bin/env python3
"""
Generate a clean solid rounded dialog/OSD background SVG for Plasma.
Apple/iOS style: large radius, solid dark/light fill, drop-shadow.
"""
import gzip, os

R = 18       # corner radius (iOS-like)
SHADOW = 12  # shadow margin on each side

VARIANTS = {
    "dark": {
        "dirs": [
            os.path.expanduser("~/.local/share/plasma/desktoptheme/bookos-dark"),
        ],
        "bg":   "#1c1c1e",
        "text": "#ffffff",
        "hl":   "#0a84ff",
        "shadow_color": "#000000",
        "shadow_opacity": "0.55",
    },
    "light": {
        "dirs": [
            os.path.expanduser("~/.local/share/plasma/desktoptheme/bookos-light"),
        ],
        "bg":   "#ffffff",
        "text": "#000000",
        "hl":   "#007aff",
        "shadow_color": "#000000",
        "shadow_opacity": "0.18",
    },
}

def make_svg(v):
    bg   = v["bg"]
    text = v["text"]
    hl   = v["hl"]
    sc   = v["shadow_color"]
    so   = v["shadow_opacity"]
    S    = SHADOW

    # Canvas: 200x200 (9-patch, scaled by Plasma)
    # Fill rect starts at (S, S), size (200-2S) x (200-2S)
    W, H = 200, 200
    FX, FY = S, S
    FW, FH = W - 2*S, H - 2*S

    k = round(R * 0.5523, 4)  # bezier handle

    # Fill rect path with rounded corners (clockwise from top-left)
    x0, y0 = FX, FY
    x1, y1 = FX + FW, FY + FH

    fill_path = (
        f"M {x0+R},{y0} "
        f"L {x1-R},{y0} "
        f"C {x1-R+k},{y0} {x1},{y0+R-k} {x1},{y0+R} "
        f"L {x1},{y1-R} "
        f"C {x1},{y1-R+k} {x1-R+k},{y1} {x1-R},{y1} "
        f"L {x0+R},{y1} "
        f"C {x0+R-k},{y1} {x0},{y1-R+k} {x0},{y1-R} "
        f"L {x0},{y0+R} "
        f"C {x0},{y0+R-k} {x0+R-k},{y0} {x0+R},{y0} Z"
    )

    return f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" version="1.1"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style type="text/css" id="current-color-scheme">
      .ColorScheme-Background {{
        color:{bg};
        stop-color:{bg};
      }}
      .ColorScheme-Text {{
        color:{text};
        stop-color:{text};
      }}
      .ColorScheme-Highlight {{
        color:{hl};
        stop-color:{hl};
      }}
      .ColorScheme-ButtonBackground {{
        color:{bg};
        stop-color:{bg};
      }}
    </style>
    <filter id="shadow" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="0" dy="2" stdDeviation="8"
                    flood-color="{sc}" flood-opacity="{so}"/>
    </filter>
  </defs>

  <!-- ═══ HINT MARGINS (9-patch) ═══ -->
  <rect id="hint-top-margin"    x="{S}" y="0"     width="1" height="{S}" fill="#ff00ff" fill-opacity="0"/>
  <rect id="hint-bottom-margin" x="{S}" y="{H-S}" width="1" height="{S}" fill="#ff00ff" fill-opacity="0"/>
  <rect id="hint-left-margin"   x="0"   y="{S}"   width="{S}" height="1" fill="#ff00ff" fill-opacity="0"/>
  <rect id="hint-right-margin"  x="{W-S}" y="{S}" width="{S}" height="1" fill="#ff00ff" fill-opacity="0"/>

  <!-- Shadow hint margins (reserve extra space for shadow blur) -->
  <rect id="shadow-hint-top-margin"    x="{S}" y="0"     width="1" height="{S}" fill="#ff6600" fill-opacity="0"/>
  <rect id="shadow-hint-bottom-margin" x="{S}" y="{H-S}" width="1" height="{S}" fill="#ff6600" fill-opacity="0"/>
  <rect id="shadow-hint-left-margin"   x="0"   y="{S}"   width="{S}" height="1" fill="#ff6600" fill-opacity="0"/>
  <rect id="shadow-hint-right-margin"  x="{W-S}" y="{S}" width="{S}" height="1" fill="#ff6600" fill-opacity="0"/>

  <!-- ═══ SHADOW LAYER ═══ -->
  <path id="shadow"
        d="{fill_path}"
        fill="{sc}" fill-opacity="{so}"
        filter="url(#shadow)"/>

  <!-- ═══ BACKGROUND FILL ═══ -->
  <!-- corners -->
  <path id="topleft"
        class="ColorScheme-Background"
        style="fill:{bg};fill-opacity:1"
        d="M {x0},{y0+R} C {x0},{round(y0+R-k,4)} {round(x0+R-k,4)},{y0} {x0+R},{y0} L {x0+R},{y0+R} Z"/>
  <path id="topright"
        class="ColorScheme-Background"
        style="fill:{bg};fill-opacity:1"
        d="M {x1-R},{y0} C {round(x1-R+k,4)},{y0} {x1},{round(y0+R-k,4)} {x1},{y0+R} L {x1-R},{y0+R} Z"/>
  <path id="bottomleft"
        class="ColorScheme-Background"
        style="fill:{bg};fill-opacity:1"
        d="M {x0},{y1-R} C {x0},{round(y1-R+k,4)} {round(x0+R-k,4)},{y1} {x0+R},{y1} L {x0+R},{y1-R} Z"/>
  <path id="bottomright"
        class="ColorScheme-Background"
        style="fill:{bg};fill-opacity:1"
        d="M {x1},{y1-R} C {x1},{round(y1-R+k,4)} {round(x1-R+k,4)},{y1} {x1-R},{y1} L {x1-R},{y1-R} Z"/>

  <!-- edges -->
  <rect id="top"    class="ColorScheme-Background" style="fill:{bg};fill-opacity:1" x="{x0+R}" y="{y0}"   width="{FW-2*R}" height="{R}"/>
  <rect id="bottom" class="ColorScheme-Background" style="fill:{bg};fill-opacity:1" x="{x0+R}" y="{y1-R}" width="{FW-2*R}" height="{R}"/>
  <rect id="left"   class="ColorScheme-Background" style="fill:{bg};fill-opacity:1" x="{x0}"   y="{y0+R}" width="{R}"      height="{FH-2*R}"/>
  <rect id="right"  class="ColorScheme-Background" style="fill:{bg};fill-opacity:1" x="{x1-R}" y="{y0+R}" width="{R}"      height="{FH-2*R}"/>

  <!-- center -->
  <rect id="center" class="ColorScheme-Background" style="fill:{bg};fill-opacity:1" x="{x0+R}" y="{y0+R}" width="{FW-2*R}" height="{FH-2*R}"/>

  <!-- compose hint -->
  <rect id="hint-compose-over-svg" x="0" y="0" width="0" height="0" fill="#ff00ff" fill-opacity="0"/>
</svg>
"""

def write_gz(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, "wb") as f:
        f.write(content.encode("utf-8"))

def write_plain(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

def main():
    for name, v in VARIANTS.items():
        svg = make_svg(v)
        for d in v["dirs"]:
            # dialogs/background.svgz
            path = f"{d}/dialogs/background.svgz"
            write_gz(path, svg)
            print(f"bookos-{name}: dialogs/background.svgz")
            # widgets/tooltip.svg (plain SVG — Plasma reads it directly)
            path_tt = f"{d}/widgets/tooltip.svg"
            write_plain(path_tt, svg)
            print(f"bookos-{name}: widgets/tooltip.svg")
            # also write to opaque/solid/translucent if they exist
            for sub in ["opaque", "solid", "translucent"]:
                dialogs_dir = f"{d}/{sub}/dialogs"
                if os.path.isdir(dialogs_dir) or True:
                    p = f"{d}/{sub}/dialogs/background.svgz"
                    write_gz(p, svg)
                    print(f"bookos-{name}: {sub}/dialogs/background.svgz")

if __name__ == "__main__":
    main()
