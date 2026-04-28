#!/usr/bin/env python3
"""
Generate a solid rounded panel-background SVG for Plasma.
Based on the default theme structure with rounded corners added.
R = corner radius in pixels.
"""
import gzip, os

R = 14  # corner radius

VARIANTS = {
    "dark": {
        "dir": os.path.expanduser("~/.local/share/plasma/desktoptheme/bookos-dark"),
        "bg":   "#000000",
        "text": "#ffffff",
        "hl":   "#0a84ff",
        "btn":  "#1c1c1e",
    },
    "light": {
        "dir": os.path.expanduser("~/.local/share/plasma/desktoptheme/bookos-light"),
        "bg":   "#ffffff",
        "text": "#000000",
        "hl":   "#007aff",
        "btn":  "#e5e5ea",
    },
}

def make_svg(v):
    bg   = v["bg"]
    text = v["text"]
    hl   = v["hl"]
    btn  = v["btn"]

    # SVG canvas: 173x56 (same as default theme)
    # 9-patch margins = R (corner radius)
    W, H = 173, 56
    m = R   # margin = corner radius
    k = round(R * 0.5523, 4)  # bezier handle for quarter circle

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
        color:{btn};
        stop-color:{btn};
      }}
      .ColorScheme-Frame {{
        color:{btn};
        stop-color:{btn};
      }}
    </style>
  </defs>

  <!-- ═══ HINT MARGIN ELEMENTS (magenta = invisible, defines 9-patch margins) ═══ -->
  <rect id="hint-top-margin"    x="{m}" y="0"     width="1" height="{m}" fill="#ff00ff" fill-opacity="0"/>
  <rect id="hint-bottom-margin" x="{m}" y="{H-m}" width="1" height="{m}" fill="#ff00ff" fill-opacity="0"/>
  <rect id="hint-left-margin"   x="0"   y="{m}"   width="{m}" height="1" fill="#ff00ff" fill-opacity="0"/>
  <rect id="hint-right-margin"  x="{W-m}" y="{m}" width="{m}" height="1" fill="#ff00ff" fill-opacity="0"/>

  <!-- ═══ CORNERS (rounded quarter-circles) ═══ -->
  <!-- topleft -->
  <path id="topleft"
        class="ColorScheme-Background"
        style="fill:{bg};fill-opacity:1"
        d="M 0,{m} C 0,{round(m-k,4)} {round(m-k,4)},0 {m},0 L {m},{m} Z"/>

  <!-- topright -->
  <path id="topright"
        class="ColorScheme-Background"
        style="fill:{bg};fill-opacity:1"
        d="M {W-m},0 C {round(W-m+k,4)},0 {W},{round(m-k,4)} {W},{m} L {W-m},{m} Z"/>

  <!-- bottomleft -->
  <path id="bottomleft"
        class="ColorScheme-Background"
        style="fill:{bg};fill-opacity:1"
        d="M 0,{H-m} C 0,{round(H-m+k,4)} {round(m-k,4)},{H} {m},{H} L {m},{H-m} Z"/>

  <!-- bottomright -->
  <path id="bottomright"
        class="ColorScheme-Background"
        style="fill:{bg};fill-opacity:1"
        d="M {W},{H-m} C {W},{round(H-m+k,4)} {round(W-m+k,4)},{H} {W-m},{H} L {W-m},{H-m} Z"/>

  <!-- ═══ EDGES ═══ -->
  <rect id="top"    class="ColorScheme-Background" style="fill:{bg};fill-opacity:1" x="{m}" y="0"     width="{W-2*m}" height="{m}"/>
  <rect id="bottom" class="ColorScheme-Background" style="fill:{bg};fill-opacity:1" x="{m}" y="{H-m}" width="{W-2*m}" height="{m}"/>
  <rect id="left"   class="ColorScheme-Background" style="fill:{bg};fill-opacity:1" x="0"   y="{m}"   width="{m}"     height="{H-2*m}"/>
  <rect id="right"  class="ColorScheme-Background" style="fill:{bg};fill-opacity:1" x="{W-m}" y="{m}" width="{m}"     height="{H-2*m}"/>

  <!-- ═══ CENTER ═══ -->
  <rect id="center" class="ColorScheme-Background" style="fill:{bg};fill-opacity:1" x="{m}" y="{m}" width="{W-2*m}" height="{H-2*m}"/>

  <!-- compose hint -->
  <rect id="hint-compose-over-svg" x="0" y="0" width="0" height="0" fill="#ff00ff" fill-opacity="0"/>
</svg>
"""

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)

def main():
    for name, v in VARIANTS.items():
        svg = make_svg(v)
        d = v["dir"]
        for sub in ["widgets", "opaque/widgets", "solid/widgets", "translucent/widgets"]:
            path = f"{d}/{sub}/panel-background.svg"
            write(path, svg)
            print(f"bookos-{name}: {sub}/panel-background.svg")

if __name__ == "__main__":
    main()
