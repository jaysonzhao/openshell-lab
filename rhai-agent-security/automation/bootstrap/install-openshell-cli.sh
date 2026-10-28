#!/usr/bin/env bash
set -euo pipefail

VERSION="${OPENSHELL_VERSION:-0.0.103}"
INSTALL_DIR="${OPENSHELL_INSTALL_DIR:-$HOME/.local/bin}"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

case "$(uname -s):$(uname -m)" in
  Darwin:arm64)
    ASSET="openshell-aarch64-apple-darwin.tar.gz"
    ;;
  Linux:x86_64)
    ASSET="openshell-x86_64-unknown-linux-musl.tar.gz"
    ;;
  Linux:aarch64|Linux:arm64)
    ASSET="openshell-aarch64-unknown-linux-musl.tar.gz"
    ;;
  *)
    printf 'Unsupported host. Use a RHEL/Fedora bastion or validated WSL2 Linux environment.\n' >&2
    exit 1
    ;;
esac

ARCHIVE="$TMP_DIR/openshell.tar.gz"
URL="https://github.com/NVIDIA/OpenShell/releases/download/v${VERSION}/${ASSET}"
CHECKSUMS="$TMP_DIR/openshell-checksums-sha256.txt"
CHECKSUMS_URL="https://github.com/NVIDIA/OpenShell/releases/download/v${VERSION}/openshell-checksums-sha256.txt"

mkdir -p "$INSTALL_DIR"
curl -fsSL "$URL" -o "$ARCHIVE"
curl -fsSL "$CHECKSUMS_URL" -o "$CHECKSUMS"
EXPECTED_SHA256=$(awk -v asset="$ASSET" '$2 == asset { print $1 }' "$CHECKSUMS")
if [[ -z "$EXPECTED_SHA256" ]]; then
  printf 'No SHA-256 entry found for %s\n' "$ASSET" >&2
  exit 1
fi
if command -v sha256sum >/dev/null 2>&1; then
  ACTUAL_SHA256=$(sha256sum "$ARCHIVE" | awk '{ print $1 }')
else
  ACTUAL_SHA256=$(shasum -a 256 "$ARCHIVE" | awk '{ print $1 }')
fi
if [[ "$ACTUAL_SHA256" != "$EXPECTED_SHA256" ]]; then
  printf 'SHA-256 verification failed for %s\n' "$ASSET" >&2
  exit 1
fi
tar xzf "$ARCHIVE" -C "$TMP_DIR"
install -m 0755 "$TMP_DIR/openshell" "$INSTALL_DIR/openshell"

if [[ "$(uname -s)" == "Darwin" ]]; then
  xattr -d com.apple.quarantine "$INSTALL_DIR/openshell" 2>/dev/null || true
fi

printf 'Installed OpenShell %s at %s\n' "$VERSION" "$INSTALL_DIR/openshell"
printf 'Add this directory to PATH if needed: %s\n' "$INSTALL_DIR"
