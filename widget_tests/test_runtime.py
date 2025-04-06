from PySide6 import QtWidgets
from lilbinboy.lbb_features.trt.panel_runtime import LBBRuntimeMetricsPanel

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd = LBBRuntimeMetricsPanel()
wnd.show()

app.exec()