from PySide6 import QtWidgets
from lilbinboy.lbb_features.trt.panel_runtime import LBBRuntimeMetrics

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd = LBBRuntimeMetrics()
wnd.show()

app.exec()