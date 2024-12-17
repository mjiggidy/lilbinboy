import re, math, random
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

		self.tabs = LBMainTabs()

		self.setCentralWidget(QtWidgets.QWidget())
		self.centralWidget().setLayout(QtWidgets.QVBoxLayout())
		self.centralWidget().layout().setContentsMargins(3,3,3,3)
		self.centralWidget().layout().addWidget(self.tabs)

		lay_id = QtWidgets.QHBoxLayout()

		self.lbl_lbb = QtWidgets.QLabel("<strong>Lil' Bin Boy</strong><br/>Pre Alpha Nightmare v0.1<br/>Report good and bad things to <a href=\"mailto:michael@glowingpixel.com\">michael@glowingpixel.com</a>")
		self.lbl_lbb.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)

		self.lbl_lbbicon = QtWidgets.QLabel()
		self.lbl_lbbicon.setPixmap(QtGui.QPixmap("lilbinboy/logos/256x256.png").scaledToHeight(48))

		lay_id.addWidget(self.lbl_lbbicon)
		lay_id.addWidget(self.lbl_lbb)
		self.centralWidget().layout().addLayout(lay_id)

	def moveEvent(self, event):
		super().moveEvent(event)
		self.sig_resized.emit(self.geometry())


	def resizeEvent(self, event):
		super().resizeEvent(event)
		self.sig_resized.emit(self.geometry())

class LBClipColorPicker(QtWidgets.QWidget):
	"""A picker of Avid clip colors for you"""

	sig_hovered_color_changed = QtCore.Signal(QtGui.QColor)
	sig_selected_color_changed = QtCore.Signal(QtGui.QColor)

	def __init__(self, colors:list[QtGui.QColor]|None=None, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setMouseTracking(True)

		self._colors = colors if colors is not None else [QtGui.QColor.fromRgba64(*a.as_rgba16()) for a in avbutils.get_default_clip_colors()]
		self._max_colors_per_row = 8

		self._color_background = QtGui.QColor(0,0,0)
		self._border_common_width = 1
		self._border_hover_width = 1
		self._border_selected_width = 2

		self._hovered_index = None
		self._selected_index = None

	def borderCommonWidth(self) -> int:
		return self._border_common_width
	
	def setBorderCommonWidth(self, width:int):
		self._border_common_width = width

	def borderHoverWidth(self) -> int:
		return self._border_hover_width
	
	def setBorderHoverWidth(self, width:int):
		self._border_hover_width = width
		
	def borderSelectedWidth(self) -> int:
		return self._border_selected_width
	
	def setBorderSelectedWidth(self, width:int) -> int:
		self._border_selected_width = width
	
	def colorSize(self) -> QtCore.QSize:
		"""Calculate color size"""
		width = self.width() / min(self.maxColorsPerRow(), len(self.colors()))
		height = self.height() / (len(self.colors()) // self.maxColorsPerRow())
		return QtCore.QSize(width, height)
	
	def calculatedPaletteSize(self) -> QtCore.QSize:
		"""Calculate the actual palette size without padding"""
		width  = self.colorSize().width() * min(len(self.colors()), self.maxColorsPerRow())
		height = self.colorSize().height() * (len(self.colors()) // self.maxColorsPerRow())
		return QtCore.QSize(width, height)
	
	def calculatedPadding(self) -> QtCore.QPoint:
		"""Required padding to center the pallete within the widget"""
		palette_size = self.calculatedPaletteSize()
		widget_size = self.size()
		diff_size = widget_size - palette_size
		return QtCore.QPoint(diff_size.width() / 2, diff_size.height() / 2)

	def setMaxColorsPerRow(self, colors_per_row:int):
		self._max_colors_per_row = colors_per_row
		self.update()
	
	def maxColorsPerRow(self) -> int:
		return self._max_colors_per_row
	
	def setColors(self, colors:list[QtGui.QColor]):
		self._colors = colors
		self.update()

	def colors(self) -> list[QtGui.QColor]:
		return self._colors

	def sizeHint(self) -> QtCore.QSize:
		color_count = len(self.colors())
		width = self.maxColorsPerRow() * 24 + self.borderHoverWidth()
		height = color_count // self.maxColorsPerRow() * 18 +  + self.borderHoverWidth()

		return QtCore.QSize(width, height)
	
	def colorRect(self, color_index:int) -> QtCore.QRect:
		"""Return the rect for a given color"""

		padding = self.calculatedPadding()

		x_pos = color_index % self.maxColorsPerRow() * self.colorSize().width() + padding.x()
		y_pos = color_index // self.maxColorsPerRow() * self.colorSize().height() + padding.y()

		return QtCore.QRect(x_pos, y_pos, self.colorSize().width(), self.colorSize().height())


	def paintEvent(self, e:QtGui.QPaintEvent):

		super().paintEvent(e)
		
		painter = QtGui.QPainter(self)
		rect_widget_bounds = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())

		# Background
		brush = painter.brush()
		brush.setStyle(QtGui.Qt.BrushStyle.SolidPattern)
		brush.setColor(self._color_background)	# TODO Might want color roles thing
		painter.setBrush(brush)

		pen = painter.pen()
		pen.setColor(self._color_background)
		pen.setJoinStyle(QtGui.Qt.PenJoinStyle.MiterJoin)
		pen.setStyle(QtGui.Qt.PenStyle.SolidLine)
		pen.setWidth(self.borderCommonWidth())
		painter.setPen(pen)

		painter.drawRect(rect_widget_bounds)

		# Draw each color
		for idx, color in enumerate(self.colors()):
			#print(color)
			brush.setColor(color)
			painter.setBrush(brush)
			painter.drawRect(self.colorRect(idx))
		
		# Highlight things
		hovered_index = self.hoveredIndex()
		selected_index = self.selectedIndex()

		# First anything hovered
		if hovered_index is not None and hovered_index != selected_index:

			border_offset = self.borderHoverWidth() // 2
			hovered_rect = self.colorRect(hovered_index).adjusted(border_offset+self.borderCommonWidth(), border_offset+self.borderCommonWidth(), -border_offset-self.borderCommonWidth(), -border_offset-self.borderCommonWidth())

			brush.setStyle(QtGui.Qt.BrushStyle.NoBrush)
			painter.setBrush(brush)
			pen.setColor(QtGui.QColor("Black"))
			pen.setWidth(self.borderHoverWidth() + 2 * self.borderCommonWidth())
			painter.setPen(pen)
			painter.drawRect(hovered_rect)

			pen.setWidth(self.borderHoverWidth())
			pen.setColor(QtGui.QColor("White"))
			pen.setStyle(QtGui.Qt.PenStyle.SolidLine)
			painter.setPen(pen)
			painter.drawRect(hovered_rect)

		if selected_index is not None:
			border_offset = self.borderSelectedWidth() // 2
			selected_rect = self.colorRect(selected_index).adjusted(border_offset+self.borderCommonWidth(), border_offset+self.borderCommonWidth(), -border_offset, -border_offset)

			brush.setStyle(QtGui.Qt.BrushStyle.NoBrush)
			painter.setBrush(brush)
			pen.setColor(QtGui.QColor("Black"))
			pen.setWidth(self.borderSelectedWidth() + 2)
			painter.setPen(pen)
			painter.drawRect(selected_rect)

			pen.setWidth(self.borderSelectedWidth())
			pen.setColor(QtGui.QColor("White"))
			pen.setStyle(QtGui.Qt.PenStyle.SolidLine)
			painter.setPen(pen)
			painter.drawRect(selected_rect)
		
		painter.end()

			
			
			
	def colorIndexFromCoords(self, coordinates:QtCore.QPoint) -> int|None:

		if not QtCore.QRect(self.calculatedPadding(), self.calculatedPaletteSize()).contains(coordinates):
			return None

		x = coordinates.x() // self.colorSize().width()
		y = coordinates.y() // self.colorSize().height()

		return x + y*self.maxColorsPerRow()
	
	def hoveredIndex(self) -> int|None:
		return self._hovered_index
	
	@QtCore.Slot(int)
	def setHoveredIndex(self, index:int):
		if index is not None and index < len(self.colors()):
			self._hovered_index = index
			self.sig_hovered_color_changed.emit(self.colors()[index])
		else:
			self._hovered_index = None
		
		self.update()
	
	def selectedIndex(self) -> int|None:
		return self._selected_index

	@QtCore.Slot(int)
	def setSelectedIndex(self, index:int):
		if index is not None and index < len(self.colors()):
			self._selected_index = index
			self.sig_selected_color_changed.emit(self.colors()[index])
		else:
			self._selected_index = None
		
		self.update()
	
	def selectedColor(self, color:QtGui.QColor|None):
		if self.selectedIndex() is not None:
			return self.colors()[self.selectedIndex()]
		return None
	
	def toolTipForIndex(self, index:int):
		if index is not None and index < len(self.colors()):
			color = self.colors()[index]
			return f"R: {color.red()}  G: {color.green()}  B: {color.blue()}"
		return None
	
	def mousePressEvent(self, event:QtGui.QMouseEvent) -> bool:
		if event.button() == QtCore.Qt.MouseButton.LeftButton:
			index = self.colorIndexFromCoords(event.position().toPoint())
			self.setSelectedIndex(index)

		return super().mousePressEvent(event)
	
	def mouseMoveEvent(self, event:QtGui.QMouseEvent):
			index = self.colorIndexFromCoords(event.position().toPoint())
			self.setHoveredIndex(index)
			return super().mouseMoveEvent(event)
	
	def leaveEvent(self, event):
		self.setHoveredIndex(None)
		return super().leaveEvent(event)

	
	def event(self, event:QtCore.QEvent) -> bool:
		
		if event.type() == QtCore.QEvent.Type.ToolTip:
			QtWidgets.QToolTip.showText(event.globalPos(), self.toolTipForIndex(self.colorIndexFromCoords(event.pos())))
		#	return True

		return super().event(event)

class LBTimelineView(QtWidgets.QWidget):
	"""A little timeline layout graphic thing"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		# Calculation Stuff
		self._total_adjust  = 0
		"""Additional frame count adjustment to total duration"""

		# Box drawing
		self._box_line_width = 1
		self._tick_line_width = 2
		self._box_inner_padding = 3
		
		# Font stuff
		self._font = QtGui.QFont()
		self._font.setPointSize(self._font.pointSize() - 2)
		self._font_height = QtGui.QFontMetrics(self._font).boundingRect("00:00:00:00").height()
		self._text_options = QtGui.QTextOption()
		self._text_options.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
		self._text_options.setWrapMode(QtGui.QTextOption.WrapMode.NoWrap)

		self.setSizePolicy(
			QtWidgets.QSizePolicy.Policy.MinimumExpanding,
			QtWidgets.QSizePolicy.Policy.Fixed
		)
	
	def sizeHint(self) -> QtCore.QSize:
		# Set size hint based on two lines of text, basically
		size = QtCore.QSize(-1, self._box_inner_padding * 3 + self._box_line_width * 2 + self._font_height * 2)

		return size

	def setBottomMargin(self, margin:int):
		self._bottom_margin = margin

	def setTotalAdjust(self, adjust:int):
		self._total_adjust = adjust
		self.update()

	def totalAdjust(self) -> int:
		"""Get the adjustment to the total"""
		return self._total_adjust

	def adjustedTotal(self) -> int:
		"""Get the total duration, including adjustments"""
		if self._total_adjust < 0:
			return self._total
		return self._total + self._total_adjust
	
	def itemTotal(self) -> int:
		"""Get the true total without adjustments"""
		return self._total

	# Debug
	def setItems(self, items:list[tuple[str,int]]):
		"""Set the items to be displayed in a timeline"""
		
		self._items = items
		
		# Build the color pallette based on item count
		self._pallette = [QtGui.QColor.fromHsvF(x/len(items), .4, .4) for x in range(len(items))]
		
		# Set the total
		self._total = sum([dur for sequence_name, dur in items])
		
		self.update()

	def paintEvent(self, e:QtGui.QPaintEvent):

		super().paintEvent(e)


		painter = QtGui.QPainter(self)
		#painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

		rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
		item_box_height = self._font_height + self._box_inner_padding*2 + self._box_line_width*2

		background_box = QtCore.QRect(0, 0, rect.width(), item_box_height)
		background_box_rect = background_box.adjusted(self._box_line_width//2, self._box_line_width//2, -self._box_line_width//2, -self._box_line_width//2)
		pen = painter.pen()
		pen.setStyle(QtGui.Qt.PenStyle.SolidLine)
		pen.setColor(QtGui.QColor.fromRgbF(0,0,0,.5))
		pen.setWidth(self._box_line_width)
		painter.setPen(pen)
		brush = painter.brush()
		brush.setColor(QtGui.QColor.fromRgbF(0,0,0,.1))
		brush.setStyle(QtGui.Qt.BrushStyle.SolidPattern)
		painter.setBrush(brush)
		painter.drawRect(background_box_rect)


		if not len(self._items):
			return
		

		x_pos = 0
		cumulative = 0

		painter.setFont(self._font)

		for idx, thing in enumerate(self._items):

			sequence_name, sequence_duration = thing

			# Draw Box
			
			# Item box
			item_box_width = math.ceil((sequence_duration / self.adjustedTotal()) * rect.width())
			item_box_rect = QtCore.QRect(x_pos, 0, item_box_width, item_box_height).adjusted(self._box_line_width//2, self._box_line_width//2, -self._box_line_width//2, -self._box_line_width//2)
			
			brush = painter.brush()
			brush.setColor(self._pallette[idx])
			brush.setStyle(QtGui.Qt.BrushStyle.SolidPattern)
			painter.setBrush(brush)
			
			pen = painter.pen()
			pen.setColor(painter.brush().color().lighter(200))
			pen.setWidth(self._box_line_width)
			pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
			painter.setPen(pen)
			
			painter.drawRect(item_box_rect)


			# Draw Box Label

			label_box_rect = item_box_rect.adjusted(self._box_inner_padding + self._tick_line_width, self._box_inner_padding, -self._box_inner_padding-self._box_line_width, -self._box_inner_padding)

			pen = painter.pen()
			pen.setColor(painter.brush().color().lighter(300))
			painter.setPen(pen)
			painter.drawText(label_box_rect, sequence_name, self._text_options)


			# Draw tick
			#painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
			pen = painter.pen()
			pen.setWidth(self._tick_line_width)
			pen.setColor(self._pallette[idx].lighter(200))
			painter.setPen(pen)

			tick_start_pos = QtCore.QPoint(max(x_pos, int(pen.width()//2)), 0)
			tick_end_pos   = QtCore.QPoint(tick_start_pos.x(), painter.device().height())

			painter.drawLine(tick_start_pos, tick_end_pos)

			# Draw Timecode
			tick_text = str(Timecode(int(cumulative))).lstrip("0:") or "0:00"
			
			pen = painter.pen()	
			pen.setColor(QtGui.QPalette().color(QtGui.QPalette.ColorRole.Text))
			painter.setPen(pen)
			
			# Timecode box rect is based on the label box, but moved down below the rect + stroke + padding
			timecode_box_rect = QtCore.QRect(label_box_rect)
			timecode_box_rect.moveTop(item_box_rect.height() + self._box_inner_padding + self._box_line_width//2)
			painter.drawText(timecode_box_rect, tick_text, self._text_options)
			
			x_pos += (sequence_duration/self.adjustedTotal())*(rect.width())
			cumulative += sequence_duration

		# Draw final tick
		#painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, False)
		pen = painter.pen()
		pen.setWidth(self._tick_line_width)
		pen.setColor(self._pallette[-1].lighter(200))
		painter.setPen(pen)

		tick_start_pos = QtCore.QPoint(item_box_rect.right() + self._tick_line_width//2, 0)
		tick_end_pos   = QtCore.QPoint(tick_start_pos.x(), rect.height())

		painter.drawLine(tick_start_pos, tick_end_pos)

		# Draw Final Timecode
		pen = painter.pen()	
		pen.setColor(QtGui.QPalette().color(QtGui.QPalette.ColorRole.Text))
		painter.setPen(pen)
		tick_text = str(Timecode(int(cumulative))).lstrip("0:") or "0:00"

		#text_location.setX(tick_start_pos.x() - font_box.width() - 5 - painter.pen().width())
		
		#painter.drawText(text_location, tick_text)


		painter.end()
	
	def event(self, event:QtCore.QEvent):

		if event.type() is QtCore.QEvent.Type.ToolTip:
			QtWidgets.QToolTip.showText(event.globalPos(), self.toolTip(event.pos()))
			return True
		
		return super().event(event)

	def toolTip(self, position:QtCore.QPoint) -> str:
		
		item_pos = 0
		for idx,item in enumerate(self._items):

			sequence_name, sequence_duration = item
			
			item_pos += (sequence_duration/self.adjustedTotal()) * self.width()
			if position.x() < item_pos:
				return f"{sequence_name} ({Timecode(sequence_duration)})"

class LBSpinBoxTC(QtWidgets.QSpinBox):

	sig_timecode_changed = QtCore.Signal(Timecode)

	MAX_TC_STRING = "100:00:00:00"
	"""Timecode string for max range calculations"""

	PAT_TC_VALID = re.compile(r"^[-+]?([0-9]{1,2}:){0,3}[0-9]{1,2}$")
	"""Valid timecode pattern for validation"""

	PAT_TC_INTER = re.compile(r"^[+-]?([0-9]{1,2}:){0,3}$")
	"""Intermediate pattern"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._rate = 24
		self._resample_on_rate_change = True

		self._allow_negative = False
		self._allow_positive = True

		self.valueChanged.connect(lambda: self.sig_timecode_changed.emit(self.timecode()))
		
		self.setKeyboardTracking(False)
		self._update_range()

	def _update_range(self):
		"""Update timecode range"""
		# TODO: Might want to make this user-facing
		self.setRange(
			Timecode(self.MAX_TC_STRING, rate=self.rate()).frame_number * -1 if self.allowNegative() else 0,
			Timecode(self.MAX_TC_STRING, rate=self.rate()).frame_number      if self.allowPositive() else 0,
		)

	@QtCore.Slot(bool)
	def setResampleOnRateChange(self, resample:bool):
		"""Resample Timecode to closest neighbor when rate changes.  If false, will maintain frame number."""
		self._resample_on_rate_change = bool(resample)
	
	def resampleOnRateChange(self) -> bool:
		"""If Timecode will be resampled when the rate changes.  If false, will maintain frame number."""
		return self._resample_on_rate_change
			
	@QtCore.Slot(bool)
	def setAllowNegative(self, allow:bool):
		"""Allow negative (<0) frame ranges"""
		self._allow_negative = bool(allow)
		self._update_range()
		self.setValue(self.value())

	def allowNegative(self) -> bool:
		"""Are negative frames (<0) allowed"""
		return self._allow_negative

	@QtCore.Slot(bool)	
	def setAllowPositive(self, allow:bool):
		"""Allow positive (>0) frame ranges"""
		self._allow_positive = bool(allow)
		self._update_range()
		self.setValue(self.value())
	
	def allowPositive(self) -> bool:
		"""Are positive frames (>0) allowed"""
		return self._allow_positive
	
	@QtCore.Slot(int)
	def setFrameNumber(self, frame_number:int):
		"""Set based on frame number"""
		self.setValue(int(frame_number))
	
	def frameNumber(self) -> int:
		"""The frame number as an integer"""
		return self.value()
	
	@QtCore.Slot(int)
	def setRate(self, rate:int):
		"""Set the timecode rate"""
		old_tc = self.timecode()

		if rate == self.rate():
			return
		elif rate < 0:
			raise ValueError(f"Invalid timecode rate ({rate})")
		
		self._rate = int(rate)
		self._update_range()

		if self.resampleOnRateChange():
			self.setValue(old_tc.resample(rate=self.rate()).frame_number)
		else:
			self.setValue(self.value())
	
	def rate(self) -> int:
		"""Timecode rate"""
		return self._rate
	
	@QtCore.Slot(Timecode)
	def setTimecode(self, timecode:Timecode):
		"""Set frame and rate from a given timecode"""
		self.setRate(timecode.rate)
		self.setValue(timecode.frame_number)
	
	def timecode(self) -> Timecode:
		"""Get the current timecode"""
		return Timecode(self.frameNumber(), rate=self.rate())
	
	def textFromValue(self, val:int) -> str:
		"""Format frame number to Timecode string"""
		# Add a '+' for positive values for differentiation
		prefix = "+" if self.allowNegative() and self.value() > 0 else ""
		return prefix + str(Timecode(val, rate=self.rate()))
	
	def valueFromText(self, text:str) -> int:
		"""Derive timecode frame number from user input text"""
		
		# Pass through valid timecode patterns
		if self.PAT_TC_VALID.match(text):
			return Timecode(text, rate=self.rate()).frame_number
		
		# Otherwise, validate() will only allow for integers hopefully lol
		# So format integer with colons (001234 -> 00:12:34)

		if not text.lstrip("+-").isnumeric():
			return 0
		
		is_negative = text.startswith("-")

		text_raw_reversed = text.lstrip("+-")[::-1]
		text_formatted = ("-" if is_negative else "") + (":".join([text_raw_reversed[idx:idx+2] for idx in range(0, len(text_raw_reversed),2)]))[::-1]
		return Timecode(text_formatted, rate=self.rate()).frame_number

	def validate(self, input:str, pos:int) -> QtGui.QValidator.State:
		
		# Match simple frame counts
		if not input:
			state = QtGui.QValidator.State.Intermediate
		elif input == "+" or input == "-":
			state = QtGui.QValidator.State.Intermediate
		elif len(input.lstrip("+-")) <= 8 and input.lstrip("+-").isnumeric():
			state = QtGui.QValidator.State.Acceptable
		
		# Match timecode
		elif self.PAT_TC_INTER.match(input):
			state = QtGui.QValidator.State.Intermediate
		elif self.PAT_TC_VALID.match(input):
			state = QtGui.QValidator.State.Acceptable
		
		# Nah
		else:
			state = QtGui.QValidator.State.Invalid

		return state
	
	def toolTip(self):
		return f"{self.timecode()} @ {self.rate()} fps"

class LBSpinBoxTC_Deprecated(QtWidgets.QSpinBox):

	PAT_VALID_TEXT = re.compile(r"^(\d+:){0,3}\d+$")
	PAT_INTER_TEXT = re.compile(r"^(\d+:?){1,4}$")

	sig_timecode_changed = QtCore.Signal(Timecode)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		self._rate = 24
		self._allow_negative = False

		self._updateTimecodeExtents()
		self.editingFinished.connect(lambda: self.sig_timecode_changed.emit(self.timecode()))
		
	
	@QtCore.Slot(int)
	def setRate(self, rate:int):
		#self.blockSignals(True)

		if rate == self.rate():
			return

		# Resample TC to new rate
		old_timecode = self.timecode()
		new_timecode = old_timecode.resample(rate=rate)
		
		self._rate = int(rate)
		self._updateTimecodeExtents()

		self.setTimecode(new_timecode)
		#self.sig_timecode_changed.emit(self.timecode())

	@QtCore.Slot()
	def _updateTimecodeExtents(self):
		"""Set min/max ranges based on rate"""
		self.setMaximum(Timecode("100:00:00:00", rate=self.rate()).frame_number)
		self.setMinimum(Timecode("-100:00:00:00", rate=self.rate()).frame_number if self.allowNegative()
			else Timecode(0, rate=self.rate()).frame_number)

	def validate(self, input:str, pos:int) -> bool:

		# Allow for one '-' if negative is allowed, by stripping it off for validation
		if self.allowNegative() and input.startswith("-"):
			input = input[1:]
		elif input.startswith("+"):
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
		#print("Hello I set to", timecode)
		self.setRate(timecode.rate)
		self.setValue(timecode.frame_number)
	
	@QtCore.Slot(bool)
	def setAllowNegative(self, allow:bool):
		if allow != self.allowNegative():
			self._allow_negative = allow
			self._updateTimecodeExtents()
		self.setTimecode(self.timecode())

	def allowNegative(self) -> bool:
		return self._allow_negative
	
	def timecode(self) -> Timecode:
		return Timecode(self.value(), rate=self.rate())

	def rate(self) -> int:
		return self._rate
	
	def textFromValue(self, val:int) -> str:
		prepend = "+" if self.allowNegative() and val > 0 else ""
		return prepend + str(Timecode(val, rate=self.rate()))
	
	def valueFromText(self, text:str) -> int:
		
		text = text.strip()
		is_negative = text.startswith("-")
		text = text.lstrip("-+")
		
		if not text.isnumeric():
			return Timecode(("-" if is_negative else "") + text, rate=self.rate()).frame_number
		
		text_reversed = text[::-1]
		processed = ":".join([text_reversed[idx:idx+2] for idx in range(0, len(text), 2)])
		final = ("-" if is_negative else "") + processed[::-1]
		return Timecode(final, rate=self.rate()).frame_number

class LBBClipColorPickerButtonDeprecated(QtWidgets.QWidget):
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