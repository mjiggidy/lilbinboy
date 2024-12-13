from PySide6 import QtCore, QtGui, QtWidgets
from lilbinboy.lbb_common import LBClipColorPicker



		
def setLabel(label:QtWidgets.QLabel, color:QtGui.QColor):
	palette = label.palette()
	palette.setColor(QtGui.QPalette.ColorRole.WindowText, color)
	label.setPalette(palette)
	label.setText("User chose this color I guess")


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	wnd = QtWidgets.QWidget()
	wnd.setLayout(QtWidgets.QVBoxLayout())
	
	picker = LBClipColorPicker()

	picker.sig_selected_color_changed.connect(lambda color: setLabel(lbl_teller, color))

	lbl_teller = QtWidgets.QLabel()

	wnd.layout().addWidget(picker)
	wnd.layout().addWidget(lbl_teller)

	wnd.show()

	app.setStyle("Fusion")
	app.exec()

