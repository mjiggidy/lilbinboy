from PySide6 import QtWidgets
from lilbinboy.lbb_features.trt import cnt_runtime, panel_runtime

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd = panel_runtime.LBBRuntimeMetricsPanel()

cnt = cnt_runtime.LBBRuntimeMetricsController(runtime_panel=wnd)

wnd.show()

app.exec()