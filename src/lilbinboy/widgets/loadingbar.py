from PySide6 import QtCore, QtGui, QtWidgets

class BSAnimatedProgressBar(QtWidgets.QProgressBar):
	"""A progress bar with animation and poise"""

	DEFAULT_PROGRESS_ANIMATION_DURATION_MSEC     = 5_000
	DEFAULT_PROGRESS_ANIMATION_EASING_CURVE_TYPE = QtCore.QEasingCurve.Type.Linear

	def __init__(self, *args, default_animation_duration_msec:int|None=None, default_animation_easing_curve_type:QtCore.QEasingCurve.Type|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._anim_progress = QtCore.QVariantAnimation(parent=self)
		
		self._anim_default_duration = default_animation_duration_msec \
			if default_animation_duration_msec is not None \
			else self.DEFAULT_PROGRESS_ANIMATION_DURATION_MSEC
		
		self._anim_default_curve_type = default_animation_easing_curve_type \
			if default_animation_easing_curve_type is not None \
			else self.DEFAULT_PROGRESS_ANIMATION_EASING_CURVE_TYPE
		
		self._anim_progress.valueChanged.connect(self.setValue)
	
	def animator(self) -> QtCore.QVariantAnimation:

		return self._anim_progress
	
	@QtCore.Slot(int)
	def animateToValue(self, to_value:int, /, duration_msec:int|None=None, easing_curve_type:QtCore.QEasingCurve.Type|None=None):
		"""Animate progress from current value to another value"""

		self._anim_progress.stop()

		self._anim_progress.setStartValue(self.value())
		self._anim_progress.setEndValue(to_value)
		self._anim_progress.setDuration(duration_msec if duration_msec is not None else self._anim_default_duration)
		self._anim_progress.setEasingCurve(easing_curve_type if easing_curve_type is not None else self._anim_default_curve_type)

#		print(f"{self._anim_progress.startValue()=} {self._anim_progress.endValue()=} {self._anim_progress.duration()=}")

		self._anim_progress.start()