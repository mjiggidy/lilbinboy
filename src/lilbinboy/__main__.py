from os import PathLike
from .core import application

def main(bin_paths:list[PathLike]) -> int:
	
	app = application.BSMainApplication()

	for bin_path in bin_paths:
		wnd = app.createMainWindow()
		wnd.loadBinFromPath(bin_path)
	
	if not bin_paths:
		wnd = app.createMainWindow(is_first_window=True)
		
	return app.exec()
	

if __name__ == "__main__":
	
	import sys
	sys.exit(main(sys.argv[1:]))