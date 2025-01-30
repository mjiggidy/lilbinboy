# Compilation configuration for Nuitka
# ---
# nuitka-project: --mode=app
# nuitka-project: --onefile-tempdir-spec="{CACHE_DIR}/{COMPANY}/{PRODUCT}/{VERSION}"
# nuitka-project: --deployment
# nuitka-project: --output-filename="lilbinboy"
# nuitka-project: --output-dir="dist/"
# nuitka-project: --remove-output
# nuitka-project: --plugin-enable=pyside6
# nuitka-project: --include-qt-plugins=sqldrivers
# nuitka-project: --noinclude-setuptools-mode="nofollow"
# ---

# Addtional flags for local builds
# (Probably not needed for Github Actions)
# ---
# nuitka-project: --disable-ccache
# nuitka-project: --assume-yes-for-downloads
# ---

# Winders Stuff
# ---
# nuitka-project: --windows-console-mode="disable"
# ---

# macOS Stuff
# ---
# nuitka-project: --macos-app-name="Lil' Bin Boy"
# nuitka-project: --macos-app-icon="build_tools/icons/macos_lilbinboy.icns"
# nuitka-project: --macos-app-version=
# nuitka-project: --macos-signed-app-name="com.glowingpixel.lilbinboy"
# ---

# Metadata Stuff
# ---
# nuitka-project: --company-name="GlowingPixel"
# nuitka-project: --product-name="lilbinboy"
# nuitka-project: --product-version=0.0.0.1
# nuitka-project: --file-version=0.0.0.1
# nuitka-project: --copyright="(c) Copyright Michael Jordan 2025"
# ---

import lilbinboy
import multiprocessing

if __name__ == "__main__":
	multiprocessing.freeze_support()
	lilbinboy.main()