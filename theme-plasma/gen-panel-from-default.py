#!/usr/bin/env python3
"""Generate BookOS panel-background SVGs from the default Plasma theme.
Uses default's proven SVG structure, just swaps ColorScheme CSS colors."""
import gzip, os, re, shutil

SRC = "/usr/share/plasma/desktoptheme/default"

VARIANTS = {
    "dark": {
        "dir": os.path.expanduser("~/.local/share/plasma/desktoptheme/bookos-dark"),
        "css": {
            "ColorScheme-Background":       "#000000",
            "ColorScheme-Frame":            "#1c1c1e",
            "ColorScheme-Text":             "#ffffff",
            "ColorScheme-Highlight":        "#0a84ff",
            "ColorScheme-ViewBackground":   "#000000",
            "ColorScheme-ViewText":         "#ffffff",
            "ColorScheme-ViewHover":        "#47a1ff",
            "ColorScheme-ViewFocus":        "#0a84ff",
            "ColorScheme-ButtonBackground": "#1c1c1e",
            "ColorScheme-ButtonText":       "#ffffff",
            "ColorScheme-ButtonHover":      "#47a1ff",
            "ColorScheme-ButtonFocus":      "#0a84ff",
        },
    },
    "light": {
        "dir": os.path.expanduser("~/.local/share/plasma/desktoptheme/bookos-light"),
        "css": {
            "ColorScheme-Background":       "#ffffff",
            "ColorScheme-Frame":            "#e5e5ea",
            "ColorScheme-Text":             "#000000",
            "ColorScheme-Highlight":        "#007aff",
            "ColorScheme-ViewBackground":   "#ffffff",
            "ColorScheme-ViewText":         "#000000",
            "ColorScheme-ViewHover":        "#5ac8fa",
            "ColorScheme-ViewFocus":        "#007aff",
            "ColorScheme-ButtonBackground": "#e5e5ea",
            "ColorScheme-ButtonText":       "#000000",
            "ColorScheme-ButtonHover":      "#5ac8fa",
            "ColorScheme-ButtonFocus":      "#007aff",
        },
    },
}

def recolor_svg(data, css_map):
    text = data.decode("utf-8", errors="replace")
    def sub(m):
        cls = m.group(1).lstrip('.')
        color = css_map.get(cls)
        if not color:
            return m.group(0)
        body = m.group(2)
        body = re.sub(r'(?<=color:)#[0-9a-fA-F]{3,8}', color, body)
        body = re.sub(r'(?<=stop-color:)#[0-9a-fA-F]{3,8}', color, body)
        return f'.{cls}{{{body}}}'
    pat = re.compile(
        r'(\.' + r'|\.'.join(re.escape(k) for k in css_map) + r')\s*\{([^}]+)\}',
        re.DOTALL
    )
    text = pat.sub(sub, text)
    return text.encode("utf-8")

def process(src_path, dst_path, css_map):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    try:
        with gzip.open(src_path, "rb") as f: data = f.read()
        data = recolor_svg(data, css_map)
        with gzip.open(dst_path, "wb") as f: f.write(data)
    except (gzip.BadGzipFile, OSError):
        with open(src_path, "rb") as f: data = f.read()
        data = recolor_svg(data, css_map)
        ext = os.path.splitext(dst_path)[1].lower()
        if ext == ".svgz":
            with gzip.open(dst_path, "wb") as f: f.write(data)
        else:
            with open(dst_path, "wb") as f: f.write(data)

PANEL_FILES = [
    # widgets/ is handled by gen-panel-from-iridescent.py (rounded dock)
    # These straight-corner variants are for opaque non-floating panels
    "opaque/widgets/panel-background.svgz",
    "solid/widgets/panel-background.svgz",
    "translucent/widgets/panel-background.svgz",
]

def main():
    for name, v in VARIANTS.items():
        css = v["css"]
        dst_dir = v["dir"]
        for rel in PANEL_FILES:
            src = os.path.join(SRC, rel)
            # dst always as .svg (uncompressed) for easier debugging
            dst_rel = rel.replace(".svgz", ".svg")
            dst = os.path.join(dst_dir, dst_rel)
            if os.path.exists(src):
                process(src, dst, css)
                print(f"bookos-{name}: {dst_rel}")
            else:
                print(f"bookos-{name}: SKIP {rel}")

if __name__ == "__main__":
    main()
