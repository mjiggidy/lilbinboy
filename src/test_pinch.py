"""
Quick n sloppy test of some trackpad event filters here
"""

import sys
from PySide6 import QtCore, QtGui, QtWidgets
from lilbinboy.utils import gestures

class MichaelsCoolVisualizerOfThePinch(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._curve_scale = QtCore.QEasingCurve()

		self._brush = QtGui.QBrush()
		self._pen   = QtGui.QPen()
		self._font  = self.font()

		self._scale_sensitivity = 0.5
		self._resting_scale     = 0.8
		self._current_scale     = self._resting_scale
		self._curve_scale.setType(QtCore.QEasingCurve.Type.InOutQuad)

		self._position_resting_offset = QtCore.QPoint(0,0) 
		self._position_current_offset = self._position_resting_offset
		self._position_sensitivity = 0.5

		self.scale_animator = QtCore.QPropertyAnimation()
		self.scale_animator.setParent(self)
		self.scale_animator.setTargetObject(self)
		self.scale_animator.setPropertyName(QtCore.QByteArray.fromStdString("scale"))
		self.scale_animator.setDuration(500) # Msec
		self.scale_animator.setEasingCurve(QtCore.QEasingCurve.Type.OutElastic)

		self.position_animator = QtCore.QPropertyAnimation()
		self.position_animator.setParent(self)
		self.position_animator.setTargetObject(self)
		self.position_animator.setPropertyName(QtCore.QByteArray.fromStdString("position_offset"))
		self.position_animator.setDuration(500) # Msec
		self.position_animator.setEasingCurve(QtCore.QEasingCurve.Type.OutElastic)

		self._setupPainters()

	def event(self, event:QtCore.QEvent) -> bool:

		if not event.type() == QtCore.QEvent.Type.PaletteChange:
			return super().event(event)
		
		self._setupPainters()
		return True

	def _setupPainters(self):

		self._brush = self.style().standardPalette().midlight()
		self._brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		self._pen.setColor(self.style().standardPalette().windowText().color())
		self._pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
		self._pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
		self._pen.setWidth(3)

		self._font = self.font()
		self._font.setPointSizeF(self.font().pointSizeF() * 0.8)

	@QtCore.Property(float)
	def scale(self) -> float:
		"""Needed for QPropertyAnimation"""

		return self._current_scale

	@scale.setter
	def scale(self, scale:float):
		"""Needed for QPropertyAnimation"""

		self._current_scale = scale
		self.update()

	@QtCore.Property(QtCore.QPoint)
	def position_offset(self) -> QtCore.QPoint:
		"""Needed for QPropertyAnimation"""

		return self._position_current_offset

	@position_offset.setter
	def position_offset(self, offset:QtCore.QPoint):
		"""Needed for QPropertyAnimation"""

		self._position_current_offset = offset
		self.update()
	
	def sizeHint(self) -> QtCore.QSize:
		return QtCore.QSize(100,100)
	
	@QtCore.Slot(float)
	def setScaleDelta(self, accumulated:float|None=None):
		"""Process delta and use it"""
		
		accumulated = accumulated or 0
		self.scale = max(0.1, min(self._resting_scale + (accumulated * self._scale_sensitivity), 2))

		self.update()
	
	def resetScale(self):

		self.scale_animator.stop()
		self.scale_animator.setStartValue(self._current_scale)
		self.scale_animator.setEndValue(self._resting_scale)
		self.scale_animator.start()

	@QtCore.Slot(QtCore.QPoint)
	def setPositionOffset(self, accumulated:QtCore.QPoint|None=None):

		accumulated = accumulated or QtCore.QPoint(0,0)

		#print(accumulated)

		self._position_current_offset = (accumulated * self._position_sensitivity)
		self.update()

	@QtCore.Slot()
	def resetPosition(self):

		self.position_animator.stop()
		self.position_animator.setStartValue(self._position_current_offset)
		self.position_animator.setEndValue(self._position_resting_offset)
		self.position_animator.start()

		#self._position_current_offset = self._position_resting_offset
		#print("Reset to ", self._position_current_offset)
		self.update()

	def paintEvent(self, event:QtGui.QPaintEvent):
		
		# Ironically NOT using an event filter here lol
		
		super().paintEvent(event)

		painter = QtGui.QPainter(self)
		painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

		try:
			self.drawVisualizer(painter, event.rect())
		except Exception as e:
			print(e, file=sys.stderr)
		finally:
			painter.end()

	def drawVisualizer(self, painter:QtGui.QPainter, bounding_rect:QtCore.QRect):
		
		base_rad = min(bounding_rect.width(), bounding_rect.height()) / 2 - painter.pen().widthF() * 2

		painter.save()

		painter.setPen(self._pen)
		painter.setBrush(self._brush)
		painter.setFont(self._font)
		painter.drawEllipse(
			bounding_rect.center() + self._position_current_offset,
			base_rad * self._current_scale,
			base_rad * self._current_scale
		)

		painter.drawText(
			bounding_rect,
			QtCore.Qt.AlignmentFlag.AlignCenter|QtCore.Qt.AlignmentFlag.AlignVCenter,
			str(round(self._current_scale, 2))
		)

		painter.restore()

class MichaelsCoolTestWindowHahaOk(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._pinch_event_filter = gestures.BSPinchEventFilter(parent=self)
		self._pan_event_filter = gestures.BSPanEventFilter(parent=self)
		self._visualizer = MichaelsCoolVisualizerOfThePinch()


		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().addWidget(self._visualizer)


		self.installEventFilter(self._pinch_event_filter)
		self.installEventFilter(self._pan_event_filter)
		
		self._pinch_event_filter.sig_user_pinch_started.connect(self._visualizer.scale_animator.stop)
		self._pinch_event_filter.sig_user_pinch_moved.connect(lambda d,a: self._visualizer.setScaleDelta(a))
		self._pinch_event_filter.sig_user_pinch_finished.connect(self._visualizer.resetScale)

		self._pan_event_filter.sig_user_pan_started.connect(self._visualizer.position_animator.stop)
		self._pan_event_filter.sig_user_pan_started.connect(lambda: self._visualizer.setMouseTracking(True))
		self._pan_event_filter.sig_user_pan_moved.connect(lambda d,a: self._visualizer.setPositionOffset(a))
		self._pan_event_filter.sig_user_pan_finished.connect(self._visualizer.resetPosition)
		self._pan_event_filter.sig_user_pan_started.connect(lambda: self._visualizer.setMouseTracking(False))

if __name__ == "__main__":

	import logging
	logging.basicConfig(level=logging.DEBUG)

	app = QtWidgets.QApplication()

	#app.setStyle("Fusion")
	app.setApplicationName("Pinchy Toy")
	app.setApplicationVersion("1.0.0")
	app.setOrganizationName("GlowingPixel")
	app.setOrganizationDomain("com.glowingpixel")

	wnd = MichaelsCoolTestWindowHahaOk()
	wnd.setWindowTitle(app.applicationDisplayName())
	
	wnd.show()

	wnd_geo = QtCore.QRect(QtCore.QPoint(0,0), QtCore.QSize(256,256))
	wnd_geo.moveCenter(app.primaryScreen().geometry().center())
	wnd.setGeometry(wnd_geo)

	sys.exit(app.exec())