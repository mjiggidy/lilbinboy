from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork
from . import releaseinfo, updatesmanager, statusdisplays

class BSUpdatesWindow(QtWidgets.QWidget):
	"""Window for displaying LBB version update info"""

	sig_requestCheckForUpdates = QtCore.Signal()
	sig_requestSetAutoCheck    = QtCore.Signal(bool)

	def __init__(self, updates_manager:updatesmanager.BSUpdatesManager|None=None, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setWindowTitle(self.tr("Check For Updates"))
		self.setMinimumWidth(375)

		self.setLayout(QtWidgets.QVBoxLayout())
		
		# Version number displays
		self._lbl_current_version = QtWidgets.QLabel()
		self._lbl_latest_release_version = QtWidgets.QLabel()

		self._btn_checkForUpdates = QtWidgets.QPushButton()
		self._btn_new_release_download = QtWidgets.QPushButton()
		
		# Loading bar

		self._status_checking        = QtWidgets.QProgressBar()
		self._status_noupdate        = statusdisplays.BSUpdateDisplayMessage()
		self._status_updateavailable = statusdisplays.BSUpdateDisplayNewReleaseAvailable()

		# New release info
		
		# Auto check toggle
		self._chk_automatic = QtWidgets.QCheckBox()

		self._setupWidgets()
		self._setupSignals()

		if updates_manager:
			self.setUpdateManager(updates_manager)
		
	def _setupWidgets(self):
		
		# Version compare setup
		lay_release_compare = QtWidgets.QGridLayout()
		lbl_this_version = QtWidgets.QLabel(self.tr("Installed Version:"))
		lbl_this_version.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		lay_release_compare.addWidget(lbl_this_version, 1, 0)
		lay_release_compare.addWidget(self._lbl_current_version, 1, 1)
		
		lbl_latest_version = QtWidgets.QLabel(self.tr("Latest Version:"))
		lbl_latest_version.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		lay_release_compare.addWidget(lbl_latest_version, 2, 0)
		lay_release_compare.addWidget(self._lbl_latest_release_version, 2, 1)
		lay_release_compare.setColumnStretch(1,1)

		self._btn_new_release_download.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.InsertLink))
		self._btn_new_release_download.setText(self.tr("Download", "Text for download button"))
		self._btn_new_release_download.setHidden(True)
		self._btn_new_release_download.setToolTip(self.tr("Download the latest release"))
		lay_release_compare.addWidget(self._btn_new_release_download, 2,2)

		self._btn_checkForUpdates.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRefresh))
		self._btn_checkForUpdates.setToolTip(self.tr("Check 'er again"))
		lay_release_compare.addWidget(self._btn_checkForUpdates, 2,3)
	
		self.layout().addLayout(lay_release_compare)
		
		# Progress bar setup
		self._status_checking.setRange(0,0)
		self._status_checking.setFormat(self.tr("Connecting to server..."))
		self._status_checking.setHidden(True)

		self._status_checking.setHidden(True)
		self._status_noupdate.setHidden(False)
		self._status_updateavailable.setHidden(True)
		self.layout().addWidget(self._status_checking)
		self.layout().addWidget(self._status_noupdate)
		self.layout().addWidget(self._status_updateavailable)

		# Check for updates
		self._chk_automatic.setText(self.tr("Automatically check for updates"))
		self.layout().addWidget(self._chk_automatic)

	def _setupSignals(self):
		"""Bind initial signals"""
		self._chk_automatic.checkStateChanged.connect(lambda: self.sig_requestSetAutoCheck.emit(self._chk_automatic.isChecked()))
		self._btn_checkForUpdates.clicked.connect(self.sig_requestCheckForUpdates)

	# ---
	# Manager setup
	# ---
	def setUpdateManager(self, manager:updatesmanager.BSUpdatesManager):
		"""Attach to an update manager"""

		# Signals to manager
		self.sig_requestSetAutoCheck.connect(manager.setAutoCheckEnabled)
		self.sig_requestCheckForUpdates.connect(manager.checkForUpdates)

		# Slots from manager
		manager.sig_networkCheckStarted.connect(self.networkCheckStart)
		manager.sig_networkCheckFinished.connect(self.networkCheckFinished)
		manager.sig_cooldownExpired.connect(self.networkCheckAvailable)
		manager.sig_newReleaseAvailable.connect(self.newReleaseAvailable)
		manager.sig_networkCheckError.connect(self.networkCheckError)
		manager.sig_releaseIsCurrent.connect(self.releaseIsCurrent)

		# Initial state
		self._lbl_current_version.setText(manager.currentVersion().toString())
		self._chk_automatic.setChecked(manager.autoCheckEnabled())
		self._btn_checkForUpdates.setDisabled(manager.cooldownInProgress())

		if manager.checkInProgress():
			self.networkCheckStart()
		elif manager.latestReleaseInfo():
			self.newReleaseAvailable(manager.latestReleaseInfo())
		else:
			self.releaseIsCurrent()

	# ---
	# Network check states
	# ---
	@QtCore.Slot()
	def networkCheckStart(self):
		self._lbl_latest_release_version.setText(self.tr("Checking...", "Checking the server for updates"))
		
		self._btn_new_release_download.setHidden(True)

		self._btn_checkForUpdates.setEnabled(False)
		self._btn_checkForUpdates.setToolTip(self.tr("Cooling down...", "Tooltip while 'check for update' button is disabled"))

		self._status_checking.setHidden(False)
		self._status_noupdate.setHidden(True)
		self._status_updateavailable.setHidden(True)
	
		self.adjustSize()
		self.setFixedSize(self.size())

	@QtCore.Slot()
	def networkCheckFinished(self):
		pass
		#self._status_checking.setHidden(True)

	@QtCore.Slot()
	def networkCheckAvailable(self):

		self._btn_checkForUpdates.setEnabled(True)
		self._btn_checkForUpdates.setToolTip(self.tr("Check 'er again"))

	# ---
	# Result displays
	# ---
	@QtCore.Slot(QtNetwork.QNetworkReply.NetworkError)
	def networkCheckError(self, error:QtNetwork.QNetworkReply.NetworkError):
		"""Network check had an error"""

		self._btn_new_release_download.setHidden(True)

		message = self.tr("Cannot connect to updates server!") if error is QtNetwork.QNetworkReply.NetworkError.HostNotFoundError \
			else self.tr("Error checking for update: {error_message}").format(error_message=error.errorString())
		
		self._status_noupdate.setMessage(message)
		self._status_noupdate.setHidden(False)
		self._status_checking.setHidden(True)
		self._status_updateavailable.setHidden(True)
		
		self.adjustSize()
		self.setFixedSize(self.size())

	@QtCore.Slot(releaseinfo.ReleaseInfo)
	def newReleaseAvailable(self, release_info:releaseinfo.ReleaseInfo):

		self._lbl_latest_release_version.setText(release_info.version.toString())

		self._btn_new_release_download.setVisible(True)
		self._btn_new_release_download.setDefault(True)
		self._btn_new_release_download.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(release_info.release_url))

		self._status_updateavailable.setReleaseInfo(release_info)

		self._status_updateavailable.setHidden(False)
		self._status_noupdate.setHidden(True)
		self._status_checking.setHidden(True)

		self.adjustSize()
		self.setMinimumSize(self.size())
		self.setMaximumSize(QtCore.QSize(1000, 1000)) #lol i dunno

	@QtCore.Slot(releaseinfo.ReleaseInfo)
	def releaseIsCurrent(self, release_info:releaseinfo.ReleaseInfo|None=None):

		self._btn_new_release_download.setHidden(True)

		version_string = release_info.version.toString() if release_info else self._lbl_current_version.text()
		self._lbl_latest_release_version.setText(version_string)

		self._status_noupdate.setMessage(self.tr("You are on the latest version.  So that's nice!"))
		self._status_noupdate.setHidden(False)
		self._status_checking.setHidden(True)
		self._status_updateavailable.setHidden(True)

		self.adjustSize()
		self.setFixedSize(self.size())