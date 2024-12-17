from PySide6 import QtCore, QtGui, QtWidgets
from lilbinboy.lbb_common import LBAboutWindow

QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_EnableHighDpiScaling)
QtCore.QCoreApplication.setAttribute(QtCore.Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd = LBAboutWindow()
wnd.show()

app.exec()