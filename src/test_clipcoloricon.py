import sys
import avbutils
from os import PathLike
from PySide6 import QtCore, QtSvg, QtGui, QtWidgets
from lilbinboy.res import icons_gui
from lilbinboy.core.icon_engines import BSPalettedClipColorIconEngine, BSPaletteWatcherForSomeReason, BSPalettedMarkerIconEngine

app = QtWidgets.QApplication()
app.setStyle("Fusion")

window_colorchips = QtWidgets.QWidget()
window_colorchips.setLayout(QtWidgets.QHBoxLayout())
window_colorchips.layout().setSpacing(0)

palette_watcher = BSPaletteWatcherForSomeReason()
app.paletteChanged.connect(palette_watcher.setPalette)

for color in avbutils.get_default_clip_colors():

	chip_color  = QtGui.QColor(*color.as_rgb8())
	chip_engine = BSPalettedClipColorIconEngine(chip_color, palette_watcher)

	window_colorchips.layout().addWidget(
		QtWidgets.QPushButton(
			icon=QtGui.QIcon(chip_engine))
	)

window_colorchips.show()

window_markers = QtWidgets.QWidget()
window_markers.setLayout(QtWidgets.QHBoxLayout())
window_markers.layout().setSpacing(0)

for marker_color in avbutils.MarkerColors:

	marker_engine = BSPalettedMarkerIconEngine(
		QtGui.QColor(marker_color.value),
		palette_watcher
	)

	window_markers.layout().addWidget(
		QtWidgets.QPushButton(
			icon=QtGui.QIcon(marker_engine)
		)
	)

window_markers.layout().addWidget(
	QtWidgets.QPushButton(
		icon=QtGui.QIcon(BSPalettedMarkerIconEngine(
			QtGui.QColor(),
			palette_watcher
		))
	)
)

window_markers.show()

sys.exit(app.exec())