import sys
import avb, avbutils
from PySide6 import QtCore, QtGui, QtWidgets

from lilbinboy.widgets import toolboxes

if __name__ == "__main__":

	app = QtWidgets.QApplication()

	app.setStyle("Fusion")

	win_appearance = toolboxes.BSBinAppearanceSettingsView()

	win_appearance.setWindowFlag(QtCore.Qt.WindowType.Tool)

	win_appearance.show()
	

	sys.exit(app.exec())

