import sys
from PySide6 import QtCore, QtGui, QtWidgets
from lilbinboy.settingseditor import panel_binloading, panel_startup, panel_ui

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd_settings = QtWidgets.QWidget()
wnd_settings.setWindowFlag(QtCore.Qt.WindowType.Tool)
wnd_settings.setWindowTitle("Settings")

tabs_settings = QtWidgets.QTabWidget()

tabs_settings.setUsesScrollButtons(False)

pnl_binloading = panel_binloading.BSSettingsBinLoading()
pnl_startup    = panel_startup.BSSettingsStartup()
pnl_ui         = panel_ui.BSSettingsUserInterface()

tabs_settings.addTab(pnl_startup, "Startup")
tabs_settings.addTab(pnl_binloading,"Bin Loading")
tabs_settings.addTab(pnl_ui, "User Interface")

tabs_settings.setTabIcon(0, QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.CallStart))
tabs_settings.setTabIcon(1, QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ImageLoading))
tabs_settings.setTabIcon(2, QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.WindowNew))

wnd_settings.setLayout(QtWidgets.QVBoxLayout())
wnd_settings.layout().addWidget(tabs_settings)

wnd_settings.show()

sys.exit(app.exec())