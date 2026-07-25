import sys
from PySide6 import QtCore, QtWidgets
from lilbinboy.settingseditor import settingswidget

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd_settings = settingswidget.BSSettingsPanel()
wnd_settings.show()

sys.exit(app.exec())