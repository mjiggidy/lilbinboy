"""
Event filters to handle particular user gestures
in a good and nice way that is good and nice
"""

import logging
from PySide6 import QtCore, QtGui


class BSPinchEventFilter(QtCore.QObject):
	"""Handle if the user gets pinchy"""

	sig_user_pinch_started  = QtCore.Signal()
	"""The user has began to pinch"""
	
	sig_user_pinch_moved    = QtCore.Signal(float, float)
	"""User is doing a pinchy (`delta since last:float`, `accumulated pinch:float`)"""

	sig_user_pinch_finished = QtCore.Signal()
	"""User has tired of the pinch"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		self._accumulated_scale     = 0
		self._tracked_gesture_count = 0

		self.parent().installEventFilter(self)
	
	def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent) -> bool:
		"""Handle pinch events via `QtGui.QNativeGestureEvent` thingies"""

		if event.type() != QtCore.QEvent.Type.NativeGesture:
			return False

		# If Begin Native Gesture
		if event.gestureType() == QtCore.Qt.NativeGestureType.BeginNativeGesture:
			
			self.reportPinchStarted()
			return True
			
		# If Actively Zooming
		elif event.gestureType() == QtCore.Qt.NativeGestureType.ZoomNativeGesture:
			
			self.reportPinchChanged(event)
			return True

		# If End Native Gesture
		elif event.gestureType() == QtCore.Qt.NativeGestureType.EndNativeGesture:
			
			self.reportPinchFinished()
			return True
		
		return False
	
	@QtCore.Slot()
	def reportPinchStarted(self):
		"""User is getting pinchy"""

		self._tracked_gesture_count += 1
		logging.getLogger(__name__).debug("Begin gesture, active_gestures=%s", self._tracked_gesture_count)
		
		if self._tracked_gesture_count == 1:
			self.sig_user_pinch_started.emit()

	@QtCore.Slot(object)
	def reportPinchChanged(self, pinch_event:QtGui.QNativeGestureEvent):
		"""Report the latest accumulated value of The Pinch"""

		self._accumulated_scale += pinch_event.value()
		self.sig_user_pinch_moved.emit(pinch_event.value(), self._accumulated_scale)

	@QtCore.Slot()
	def reportPinchFinished(self):
		"""User has finished with his little pinches"""

		self._tracked_gesture_count -= 1
		logging.getLogger(__name__).debug("End gesture, active_gestures=%s",self._tracked_gesture_count)
		
		if self._tracked_gesture_count < 1:
			
			self._reset()
			self.sig_user_pinch_finished.emit()
	
	def _reset(self):
		"""Reset tracking values for next pinch"""

		self._tracked_gesture_count = 0
		self._accumulated_scale = 0
		
		logging.getLogger(__name__).debug("Pinch reset")


class BSPanEventFilter(QtCore.QObject):
	"""Handle user panning via mouse wheel or multitouch trackpad"""

	sig_user_pan_started  = QtCore.Signal()
	"""User began the pan"""

	sig_user_pan_moved    = QtCore.Signal(QtCore.QPoint, QtCore.QPoint)
	"""User has panned (`delta:QtCore.QPoint`, `accumulated:QtCore.QPoint`)"""

	sig_user_pan_finished = QtCore.Signal()
	"""User has tired of the pan"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._panning_active = False
		self._accumulated_pan = QtCore.QPoint(0,0)
		self._last_start_pos  = QtCore.QPoint(0,0)

		self.parent().installEventFilter(self)

	def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent) -> bool:
		
		if event.type() == QtCore.QEvent.Type.Wheel and event.deviceType() == QtGui.QInputDevice.DeviceType.TouchPad:
			return self.handleTouchpadInput(event)
		
		elif event.type() in (QtCore.QEvent.Type.MouseButtonPress, QtCore.QEvent.Type.MouseButtonRelease, QtCore.QEvent.Type.MouseMove):
			return self.handleMouseInput(event)
		
		#else:
		#	print("Skip", event)
		
		return False
	
	def handleMouseInput(self, mouse_event:QtGui.QMouseEvent) -> bool:

		if mouse_event.type() == QtCore.QEvent.Type.MouseButtonPress and mouse_event.button() == QtCore.Qt.MouseButton.MiddleButton:

			self.reportPanStarted(mouse_event)
			return True

		elif mouse_event.type() == QtCore.QEvent.Type.MouseMove and self._panning_active:

			# Calculate position changed since last sample
			pos_abs   = mouse_event.position().toPoint()
			pos_delta = pos_abs - self._last_start_pos

			self._last_start_pos = pos_abs
			
			self.reportPanChanged(mouse_event, pos_delta)
			return True
		
		elif mouse_event.type() == QtCore.QEvent.Type.MouseButtonRelease and mouse_event.button() == QtCore.Qt.MouseButton.MiddleButton:

			self.reportPanFinished(mouse_event)
			return True
		
		return False
	
	def handleTouchpadInput(self, pan_event:QtGui.QWheelEvent) -> bool:
		"""Handle pan from touchpad"""

		if pan_event.phase() == QtCore.Qt.ScrollPhase.ScrollUpdate:
				
			self.reportPanChanged(pan_event, pan_event.angleDelta())
			return True
		
		elif pan_event.phase() == QtCore.Qt.ScrollPhase.ScrollEnd:
			
			self.reportPanFinished(pan_event)
			return True
		
		return False
	
	def reportPanStarted(self, pan_event:QtGui.QMouseEvent):
		"""User started to pan"""

		if self._panning_active:
			return
		
		self._last_start_pos = pan_event.position().toPoint()
		self._panning_active = True
		
		logging.getLogger(__name__).debug("Pan started (device=%s, start_pos=%s)", pan_event.device(), self._last_start_pos)
		
		self.sig_user_pan_started.emit()

	def reportPanChanged(self, pan_event:QtGui.QMouseEvent, pan_delta:QtCore.QPoint):
		"""User is panning around"""

		if not self._panning_active:
			self.reportPanStarted(pan_event)

		self._accumulated_pan += pan_delta

		self.sig_user_pan_moved.emit(pan_delta, self._accumulated_pan)
	
	def reportPanFinished(self, pan_event:QtGui.QMouseEvent):
		"""User is no longer panning"""

		if not self._panning_active:
			return
		
		self._panning_active = False
		self._accumulated_pan = QtCore.QPoint(0,0)
		self._last_start_pos = QtCore.QPoint(0,0)

		logging.getLogger(__name__).debug("Pan finished (device=%s)", pan_event.device())

		self.sig_user_pan_finished.emit()


class BSWheelZoomEventFilter(QtCore.QObject):
	"""Handle user zoom by scroll wheel"""

	sig_user_zoomed = QtCore.Signal(int, QtCore.Qt.Orientation)
	sig_zoom_reset  = QtCore.Signal()

	def __init__(self, *args, modifier_keys:QtCore.Qt.KeyboardModifier|None=None, angle_threshold:int=24, threshold_ms:int=100, **kwargs):

		super().__init__(*args, **kwargs)

		self._modifiers        = modifier_keys
		self._threshold        = abs(angle_threshold)

		self._accumulated      = 0
		self._last_orientation = QtCore.Qt.Orientation.Vertical
		
		self._threshold_timer  = QtCore.QTimer(parent=self)
		self._threshold_timer.setInterval(threshold_ms)
		self._threshold_timer.setSingleShot(True)
		self._threshold_timer.timeout.connect(self.reset)

		self.parent().installEventFilter(self)

	def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent):
		
		# Skip if non-wheel
		if not event.type() == QtCore.QEvent.Type.Wheel:
			return False

		# Skip if modifiers not included
		if self._modifiers and not event.modifiers() & self._modifiers:
			return False
		
		# Consume but ignore ScrollStart/End
		if event.phase() not in (QtCore.Qt.ScrollPhase.ScrollUpdate, QtCore.Qt.ScrollPhase.NoScrollPhase):
			return True
		
		#print(event.angleDelta())
		
		# Handle, orientation-aware
		if abs(event.angleDelta().x()) > abs(event.angleDelta().y()):
			self.updateLastScroll(event.angleDelta().x(), QtCore.Qt.Orientation.Horizontal)

		elif abs(event.angleDelta().y()) > abs(event.angleDelta().x()):
			self.updateLastScroll(event.angleDelta().y(), QtCore.Qt.Orientation.Vertical)
		
		else:
			logging.getLogger(__name__).warning("Got weird zero-length scroll value: %s", str(event))
			return False

		return True
	
	def updateLastScroll(self, delta:int, orientation:QtCore.Qt.Orientation):

		if orientation != self._last_orientation:
			logging.getLogger(__name__).debug("Resetting: New orientation")
			self.reset()
		
		elif (delta > 0 and self._accumulated < 0) or (delta < 0 and self._accumulated > 0):
			logging.getLogger(__name__).debug("Resetting: New direction")
			self.reset()

		self._last_orientation  = orientation
		self._accumulated      += delta

		if abs(self._accumulated) >= self._threshold:

			self.sig_user_zoomed.emit(self._accumulated, self._last_orientation)
			self.reset()

		else:
#			print(f"{abs(self._accumulated)=} >= {self._threshold=}")
			self._threshold_timer.start()

		return True

	def reset(self):

		self._threshold_timer.stop()

		self._accumulated = 0
		self._last_orientation = QtCore.Qt.Orientation.Vertical

		logging.getLogger(__name__).debug("Accumulation timer reset")
		self.sig_zoom_reset.emit()