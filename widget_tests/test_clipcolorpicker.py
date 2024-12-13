import avbutils
import random
from PySide6 import QtCore, QtGui, QtWidgets

class ClipColorPicker(QtWidgets.QWidget):
	"""A picker of Avid clip colors"""

	sig_hovered_color_changed = QtCore.Signal(QtGui.QColor)
	sig_selected_color_changed = QtCore.Signal(QtGui.QColor)

	def __init__(self, colors:list[QtGui.QColor]|None=None, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setMouseTracking(True)

		self._colors = colors if colors is not None else [QtGui.QColor.fromRgba64(*a.as_rgba16()) for a in avbutils.get_default_clip_colors()]
		self._max_colors_per_row = 8

		self._color_background = QtGui.QColor(0,0,0)
		self._border_width = 1

		self._hovered_index = None
		self._selected_index = None

	def setBorderWidth(self, width:int):
		self._border_width = width
	
	def borderWidth(self) -> int:
		return self._border_width
	
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
		width = self.maxColorsPerRow() * 24 + self.borderWidth()
		height = color_count // self.maxColorsPerRow() * 18 +  + self.borderWidth()

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
		pen.setWidth(self.borderWidth())
		painter.setPen(pen)

		painter.drawRect(rect_widget_bounds)

		# Draw each color
		for idx, color in enumerate(self.colors()):
			#print(color)
			brush.setColor(color)
			painter.setBrush(brush)
			painter.drawRect(self.colorRect(idx))
		
		# Highlight selected index
		selected_index = self.hoveredIndex()
		if selected_index is not None:
			pen.setWidth(2 * self.borderWidth())
			pen.setColor(QtGui.QColor("White"))
			pen.setStyle(QtGui.Qt.PenStyle.SolidLine)
			painter.setPen(pen)
			brush.setStyle(QtGui.Qt.BrushStyle.NoBrush)
			painter.setBrush(brush)

			painter.drawRect(self.colorRect(selected_index))
			
			pen.setColor(QtGui.QColor("Black"))
			pen.setWidth(self.borderWidth())
			painter.setPen(pen)
			
			painter.drawRect(self.colorRect(selected_index).adjusted(pen.width(), pen.width(), -pen.width(), -pen.width()))
			painter.drawRect(self.colorRect(selected_index).adjusted(-pen.width(), -pen.width(), pen.width(), pen.width()))

	def colorIndexFromCoords(self, coordinates:QtCore.QPoint) -> int|None:

		if not QtCore.QRect(self.calculatedPadding(), self.calculatedPaletteSize()).contains(coordinates):
			return None

		x = coordinates.x() // self.colorSize().width()
		y = coordinates.y() // self.colorSize().height()

		return x + y*self.maxColorsPerRow()
	
	def hoveredIndex(self) -> int|None:
		return self._hovered_index
	
	def setHoveredIndex(self, index:int):
		if index is not None and index < len(self.colors()):
			self._hovered_index = index
			self.sig_hovered_color_changed.emit(self.colors()[index])
		else:
			self._hovered_index = None
		
		self.update()
	
	def selectedIndex(self) -> int|None:
		return self._selected_index

	def setSelectedIndex(self, index:int):
		if index is not None and index < len(self.colors()):
			self._selected_index = index
			self.sig_selected_color_changed.emit(self.colors()[index])
		else:
			self._selected_index = None
		
		self.update()
	
	def toolTipForIndex(self, index:int):
		if index is not None and index < len(self.colors()):
			color = self.colors()[index]
			return f"R: {color.red()}  G: {color.green()}  B: {color.blue()}"
		return None
	
	def mousePressEvent(self, event) -> bool:
		if event.button() == QtCore.Qt.MouseButton.LeftButton:
			index = self.colorIndexFromCoords(event.position().toPoint())
			self.setSelectedIndex(index)
			return True
		else:
			return super().mousePressEvent(event)
			
		
	
	def event(self, event:QtCore.QEvent) -> bool:

		if event.type() == QtCore.QEvent.Type.MouseMove:
			self.setHoveredIndex(self.colorIndexFromCoords(event.position().toPoint()))
			return True
		
		elif event.type() == QtCore.QEvent.Type.HoverLeave:
			#print("OOOH BYE")
			return True
		
		elif event.type() == QtCore.QEvent.Type.ToolTip:
			QtWidgets.QToolTip.showText(event.globalPos(), self.toolTipForIndex(self.colorIndexFromCoords(event.pos())))
			return True

		return super().event(event)


		
def setLabel(label:QtWidgets.QLabel, color:QtGui.QColor):
	palette = label.palette()
	palette.setColor(QtGui.QPalette.ColorRole.WindowText, color)
	label.setPalette(palette)
	label.setText("User chose this color I guess")


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	wnd = QtWidgets.QWidget()
	wnd.setLayout(QtWidgets.QVBoxLayout())
	
	picker = ClipColorPicker()

	picker.sig_selected_color_changed.connect(lambda color: setLabel(lbl_teller, color))

	lbl_teller = QtWidgets.QLabel()

	wnd.layout().addWidget(picker)
	wnd.layout().addWidget(lbl_teller)

	wnd.show()

	app.setStyle("Fusion")
	app.exec()

