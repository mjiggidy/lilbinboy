import sys
from PySide6 import QtCore, QtGui, QtWidgets
from lilbinboy.settingseditor import panel_binloading, panel_startup, panel_ui

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd_settings = QtWidgets.QTabWidget()
wnd_settings.setWindowFlag(QtCore.Qt.WindowType.Dialog|QtCore.Qt.WindowType.Tool)

wnd_settings.setUsesScrollButtons(False)

pnl_binloading = panel_binloading.BSSettingsBinLoading()
pnl_startup    = panel_startup.BSSettingsStartup()
pnl_ui         = panel_ui.BSSettingsUserInterface()

wnd_settings.addTab(pnl_startup, "Startup")
wnd_settings.addTab(pnl_binloading,"Bin Loading")
wnd_settings.addTab(pnl_ui, "User Interface")

wnd_settings.setTabIcon(0, QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.CallStart))
wnd_settings.setTabIcon(1, QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ImageLoading))
wnd_settings.setTabIcon(2, QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.WindowNew))

wnd_settings.show()

sys.exit(app.exec())