#!/usr/bin/env bash

arch=$1
version_number=$2

# Install dependencies
echo "Installing dependencies..."
brew install imagemagick
pip install "dmgbuild[badge_icons]"

# Name the app
mv build/main.app "build/Lil' Bin Boy.app"
ls -l build

# Bake the app info into the DMG background image
magick build_tools/bkgs/macos_dmg_bkg_src.png -gravity southeast -pointsize 24 -fill black -annotate +20+20 "Lil' Bin Boy  |  macOS ${arch}  |  Version ${version_number}" build_tools/bkgs/macos_dmg_bkg@2x.png
magick build_tools/bkgs/macos_dmg_bkg@2x.png -resize 50% build_tools/bkgs/macos_dmg_bkg.png

# Make the hi-dpi background image
tiffutil -cathidpicheck build_tools/bkgs/macos_dmg_bkg.png build_tools/bkgs/macos_dmg_bkg@2x.png -out build_tools/bkgs/macos_dmg_bkg.tiff

# Prep the dist folder
mkdir dist

# Investigate format=UDZO or UDBZ
dmgbuild \
	"Lil' Bin Boy" \
	"dist/lilbinboy_macos_${version_number}_${arch}.dmg" \
	-s build_tools/mac_dmgbuild_settings.py