from PySide6 import QtCore, QtWidgets

class TRTBinLoadingProgressBar(QtWidgets.QProgressBar):

	sig_progress_active    = QtCore.Signal()
	"""Progress has started or is added to"""

	sig_progress_completed = QtCore.Signal()
	"""Steps are complete"""

	TIMEOUT_BEFORE_HIDE:int = 1000
	"""Timeout (in msec) before emitting `sig_progress_completed`"""

	def __init__(self):
		super().__init__()

		self.setFormat("Loading %v of %m bins...")

		# Setup timer to hide
		self._reset_timer = QtCore.QTimer()
		self._reset_timer.setInterval(self.TIMEOUT_BEFORE_HIDE)
		self._reset_timer.setSingleShot(True)

		self._reset_timer.timeout.connect(self.reset)
		
		# self.reset() # TODO: Verify I don't need this

	@QtCore.Slot()
	def step_added(self):
		self._reset_timer.stop()
		self.setMaximum(self.maximum() + 1)
		self.sig_progress_active.emit()
	
	@QtCore.Slot()
	def step_complete(self):
		self.setValue(self.value() + 1)
		if self.value() == self.maximum():
			self._reset_timer.start()
	
	@QtCore.Slot()
	def reset(self):
		self.setRange(0,0)
		self.setValue(0)
		self.sig_progress_completed.emit()