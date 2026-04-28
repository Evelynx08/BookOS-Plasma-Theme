#!/usr/bin/env python3
"""Generate BookOS color-scheme variants from Dark/Light blue baseline."""
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
BLUE_DARK = os.path.expanduser("~/.local/share/color-schemes/BookOSDark.colors")
BLUE_LIGHT = os.path.expanduser("~/.local/share/color-schemes/BookOSLight.colors")

# Apple system colors (R,G,B) — dark variant, light variant
ACCENTS = {
    "blue":   ("10,132,255",  "0,122,255"),
    "red":    ("255,69,58",   "255,59,48"),
    "green":  ("48,209,88",   "52,199,89"),
    "purple": ("191,90,242",  "175,82,222"),
    "orange": ("255,159,10",  "255,149,0"),
    "pink":   ("255,55,95",   "255,45,85"),
}

# Tokens that hold the accent in the baseline (blue) files
DARK_ACCENT_RE  = re.compile(r"\b10,132,255\b")
LIGHT_ACCENT_RE = re.compile(r"\b0,122,255\b")
# Visited fg uses a lighter shade derived from accent in original; keep as-is
# Selection foreground stays white/black — only accent backgrounds change

def make_variant(src_path: str, accent_rgb: str, mode: str, color: str, dst_dir: str):
    with open(src_path, "r") as f:
        text = f.read()
    pat = DARK_ACCENT_RE if mode == "dark" else LIGHT_ACCENT_RE
    text = pat.sub(accent_rgb, text)
    nice = color.capitalize()
    mode_nice = mode.capitalize()
    # Update Name + ColorScheme fields
    text = re.sub(r"^Name=BookOS (Dark|Light)$",
                  f"Name=BookOS {mode_nice} {nice}",
                  text, flags=re.MULTILINE)
    text = re.sub(r"^ColorScheme=BookOS(Dark|Light)$",
                  f"ColorScheme=BookOS{mode_nice}{nice}",
                  text, flags=re.MULTILINE)
    out = os.path.join(dst_dir, f"BookOS{mode_nice}{nice}.colors")
    with open(out, "w") as f:
        f.write(text)
    print(f"  -> {os.path.basename(out)}")

def main():
    if not (os.path.exists(BLUE_DARK) and os.path.exists(BLUE_LIGHT)):
        raise SystemExit("Baseline BookOSDark.colors / BookOSLight.colors not found in ~/.local/share/color-schemes/")
    print("Generating variants in", HERE)
    for color, (dark_rgb, light_rgb) in ACCENTS.items():
        make_variant(BLUE_DARK,  dark_rgb,  "dark",  color, HERE)
        make_variant(BLUE_LIGHT, light_rgb, "light", color, HERE)
    print("Done.")

if __name__ == "__main__":
    main()
