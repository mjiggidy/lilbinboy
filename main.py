# Compilation configuration for Nuitka
# ---
# nuitka-project: --standalone
# nuitka-project: --deployment
# nuitka-project: --plugin-enable=pyside6
# nuitka-project: --disable-ccache
# nuitka-project: --output-filename="lilbinboy"
# nuitka-project: --output-dir="dist/"
# nuitka-project: --remove-output
# nuitka-project: --assume-yes-for-downloads
# nuitka-project: --noinclude-setuptools-mode="nofollow"
# ---

# Winders Stuff
# ---
# nuitka-project: --windows-console-mode="disable"
# ---

# macOS Stuff
# ---
# nuitka-project: --macos-create-app-bundle
# nuitka-project: --macos-app-name="Lil' Bin Boy"
# nuitka-project: --macos-app-version=
# nuitka-project: --macos-signed-app-name="com.glowingpixel.lilbinboy"
# ---

# Metadata Stuff
# ---
# nuitka-project: --company-name="GlowingPixel"
# nuitka-project: --product-name="lilbinboy"
# nuitka-project: --product-version=
# nuitka-project: --file-version=
# nuitka-project: --copyright="(c) Copyright Michael Jordan 2025"
# ---

import lilbinboy

if __name__ == "__main__":
	import multiprocessing
	multiprocessing.freeze_support()
	lilbinboy.main()