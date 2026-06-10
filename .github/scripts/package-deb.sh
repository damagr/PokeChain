#!/usr/bin/env bash
# package-deb.sh — Empaqueta el output de PyInstaller como .deb
# Uso: bash package-deb.sh <dist_dir> <app_name> <version>
# Ejecutar desde la raíz del repo.

set -euo pipefail

DIST_DIR="$1"
APP_NAME="$2"
VERSION="$3"
PACKAGE_DIR="$(mktemp -d)"

echo "=== Iniciando empaquetado .deb ==="
echo "DIST_DIR=$DIST_DIR"
echo "APP_NAME=$APP_NAME"
echo "VERSION=$VERSION"
echo "PACKAGE_DIR=$PACKAGE_DIR"

# Crear estructura
mkdir -p "$PACKAGE_DIR/DEBIAN"
mkdir -p "$PACKAGE_DIR/usr/bin"
mkdir -p "$PACKAGE_DIR/usr/share/applications"
mkdir -p "$PACKAGE_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$PACKAGE_DIR/opt/$APP_NAME"

# Copiar ejecutable y recursos
SRC_DIR="$DIST_DIR/$APP_NAME"
echo "Copiando desde: $SRC_DIR"
if [ ! -d "$SRC_DIR" ]; then
    echo "ERROR: Directorio origen no existe: $SRC_DIR"
    ls -la "$DIST_DIR/"
    exit 1
fi

cp -a "$SRC_DIR"/* "$PACKAGE_DIR/opt/$APP_NAME/" || {
    echo "ERROR: Falló cp desde $SRC_DIR"
    ls -la "$SRC_DIR/"
    exit 1
}

ln -sf "/opt/$APP_NAME/$APP_NAME" "$PACKAGE_DIR/usr/bin/$APP_NAME"

# Buscar .desktop e icono relativos a la raíz del repo
FOR_DESKTOP=".github/scripts/$APP_NAME.desktop"
FOR_ICON="icono.png"

if [ ! -f "$FOR_DESKTOP" ]; then
    FOR_DESKTOP="build/$APP_NAME.desktop"
fi
if [ ! -f "$FOR_DESKTOP" ]; then
    echo "ERROR: $APP_NAME.desktop no encontrado"
    exit 1
fi
if [ ! -f "$FOR_ICON" ]; then
    echo "ERROR: icono.png no encontrado"
    exit 1
fi

cp "$FOR_DESKTOP" "$PACKAGE_DIR/usr/share/applications/"
cp "$FOR_ICON" "$PACKAGE_DIR/usr/share/icons/hicolor/256x256/apps/$APP_NAME.png"

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

find "$PACKAGE_DIR" -type d -exec chmod 755 {} \;

# chmod del ejecutable si existe
EXE_PATH="$PACKAGE_DIR/opt/$APP_NAME/$APP_NAME"
if [ -f "$EXE_PATH" ]; then
    chmod 755 "$EXE_PATH"
fi

# chmod del symlink
SYMLINK="$PACKAGE_DIR/usr/bin/$APP_NAME"
if [ -L "$SYMLINK" ]; then
    chmod 755 "$SYMLINK" 2>/dev/null || true
fi

# chmod de .so si existen
find "$PACKAGE_DIR/opt/$APP_NAME" -name '*.so' -exec chmod 755 {} \; 2>/dev/null || true

# Construir .deb
DEB_FILE="$DIST_DIR/${APP_NAME}_${VERSION}_amd64.deb"
echo "Construyendo .deb: $DEB_FILE"
dpkg-deb -Zxz --build "$PACKAGE_DIR" "$DEB_FILE" || {
    echo "ERROR: dpkg-deb falló"
    exit 1
}

# Cleanup
rm -rf "$PACKAGE_DIR"

echo "OK: $DEB_FILE"
ls -la "$DEB_FILE"