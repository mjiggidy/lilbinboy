from PySide6 import QtCore, QtGui, QtWidgets
from lilbinboy.lbb_common.paint_delegates import LBClipColorPainter

def make_icon(clip_color:QtGui.QColor):

	pix_icon = QtGui.QPixmap(QtCore.QSize(16, 16))
	pix_clip_color.fill(QtCore.Qt.GlobalColor.transparent)
	painter = QtGui.QPainter(pix_icon)
	LBClipColorPainter(pix_icon.rect(), painter, clip_color=clip_color)
	painter.end()
	return QtGui.QIcon(pix_clip_color)
		


app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd_main = QtWidgets.QWidget()

wnd_main.setWindowTitle("Hey:)")
wnd_main.setLayout(QtWidgets.QVBoxLayout())

pix_clip_color = QtGui.QPixmap(QtCore.QSize(48,48))
pix_clip_color.fill(QtCore.Qt.GlobalColor.transparent)

painter = QtGui.QPainter(pix_clip_color)
LBClipColorPainter(pix_clip_color.rect(), painter, pen_width=3, shadow_offset=QtCore.QPoint(2,2), padding=QtCore.QSize(8,8), clip_color=QtGui.QColor("Magenta"))
painter.end()

lbl_icon =  QtWidgets.QLabel()
lbl_icon.setPixmap(pix_clip_color)

btn_icon = QtWidgets.QPushButton()

icn=make_icon(QtGui.QColor("Blue"))
print(icn)
btn_icon.setIcon(icn)
btn_icon.setText("Hi")

wnd_main.layout().addWidget(lbl_icon)
wnd_main.layout().addWidget(btn_icon)

wnd_main.show()
app.exec()