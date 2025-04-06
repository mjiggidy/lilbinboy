from PySide6 import QtWidgets
from lilbinboy.lbb_features.trt.panel_runtime import LBBRuntimeMetrics

app = QtWidgets.QApplication()

wnd = LBBRuntimeMetrics()
wnd.show()

app.exec()