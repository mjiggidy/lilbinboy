import random
from PySide6 import QtCore, QtGui, QtWidgets
from lilbinboy.lbb_common.paint_delegates import LBClipColorPainter

@QtCore.Slot()
def rand_icon_size():
	rand_size = random.choice(icon.availableSizes())
	lbl_icon.setPixmap(icon.pixmap(rand_size))
	lbl_status.setText("Set random size: " + str(rand_size))

app = QtWidgets.QApplication()
#app.setStyle("Fusion")

icon = QtGui.QIcon()
sizes = [16, 24, 32, 48, 64, 128, 256, 512]

for size in sizes:
	
	pix_clip_color = QtGui.QPixmap(QtCore.QSize(size,size))
	pix_clip_color.fill(QtCore.Qt.GlobalColor.transparent)

	rand_clip_color = QtGui.QColor(random.randint(0,255), random.randint(0,255), random.randint(0,255))
	
	painter = QtGui.QPainter(pix_clip_color)
	LBClipColorPainter(pix_clip_color.rect(), painter, pen_width=1, shadow_offset=QtCore.QPoint(1,1), padding=QtCore.QSize(2,2), clip_color=rand_clip_color)
	
	pen = painter.pen()
	pen.setColor(rand_clip_color.darker())
	painter.setPen(pen)
	painter.drawText(pix_clip_color.rect().translated(1,1), str(size), QtCore.Qt.AlignmentFlag.AlignCenter|QtCore.Qt.AlignmentFlag.AlignVCenter)

	pen.setColor(rand_clip_color.lighter())
	painter.setPen(pen)
	painter.drawText(pix_clip_color.rect(), str(size), QtCore.Qt.AlignmentFlag.AlignCenter|QtCore.Qt.AlignmentFlag.AlignVCenter)
	
	painter.end()

	icon.addPixmap(pix_clip_color)
	#pix_clip_color.setDevicePixelRatio(2)
	#icon.addPixmap(pix_clip_color)


wnd_main = QtWidgets.QWidget()

wnd_main.setWindowTitle("Hey:)")
wnd_main.setLayout(QtWidgets.QVBoxLayout())

rand_size = sizes[random.randint(0, len(sizes) -1)]


lbl_icon =  QtWidgets.QLabel()
lbl_icon.setFixedSize(max(icon.availableSizes(), key=lambda s: s.width()))
lbl_icon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter|QtCore.Qt.AlignmentFlag.AlignVCenter)
lbl_icon.setPixmap(icon.pixmap(rand_size,rand_size))

btn_icon = QtWidgets.QPushButton()

btn_icon.setIcon(icon)
btn_icon.setText("Hi :3")
btn_icon.clicked.connect(rand_icon_size)

lbl_status = QtWidgets.QLabel()
lbl_status.setFrameShadow(QtWidgets.QLabel.Shadow.Sunken)
lbl_status.setFrameShape(QtWidgets.QLabel.Shape.WinPanel)
lbl_status.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter|QtCore.Qt.AlignmentFlag.AlignVCenter)

txt_info = QtWidgets.QPlainTextEdit()
txt_info.setPlainText(str(icon))

wnd_main.layout().addWidget(lbl_icon)
wnd_main.layout().addWidget(btn_icon)
wnd_main.layout().addWidget(lbl_status)
wnd_main.layout().addWidget(txt_info)

wnd_main.show()
app.exec()