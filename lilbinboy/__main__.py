from PySide6 import QtWidgets
from . import lbb_common, lbb_features, APP_NAME


app = QtWidgets.QApplication()

app.setApplicationDisplayName(APP_NAME)
app.setApplicationName(APP_NAME)
app.setStyle("Fusion")

wnd_main = lbb_common.LBMainWindow()
wnd_main.show()

for name, panel in lbb_features.features.items():
	wnd_main.centralWidget().addTab(panel(), str(name))

app.exec()