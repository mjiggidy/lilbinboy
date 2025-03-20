import dataclasses
from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork

URL_RELEASES =  "https://api.github.com/repos/mjiggidy/lilbinboy/releases"

@dataclasses.dataclass
class ReleaseInfo:
	"""Information for a lil' release boy"""

	name:str
	"""Release Name"""

	date:str
	"""Release datetime (UTC)"""

	version:str
	"""Version number"""

	release_notes:str
	"""Release notes (Markdown)"""

	release_url:str
	"""Github Release Page"""

class LBCheckForUpdatesWindow(QtWidgets.QWidget):
	"""Window for displaying LBB version update info"""

	sig_requestCheckForUpdates = QtCore.Signal()
	sig_requestSetAutoCheck    = QtCore.Signal(bool)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setWindowTitle("Check For Updates")
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
		lbl_this_version = QtWidgets.QLabel("Installed Version:")
		lbl_this_version.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		lay_release_compare.addWidget(lbl_this_version, 1, 0)
		lay_release_compare.addWidget(self._lbl_current_version, 1, 1)
		
		lbl_latest_version = QtWidgets.QLabel("Latest Version:")
		lbl_latest_version.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		lay_release_compare.addWidget(lbl_latest_version, 2, 0)
		lay_release_compare.addWidget(self._lbl_latest_release_version, 2, 1)
		lay_release_compare.setColumnStretch(1,1)

		self._btn_new_release_download.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.InsertLink))
		self._btn_new_release_download.setText("Download")
		self._btn_new_release_download.setHidden(True)
		self._btn_new_release_download.setToolTip("Download the latest release")
		lay_release_compare.addWidget(self._btn_new_release_download, 2,2)

		self._btn_checkForUpdates.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRefresh))
		self._btn_checkForUpdates.setToolTip("Check 'er again")
		lay_release_compare.addWidget(self._btn_checkForUpdates, 2,3)
	
		self.layout().addLayout(lay_release_compare)
		
		# Progress bar setup
		self._prg_checking.setRange(0,0)
		self._prg_checking.setFormat("Connecting to server...")
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
		self._chk_automatic.setText("Automatically check for updates")
		self.layout().addWidget(self._chk_automatic)

	def _setupSignals(self):
		"""Bind initial signals"""
		self._chk_automatic.checkStateChanged.connect(lambda: self.sig_requestSetAutoCheck.emit(self._chk_automatic.isChecked()))
		self._btn_checkForUpdates.clicked.connect(self.sig_requestCheckForUpdates)

	# ---
	# Manager setup
	# ---
	def setUpdateManager(self, manager:"LBUpdateManager"):
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
			self.newReleaseAvailable(manager.latestReleaseInfo)
		else:
			self.releaseIsCurrent()

	# ---
	# Network check states
	# ---
	@QtCore.Slot()
	def networkCheckStart(self):
		self._lbl_latest_release_version.setText("Checking...")
		
		self._prg_checking.setVisible(True)
		self._grp_new_release_info.setHidden(True)
		self._grp_no_update.setHidden(True)

		self._btn_new_release_download.setHidden(True)

		self._btn_checkForUpdates.setEnabled(False)
		self._btn_checkForUpdates.setToolTip("Cooling down...")
	
		self.adjustSize()

	@QtCore.Slot()
	def networkCheckFinished(self):
		self._prg_checking.setHidden(True)

	@QtCore.Slot()
	def networkCheckAvailable(self):
		self._btn_checkForUpdates.setEnabled(True)
		self._btn_checkForUpdates.setToolTip("Check 'er again")

	# ---
	# Result displays
	# ---
	@QtCore.Slot(QtNetwork.QNetworkReply.NetworkError)
	def networkCheckError(self, error:QtNetwork.QNetworkReply.NetworkError):
		"""Network check had an error"""

		if error is QtNetwork.QNetworkReply.NetworkError.HostNotFoundError:
			self._lbl_no_update_status.setText(f"Cannot connect to updates server!")
		else:
			self._lbl_no_update_status.setText(f"Error checking for update: {error.name}")
		self._grp_no_update.setVisible(True)
		
		self.adjustSize()

	@QtCore.Slot(ReleaseInfo)
	def newReleaseAvailable(self, release_info:ReleaseInfo):

		self._lbl_latest_release_version.setText(release_info.version)

		self._btn_new_release_download.setVisible(True)

		self._lbl_new_version_name.setText(release_info.name)
		self._lbl_new_release_date.setText("Released " + QtCore.QDateTime.fromString(release_info.date, QtCore.Qt.DateFormat.ISODate).toLocalTime().toString("dd MMMM yyyy"))
		self._btn_new_release_download.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(release_info.release_url)))
		self._txt_new_release_notes.setMarkdown(release_info.release_notes)
		
		self._grp_new_release_info.setVisible(True)

		self.adjustSize()

	@QtCore.Slot(ReleaseInfo)
	def releaseIsCurrent(self, release_info:ReleaseInfo|None=None):

		version_string = release_info.version if release_info else self._lbl_current_version.text()
		self._lbl_latest_release_version.setText(version_string)
		self._grp_new_release_info.setHidden(True)
		self._lbl_no_update_status.setText("You are on the latest version.  So that's nice!")
		self._grp_no_update.setVisible(True)

		self.adjustSize()

	


class LBUpdateManager(QtCore.QObject):
	"""Controller for checking for LBB version updates via Github releases"""

	sig_networkCheckStarted  = QtCore.Signal()
	sig_networkCheckFinished = QtCore.Signal()
	sig_networkCheckError    = QtCore.Signal(QtNetwork.QNetworkReply.NetworkError)
	sig_cooldownExpired      = QtCore.Signal()

	sig_newReleaseAvailable  = QtCore.Signal(ReleaseInfo)
	sig_releaseIsCurrent     = QtCore.Signal(ReleaseInfo)

	def __init__(self, url_releases:QtCore.QUrl, *args, **kwargs):

		self._netman = QtNetwork.QNetworkAccessManager()
		self._url_releases = url_releases
		self._current_request = None
		self._cooldown_timer = QtCore.QTimer(interval=10000, singleShot=True)  # 10 seconds

		self._autocheck_timer = QtCore.QTimer(interval=30000, singleShot=True) # 30 seconds
		self._autocheck_enabled = False

		self._latest_release_info = None
		"""The last latest release found"""

		super().__init__(*args, **kwargs)

		# Signals
		self._cooldown_timer.timeout.connect(self.sig_cooldownExpired)
		self._autocheck_timer.timeout.connect(self.checkForUpdates)
		self._autocheck_timer.timeout.connect(lambda: print("AUTOCHECK BOYYYY"))

		self._netman.finished.connect(self._cooldown_timer.start)
		self._netman.finished.connect(self.processNetworkReply)
		self._netman.finished.connect(self.sig_networkCheckFinished)
	
	# ---
	# Releases URL
	# ---
	def releasesUrl(self) -> QtCore.QUrl:
		"""URL for Release Info JSON"""
		return self._url_releases
	
	def setReleasesUrl(self, url_releases:QtCore.QUrl):
		"""Set the URL for Release Info JSON"""
		self._url_releases = url_releases

	# ---
	# Cooldown timer for API rate limiting
	# ---
	def setCooldownInterval(self, milliseconds:int):
		"""Set cooldown interval (in milliseconds) for API rate limiting"""
		if milliseconds > self.autoCheckInterval():
			raise ValueError(f"Cooldown interval must be less than autocheck interval")
		self._cooldown_timer.setInterval(milliseconds)
	
	def cooldownInterval(self) -> int:
		"""Cooldown interval (in milliseconds) for API rate limiting"""
		return self._cooldown_timer.interval()
	
	def cooldownInProgress(self) -> bool:
		"""Whether we coolin it"""
		return self._cooldown_timer.isActive()
	
	# ---
	# Autocheck
	# ---
	def setAutoCheckEnabled(self, autocheck:bool):
		"""Set automatically check for updates"""
		self._autocheck_enabled = autocheck

		# Start autocheck if a new release hasn't already been found
		if self.autoCheckEnabled() and self.latestReleaseInfo() is None:
			if self._cooldown_timer.isActive():
				print("Sched")
				# Schedule autocheck
				self._autocheck_timer.start()
			else:
				# or just do it
				self.checkForUpdates()

		else:
			self._autocheck_timer.stop()

	def autoCheckEnabled(self) -> bool:
		"""Is automatically checl for updates enabled"""
		return self._autocheck_enabled
	
	def setAutoCheckInterval(self, milliseconds:int):
		"""Set how often (in milliseconds) to check for updates if autocheck is enabled"""
		if milliseconds < self.cooldownInterval():
			raise ValueError(f"Autocheck interval must be greater than cooldown interval")
		self._autocheck_timer.setInterval(milliseconds)

	def autoCheckInterval(self) -> int:
		"""How often (in milliseconds) to check for updates if autocheck is enabled"""
		return self._autocheck_timer.interval()
	
	# ---
	# Version/Release info
	# ---
	def currentVersion(self) -> str:
		"""Get Lil' Bin Boy current version"""
		return QtWidgets.QApplication.instance().applicationVersion()
	
	def latestReleaseInfo(self) -> ReleaseInfo|None:
		"""The latest release info gathered from the last time network check succeeded"""
		return self._latest_release_info

	# ---
	# Network Check
	# ---

	def checkInProgress(self) -> bool:
		"""Indicates a current check is in progress"""
		# Useful for setting window initial state
		return self._current_request is not None
	
	@QtCore.Slot()
	def checkForUpdates(self):
		"""Initiate check for updates via network"""
		
		# Skip if we have an active QNetworkRequest or in cooldown period
		if self.checkInProgress() or self._cooldown_timer.isActive():
			return
		
		self.sig_networkCheckStarted.emit()
		self._current_request = self._netman.get(QtNetwork.QNetworkRequest(self.releasesUrl()))

	@QtCore.Slot(QtNetwork.QNetworkReply)
	def processNetworkReply(self, reply:QtNetwork.QNetworkReply):
		"""Read the ReleaseInfo JSON and determine if a new version is available"""

		# Unset current
		self._current_request = None

		if reply.error() is not QtNetwork.QNetworkReply.NetworkError.NoError:
			self.sig_networkCheckError.emit(reply.error())
			#print(reply.error())
			return

		# Parse JSON for latest version
		response = QtCore.QJsonDocument.fromJson(reply.readAll())
		latest_release:dict = response.array().first().toObject()

		# Latest version to `ReleaseInfo` struct
		latest_release_info = ReleaseInfo(
			name = latest_release.get("name"),
			version = latest_release.get("tag_name")[1:], # Strip 'v'
			release_notes = latest_release.get("body"),
			release_url = latest_release.get("html_url"),
			date = latest_release.get("published_at")
		)

		if self.currentVersion() != latest_release_info.version:
			# Store and emit new release info
			self._latest_release_info = latest_release_info
			self.sig_newReleaseAvailable.emit(latest_release_info)
		
		else:
			# Restart autocheck
			self.sig_releaseIsCurrent.emit(latest_release_info)
			if self.autoCheckEnabled():
				self._autocheck_timer.start()

if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")
	app.setApplicationVersion("0.1.8")

	man = LBUpdateManager(QtCore.QUrl(URL_RELEASES))
	man.checkForUpdates()

	wnd = LBCheckForUpdatesWindow()
	wnd.setUpdateManager(man)

	wnd.show()
	app.exec()