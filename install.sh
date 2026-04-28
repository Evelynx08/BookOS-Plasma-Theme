#!/usr/bin/env bash
# BookOS Plasma color-scheme installer
# Installs BookOS color-schemes (.colors) into KDE Plasma.

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
SRC_DIR="$SCRIPT_DIR/color-schemes"

VALID_COLORS=(blue red green purple orange pink)
VALID_MODES=(dark light)

# ---- Defaults --------------------------------------------------------------
COLORS=()
MODES=()
SYSTEM=0
ALL=0
FORCE=0

usage() {
    cat <<EOF
${C_BOLD}BookOS Color Scheme Installer${C_RESET}

Usage: $0 [options]

${C_BOLD}Color flags${C_RESET} (pick one or more, default: blue):
  --blue --red --green --purple --orange --pink

${C_BOLD}Mode flags${C_RESET} (pick one or both, default: both):
  --dark --light

${C_BOLD}Other${C_RESET}:
  --all       Install every color and mode (12 schemes)
  --system    Install system-wide to /usr/share (requires sudo)
  --force     Overwrite without asking
  -h, --help  Show this help

${C_BOLD}Examples${C_RESET}:
  $0 --blue --dark              ${C_DIM}# Just BookOS Dark Blue${C_RESET}
  $0 --red --green              ${C_DIM}# Red and Green, both modes${C_RESET}
  $0 --all                      ${C_DIM}# Everything${C_RESET}
  sudo $0 --all --system        ${C_DIM}# All schemes, system-wide${C_RESET}
EOF
}

# ---- Parse args ------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --blue|--red|--green|--purple|--orange|--pink) COLORS+=("${1#--}") ;;
        --dark|--light) MODES+=("${1#--}") ;;
        --all)    ALL=1 ;;
        --system) SYSTEM=1 ;;
        --force)  FORCE=1 ;;
        -h|--help) usage; exit 0 ;;
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

# ---- Resolve destination ---------------------------------------------------
if [[ $SYSTEM -eq 1 ]]; then
    if [[ $EUID -ne 0 ]]; then
        err "--system requires root. Run with sudo."
        exit 1
    fi
    DST_DIR="/usr/share/color-schemes"
else
    DST_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/color-schemes"
fi

mkdir -p "$DST_DIR"

# ---- Verify source ---------------------------------------------------------
if [[ ! -d "$SRC_DIR" ]]; then
    err "Color schemes folder not found: $SRC_DIR"
    exit 1
fi

# ---- Summary before install ------------------------------------------------
cap() { local s="$1"; echo "${s^}"; }

echo
printf "%s%sBookOS Color Scheme Installer%s\n" "$C_BOLD" "$C_BLUE" "$C_RESET"
printf "%s\n" "$(printf '%.0s=' {1..32})"
info "Destination: $DST_DIR"
info "Colors:      ${COLORS[*]}"
info "Modes:       ${MODES[*]}"
echo

# ---- Install ---------------------------------------------------------------
installed=0
skipped=0
missing=0

for mode in "${MODES[@]}"; do
    for color in "${COLORS[@]}"; do
        name="BookOS$(cap "$mode")$(cap "$color").colors"
        src="$SRC_DIR/$name"
        dst="$DST_DIR/$name"

        if [[ ! -f "$src" ]]; then
            warn "Missing source: $name"
            missing=$((missing+1))
            continue
        fi

        if [[ -f "$dst" && $FORCE -ne 1 ]]; then
            read -rp "$(printf '%s[?]%s %s exists. Overwrite? [y/N] ' "$C_YELLOW" "$C_RESET" "$name")" ans
            if [[ ! "$ans" =~ ^[Yy]$ ]]; then
                skipped=$((skipped+1))
                continue
            fi
        fi

        cp "$src" "$dst"
        ok "Installed $name"
        installed=$((installed+1))
    done
done

echo
printf "%s\n" "$(printf '%.0s-' {1..32})"
ok "Installed: $installed"
[[ $skipped -gt 0 ]] && warn "Skipped:   $skipped"
[[ $missing -gt 0 ]] && warn "Missing:   $missing"
echo
info "Activate from: System Settings -> Colors"
