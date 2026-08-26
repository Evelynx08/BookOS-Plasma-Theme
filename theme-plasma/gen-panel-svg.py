#!/usr/bin/env python3
"""Generate dock-style rounded panel-background.svg for Plasma Desktop Theme."""
import os, gzip

# Corner radius for dock appearance
R = 16

# Colors per variant
VARIANTS = {
    "dark": {
        "bg":      "#1c1c1e",
        "bg_alt":  "#000000",
        "border":  "#3a3a3c",
        "shadow":  "#000000",
        "css_bg":  "ColorScheme-Background",
        "theme_dir": os.path.expanduser("~/.local/share/plasma/desktoptheme/bookos-dark"),
    },
    "light": {
        "bg":      "#f2f2f7",
        "bg_alt":  "#ffffff",
        "border":  "#c7c7cc",
        "shadow":  "#000000",
        "css_bg":  "ColorScheme-Background",
        "theme_dir": os.path.expanduser("~/.local/share/plasma/desktoptheme/bookos-light"),
    },
}

def make_panel_svg(v):
    bg = v["bg"]
    border = v["border"]
    shadow = v["shadow"]
    # SVG dimensions — 9-patch: R corners, 1px center strip
    W = R * 2 + 1   # 33
    H = R * 2 + 1   # 33

    # Bezier control point for quarter circle radius R
    k = round(R * 0.5523, 3)

    # hint margin = R
    hm = R

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <style>
      .ColorScheme-Background {{
        color:{bg};
        stop-color:{bg};
      }}
      .ColorScheme-Text {{
        color:#ffffff;
        stop-color:#ffffff;
      }}
      .ColorScheme-Highlight {{
        color:#0a84ff;
        stop-color:#0a84ff;
      }}
    </style>

    <!-- Shadow filter -->
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="2" stdDeviation="4"
                    flood-color="{shadow}" flood-opacity="0.4"/>
    </filter>

    <!-- Clip for rounded rect -->
    <clipPath id="roundclip">
      <rect x="0" y="0" width="{W}" height="{H}" rx="{R}" ry="{R}"/>
    </clipPath>

    <!-- Gradient: subtle top highlight -->
    <linearGradient id="topshine" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#ffffff" stop-opacity="0.06"/>
      <stop offset="1" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <!-- ═══ HINT ELEMENTS (Plasma reads these for margin sizes) ═══ -->
  <rect id="hint-top-margin"
        x="{R}" y="0" width="1" height="{hm}"
        fill="#ff00ff" fill-opacity="0"/>
  <rect id="hint-bottom-margin"
        x="{R}" y="{H - hm}" width="1" height="{hm}"
        fill="#ff00ff" fill-opacity="0"/>
  <rect id="hint-left-margin"
        x="0" y="{R}" width="{hm}" height="1"
        fill="#ff00ff" fill-opacity="0"/>
  <rect id="hint-right-margin"
        x="{W - hm}" y="{R}" width="{hm}" height="1"
        fill="#ff00ff" fill-opacity="0"/>

  <!-- ═══ CORNER ELEMENTS ═══ -->
  <!-- topleft: quarter circle, top-left -->
  <g id="topleft">
    <path class="ColorScheme-Background"
          d="M 0 {R} C 0 {round(R-k,3)} {round(R-k,3)} 0 {R} 0 L {R} {R} L 0 {R} Z"
          fill="{bg}"/>
    <path d="M 0 {R} C 0 {round(R-k,3)} {round(R-k,3)} 0 {R} 0"
          fill="none" stroke="{border}" stroke-width="1" opacity="0.6"/>
  </g>

  <!-- topright: quarter circle, top-right -->
  <g id="topright">
    <path class="ColorScheme-Background"
          d="M {R+1} 0 C {round(R+1+k,3)} 0 {W} {round(R-k,3)} {W} {R} L {R+1} {R} Z"
          fill="{bg}"/>
    <path d="M {R+1} 0 C {round(R+1+k,3)} 0 {W} {round(R-k,3)} {W} {R}"
          fill="none" stroke="{border}" stroke-width="1" opacity="0.6"/>
  </g>

  <!-- bottomleft: quarter circle, bottom-left -->
  <g id="bottomleft">
    <path class="ColorScheme-Background"
          d="M 0 {R+1} C 0 {round(R+1+k,3)} {round(R-k,3)} {H} {R} {H} L 0 {R+1} Z"
          fill="{bg}"/>
    <path d="M 0 {R+1} C 0 {round(R+1+k,3)} {round(R-k,3)} {H} {R} {H}"
          fill="none" stroke="{border}" stroke-width="1" opacity="0.6"/>
  </g>

  <!-- bottomright: quarter circle, bottom-right -->
  <g id="bottomright">
    <path class="ColorScheme-Background"
          d="M {W} {R+1} C {W} {round(R+1+k,3)} {round(R+1+k,3)} {H} {R+1} {H} L {W} {R+1} Z"
          fill="{bg}"/>
    <path d="M {W} {R+1} C {W} {round(R+1+k,3)} {round(R+1+k,3)} {H} {R+1} {H}"
          fill="none" stroke="{border}" stroke-width="1" opacity="0.6"/>
  </g>

  <!-- ═══ EDGE ELEMENTS ═══ -->
  <rect id="top"
        class="ColorScheme-Background"
        x="{R}" y="0" width="1" height="{R}"
        fill="{bg}"/>
  <rect id="bottom"
        class="ColorScheme-Background"
        x="{R}" y="{R+1}" width="1" height="{R}"
        fill="{bg}"/>
  <rect id="left"
        class="ColorScheme-Background"
        x="0" y="{R}" width="{R}" height="1"
        fill="{bg}"/>
  <rect id="right"
        class="ColorScheme-Background"
        x="{R+1}" y="{R}" width="{R}" height="1"
        fill="{bg}"/>

  <!-- ═══ CENTER ═══ -->
  <rect id="center"
        class="ColorScheme-Background"
        x="{R}" y="{R}" width="1" height="1"
        fill="{bg}"/>

  <!-- ═══ TOP BORDER LINES (edges only, corners use path above) ═══ -->
  <line id="border-top"
        x1="{R}" y1="0.5" x2="{R+1}" y2="0.5"
        stroke="{border}" stroke-width="1" opacity="0.6"/>
  <line id="border-bottom"
        x1="{R}" y1="{H-0.5}" x2="{R+1}" y2="{H-0.5}"
        stroke="{border}" stroke-width="1" opacity="0.6"/>
  <line id="border-left"
        x1="0.5" y1="{R}" x2="0.5" y2="{R+1}"
        stroke="{border}" stroke-width="1" opacity="0.6"/>
  <line id="border-right"
        x1="{W-0.5}" y1="{R}" x2="{W-0.5}" y2="{R+1}"
        stroke="{border}" stroke-width="1" opacity="0.6"/>

  <!-- hint: compose the SVG over the background -->
  <rect id="hint-compose-over-svg" x="0" y="0" width="0" height="0" fill="#ff00ff" fill-opacity="0"/>
</svg>
"""

def write_svgz(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with gzip.open(path, 'wb') as f:
        f.write(content.encode('utf-8'))

def write_svg(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def main():
    for name, v in VARIANTS.items():
        svg = make_panel_svg(v)
        d = v["theme_dir"]

        # Write to all panel-background locations
        write_svg(f"{d}/widgets/panel-background.svg", svg)
        write_svgz(f"{d}/opaque/widgets/panel-background.svgz", svg)
        write_svgz(f"{d}/solid/widgets/panel-background.svgz", svg)
        write_svgz(f"{d}/translucent/widgets/panel-background.svgz", svg)

        print(f"bookos-{name}: panel-background written (R={R}px)")

if __name__ == "__main__":
    main()
