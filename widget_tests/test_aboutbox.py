from PySide6 import QtCore, QtGui, QtWidgets
from lilbinboy.lbb_common.wnd_about import LBAboutWindow

app = QtWidgets.QApplication()
app.setApplicationVersion("0.0.1a-pre-alpha-nightmare")
app.setStyle("Fusion")

wnd = LBAboutWindow()
wnd.show()

app.exec()