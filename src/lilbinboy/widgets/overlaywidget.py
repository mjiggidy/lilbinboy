"""
An overlay widget for drawing above a widget and its children
"""

from PySide6 import QtCore, QtGui, QtWidgets

class BSAbstractOverlayWidget(QtWidgets.QWidget):
	"""A transparent widget for drawing above a given widget.."""

	def __init__(self, parent:QtWidgets.QWidget, install_event_filter:bool=True):

		super().__init__(parent=parent)

		self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TransparentForMouseEvents)
		self.setAttribute(QtCore.Qt.WidgetAttribute.WA_NoSystemBackground)

		if install_event_filter:
			self.parent().installEventFilter(self)

	def eventFilter(self, watched:QtWidgets.QWidget, event:QtCore.QEvent):
		
		if event.type() == QtCore.QEvent.Type.Resize:

			self.resize(event.size())
			return True
		
		return super().eventFilter(watched, event)
	
class BSDragDropOverlayWidget(BSAbstractOverlayWidget):

	sig_margins_changed = QtCore.Signal(QtCore.QMarginsF)
	sig_enabled_changed = QtCore.Signal(bool)

	def __init__(self, parent:QtWidgets.QWidget, *args, margins:QtCore.QMarginsF|None=None, is_visible:bool=True, install_event_filter:bool=True, **kwargs):

		super().__init__(parent=parent, install_event_filter=install_event_filter)

		self._margins = margins or QtCore.QMarginsF(32,32,32,32)
		self._lerp_margins = QtCore.QMarginsF(0,0,0,0)

		self._animator = QtCore.QVariantAnimation(parent=self)
		
		self._animator.setStartValue(0.0)
		self._animator.setEndValue(1.0)
		self._animator.setDuration(300) #ms
		self._animator.setEasingCurve(QtCore.QEasingCurve.Type.OutExpo)

		self.setVisible(is_visible)

		self._animator.valueChanged.connect(self.update)

	@QtCore.Slot()
	def show(self):

		self.dragStarted()

		return super().show()

	@QtCore.Slot()
	def dragStarted(self):

		self._animator.start()
	
	def margins(self) -> QtCore.QMarginsF:

		return self._margins
	
	@QtCore.Slot(QtCore.QMarginsF)
	def setMargins(self, margins:QtCore.QMarginsF):

		if self._margins == margins:
			return
		
		self._margins = QtCore.QMarginsF(margins)

		if self.isVisible():
			self.update()

		self.sig_margins_changed.emit(margins)

	def paintEvent(self, event:QtGui.QPaintEvent):

		if not self.isVisible():
#			print("NOPE")
			return
		
		MAX_BG_OPACITY = 0.5
		
		lerp_margins = self._animator.currentValue()
		#print(lerp_margins)
		
		color_border = QtGui.QColor(self.parent().palette().highlight().color())
		color_border.setAlphaF(self._animator.currentValue())

		color_background = QtGui.QColor(self.parent().palette().dark().color())
		color_background.setAlphaF(self._animator.currentValue() * MAX_BG_OPACITY)

		pen = QtGui.QPen()
		pen.setWidth(2)
		pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
		pen.setColor(color_border)

		brush = QtGui.QBrush()
		brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
		brush.setColor(color_background)

		painter = QtGui.QPainter(self)
		painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
		painter.setPen(pen)
		painter.setBrush(brush)
		painter.drawRoundedRect(
			QtCore.QRectF(
				self.parent().rect()
			).marginsRemoved(self._margins * lerp_margins),
			10,
			10,
			QtCore.Qt.SizeMode.AbsoluteSize
		)

		painter.drawText(self.rect(), self.tr("Drop 'er on down here, buddy"), QtCore.Qt.AlignmentFlag.AlignCenter)
		painter.end()