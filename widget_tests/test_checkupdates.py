import dataclasses
from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork
from lilbinboy.lbb_common.wnd_checkforupdates import LBCheckForUpdatesWindow, LBUpdateManager

URL_RELEASES =  "https://api.github.com/repos/mjiggidy/lilbinboy/releases"




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