from __future__ import annotations

from os import PathLike

from lilbinboy import binwatcher

def watch_bin(bin_path:PathLike):

	print("Watching ", bin_path)

if __name__ == "__main__":

	import sys, pathlib

	if not len(sys.argv) > 1:
		sys.exit(f"Usage: {pathlib.Path(sys.argv[0]).name} avid_bin.avb")
	
	binwatcher.BSBinLockWatcher(sys.argv[1])