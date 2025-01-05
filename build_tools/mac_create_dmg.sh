#!/usr/bin/env bash

arch=$1
version_number=$2

# Install dependencies
echo "Installing dependencies..."
brew install imagemagick
brew install create-dmg

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

echo "Creating DMG..."
create-dmg \
	--volname "Lil' Bin Boy!" \
	--volicon "build_tools/icons/macos_lilbinboy.icns" \
	--background "build_tools/bkgs/macos_dmg_bkg.tiff" \
	--window-size 500 250 \
	--icon-size 128 \
	--icon "Lil' Bin Boy.app" 100 50 \
	--app-drop-link 600 50 \
	--skip-jenkins \
	--no-internet-enable \
	--eula "EULA"\
	"dist/lilbinboy_macos_${arch}_v${version_number}.dmg" \
	"build/"