#!/usr/bin/env python3
"""
Recolor Iridescent-round panel-background.svg to BookOS Dark / Light.
Copies ALL panel SVGs from Iridescent-round structure.
"""
import gzip, os, re, shutil

SRC_DIR = "/usr/share/plasma/desktoptheme/Iridescent-round"

VARIANTS = {
    "dark": {
        "dir": os.path.expanduser("~/.local/share/plasma/desktoptheme/bookos-dark"),
        "panel_body_color": None,  # keep #000000 as-is for dark
        "color_map": {
            "#31363b": "#1c1c1e",
            "#232629": "#000000",
            "#1a1a1a": "#000000",
            "#eff0f1": "#ffffff",
            "#EFF0F1": "#ffffff",
            "#fcfcfc": "#ffffff",
            "#FCFCFC": "#ffffff",
            "#cbcbcb": "#aeaeb2",
            "#666666": "#48484a",
            "#3daee9": "#0a84ff",
            "#3DAEE6": "#0a84ff",
            "#3daee6": "#0a84ff",
            "#93cee9": "#47a1ff",
            "#1E92FF": "#0a84ff",
            "#1a73e8": "#0a84ff",
        },
        "cs_classes": {
            "ColorScheme-Text":             "#ffffff",
            "ColorScheme-Background":       "#000000",
            "ColorScheme-Highlight":        "#0a84ff",
            "ColorScheme-ViewText":         "#ffffff",
            "ColorScheme-ViewBackground":   "#000000",
            "ColorScheme-ViewHover":        "#47a1ff",
            "ColorScheme-ViewFocus":        "#0a84ff",
            "ColorScheme-ButtonText":       "#ffffff",
            "ColorScheme-ButtonBackground": "#1c1c1e",
            "ColorScheme-ButtonHover":      "#47a1ff",
            "ColorScheme-ButtonFocus":      "#0a84ff",
        },
    },
    "light": {
        "dir": os.path.expanduser("~/.local/share/plasma/desktoptheme/bookos-light"),
        "panel_body_color": "#ffffff",  # pure white panel body fills for light theme
        "color_map": {
            "#31363b": "#c7c7cc",
            "#232629": "#f2f2f7",
            "#1a1a1a": "#e5e5ea",
            "#eff0f1": "#f2f2f7",
            "#EFF0F1": "#f2f2f7",
            "#fcfcfc": "#ffffff",
            "#FCFCFC": "#ffffff",
            "#cbcbcb": "#c7c7cc",
            "#666666": "#8e8e93",
            "#3daee9": "#007aff",
            "#3DAEE6": "#007aff",
            "#3daee6": "#007aff",
            "#93cee9": "#5ac8fa",
            "#1E92FF": "#007aff",
            "#1a73e8": "#007aff",
        },
        "cs_classes": {
            "ColorScheme-Text":             "#000000",
            "ColorScheme-Background":       "#ffffff",
            "ColorScheme-Highlight":        "#007aff",
            "ColorScheme-ViewText":         "#000000",
            "ColorScheme-ViewBackground":   "#ffffff",
            "ColorScheme-ViewHover":        "#5ac8fa",
            "ColorScheme-ViewFocus":        "#007aff",
            "ColorScheme-ButtonText":       "#000000",
            "ColorScheme-ButtonBackground": "#e5e5ea",
            "ColorScheme-ButtonHover":      "#5ac8fa",
            "ColorScheme-ButtonFocus":      "#007aff",
        },
    },
}

_CS_PATTERN_CACHE = {}

def fix_cs_classes(text, classes):
    key = id(classes)
    if key not in _CS_PATTERN_CACHE:
        _CS_PATTERN_CACHE[key] = re.compile(
            r'(\.' + r'|\.'.join(re.escape(k) for k in classes) + r')\s*\{([^}]+)\}',
            re.DOTALL
        )
    pat = _CS_PATTERN_CACHE[key]
    def sub(m):
        cls = m.group(1).lstrip('.')
        body = m.group(2)
        c = classes.get(cls)
        if not c: return m.group(0)
        body = re.sub(r'(?<=color:)#[0-9a-fA-F]{3,8}', c, body)
        body = re.sub(r'(?<=stop-color:)#[0-9a-fA-F]{3,8}', c, body)
        return f'.{cls} {{{body}}}'
    return pat.sub(sub, text)

def recolor(data_bytes, color_map, cs_classes, panel_body_color=None):
    text = data_bytes.decode("utf-8", errors="replace")
    sorted_map = sorted(color_map.items(), key=lambda x: len(x[0]), reverse=True)
    for src, dst in sorted_map:
        text = re.sub(re.escape(src), dst, text, flags=re.IGNORECASE)
    # Replace high-opacity panel body fills with solid color (not shadow gradients)
    if panel_body_color is not None:
        # Replace the fill color AND make fully opaque
        text = re.sub(
            r'opacity:0\.97;fill:#000000',
            'opacity:1;fill:' + panel_body_color,
            text
        )
    else:
        # Dark: keep fill:#000000 but make fully opaque
        text = re.sub(
            r'opacity:0\.97;fill:#000000',
            'opacity:1;fill:#000000',
            text
        )
    text = fix_cs_classes(text, cs_classes)
    return text.encode("utf-8")

def process_file(src_path, dst_path, color_map, cs_classes, panel_body_color=None):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    ext = os.path.splitext(src_path)[1].lower()
    if ext in (".svg", ".svgz"):
        try:
            with gzip.open(src_path, "rb") as f: data = f.read()
            data = recolor(data, color_map, cs_classes, panel_body_color)
            with gzip.open(dst_path, "wb") as f: f.write(data)
        except (gzip.BadGzipFile, OSError):
            with open(src_path, "rb") as f: data = f.read()
            data = recolor(data, color_map, cs_classes, panel_body_color)
            with open(dst_path, "wb") as f: f.write(data)
    else:
        shutil.copy2(src_path, dst_path)

# Panel SVG files to copy from Iridescent-round
PANEL_FILES = [
    "widgets/panel-background.svg",
    "opaque/widgets/panel-background.svgz",
    "solid/widgets/panel-background.svgz",
    "translucent/widgets/panel-background.svgz",
]

def main():
    for name, v in VARIANTS.items():
        dst_dir = v["dir"]
        cm = v["color_map"]
        cs = v["cs_classes"]
        pbc = v.get("panel_body_color")
        # Only generate widgets/panel-background.svg (rounded dock)
        # opaque/solid/translucent are handled by gen-panel-from-default.py
        main_svg_rel = "widgets/panel-background.svg"
        main_svg_dst = os.path.join(dst_dir, main_svg_rel)
        main_src = os.path.join(SRC_DIR, main_svg_rel)
        if os.path.exists(main_src):
            process_file(main_src, main_svg_dst, cm, cs, pbc)
            print(f"bookos-{name}: {main_svg_rel}")

        for rel in PANEL_FILES:
            src = os.path.join(SRC_DIR, rel)
            dst = os.path.join(dst_dir, rel)
            if os.path.exists(src):
                process_file(src, dst, cm, cs, pbc)
                print(f"bookos-{name}: {rel}")
            else:
                # For svgz variants, try svg fallback
                src_svg = src[:-1]  # remove z
                if os.path.exists(src_svg):
                    process_file(src_svg, dst, cm, cs, pbc)
                    print(f"bookos-{name}: {rel} (from .svg)")
                else:
                    print(f"bookos-{name}: SKIP {rel} (not found in source)")

if __name__ == "__main__":
    main()
