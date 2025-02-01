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
		#self._prg_checking.setHidden(True)

		self._grp_new_version = QtWidgets.QGroupBox()
		self._grp_new_version.setLayout(QtWidgets.QHBoxLayout())
		#self._grp_new_version.layout().setSpacing(0)
		#self._grp_new_version.layout().setContentsMargins(0,0,0,0)
		self._grp_new_version.layout().addWidget(QtWidgets.QLabel("A new version is available!"))
		self._grp_new_version.layout().addStretch()
		
		self._btn_download = QtWidgets.QPushButton()
		self._btn_download.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.InsertLink))
		self._btn_download.setText("Download")
		self._grp_new_version.layout().addWidget(self._btn_download)

		self._grp_no_update = QtWidgets.QGroupBox()
		self._grp_no_update.setLayout(QtWidgets.QHBoxLayout())
		#self._grp_no_update.layout().setSpacing(0)
		#self._grp_no_update.setContentsMargins(0,0,0,0)
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

		self._grp_release_info = QtWidgets.QGroupBox()
		self._grp_release_info.setLayout(QtWidgets.QVBoxLayout())
		#elf._grp_release_info.layout().setSpacing(0)
		#self._grp_release_info.layout().setContentsMargins(0,0,0,0)
		self._grp_release_info.setHidden(True)

		self._grp_release_info.layout().addWidget(self._lbl_release_name)
		self._grp_release_info.layout().addWidget(self._lbl_release_date)
		self._grp_release_info.layout().addWidget(self._txt_release_notes)
		#self._grp_release_info.layout().addWidget(self._btn_download)

		self.layout().addWidget(self._grp_release_info)

		self.layout().addWidget(self._chk_automatic)
	
	@QtCore.Slot()
	def networkCheckStart(self):
		self._stack_status.setCurrentWidget(self._prg_checking)
	
	def networkCheckFinished(self):
		pass
		#self._prg_checking.setHidden(True)
	
	def setLatestVersion(self, release_info:ReleaseInfo):

		if release_info.version != QtWidgets.QApplication.instance().applicationVersion():
			self._lbl_version_latest.setText(release_info.version)

			self._lbl_release_name.setText(release_info.name)
			self._lbl_release_date.setText("Released " + QtCore.QDateTime.fromString(release_info.date, QtCore.Qt.DateFormat.ISODate).toLocalTime().toString("dd MMMM yyyy"))
			self._btn_download.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl(release_info.release_url)))
			self._txt_release_notes.setMarkdown(release_info.release_notes)
			self._grp_release_info.setHidden(False)

			self._stack_status.setCurrentWidget(self._grp_new_version)
		
		else:
			self._stack_status.setCurrentWidget(self._grp_no_update)
			self._lbl_release_name.setText("You are on the latest version")
	
	@QtCore.Slot(QtNetwork.QNetworkReply)
	def processNetworkReply(self, reply:QtNetwork.QNetworkReply):
		response = QtCore.QJsonDocument.fromJson(reply.readAll())
		latest_release:dict = response.array().first().toObject()

		release_info = ReleaseInfo(
			name = latest_release.get("name"),
			version = latest_release.get("tag_name")[1:], # Strip 'v'
			release_notes = latest_release.get("body"),
			release_url = latest_release.get("html_url"),
			date = latest_release.get("published_at")
		)

		self.setLatestVersion(release_info)

	def checkForUpdates(self, api_url:str=URL_RELEASES):
		self.netman = QtNetwork.QNetworkAccessManager()

		self.netman.finished.connect(self.networkCheckFinished)
		self.netman.finished.connect(self.processNetworkReply)

		self.networkCheckStart()

		self.netman.get(QtNetwork.QNetworkRequest(QtCore.QUrl(api_url)))