import math
from PySide6 import QtWidgets, QtCore, QtGui
from timecode import Timecode

class LBTimelineView(QtWidgets.QWidget):
	"""A little timeline layout graphic thing"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._items = []

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

		# TODO: Avoiding DivideByZero below -- probably should do things differently
		if not self.adjustedTotal():
			return

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