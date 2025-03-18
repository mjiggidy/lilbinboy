import dataclasses
from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork

URL_RELEASES = r"https://api.github.com/repos/mjiggidy/lilbinboy/releases"

@dataclasses.dataclass
class ReleaseInfo:
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

	release_url:str

class LBCheckForUpdatesWindow(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setWindowTitle("Check For Updates")
		#self.setFixedWidth(300)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._stack_status = QtWidgets.QStackedWidget()

		self._chk_automatic = QtWidgets.QCheckBox("Check automatically at startup")

		self._prg_checking = QtWidgets.QProgressBar()
		self._prg_checking.setRange(0,0)
		self._prg_checking.setFormat("Connecting to server...")

		self._grp_new_version = QtWidgets.QGroupBox()
		self._grp_new_version.setLayout(QtWidgets.QVBoxLayout())

		self._lay_new_version_announce = QtWidgets.QHBoxLayout()


		self._lay_new_version_announce.addWidget(QtWidgets.QLabel("A new version is available!"))
		self._lay_new_version_announce.addStretch()
		
		self._btn_download = QtWidgets.QPushButton()
		self._btn_download.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.InsertLink))
		self._btn_download.setText("Download")
		self._lay_new_version_announce.addWidget(self._btn_download)

		self._grp_new_version.layout().addLayout(self._lay_new_version_announce)

		self._grp_no_update = QtWidgets.QGroupBox()
		self._grp_no_update.setLayout(QtWidgets.QHBoxLayout())

		self._grp_no_update.layout().addWidget(QtWidgets.QLabel("You are on the latest version.  That's nice!"))

		self._lbl_version_latest = QtWidgets.QLabel("Checking...")
		
		self._lbl_release_name = QtWidgets.QLabel()
		font = self._lbl_release_name.font()
		font.setBold(True)
		self._lbl_release_name.setFont(font)

		self._lbl_release_date = QtWidgets.QLabel()
		self._lbl_version_url = QtWidgets.QLabel()
		self._lbl_version_url.setOpenExternalLinks(True)
		self._lbl_version_url.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByKeyboard|QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse)

		self._txt_release_notes = QtWidgets.QTextBrowser()
		self._txt_release_notes.setReadOnly(True)
		self._txt_release_notes.setOpenLinks(False)
		self._txt_release_notes.setOpenExternalLinks(False)
		self._txt_release_notes.anchorClicked.connect(QtGui.QDesktopServices.openUrl)

		#self._txt_release_notes.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.LinksAccessibleByKeyboard|QtCore.Qt.TextInteractionFlag.LinksAccessibleByMouse)

		lay_version = QtWidgets.QGridLayout()
		lbl_this_version = QtWidgets.QLabel("Installed Version:")
		lbl_this_version.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		lay_version.addWidget(lbl_this_version, 1, 0)
		lay_version.addWidget(QtWidgets.QLabel(QtWidgets.QApplication.instance().applicationVersion()), 1, 1)
		
		lbl_latest_version = QtWidgets.QLabel("Latest Version:")
		lbl_latest_version.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		lay_version.addWidget(lbl_latest_version, 2, 0)
		lay_version.addWidget(self._lbl_version_latest, 2, 1)
		lay_version.setColumnStretch(2,1)


		
		#self.layout().addWidget(QtWidgets.QLabel("Lil' Bin Boy"))
		self.layout().addLayout(lay_version)


		self._stack_status.addWidget(self._prg_checking)
		self._stack_status.addWidget(self._grp_new_version)
		self._stack_status.addWidget(self._grp_no_update)
		self.layout().addWidget(self._stack_status)

		self.layout().addStretch()

		self._grp_release_info = QtWidgets.QVBoxLayout()
		#elf._grp_release_info.layout().setSpacing(0)
		#self._grp_release_info.layout().setContentsMargins(0,0,0,0)
		#self._grp_release_info.setHidden(True)

		self._grp_release_info.addWidget(self._lbl_release_name)
		self._grp_release_info.addWidget(self._lbl_release_date)
		self._grp_release_info.addWidget(self._txt_release_notes)
		#self._grp_release_info.layout().addWidget(self._btn_download)

		self._grp_new_version.layout().addLayout(self._grp_release_info)

		self.layout().addWidget(self._chk_automatic)
	

		#self._prg_checking.setHidden(True)
	
	@QtCore.Slot()
	def networkCheckStart(self):
		self._stack_status.setCurrentWidget(self._prg_checking)

	@QtCore.Slot(ReleaseInfo)
	def setLatestVersion(self, release_info:ReleaseInfo):

		if release_info.version != QtWidgets.QApplication.instance().applicationVersion():
			self._lbl_version_latest.setText(release_info.version)

			self._lbl_release_name.setText(release_info.name)
			self._lbl_release_date.setText("Released " + QtCore.QDateTime.fromString(release_info.date, QtCore.Qt.DateFormat.ISODate).toLocalTime().toString("dd MMMM yyyy"))
			self._btn_download.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(release_info.release_url)))
			self._txt_release_notes.setMarkdown(release_info.release_notes)
			#self._grp_release_info.setHidden(False)

			self._stack_status.setCurrentWidget(self._grp_new_version)
		
		else:
			self._stack_status.setCurrentWidget(self._grp_no_update)
			self._lbl_release_name.setText("You are on the latest version")
	


class LBUpdateManager(QtCore.QObject):

	sig_networkCheckStarted  = QtCore.Signal()
	sig_networkCheckFinished = QtCore.Signal()
	sig_newReleaseAvailable  = QtCore.Signal(ReleaseInfo)


	def __init__(self, url_releases:QtCore.QUrl, *args, **kwargs):

		self._netman = QtNetwork.QNetworkAccessManager()
		self._url_releases = url_releases
		self._current_request = None

		self._auto_check_timer = QtCore.QTimer(interval=10000, singleShot=True) # 10 seconds
		self._auto_check = False

		super().__init__(*args, **kwargs)

		# Signals
		self._auto_check_timer.timeout.connect(self.checkForUpdates)

		self._netman.finished.connect(self.sig_networkCheckFinished)
		self._netman.finished.connect(self.processNetworkReply)
	
	def releasesUrl(self) -> QtCore.QUrl:
		return self._url_releases
	
	def setReleasesUrl(self, url_releases:str):
		self._url_releases = url_releases
	
	def setAutomaticallyCheckForUpdates(self, autocheck:bool):
		self._auto_check = autocheck

		if autocheck and not self._auto_check_timer.isActive():
			self._auto_check_timer.start()

	def automaticallyCheckForUpdates(self) -> bool:
		return self._auto_check
	
	def setAutoCheckInterval(self, milliseconds:int):
		self._auto_check_timer.setInterval(milliseconds)
	
	def autoCheckInterval(self) -> int:
		return self._auto_check_timer.interval()
	
	def currentVersion(self) -> str:
		return QtWidgets.QApplication.instance().applicationVersion()
	
	def networkCheckFinished(self):
		pass

	@QtCore.Slot(QtNetwork.QNetworkReply)
	def processNetworkReply(self, reply:QtNetwork.QNetworkReply):

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

		if self.automaticallyCheckForUpdates() and not self._auto_check_timer.isActive():
			print("Restarting")
			self._auto_check_timer.start()

		# New version available?
		if self.currentVersion() != latest_release_info.version:
			print("Oh yeah")
			self.sig_newReleaseAvailable.emit(latest_release_info)

	def checkForUpdates(self):
		if self._current_request:
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
	man.checkForUpdates()
#	man.setAutomaticallyCheckForUpdates(True)

	wnd = LBCheckForUpdatesWindow()
	wnd.show()

	wnd._chk_automatic.checkStateChanged.connect(lambda: man.setAutomaticallyCheckForUpdates(wnd._chk_automatic.isChecked()))

	app.exec()