from lilbinboy.lbb_features.trt.treeview_trt import TRTTreeView
from PySide6 import QtWidgets, QtGui, QtCore

app = QtWidgets.QApplication()
app.setStyle("Fusion")

treeview = TRTTreeView()
treeview.show()

app.exec()
