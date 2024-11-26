import random, math
from PySide6 import QtWidgets, QtCore, QtGui
from timecode import Timecode


class LBTimelineView(QtWidgets.QWidget):
	"""A little timeline layout graphic thing"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		# Set size hint based on two lines of text, basically
		box = QtGui.QFontMetrics("test").boundingRect("00:00:00:00")

		self.setMinimumHeight(box.height() * 2 + 6)
		self.setSizePolicy(
			QtWidgets.QSizePolicy.Policy.MinimumExpanding,
			QtWidgets.QSizePolicy.Policy.Maximum
		)

	def setBottomMargin(self, margin:int):
		self._bottom_margin = margin

	def setCornerRadius(self, radius:int):
		self._corner_radius = radius

	# Debug
	def setThings(self, things:list[int]):
		self._things = things
		self._pallette = [QtGui.QColor.fromHsvF(x/len(things), .4, .4) for x in range(len(things))]
		self._total = sum(things)
		self.update()

	def paintEvent(self, e:QtGui.QPaintEvent):

		painter = QtGui.QPainter(self)

		rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
		
		font = painter.font()
		font.setPointSize(font.pointSize() - 3)
		painter.setFont(font)

		# Determine bottom margin
		font_metrics = painter.fontMetrics()
		font_box = font_metrics.boundingRect("00:00")
		self._bottom_margin = font_box.height() + 4 # 4x padding


		x_pos = 0

		for idx, thing in enumerate(self._things):

			# Draw Box
			painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
			rect = QtCore.QRect(x_pos, 0, math.ceil((thing/self._total)*(painter.device().width())), painter.device().height() - self._bottom_margin)
			
			brush = painter.brush()
			brush.setColor(self._pallette[idx])
			brush.setStyle(QtGui.Qt.BrushStyle.SolidPattern)
			painter.setBrush(brush)
			
			pen = painter.pen()
			pen.setColor(painter.brush().color().lighter(200))
			pen.setWidth(1)
			painter.setPen(pen)
			
			painter.drawRoundedRect(rect, self._corner_radius, self._corner_radius)

			# Draw Box Label
			pen = painter.pen()
			pen.setColor(painter.brush().color().lighter(300))
			painter.setPen(pen)
			text_location = QtCore.QPoint(x_pos + 5, painter.device().height() - 5 - self._bottom_margin)
			painter.drawText(text_location, "SNL Reel " + str(idx+1))

			# Draw tick
			painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
			pen = painter.pen()
			pen.setWidth(2)
			pen.setColor(self._pallette[idx].lighter(200))
			painter.setPen(pen)

			tick_start_pos = QtCore.QPoint(max(x_pos, int(pen.width()/2)), 0)
			tick_end_pos   = QtCore.QPoint(tick_start_pos.x(), painter.device().height())

			painter.drawLine(tick_start_pos, tick_end_pos)

			# Draw Timecode
			pen = painter.pen()	
			pen.setColor(QtGui.QPalette().color(QtGui.QPalette.ColorRole.Text))
			painter.setPen(pen)
			tick_text = str(Timecode(int(x_pos))).lstrip("0:") or "0:00"
			text_location.setY(painter.device().height() - self._bottom_margin + 12)
			painter.drawText(text_location, tick_text)
			
			x_pos += (thing/self._total)*(painter.device().width())

		# Draw final tick
		painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
		pen = painter.pen()
		pen.setWidth(2)
		pen.setColor(self._pallette[-1].lighter(200))
		painter.setPen(pen)

		tick_start_pos = QtCore.QPoint(painter.device().width() - pen.width()/2, 0)
		tick_end_pos   = QtCore.QPoint(tick_start_pos.x(), painter.device().height())

		painter.drawLine(tick_start_pos, tick_end_pos)

		# Draw Final Timecode
		pen = painter.pen()	
		pen.setColor(QtGui.QPalette().color(QtGui.QPalette.ColorRole.Text))
		painter.setPen(pen)
		tick_text = str(Timecode(int(x_pos))).lstrip("0:") or "0:00"
		text_location.setY(painter.device().height() - self._bottom_margin + 12)
		
		font_metrics = painter.fontMetrics()
		font_box = font_metrics.boundingRect(tick_text)
		text_location.setX(painter.device().width() - font_box.width() - 5 - painter.pen().width())
		
		painter.drawText(text_location, tick_text)


		painter.end()
	
	def event(self, event:QtCore.QEvent):

		if event.type() is QtCore.QEvent.Type.ToolTip:
			QtWidgets.QToolTip.showText(event.globalPos(), self.toolTip(event.pos()))
		
		else:
			super().event(event)

	def toolTip(self, position:QtCore.QPoint) -> str:
		
		item_pos = 0
		for idx,item in enumerate(self._things):
			
			item_pos += (item/self._total) * self.width()
			if position.x() < item_pos:
				return f"SNL Reel {idx + 1}"
			

		

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