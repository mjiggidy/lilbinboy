from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork

URL_RELEASES = r"https://api.github.com/repos/mjiggidy/lilbinboy/releases"

class LBCheckForUpdatesWindow(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setWindowTitle("Check For Updates")
		self.setLayout(QtWidgets.QVBoxLayout())

		self._prg_checking = QtWidgets.QProgressBar()
		self._prg_checking.setRange(0,0)
		self._prg_checking.setHidden(True)

		self._lbl_version_latest = QtWidgets.QLabel("Checking...")
		
		self._lbl_release_name = QtWidgets.QLabel()
		
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
		lay_version.addWidget(QtWidgets.QLabel("Installed Version:"), 1, 0)
		lay_version.addWidget(QtWidgets.QLabel(QtWidgets.QApplication.instance().applicationVersion()), 1, 1)
		lay_version.addWidget(QtWidgets.QLabel("Latest Version:"), 2, 0)
		lay_version.addWidget(self._lbl_version_latest, 2, 1)
		lay_version.setColumnStretch(2,1)


		self.layout().addWidget(QtWidgets.QLabel("Lil' Bin Boy"))
		self.layout().addLayout(lay_version)

		self.layout().addWidget(self._prg_checking)
		self.layout().addStretch()

		self.layout().addWidget(self._lbl_release_name)
		self.layout().addWidget(self._lbl_version_url)
		self.layout().addWidget(self._txt_release_notes)
	
	@QtCore.Slot()
	def networkCheckStart(self):
		self._prg_checking.setHidden(False)
	
	def networkCheckFinished(self):
		self._prg_checking.setHidden(True)
	
	def setLatestVersion(self, name:str, version:str, release_notes:str, release_url:str):

		if version != QtWidgets.QApplication.instance().applicationVersion():
			self._lbl_release_name.setText(name)
			self._lbl_version_latest.setText(version)
			self._txt_release_notes.setMarkdown(release_notes)
			self._lbl_version_url.setText(f"<a href=\"{release_url}\">{release_url}</a>")
		
		else:
			self._lbl_release_name.setText("You are on the latest version")


@QtCore.Slot(QtNetwork.QNetworkReply)
def show_results(reply:QtNetwork.QNetworkReply):
	response = QtCore.QJsonDocument.fromJson(reply.readAll())
	latest_release:dict = response.array().first().toObject()

	release_name = latest_release.get("name")
	version = latest_release.get("tag_name")[1:] # Strip 'v'
	release_notes = latest_release.get("body")
	release_url = latest_release.get("html_url")
	#print(release_url)
	#print(release_notes)
	wnd_main.setLatestVersion(release_name, version, release_notes, release_url)

app = QtWidgets.QApplication()

wnd_main = LBCheckForUpdatesWindow()
wnd_main.show()

netman = QtNetwork.QNetworkAccessManager()
netman.finished.connect(show_results)
netman.finished.connect(wnd_main.networkCheckFinished)

wnd_main.networkCheckStart()
netman.get(QtNetwork.QNetworkRequest(QtCore.QUrl(URL_RELEASES)))

app.exec()