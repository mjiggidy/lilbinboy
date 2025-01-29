from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork

from lilbinboy.lbb_common.wnd_checkforupdates import LBCheckForUpdatesWindow

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd_main = LBCheckForUpdatesWindow()
wnd_main.show()

wnd_main.checkForUpdates()

app.exec()