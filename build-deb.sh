#!/bin/bash
set -e

VERSION="0.1.0"
PKGNAME="barulho"
PKGDIR="${PKGNAME}_${VERSION}"

echo "Building ${PKGNAME} ${VERSION} .deb package..."

# Clean previous build
rm -rf "$PKGDIR" "${PKGDIR}.deb"

# Create directory structure
mkdir -p "$PKGDIR/DEBIAN"
mkdir -p "$PKGDIR/usr/bin"
mkdir -p "$PKGDIR/usr/share/barulho"
mkdir -p "$PKGDIR/usr/share/applications"
mkdir -p "$PKGDIR/usr/share/icons/hicolor/scalable/apps"

# Copy application files
cp -r barulho "$PKGDIR/usr/share/barulho/"
cp run.py "$PKGDIR/usr/share/barulho/"

# Create launcher script
cat > "$PKGDIR/usr/bin/barulho" << 'EOF'
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/usr/share/barulho')
from barulho.main import main
main()
EOF
chmod +x "$PKGDIR/usr/bin/barulho"

# Copy desktop entry and icon
cp barulho.desktop "$PKGDIR/usr/share/applications/"
cp icons/barulho.svg "$PKGDIR/usr/share/icons/hicolor/scalable/apps/"

# Create control file
cat > "$PKGDIR/DEBIAN/control" << EOF
Package: barulho
Version: ${VERSION}
Section: sound
Priority: optional
Architecture: all
Depends: python3 (>= 3.10), python3-gi, python3-gi-cairo, gir1.2-gtk-4.0, gstreamer1.0-plugins-good, gstreamer1.0-plugins-bad, python3-rtmidi
Maintainer: Your Name <your.email@example.com>
Description: MIDI sample player
 Barulho plays audio samples in response to MIDI events.
 Supports MIDI over Bluetooth, per-mapping volume and velocity
 sensitivity, and auto-saves configuration.
EOF

# Create postinst to update icon cache
cat > "$PKGDIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor || true
fi
EOF
chmod +x "$PKGDIR/DEBIAN/postinst"

# Build the package
dpkg-deb --build "$PKGDIR"

# Clean up
rm -rf "$PKGDIR"

echo "Done! Package created: ${PKGDIR}.deb"
echo "Install with: sudo dpkg -i ${PKGDIR}.deb"
