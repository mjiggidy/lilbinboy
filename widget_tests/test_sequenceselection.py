from PySide6 import QtWidgets
from lilbinboy.lbb_features.trt import dlg_sequence_selection

app = QtWidgets.QApplication()
app.setStyle("Fusion")
wnd = dlg_sequence_selection.TRTSequenceSelection()
wnd.show()

app.exec()