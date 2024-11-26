import re, math
import avbutils
from PySide6 import QtWidgets, QtCore, QtGui
from timecode import Timecode

class LBUtilityTab(QtWidgets.QWidget):
	"""Lil' Utility Container Boy"""



class LBMainTabs(QtWidgets.QTabWidget):
	"""Lil' Tab Manager Boy"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		#self.addTab(LBTRTCalculator(), "TRT Calculator")
		#self.addTab(LBUtilityTab(), "Continuity Generator")
		#self.addTab(LBUtilityTab(), "Lock Jockey")
		#self.addTab(LBUtilityTab(), "Batch Bin Boy")



class LBMainWindow(QtWidgets.QMainWindow):
	"""Lil' Main Window Boy"""

	sig_resized = QtCore.Signal(QtCore.QRect)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setCentralWidget(LBMainTabs())

	def moveEvent(self, event):
		super().moveEvent(event)
		self.sig_resized.emit(self.geometry())


	def resizeEvent(self, event):
		super().resizeEvent(event)
		self.sig_resized.emit(self.geometry())

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
	def setThings(self, things:list[tuple[str,int]]):
		self._things = things
		self._pallette = [QtGui.QColor.fromHsvF(x/len(things), .4, .4) for x in range(len(things))]
		self._total = sum([dur for sequence_name, dur in things])
		self.update()

	def paintEvent(self, e:QtGui.QPaintEvent):

		super().paintEvent(e)

		if not len(self._things):
			return

		painter = QtGui.QPainter(self)

		rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
		
		font = painter.font()
		font.setPointSize(font.pointSize() - 2)
		painter.setFont(font)

		# Determine bottom margin
		font_metrics = painter.fontMetrics()
		font_box = font_metrics.boundingRect("00:00")
		self._bottom_margin = font_box.height() + 4 # 4x padding


		x_pos = 0
		cumulative = 0

		for idx, thing in enumerate(self._things):

			sequence_name, sequence_duration = thing

			# Draw Box
			painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
			rect = QtCore.QRect(x_pos, 0, math.ceil((sequence_duration/self._total)*(painter.device().width())), painter.device().height() - self._bottom_margin)
			
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
			painter.drawText(text_location, sequence_name)

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
			tick_text = str(Timecode(int(cumulative))).lstrip("0:") or "0:00"
			text_location.setY(painter.device().height() - self._bottom_margin + 12)
			painter.drawText(text_location, tick_text)
			
			x_pos += (sequence_duration/self._total)*(painter.device().width())
			cumulative += sequence_duration

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
		tick_text = str(Timecode(int(cumulative))).lstrip("0:") or "0:00"
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

			sequence_name, sequence_duration = item
			
			item_pos += (sequence_duration/self._total) * self.width()
			if position.x() < item_pos:
				return f"{sequence_name} ({Timecode(sequence_duration)})"



class LBSpinBoxTC(QtWidgets.QSpinBox):

	PAT_VALID_TEXT = re.compile(r"^(\d+:){0,3}\d+$")
	PAT_INTER_TEXT = re.compile(r"^(\d+:?){1,4}$")

	sig_timecode_changed = QtCore.Signal(Timecode)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		self._rate = 24
		self._allow_negative = False
		self.valueChanged.connect(lambda: self.sig_timecode_changed.emit(self.timecode()))
	
	@QtCore.Slot()
	def setRate(self, rate:int):
		self._rate = rate
		self.updateMaximumTC()
		self.sig_timecode_changed.emit(self.timecode())

	@QtCore.Slot()
	def updateMaximumTC(self):
		self.setMaximum(Timecode("100:00:00:00", rate=self.rate()).frame_number)
		self.setMinimum(Timecode("-100:00:00:00", rate=self.rate()).frame_number if self.allowNegative() else Timecode(0, rate=self.rate()).frame_number)

	def validate(self, input:str, pos:int) -> bool:

		# Allow for one '-' if negative is allowed, by stripping it off for validation
		if self.allowNegative() and input.startswith("-"):
			input = input[1:]

		if self.__class__.PAT_VALID_TEXT.match(input):
			return QtGui.QValidator.State.Acceptable 
		elif self.__class__.PAT_INTER_TEXT.match(input):
			return QtGui.QValidator.State.Intermediate
		elif input == "":
			return QtGui.QValidator.State.Intermediate 
		else:
			return QtGui.QValidator.State.Invalid
	
	@QtCore.Slot(Timecode)
	def setTimecode(self, timecode:Timecode):
		self.setRate(timecode.rate)
		self.setValue(timecode.frame_number)
	
	def setAllowNegative(self, allow:bool):
		if allow != self.allowNegative():
			self._allow_negative = allow
			self.updateMaximumTC()

	def allowNegative(self) -> bool:
		return self._allow_negative
	
	def timecode(self) -> Timecode:
		return Timecode(self.value(), rate=self.rate())

	def rate(self) -> int:
		return self._rate
	
	def textFromValue(self, val:int) -> str:
		return str(Timecode(val, rate=self.rate()))
	
	def valueFromText(self, text:str) -> int:
		return Timecode(text, rate=self.rate()).frame_number

class LBBClipColorPicker(QtWidgets.QWidget):
	"""Clip color picker widget"""

	sig_color_chosen = QtCore.Signal(avbutils.ClipColor)

	class LBBColorButton(QtWidgets.QPushButton):
		"""Click color picker button"""

		sig_color_chosen = QtCore.Signal(avbutils.ClipColor)

		def __init__(self, color:QtGui.QRgba64, *args, **kwargs):
			
			super().__init__(*args, **kwargs)

			#self.setFlat(True)
			
			self._clip_color = None

			self.setClipColor(color)

			self.clicked.connect(lambda: self.sig_color_chosen.emit(self.clipColor()))
		
		def setClipColor(self, color:avbutils.ClipColor):
			"""Set the color the button represents"""

			self._clip_color = color

			# Setup Button Visual Color
			p = self.palette()
			p.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor.fromRgba64(*self._clip_color.as_rgb16(), self._clip_color.max_16b()))
			self.setPalette(p)

			# Setup tooltip
			rgb8 = self.palette().color(QtGui.QPalette.ColorRole.Button)
			self.setToolTip(f"R: {rgb8.red()}  G: {rgb8.green()}  B: {rgb8.blue()}")

		def clipColor(self):
			"""The color the button represents"""
			return self._clip_color
		
	def __init__(self):
		super().__init__()

		self.setLayout(QtWidgets.QGridLayout())
		self.buttonGroup = QtWidgets.QButtonGroup()
		#self.layout().setContentsMargins(0,0,0,0)
		self.layout().setSpacing(0)

		for idx, color in enumerate(avbutils.get_default_clip_colors()):
			b = self.LBBColorButton(color)
			self.buttonGroup.addButton(b)
			b.setContentsMargins(0,0,0,0)
			b.setFixedSize(24,24)
			b.setCheckable(True)
			
			self.layout().addWidget(b, idx//8, idx%8)
		
		self.buttonGroup.buttonClicked.connect(lambda b: self.sig_color_chosen.emit(b.clipColor()))