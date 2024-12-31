from PySide6 import QtWidgets, QtCore, QtGui
from lilbinboy import lbb_common, lbb_features, Config, main
#from .lbb_common import resources
import pathlib



if __name__ == "__main__":
	import multiprocessing
	multiprocessing.freeze_support()
	main()