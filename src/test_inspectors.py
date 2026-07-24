import sys
from PySide6 import QtCore, QtWidgets

from lilbinboy.appearanceeditor import appearancewidget

if __name__ == "__main__":

	app = QtWidgets.QApplication()

	app.setStyle("Fusion")

	win_appearance = appearancewidget.BSBinAppearanceSettingsView()

	win_appearance.setWindowFlag(QtCore.Qt.WindowType.Tool)

	win_appearance.show()
	

	sys.exit(app.exec())

