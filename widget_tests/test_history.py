from PySide6 import QtWidgets
from lilbinboy.lbb_features.trt.wnd_history import TRTHistoryViewer

app = QtWidgets.QApplication()

wnd_history = TRTHistoryViewer()
wnd_history.show()

app.exec()