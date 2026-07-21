import sys
from PySide6 import QtCore, QtWidgets, QtNetwork
from lilbinboy.softwareupdates import updatesmanager, updatesviewer, releaseinfo

class Swapper(QtWidgets.QWidget):

	sig_show_loading   = QtCore.Signal()
	sig_show_error     = QtCore.Signal(object)
	sig_show_no_update = QtCore.Signal()
	sig_show_update    = QtCore.Signal(object)

	def __init__(self):

		super().__init__()

		self.setLayout(QtWidgets.QHBoxLayout())

		self._test_release = releaseinfo.ReleaseInfo(
			name = "v1.0.1 - Test Release",
			release_notes = "This is a test release.",
			date=QtCore.QDateTime.currentDateTime(),
			version = QtCore.QVersionNumber(1,1,0),
			release_url = QtCore.QUrl("https://glowingpixel.com/")
		)

		self._test_error = QtNetwork.QNetworkReply.NetworkError.ConnectionRefusedError
		
		self._btn_show_loading = QtWidgets.QPushButton(text="Loading")
		self._btn_show_loading.clicked.connect(self.sig_show_loading)

		self._btn_show_error = QtWidgets.QPushButton(text="Network Error")
		self._btn_show_error.clicked.connect(lambda: self.sig_show_error.emit(self._test_error))

		self._btn_show_no_update = QtWidgets.QPushButton(text="No Update")
		self._btn_show_no_update.clicked.connect(self.sig_show_no_update)

		self._btn_show_update    = QtWidgets.QPushButton(text="Has Update")
		self._btn_show_update.clicked.connect(lambda: self.sig_show_update.emit(self._test_release))


		self.layout().addWidget(self._btn_show_loading)
		self.layout().addWidget(self._btn_show_error)
		self.layout().addWidget(self._btn_show_no_update)
		self.layout().addWidget(self._btn_show_update)

app = QtWidgets.QApplication()
app.setStyle("Fusion")

swapper = Swapper()
swapper.show()

updates_manager = updatesmanager.BSUpdatesManager(
	parent=app,
	url_releases=QtCore.QUrl("https://api.github.com/repos/mjiggidy/lilbinboy/releases"),
	autocheck_enabled=False,
	current_version=QtCore.QVersionNumber(0,0,26)
)
updates_window = updatesviewer.BSUpdatesWindow(updates_manager=updates_manager)

swapper.sig_show_loading.connect(updates_window.networkCheckStart)
swapper.sig_show_no_update.connect(updates_window.releaseIsCurrent)
swapper.sig_show_update.connect(updates_window.newReleaseAvailable)
swapper.sig_show_error.connect(updates_window.networkCheckError)

updates_window.show()

sys.exit(app.exec())