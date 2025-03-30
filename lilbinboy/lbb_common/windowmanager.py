from PySide6 import QtCore, QtGui, QtWidgets

class WindowManager(QtCore.QObject):

	def __init__(self, window:QtWidgets.QWidget, settings:QtCore.QSettings, settings_name:str, relative_to:QtWidgets.QWidget|None=None):

		super().__init__()
		
		self._window = window
		self._settings = settings
		self._settings_name = settings_name
		self._wndow_relative_to = relative_to

		self._timer_window_geometry = QtCore.QTimer(singleShot=True, interval=200)

		self._setupSignals()

		self._window.installEventFilter(self)

	def _setupSignals(self):

		# Timer to save window geometry changes (fired via self.eventFilter)
		self._timer_window_geometry.timeout.connect(self.saveWindowGeometry)

		# Screens added or removed
		QtWidgets.QApplication.instance().screenAdded.connect(self.screenWasAdded)
		QtWidgets.QApplication.instance().screenAdded.connect(self.screenLayoutChanged)
		QtWidgets.QApplication.instance().screenRemoved.connect(self.screenLayoutChanged)

	@QtCore.Slot(QtGui.QScreen)
	def screenWasAdded(self, screen:QtGui.QScreen):
		# Setup listeners for screens added/removed/changed

		screen.geometryChanged.connect(self.screenLayoutChanged)

	@QtCore.Slot(QtGui.QScreen)	# screenAdded/screenRemoved
	@QtCore.Slot(QtCore.QRect)	# geometryChanged
	def screenLayoutChanged(self, changed:QtGui.QScreen|QtCore.QRect):
		"""Screens were added, removed, or changed"""

		self.restoreWindowGeometry()

	@QtCore.Slot()
	def restoreWindowGeometry(self):
		"""Restore a window's position from settings (or default)"""

		# NOTE: Screen geometry and window geometry are both returned as `QRect`s
		# in a global space.  So, will want to validate QScreen.geometry().contains(QWindow.geometry())

		saved_window_geometry = self._settings.value(self._settings_name+"/window_geometry", self._window.geometry())

		new_window_geometry = None

		for screen in QtWidgets.QApplication.screens():
			if screen.geometry().contains(saved_window_geometry):
				new_window_geometry = saved_window_geometry
		
		# Center window in primary screen if nothing else
		# NOTE: Maybe adapt this for "relative to" windows
		if new_window_geometry is None:
			primary_screen_geometry = QtWidgets.QApplication.primaryScreen().geometry()
			new_window_geometry = saved_window_geometry
			new_window_geometry.moveCenter(primary_screen_geometry.center())

		self._window.setGeometry(new_window_geometry)
	
	@QtCore.Slot()
	def saveWindowGeometry(self):
		"""Save a window's geometry"""

		self._settings.setValue(self._settings_name+"/window_geometry", self._window.geometry())

	def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent):
		"""Watch window events"""

		if watched == self._window:
			if event.type() == QtCore.QEvent.Type.Resize or event.type() == QtCore.QEvent.Type.Move:
				self._timer_window_geometry.start()


		return super().eventFilter(watched, event)