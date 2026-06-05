import sys

from PySide6 import QtCore, QtGui, QtWidgets

from lilbinboy.binwidget import scrollwidgets
from lilbinboy.widgets import buttons
from lilbinboy.core import icon_engines
from lilbinboy.res import icons_gui

class MyKewlTestWindow(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QHBoxLayout())

		self._scroll = QtWidgets.QScrollArea()
		self._scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

		self._scroll.addScrollBarWidget(
			scrollwidgets.BSBinStatsLabel("Showing 12 of 14,000"), QtCore.Qt.AlignmentFlag.AlignLeft
		)
		
		self.layout().addWidget(self._scroll)

		

	def addButton(self, button:buttons.BSPalettedActionPushButton):

		self._scroll.addScrollBarWidget(button, QtCore.Qt.AlignmentFlag.AlignLeft)


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = MyKewlTestWindow()
	wnd.setMinimumSize(QtCore.QSize(400, 100))
	wnd.show()

	
	#act.setIcon(QtGui.QIcon(":/icons/gui/toggle_frame_ruler.svg"))
	#act.setCheckable(True)

	for svg in [
		":/icons/gui/toggle_frame_ruler.svg",
		":/icons/gui/toggle_frame_grid.svg",
		":/icons/gui/toggle_frame_map.svg",
		":/icons/gui/toggle_frame_showall.svg",
		":/icons/gui/toggle_appearance.svg",
	]:
	
		butt = buttons.BSPalettedActionPushButton(QtGui.QAction(checkable=True), show_text=False, icon_engine=icon_engines.BSPalettedSvgIconEngine(svg))
		butt.setFixedWidth(16)
		butt.setIconSize(QtCore.QSize(8,8))
		#butt.setFixedSize(QtCore.QSize(16,16))

		wnd.addButton(
			butt
		)






	sys.exit(app.exec())