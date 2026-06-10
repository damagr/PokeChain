#!/usr/bin/env bash
# package-deb.sh — Empaqueta el output de PyInstaller como .deb
# Uso: bash package-deb.sh <dist_dir> <app_name> <version>

set -euo pipefail

DIST_DIR="$1"
APP_NAME="$2"
VERSION="$3"
PACKAGE_DIR="$(mktemp -d)"

# Crear estructura
mkdir -p "$PACKAGE_DIR/DEBIAN"
mkdir -p "$PACKAGE_DIR/usr/bin"
mkdir -p "$PACKAGE_DIR/usr/share/applications"
mkdir -p "$PACKAGE_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$PACKAGE_DIR/opt/$APP_NAME"

# Copiar ejecutable y recursos
cp -a "$DIST_DIR/$APP_NAME"/* "$PACKAGE_DIR/opt/$APP_NAME/"
ln -sf "/opt/$APP_NAME/$APP_NAME" "$PACKAGE_DIR/usr/bin/$APP_NAME"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cp "$SCRIPT_DIR/$APP_NAME.desktop" "$PACKAGE_DIR/usr/share/applications/"
cp "$PROJECT_DIR/icono.png" "$PACKAGE_DIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png"

# Control file
cat > "$PACKAGE_DIR/DEBIAN/control" <<EOF
Package: $APP_NAME
Version: $VERSION
Section: games
Priority: optional
Architecture: amd64
Depends: python3 (>= 3.10), libnotify-bin
Maintainer: PokeChain Team
Description: Pokemon search string generator
 Genera cadenas de busqueda optimizadas de Pokemon
 usando rankings de PvPoke y DialgaDex.
EOF

# Fijar permisos y construir .deb
chmod 755 "$PACKAGE_DIR/DEBIAN"
chmod 644 "$PACKAGE_DIR/DEBIAN/control"

find "$PACKAGE_DIR" -type d -exec chmod 755 {} +
find "$PACKAGE_DIR/opt/$APP_NAME/_internal" -name '*.so' -exec chmod 755 {} +
chmod 755 "$PACKAGE_DIR/opt/$APP_NAME/$APP_NAME"
chmod 755 "$PACKAGE_DIR/usr/bin/$APP_NAME"

# Construir .deb
DEB_FILE="$DIST_DIR/${APP_NAME}_${VERSION}_amd64.deb"
dpkg-deb -Zxz --build "$PACKAGE_DIR" "$DEB_FILE"

# Cleanup
rm -rf "$PACKAGE_DIR"

echo "OK: $DEB_FILE"
