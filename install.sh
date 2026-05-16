#!/usr/bin/env bash
# BookOS Plasma Theme installer.
# Installs BookOS color-schemes (.colors) and Plasma desktopthemes (panel/widgets/dialogs).

set -euo pipefail

# ---- ANSI colors -----------------------------------------------------------
if [[ -t 1 ]]; then
    C_RESET=$'\e[0m'; C_BOLD=$'\e[1m'
    C_BLUE=$'\e[34m'; C_GREEN=$'\e[32m'; C_YELLOW=$'\e[33m'; C_RED=$'\e[31m'; C_DIM=$'\e[2m'
else
    C_RESET=""; C_BOLD=""; C_BLUE=""; C_GREEN=""; C_YELLOW=""; C_RED=""; C_DIM=""
fi

ok()   { printf "%s[OK]%s %s\n"   "$C_GREEN"  "$C_RESET" "$*"; }
info() { printf "%s[i]%s %s\n"    "$C_BLUE"   "$C_RESET" "$*"; }
warn() { printf "%s[!]%s %s\n"    "$C_YELLOW" "$C_RESET" "$*"; }
err()  { printf "%s[x]%s %s\n"    "$C_RED"    "$C_RESET" "$*" >&2; }

# ---- Paths -----------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_SCHEMES="$SCRIPT_DIR/color-schemes"
SRC_DESKTOPTHEME="$SCRIPT_DIR/desktoptheme"
SRC_KVANTUM="$SCRIPT_DIR/kvantum"
SRC_AURORAE="$SCRIPT_DIR/aurorae/themes"

VALID_COLORS=(blue red green purple orange pink)
VALID_MODES=(dark light)

# ---- Defaults --------------------------------------------------------------
COLORS=()
MODES=()
SYSTEM=0
ALL=0
ONLY_SCHEMES=0
ONLY_THEME=0
ONLY_KVANTUM=0
NO_KVANTUM=0
ONLY_AURORAE=0
NO_AURORAE=0
SKIP_PKG=0

usage() {
    cat <<EOF
${C_BOLD}BookOS Plasma Theme Installer${C_RESET}

Installs:
  - Color schemes (window/button/widget colors)
  - Plasma desktopthemes (panel, system tray, dialogs, widgets)

Usage: $0 [options]

${C_BOLD}Color flags${C_RESET} (pick one or more, default: blue):
  --blue --red --green --purple --orange --pink

${C_BOLD}Mode flags${C_RESET} (pick one or both, default: both):
  --dark --light

${C_BOLD}Component flags${C_RESET} (default: install all):
  --schemes-only       Install only color schemes
  --desktoptheme-only  Install only Plasma desktopthemes
  --kvantum-only       Install only Kvantum themes
  --no-kvantum         Skip Kvantum themes
  --aurorae-only       Install only Aurorae window decorations
  --no-aurorae         Skip Aurorae window decorations

${C_BOLD}Other${C_RESET}:
  --all        Install every color and mode (12 of each component)
  --system     Install system-wide to /usr/share (requires sudo)
  --skip-pkg   Don't try to install kvantum package (use existing install)
  -h, --help   Show this help

${C_BOLD}Examples${C_RESET}:
  $0 --blue --dark              ${C_DIM}# Just BookOS Dark Blue (both components)${C_RESET}
  $0 --red --green              ${C_DIM}# Red and Green, both modes${C_RESET}
  $0 --all                      ${C_DIM}# Everything${C_RESET}
  $0 --all --schemes-only       ${C_DIM}# All color schemes, no desktoptheme${C_RESET}
  sudo $0 --all --system        ${C_DIM}# All, system-wide${C_RESET}
EOF
}

# ---- Parse args ------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --blue|--red|--green|--purple|--orange|--pink) COLORS+=("${1#--}") ;;
        --dark|--light) MODES+=("${1#--}") ;;
        --all)               ALL=1 ;;
        --system)            SYSTEM=1 ;;
        --schemes-only)      ONLY_SCHEMES=1 ;;
        --desktoptheme-only) ONLY_THEME=1 ;;
        --kvantum-only)      ONLY_KVANTUM=1 ;;
        --no-kvantum)        NO_KVANTUM=1 ;;
        --aurorae-only)      ONLY_AURORAE=1 ;;
        --no-aurorae)        NO_AURORAE=1 ;;
        --skip-pkg)          SKIP_PKG=1 ;;
        -h|--help)           usage; exit 0 ;;
        *) err "Unknown option: $1"; usage; exit 1 ;;
    esac
    shift
done

if [[ $ALL -eq 1 ]]; then
    COLORS=("${VALID_COLORS[@]}")
    MODES=("${VALID_MODES[@]}")
fi
[[ ${#COLORS[@]} -eq 0 ]] && COLORS=(blue)
[[ ${#MODES[@]}  -eq 0 ]] && MODES=("${VALID_MODES[@]}")

INSTALL_SCHEMES=1
INSTALL_THEME=1
INSTALL_KVANTUM=1
INSTALL_AURORAE=1
if [[ $ONLY_SCHEMES -eq 1 ]]; then INSTALL_THEME=0; INSTALL_KVANTUM=0; INSTALL_AURORAE=0; fi
if [[ $ONLY_THEME   -eq 1 ]]; then INSTALL_SCHEMES=0; INSTALL_KVANTUM=0; INSTALL_AURORAE=0; fi
if [[ $ONLY_KVANTUM -eq 1 ]]; then INSTALL_SCHEMES=0; INSTALL_THEME=0; INSTALL_AURORAE=0; fi
if [[ $ONLY_AURORAE -eq 1 ]]; then INSTALL_SCHEMES=0; INSTALL_THEME=0; INSTALL_KVANTUM=0; fi
[[ $NO_KVANTUM -eq 1 ]] && INSTALL_KVANTUM=0
[[ $NO_AURORAE -eq 1 ]] && INSTALL_AURORAE=0

# ---- Resolve destination ---------------------------------------------------
if [[ $SYSTEM -eq 1 ]]; then
    if [[ $EUID -ne 0 ]]; then
        err "--system requires root. Run with sudo."
        exit 1
    fi
    DST_SCHEMES="/usr/share/color-schemes"
    DST_THEME="/usr/share/plasma/desktoptheme"
    DST_KVANTUM="/usr/share/Kvantum"
    DST_AURORAE="/usr/share/aurorae/themes"
else
    DST_SCHEMES="${XDG_DATA_HOME:-$HOME/.local/share}/color-schemes"
    DST_THEME="${XDG_DATA_HOME:-$HOME/.local/share}/plasma/desktoptheme"
    DST_KVANTUM="${XDG_CONFIG_HOME:-$HOME/.config}/Kvantum"
    DST_AURORAE="${XDG_DATA_HOME:-$HOME/.local/share}/aurorae/themes"
fi

# ---- Package install (kvantum) ---------------------------------------------
install_kvantum_pkg() {
    [[ $SKIP_PKG -eq 1 ]] && return 0
    if command -v kvantummanager >/dev/null 2>&1 || command -v kvantummanager-qt6 >/dev/null 2>&1; then
        info "Kvantum already installed"
        return 0
    fi
    local pm pkg sudo_cmd=""
    [[ $EUID -ne 0 ]] && sudo_cmd="sudo"
    if   command -v pacman >/dev/null;  then pm="pacman -S --noconfirm";          pkg="kvantum";
    elif command -v dnf >/dev/null;     then pm="dnf install -y";                 pkg="kvantum";
    elif command -v apt-get >/dev/null; then pm="apt-get install -y";             pkg="qt6-style-kvantum";
    elif command -v zypper >/dev/null;  then pm="zypper install -y";              pkg="kvantum-manager";
    elif command -v xbps-install >/dev/null; then pm="xbps-install -y";           pkg="kvantum";
    else warn "Unknown package manager. Install kvantum manually."; return 0; fi
    info "Installing $pkg via $pm"
    $sudo_cmd $pm $pkg || warn "Failed to install $pkg (continuing)"
}

# ---- Helpers ---------------------------------------------------------------
cap() { local s="$1"; echo "${s^}"; }

# ---- Banner ----------------------------------------------------------------
echo
printf "%s%sBookOS Plasma Theme Installer%s\n" "$C_BOLD" "$C_BLUE" "$C_RESET"
printf "%s\n" "$(printf '%.0s=' {1..32})"
info "Colors:           ${COLORS[*]}"
info "Modes:            ${MODES[*]}"
[[ $INSTALL_SCHEMES -eq 1 ]] && info "Schemes -> $DST_SCHEMES"
[[ $INSTALL_THEME   -eq 1 ]] && info "Desktoptheme -> $DST_THEME"
[[ $INSTALL_KVANTUM -eq 1 ]] && info "Kvantum -> $DST_KVANTUM"
[[ $INSTALL_AURORAE -eq 1 ]] && info "Aurorae -> $DST_AURORAE"
echo

# ---- Install color schemes -------------------------------------------------
installed_s=0
skipped_s=0
missing_s=0

if [[ $INSTALL_SCHEMES -eq 1 ]]; then
    if [[ ! -d "$SRC_SCHEMES" ]]; then
        err "color-schemes folder not found: $SRC_SCHEMES"
        exit 1
    fi
    mkdir -p "$DST_SCHEMES"
    printf "%s\n" "${C_BOLD}Color schemes${C_RESET}"
    for mode in "${MODES[@]}"; do
        for color in "${COLORS[@]}"; do
            name="BookOS$(cap "$mode")$(cap "$color").colors"
            src="$SRC_SCHEMES/$name"
            dst="$DST_SCHEMES/$name"
            if [[ ! -f "$src" ]]; then
                warn "Missing source: $name"
                missing_s=$((missing_s+1))
                continue
            fi
            cp -f "$src" "$dst"
            ok "Installed $name"
            installed_s=$((installed_s+1))
        done
    done
    echo
fi

# ---- Install desktopthemes -------------------------------------------------
installed_t=0
skipped_t=0
missing_t=0

if [[ $INSTALL_THEME -eq 1 ]]; then
    if [[ ! -d "$SRC_DESKTOPTHEME" ]]; then
        err "desktoptheme folder not found: $SRC_DESKTOPTHEME"
        exit 1
    fi
    mkdir -p "$DST_THEME"
    printf "%s\n" "${C_BOLD}Desktopthemes${C_RESET}"
    for mode in "${MODES[@]}"; do
        for color in "${COLORS[@]}"; do
            name="BookOS-$(cap "$mode")-$(cap "$color")"
            src="$SRC_DESKTOPTHEME/$name"
            dst="$DST_THEME/$name"
            if [[ ! -d "$src" ]]; then
                warn "Missing source: $name"
                missing_t=$((missing_t+1))
                continue
            fi
            [[ -d "$dst" ]] && rm -rf "$dst"
            cp -r "$src" "$dst"
            ok "Installed $name"
            installed_t=$((installed_t+1))
        done
    done

    # Always install base themes (referenced by BookOS Look-and-Feel)
    for base in bookos-dark bookos-light; do
        src="$SRC_DESKTOPTHEME/$base"
        dst="$DST_THEME/$base"
        if [[ -d "$src" ]]; then
            [[ -d "$dst" ]] && rm -rf "$dst"
            cp -r "$src" "$dst"
            ok "Installed $base (base)"
            installed_t=$((installed_t+1))
        fi
    done
    echo
fi

# ---- Install Kvantum themes ------------------------------------------------
installed_k=0
missing_k=0

if [[ $INSTALL_KVANTUM -eq 1 ]]; then
    install_kvantum_pkg
    if [[ ! -d "$SRC_KVANTUM" ]]; then
        warn "kvantum folder not found: $SRC_KVANTUM (skipping)"
    else
        mkdir -p "$DST_KVANTUM"
        printf "%s\n" "${C_BOLD}Kvantum themes${C_RESET}"
        for theme in "$SRC_KVANTUM"/*/; do
            [[ -d "$theme" ]] || continue
            name="$(basename "$theme")"
            dst="$DST_KVANTUM/$name"
            [[ -d "$dst" ]] && rm -rf "$dst"
            cp -r "$theme" "$dst"
            ok "Installed $name"
            installed_k=$((installed_k+1))
        done
        echo
    fi
fi

# ---- Install Aurorae window decorations ------------------------------------
installed_a=0

if [[ $INSTALL_AURORAE -eq 1 ]]; then
    if [[ ! -d "$SRC_AURORAE" ]]; then
        warn "aurorae folder not found: $SRC_AURORAE (skipping)"
    else
        mkdir -p "$DST_AURORAE"
        printf "%s\n" "${C_BOLD}Aurorae window decorations${C_RESET}"
        for theme in "$SRC_AURORAE"/*/; do
            [[ -d "$theme" ]] || continue
            name="$(basename "$theme")"
            dst="$DST_AURORAE/$name"
            [[ -d "$dst" ]] && rm -rf "$dst"
            cp -r "$theme" "$dst"
            ok "Installed $name"
            installed_a=$((installed_a+1))
        done
        echo
    fi
fi

# ---- Summary ---------------------------------------------------------------
printf "%s\n" "$(printf '%.0s-' {1..32})"
if [[ $INSTALL_SCHEMES -eq 1 ]]; then
    ok "Color schemes: $installed_s installed"
    [[ $skipped_s -gt 0 ]] && warn "  skipped: $skipped_s"
    [[ $missing_s -gt 0 ]] && warn "  missing: $missing_s"
fi
if [[ $INSTALL_THEME -eq 1 ]]; then
    ok "Desktopthemes: $installed_t installed"
    [[ $skipped_t -gt 0 ]] && warn "  skipped: $skipped_t"
    [[ $missing_t -gt 0 ]] && warn "  missing: $missing_t"
fi
if [[ $INSTALL_KVANTUM -eq 1 ]]; then
    ok "Kvantum themes: $installed_k installed"
fi
if [[ $INSTALL_AURORAE -eq 1 ]]; then
    ok "Aurorae decorations: $installed_a installed"
fi
echo
info "Activate from:"
info "  Colors:       System Settings -> Colors"
info "  Desktoptheme: System Settings -> Plasma Style"
[[ $INSTALL_KVANTUM -eq 1 ]] && info "  Kvantum:      run 'kvantummanager' and select bookos-dark-blue / bookos-light-blue"
[[ $INSTALL_AURORAE -eq 1 ]] && info "  Decorations:  System Settings -> Window Decorations -> 'BookOS App Dark/Light'"
