#!/usr/bin/env python3
"""Generate 12 BookOS Plasma desktopthemes (dark/light x 6 accents) from cachyos-emerald.

Run on a machine that has cachyos-emerald installed at /usr/share/plasma/desktoptheme/cachyos-emerald.
Output goes to ../desktoptheme/<name>/ in the repo, ready to ship.
"""
import gzip
import io
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = "/usr/share/plasma/desktoptheme/cachyos-emerald"
OUT_ROOT = os.path.join(REPO, "desktoptheme")

# Accent hex per color (dark / light variant)
ACCENTS = {
    "blue":   {"dark": "#0a84ff", "light": "#007aff", "light_alt": "#47a1ff", "sky": "#64d2ff", "softer": "#5e9fff"},
    "red":    {"dark": "#ff453a", "light": "#ff3b30", "light_alt": "#ff6961", "sky": "#ff8c80", "softer": "#ff7a70"},
    "green":  {"dark": "#30d158", "light": "#34c759", "light_alt": "#5edc7f", "sky": "#80e09a", "softer": "#6fd88c"},
    "purple": {"dark": "#bf5af2", "light": "#af52de", "light_alt": "#cf86f5", "sky": "#dba8f7", "softer": "#c876ed"},
    "orange": {"dark": "#ff9f0a", "light": "#ff9500", "light_alt": "#ffb340", "sky": "#ffc873", "softer": "#ffae3a"},
    "pink":   {"dark": "#ff375f", "light": "#ff2d55", "light_alt": "#ff6385", "sky": "#ff8aa3", "softer": "#ff7290"},
}

# Light/Dark mode shared background palette
DARK_BG = {
    "main_bg":   "#000000",
    "surface":   "#1c1c1e",
    "alt":       "#0d0d0f",
    "text":      "#ffffff",
    "text_alt":  "#ebebf0",
    "muted_1":   "#c7c7cc",
    "muted_2":   "#aeaeb2",
    "muted_3":   "#8e8e93",
    "muted_4":   "#636366",
    "muted_5":   "#48484a",
    "muted_6":   "#3a3a3c",
    "muted_7":   "#2c2c2e",
}
LIGHT_BG = {
    "main_bg":   "#ffffff",
    "surface":   "#f2f2f7",
    "alt":       "#e5e5ea",
    "text":      "#000000",
    "text_alt":  "#1c1c1e",
    "muted_1":   "#3a3a3c",
    "muted_2":   "#48484a",
    "muted_3":   "#636366",
    "muted_4":   "#8e8e93",
    "muted_5":   "#aeaeb2",
    "muted_6":   "#c7c7cc",
    "muted_7":   "#d1d1d6",
}

def build_color_map(mode: str, accent: str) -> dict:
    bg = DARK_BG if mode == "dark" else LIGHT_BG
    acc = ACCENTS[accent]
    accent_main = acc["dark"] if mode == "dark" else acc["light"]
    return {
        # Backgrounds
        "#232629": bg["main_bg"],
        "#1a1a1a": bg["main_bg"],
        "#31363b": bg["surface"],
        "#2e2e2e": bg["surface"],
        "#313338": bg["surface"],
        "#36393e": bg["surface"],
        "#14171f": bg["main_bg"],
        "#161a23": bg["main_bg"],
        "#212329": bg["alt"],
        # Accent
        "#3daee9": accent_main,
        "#3DAEE6": accent_main,
        "#3daee6": accent_main,
        "#1E92FF": accent_main,
        "#1a73e8": accent_main,
        "#1a92ff": accent_main,
        "#93cee9": acc["light_alt"],
        "#71dbff": acc["sky"],
        "#82afe6": acc["softer"],
        # Text
        "#eff0f1": bg["text"],
        "#EFF0F1": bg["text"],
        "#fcfcfc": bg["text"],
        "#FCFCFC": bg["text"],
        "#dfdfdf": bg["text_alt"],
        "#d4d4d4": bg["muted_1"],
        "#c8c8c8": bg["muted_2"],
        "#cbcbcb": bg["muted_2"],
        "#a8a8a8": bg["muted_3"],
        "#a9a9a9": bg["muted_3"],
        "#818181": bg["muted_4"],
        "#666666": bg["muted_5"],
        "#565656": bg["muted_6"],
        "#505050": bg["muted_7"],
        "#3a3a3a": bg["muted_7"],
        "#363636": bg["muted_7"],
        "#5e5e5e": bg["muted_5"],
        "#8b8b8b": bg["muted_4"],
        "#7B7C7E": bg["muted_4"],
        # Always-bright accents (semantic — stay the same regardless of accent)
        "#da4453": "#ff453a",
        "#ff2a2a": "#ff453a",
        "#ef5350": "#ff453a",
        "#27ae60": "#30d158",
        "#27ad60": "#30d158",
        "#26ad5f": "#30d158",
        "#2ecc71": "#32d74b",
        "#4caf50": "#30d158",
        "#f67400": "#ff9f0a",
        "#ff6600": "#ff9f0a",
        "#ff9800": "#ff9f0a",
        "#ffca28": "#ffd60a",
        "#ffb54d": "#ff9f0a",
    }

def colorscheme_classes(mode: str, accent: str) -> dict:
    acc = ACCENTS[accent]
    accent_main = acc["dark"] if mode == "dark" else acc["light"]
    bg = DARK_BG if mode == "dark" else LIGHT_BG
    return {
        "ColorScheme-Text":              bg["text"],
        "ColorScheme-Background":        bg["main_bg"],
        "ColorScheme-Highlight":         accent_main,
        "ColorScheme-HighlightedText":   "#ffffff",
        "ColorScheme-PositiveText":      "#30d158",
        "ColorScheme-NeutralText":       "#ffd60a",
        "ColorScheme-NegativeText":      "#ff453a",
        "ColorScheme-ActiveText":        accent_main,
        "ColorScheme-LinkText":          accent_main,
        "ColorScheme-VisitedText":       acc["softer"],
        "ColorScheme-ViewText":          bg["text"],
        "ColorScheme-ViewBackground":    bg["main_bg"],
        "ColorScheme-ViewHover":         acc["light_alt"],
        "ColorScheme-ViewFocus":         accent_main,
        "ColorScheme-ButtonText":        bg["text"],
        "ColorScheme-ButtonBackground":  bg["surface"],
        "ColorScheme-ButtonHover":       acc["light_alt"],
        "ColorScheme-ButtonFocus":       accent_main,
        "ColorScheme-ComplementaryText": bg["text"],
        "ColorScheme-ComplementaryBackground": bg["alt"],
        "ColorScheme-HeaderText":        bg["text"],
        "ColorScheme-HeaderBackground":  bg["surface"],
    }

def make_recolor(color_map: dict, cs_classes: dict):
    sorted_map = sorted(color_map.items(), key=lambda x: len(x[0]), reverse=True)
    cs_pattern = re.compile(
        r'(\.' + r'|\.'.join(re.escape(k) for k in cs_classes) + r')\s*\{([^}]+)\}',
        re.DOTALL
    )

    def fix_cs(text: str) -> str:
        def replacer(m):
            cls = m.group(1).lstrip('.')
            body = m.group(2)
            color = cs_classes.get(cls)
            if not color:
                return m.group(0)
            body = re.sub(r'(?<=color:)#[0-9a-fA-F]{3,8}', color, body)
            body = re.sub(r'(?<=stop-color:)#[0-9a-fA-F]{3,8}', color, body)
            return f'.{cls} {{{body}}}'
        return cs_pattern.sub(replacer, text)

    def recolor(data: bytes) -> bytes:
        text = data.decode("utf-8", errors="replace")
        for src_color, dst_color in sorted_map:
            text = re.sub(re.escape(src_color), dst_color, text, flags=re.IGNORECASE)
        text = fix_cs(text)
        return text.encode("utf-8")
    return recolor

def copy_file(src_path: str, dst_path: str, recolor):
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    ext = os.path.splitext(src_path)[1].lower()
    if ext in (".svg", ".svgz"):
        try:
            with gzip.open(src_path, "rb") as f:
                data = f.read()
            data = recolor(data)
            with gzip.open(dst_path, "wb") as f:
                f.write(data)
        except (gzip.BadGzipFile, OSError):
            with open(src_path, "rb") as f:
                data = f.read()
            if data[:2] == b'\x1f\x8b':
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

def make_metadata(mode: str, accent: str) -> str:
    nice_mode = mode.capitalize()
    nice_accent = accent.capitalize()
    plugin = f"bookos-{mode}-{accent}"
    name = f"BookOS {nice_mode} {nice_accent}"
    return f"""[Desktop Entry]
Comment=BookOS {nice_mode} {nice_accent} - Plasma Desktop Theme
Name={name}
X-KDE-PluginInfo-Author=BookOS
X-KDE-PluginInfo-Category=Plasma Theme
X-KDE-PluginInfo-Email=
X-KDE-PluginInfo-License=GPL3.0
X-KDE-PluginInfo-Name={plugin}
X-KDE-PluginInfo-Version=1.0.0
X-Plasma-API=5.0
"""

def build_one(mode: str, accent: str):
    name = f"BookOS-{mode.capitalize()}-{accent.capitalize()}"
    dst = os.path.join(OUT_ROOT, name)
    if os.path.exists(dst):
        shutil.rmtree(dst)

    color_map = build_color_map(mode, accent)
    cs_classes = colorscheme_classes(mode, accent)
    recolor = make_recolor(color_map, cs_classes)

    count = 0
    for root, _, files in os.walk(SRC):
        for fname in files:
            if fname == "metadata.desktop":
                continue
            src = os.path.join(root, fname)
            rel = os.path.relpath(src, SRC)
            try:
                copy_file(src, os.path.join(dst, rel), recolor)
                count += 1
            except Exception as e:
                print(f"  SKIP {rel}: {e}")

    with open(os.path.join(dst, "metadata.desktop"), "w") as f:
        f.write(make_metadata(mode, accent))

    print(f"[OK] {name} ({count} files)")

def main():
    if not os.path.isdir(SRC):
        raise SystemExit(f"Source theme not found: {SRC}\nInstall cachyos-emerald on this machine first.")
    os.makedirs(OUT_ROOT, exist_ok=True)
    for mode in ("dark", "light"):
        for accent in ACCENTS:
            build_one(mode, accent)
    print(f"\nDone. Output at {OUT_ROOT}")

if __name__ == "__main__":
    main()
