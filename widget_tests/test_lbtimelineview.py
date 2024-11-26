import random
from PySide6 import QtWidgets, QtCore, QtGui
from timecode import Timecode


class LBTimelineView(QtWidgets.QWidget):
	"""A little timeline layout graphic thing"""

	def setBottomMargin(self, margin:int):
		self._bottom_margin = margin

	def setCornerRadius(self, radius:int):
		self._corner_radius = radius

	# Debug
	def setThings(self, things:list[int]):
		self._things = things
		self._pallette = [QtGui.QColor.fromHsvF(x/len(things), .6, .65) for x in range(len(things))]
		self._total = sum(things)
		self.update()

	def paintEvent(self, e:QtGui.QPaintEvent):

		painter = QtGui.QPainter(self)

		rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
		brush = QtGui.QBrush()

		x_pos = 0
		for idx, thing in enumerate(self._things):

			painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

			rect = QtCore.QRectF(x_pos, 0, (thing/self._total)*(painter.device().width()), painter.device().height() - self._bottom_margin)
			
			brush.setColor(self._pallette[idx])
			brush.setStyle(QtGui.Qt.SolidPattern)

			pen = QtGui.QPen()
			pen.setColor(QtGui.QColor("Black"))
			pen.setWidth(1)


			painter.setBrush(brush)
			painter.setPen(pen)

			painter.drawRoundedRect(rect, self._corner_radius, self._corner_radius)

			text_location = QtCore.QPoint(x_pos + 5, painter.device().height() - 5 - self._bottom_margin)
			painter.drawText(text_location, "SNL Reel " + str(thing))

			pen.setWidth(2)
			painter.setPen(pen)
			painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
			
			pen.setColor(QtGui.QPalette().color(QtGui.QPalette.ColorRole.Text))
			painter.setPen(pen)
			tick_text = str(Timecode(int(x_pos))).lstrip("0:") or "0:00"
			painter.drawLine(x_pos, 0, x_pos, painter.device().height() - 15)

			font_metrics = QtGui.QFontMetrics(painter.font())
			tick_text_rect = font_metrics.boundingRect(tick_text)

			tick_text_rect.moveCenter(QtCore.QPoint(max(x_pos, tick_text_rect.width()/2), painter.device().height() - tick_text_rect.height()/2-2))
			tick_text_rect.adjust(-10, 0, 10, 0)

			
			pen.setColor(QtGui.QPalette().windowText().color())
			painter.setPen(pen)
			painter.drawText(tick_text_rect, QtCore.Qt.AlignmentFlag.AlignCenter, tick_text)
			

			x_pos += (thing/self._total)*(painter.device().width())

		pen.setWidth(2)
		painter.setPen(pen)
		painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
		
		tick_text = str(Timecode(int(x_pos))).lstrip("0:") or "0:00"
		painter.drawLine(x_pos, 0, x_pos, painter.device().height() - 15)
		font_metrics = QtGui.QFontMetrics(painter.font())
		tick_text_rect = font_metrics.boundingRect(tick_text)

		tick_text_rect.moveCenter(QtCore.QPoint(min(x_pos, painter.device().width() - tick_text_rect.width()/2), painter.device().height() - tick_text_rect.height()/2-2))

		
		pen.setColor(QtGui.QPalette().windowText().color())
		painter.setPen(pen)
		painter.drawText(tick_text_rect, QtCore.Qt.AlignmentFlag.AlignCenter, tick_text)

		painter.end()

app = QtWidgets.QApplication()
app.setStyle("Fusion")
wnd_main = QtWidgets.QMainWindow()

wdg_main = QtWidgets.QWidget()
wdg_main.setLayout(QtWidgets.QVBoxLayout())

view_timeline = LBTimelineView()
view_timeline.setThings([random.randint(1,10) for _ in range(random.randint(1,10))])
view_timeline.setCornerRadius(0)
view_timeline.setBottomMargin(20)

wdg_main.layout().addWidget(view_timeline)
wdg_main.layout().addWidget(QtWidgets.QPushButton(text="Random", clicked=lambda: view_timeline.setThings([random.randint(1,10) for _ in range(random.randint(1,10))])))

wnd_main.setCentralWidget(wdg_main)
wnd_main.show()
app.exec()