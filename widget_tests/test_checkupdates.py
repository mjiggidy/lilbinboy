import dataclasses
from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork

URL_RELEASES = r"https://api.github.com/repos/mjiggidy/lilbinboy/releases"

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

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setWindowTitle("Check For Updates")

		self.setLayout(QtWidgets.QVBoxLayout())

		# Set up widgets
		self._stack_status = QtWidgets.QStackedWidget()	# 

		self._btn_check = QtWidgets.QPushButton()
		self._chk_automatic = QtWidgets.QCheckBox("Automatically check for updates")
		self._prg_checking = QtWidgets.QProgressBar()

		self._prg_checking.setRange(0,0)
		self._prg_checking.setFormat("Connecting to server...")

		self._grp_new_release_info = QtWidgets.QGroupBox()
		self._grp_new_release_info.setLayout(QtWidgets.QVBoxLayout())

		self._lay_new_version_info = QtWidgets.QHBoxLayout()


		self._lay_new_version_info.addWidget(QtWidgets.QLabel("A new version is available!"))
		self._lay_new_version_info.addStretch()
		
		self._btn_new_release_download = QtWidgets.QPushButton()
		self._btn_new_release_download.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.InsertLink))
		self._btn_new_release_download.setText("Download")
		self._lay_new_version_info.addWidget(self._btn_new_release_download)

		self._grp_new_release_info.layout().addLayout(self._lay_new_version_info)

		self._grp_no_update = QtWidgets.QGroupBox()
		self._grp_no_update.setLayout(QtWidgets.QHBoxLayout())

		self._grp_no_update.layout().addWidget(QtWidgets.QLabel("You are on the latest version.  That's nice!"))

		self._lbl_latest_release_version = QtWidgets.QLabel("Checking...")
		
		self._lbl_new_version_name = QtWidgets.QLabel()
		font = self._lbl_new_version_name.font()
		font.setBold(True)
		self._lbl_new_version_name.setFont(font)

		self._lbl_new_release_date = QtWidgets.QLabel()
		self._lbl_new_release_url = QtWidgets.QLabel()
		self._lbl_new_release_url.setOpenExternalLinks(True)
		self._lbl_new_release_url.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByKeyboard|QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse)

		self._txt_new_release_notes = QtWidgets.QTextBrowser()
		self._txt_new_release_notes.setReadOnly(True)
		self._txt_new_release_notes.setOpenLinks(False)
		self._txt_new_release_notes.setOpenExternalLinks(False)
		self._txt_new_release_notes.anchorClicked.connect(QtGui.QDesktopServices.openUrl)

		#self._txt_release_notes.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByKeyboard|QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse)

		lay_release_compare = QtWidgets.QGridLayout()
		lbl_this_version = QtWidgets.QLabel("Installed Version:")
		lbl_this_version.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		lay_release_compare.addWidget(lbl_this_version, 1, 0)
		lay_release_compare.addWidget(QtWidgets.QLabel(QtWidgets.QApplication.instance().applicationVersion()), 1, 1)
		
		lbl_latest_version = QtWidgets.QLabel("Latest Version:")
		lbl_latest_version.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		lay_release_compare.addWidget(lbl_latest_version, 2, 0)
		lay_release_compare.addWidget(self._lbl_latest_release_version, 2, 1)
		lay_release_compare.setColumnStretch(1,1)

		#self._btn_check.setText("Refresh")
		self._btn_check.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRefresh))
		self._btn_check.setToolTip("Check 'er again")
		self._btn_check.setIconSize(QtCore.QSize(8,8))
		lay_release_compare.addWidget(self._btn_check, 2, 2)
		




		
		#self.layout().addWidget(QtWidgets.QLabel("Lil' Bin Boy"))
		self.layout().addLayout(lay_release_compare)


		self._stack_status.addWidget(self._prg_checking)
		#self._stack_status.addWidget(self._grp_new_release_info)
		#self._stack_status.addWidget(self._grp_no_update)
		self.layout().addWidget(self._stack_status)

		self.layout().addStretch()

		self._grp_release_info = QtWidgets.QVBoxLayout()
		#elf._grp_release_info.layout().setSpacing(0)
		#self._grp_release_info.layout().setContentsMargins(0,0,0,0)
		#self._grp_release_info.setHidden(True)

		self._grp_release_info.addWidget(self._lbl_new_version_name)
		self._grp_release_info.addWidget(self._lbl_new_release_date)
		self._grp_release_info.addWidget(self._txt_new_release_notes)
		#self._grp_release_info.layout().addWidget(self._btn_download)

		self._grp_new_release_info.layout().addLayout(self._grp_release_info)

		self.layout().addWidget(self._chk_automatic)
	

		#self._prg_checking.setHidden(True)
	
	@QtCore.Slot()
	def networkCheckStart(self):
		self._stack_status.setCurrentWidget(self._prg_checking)

	@QtCore.Slot(ReleaseInfo)
	def setLatestVersion(self, release_info:ReleaseInfo):

		if release_info.version != QtWidgets.QApplication.instance().applicationVersion():
			self._lbl_latest_release_version.setText(release_info.version)

			self._lbl_new_version_name.setText(release_info.name)
			self._lbl_new_release_date.setText("Released " + QtCore.QDateTime.fromString(release_info.date, QtCore.Qt.DateFormat.ISODate).toLocalTime().toString("dd MMMM yyyy"))
			self._btn_new_release_download.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(release_info.release_url)))
			self._txt_new_release_notes.setMarkdown(release_info.release_notes)
			#self._grp_release_info.setHidden(False)

			self._stack_status.setCurrentWidget(self._grp_new_release_info)
		
		else:
			self._stack_status.setCurrentWidget(self._grp_no_update)
			self._lbl_new_version_name.setText("You are on the latest version")
	


class LBUpdateManager(QtCore.QObject):

	sig_networkCheckStarted  = QtCore.Signal()
	sig_networkCheckFinished = QtCore.Signal()
	sig_cooldownExpired		 = QtCore.Signal()
	sig_newReleaseAvailable  = QtCore.Signal(ReleaseInfo)


	def __init__(self, url_releases:QtCore.QUrl, *args, **kwargs):

		self._netman = QtNetwork.QNetworkAccessManager()
		self._url_releases = url_releases
		self._current_request = None

		self._autocheck_timer = QtCore.QTimer(interval=30000, singleShot=False) # 30 seconds, looping
		self._autocheck_enabled = False

		self._cooldown_timer = QtCore.QTimer(interval=10000, singleShot=True)  # 10 seconds

		super().__init__(*args, **kwargs)

		# Signals
		self._cooldown_timer.timeout.connect(self.sig_cooldownExpired)
		self._autocheck_timer.timeout.connect(self.checkForUpdates)
		self._autocheck_timer.timeout.connect(lambda: print("AUTOCHECK BOYYYY"))

		self._netman.finished.connect(self.sig_networkCheckFinished)
		self._netman.finished.connect(self.processNetworkReply)
	
	def releasesUrl(self) -> QtCore.QUrl:
		"""URL for Release Info JSON"""
		return self._url_releases
	
	def setReleasesUrl(self, url_releases:QtCore.QUrl):
		"""Set the URL for Release Info JSON"""
		self._url_releases = url_releases
	
	def setAutoCheckEnabled(self, autocheck:bool):
		"""Set automatically check for updates"""
		self._autocheck_enabled = autocheck
		if self.autoCheckEnabled():
			self._autocheck_timer.start()
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
	
	def setCooldownInterval(self, milliseconds:int):
		"""Set cooldown interval (in milliseconds) for API rate limiting"""
		if milliseconds > self.autoCheckInterval():
			raise ValueError(f"Cooldown interval must be less than autocheck interval")
		self._cooldown_timer.setInterval(milliseconds)
	
	def cooldownInterval(self) -> int:
		"""Cooldown interval (in milliseconds) for API rate limiting"""
		return self._cooldown_timer.interval()
	
	def currentVersion(self) -> str:
		"""Get Lil' Bin Boy current version"""
		return QtWidgets.QApplication.instance().applicationVersion()
	
	def networkCheckFinished(self):
		"""Check for updates is complete"""
		pass

	@QtCore.Slot(QtNetwork.QNetworkReply)
	def processNetworkReply(self, reply:QtNetwork.QNetworkReply):
		"""Read the ReleaseInfo JSON and determine if a new version is available"""

		# Restart cooldown period
		self._cooldown_timer.start()

		# Unset current
		self._current_request = None

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

		# New version available?
		if self.currentVersion() != latest_release_info.version:
			print("Oh yeah")
			self.sig_newReleaseAvailable.emit(latest_release_info)

	@QtCore.Slot()
	def checkForUpdates(self):
		"""Initiate check for updates via network"""
		
		# Skip if we have an active QNetworkRequest or in cooldown period
		if self._current_request is not None or self._cooldown_timer.isActive():
			print("Ignore")
			return
		
		print("Check")
		self.sig_networkCheckStarted.emit()
		self._current_request = self._netman.get(QtNetwork.QNetworkRequest(self.releasesUrl()))


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")
	app.setApplicationVersion("0.1.8")

	man = LBUpdateManager(QtCore.QUrl(URL_RELEASES))
	wnd = LBCheckForUpdatesWindow()

	wnd._chk_automatic.checkStateChanged.connect(lambda: man.setAutoCheckEnabled(wnd._chk_automatic.isChecked()))
	wnd._btn_check.clicked.connect(man.checkForUpdates)

	man.sig_networkCheckStarted.connect(lambda: wnd._btn_check.setEnabled(False))
	man.sig_cooldownExpired.connect(lambda: wnd._btn_check.setEnabled(True))

#	man.checkForUpdates()
#	man.setAutoCheckEnabled(True)
	wnd.show()
	app.exec()