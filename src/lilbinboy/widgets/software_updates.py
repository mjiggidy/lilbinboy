from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork
from ..managers import software_updates

class BSCheckForUpdatesWindow(QtWidgets.QWidget):
	"""Window for displaying LBB version update info"""

	sig_requestCheckForUpdates = QtCore.Signal()
	sig_requestSetAutoCheck    = QtCore.Signal(bool)

	def __init__(self, *args, **kwargs):
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
		self._prg_checking = QtWidgets.QProgressBar()

		# New release info
		self._grp_new_release_info = QtWidgets.QGroupBox()
		self._lbl_new_version_name = QtWidgets.QLabel()
		self._lbl_new_release_date = QtWidgets.QLabel()
		self._txt_new_release_notes = QtWidgets.QTextBrowser()

		# No updates info
		self._grp_no_update = QtWidgets.QGroupBox()
		self._lbl_no_update_status = QtWidgets.QLabel()
		
		# Auto check toggle
		self._chk_automatic = QtWidgets.QCheckBox()

		self._setupWidgets()
		self._setupSignals()
		
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
		self._prg_checking.setRange(0,0)
		self._prg_checking.setFormat(self.tr("Connecting to server..."))
		self._prg_checking.setHidden(True)

		self.layout().addWidget(self._prg_checking)

		# New release info
		self._grp_new_release_info.setLayout(QtWidgets.QVBoxLayout())

		font = self._lbl_new_version_name.font()
		font.setBold(True)
		self._lbl_new_version_name.setFont(font)

		self._txt_new_release_notes.setReadOnly(True)
		self._txt_new_release_notes.setOpenLinks(False)
		self._txt_new_release_notes.setOpenExternalLinks(False)
		self._txt_new_release_notes.anchorClicked.connect(QtGui.QDesktopServices.openUrl)

		self._grp_new_release_info.setLayout(QtWidgets.QVBoxLayout())
		self._grp_new_release_info.layout().addWidget(self._lbl_new_version_name)
		self._grp_new_release_info.layout().addWidget(self._lbl_new_release_date)
		self._grp_new_release_info.layout().addWidget(self._txt_new_release_notes)
		self._grp_new_release_info.setHidden(True)

		self.layout().addWidget(self._grp_new_release_info)

		# No update status info
		self._grp_no_update.setLayout(QtWidgets.QHBoxLayout())
		self._grp_no_update.layout().addWidget(self._lbl_no_update_status)
		self._grp_no_update.setHidden(True)
		
		self.layout().addWidget(self._grp_no_update)

		self.layout().addStretch()

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
	def setUpdateManager(self, manager:software_updates.BSUpdatesManager):
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
		self._lbl_current_version.setText(manager.currentVersion())
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
		
		self._prg_checking.setVisible(True)
		self._grp_new_release_info.setHidden(True)
		self._grp_no_update.setHidden(True)

		self._btn_new_release_download.setHidden(True)

		self._btn_checkForUpdates.setEnabled(False)
		self._btn_checkForUpdates.setToolTip(self.tr("Cooling down...", "Tooltip while 'check for update' button is disabled"))
	
		self.adjustSize()

	@QtCore.Slot()
	def networkCheckFinished(self):
		self._prg_checking.setHidden(True)

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

		if error is QtNetwork.QNetworkReply.NetworkError.HostNotFoundError:
			self._lbl_no_update_status.setText(self.tr("Cannot connect to updates server!"))
		else:
			self._lbl_no_update_status.setText(self.tr("Error checking for update: {error_message}").format(error_message=error.name))
		self._grp_no_update.setVisible(True)
		
		self.adjustSize()

	@QtCore.Slot(software_updates.ReleaseInfo)
	def newReleaseAvailable(self, release_info:software_updates.ReleaseInfo):

		self._lbl_latest_release_version.setText(release_info.version)

		self._btn_new_release_download.setVisible(True)
		self._btn_new_release_download.setDefault(True)

		self._lbl_new_version_name.setText(release_info.name)
		self._lbl_new_release_date.setText(self.tr("Released {date_of_release}").format(
			date_of_release=QtCore.QDateTime.fromString(release_info.date, QtCore.Qt.DateFormat.ISODate).toLocalTime().toString("dd MMMM yyyy"))
		)
		self._btn_new_release_download.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(release_info.release_url)))
		self._txt_new_release_notes.setMarkdown(release_info.release_notes)
		
		self._grp_new_release_info.setVisible(True)

		self.adjustSize()

	@QtCore.Slot(software_updates.ReleaseInfo)
	def releaseIsCurrent(self, release_info:software_updates.ReleaseInfo|None=None):

		version_string = release_info.version if release_info else self._lbl_current_version.text()
		self._lbl_latest_release_version.setText(version_string)
		self._grp_new_release_info.setHidden(True)
		self._lbl_no_update_status.setText(self.tr("You are on the latest version.  So that's nice!"))
		self._grp_no_update.setVisible(True)

		self.adjustSize()