import sys
from os import PathLike
from PySide6 import QtCore, QtSvg, QtGui, QtWidgets
from lilbinboy.res import icons_gui
from lilbinboy.core.icon_engines import BSPalettedSvgIconEngine
	


ICON_RESOURCES = ["list","frame","script"]

app = QtWidgets.QApplication()
app.setStyle("Fusion")

window = QtWidgets.QWidget()
window.setLayout(QtWidgets.QHBoxLayout())
window.layout().setSpacing(0)

for mode in ICON_RESOURCES:

	icon_engine = BSPalettedSvgIconEngine(f":/icons/gui/view_{mode}.svg")
	icon = QtGui.QIcon(icon_engine)

	button = QtWidgets.QPushButton()
	button.setIconSize(QtCore.QSize(16,16))
	button.setIcon(icon)

	app.paletteChanged.connect(lambda pal: icon_engine.setPalette(pal))

	window.layout().addWidget(button)

window.show()

sys.exit(app.exec())