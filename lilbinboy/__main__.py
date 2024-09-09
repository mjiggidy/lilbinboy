from PySide6 import QtWidgets, QtCore, QtGui
from . import lbb_common, lbb_features, APP_NAME


app = QtWidgets.QApplication()

app.setStyle("Fusion")

app.setOrganizationName("GlowingPixel")
app.setOrganizationDomain("glowingpixel.com")
app.setApplicationName(APP_NAME)
app_settings = QtCore.QSettings()

surface_format = QtGui.QSurfaceFormat()
surface_format.setAlphaBufferSize(8)
QtGui.QSurfaceFormat.setDefaultFormat(surface_format)

wnd_main = lbb_common.LBMainWindow()
wnd_main.setGeometry(app_settings.value("main/window_geometry", QtCore.QRect()))
wnd_main.setAttribute(QtCore.Qt.WA_TranslucentBackground)

wnd_main.sig_resized.connect(lambda rect: app_settings.setValue("main/window_geometry", rect))

wnd_main.show()

for name, panel in lbb_features.features.items():
	wnd_main.centralWidget().addTab(panel(), str(name))
	print("For you I add", panel.PATH_ICON)
	wnd_main.centralWidget().setTabIcon(wnd_main.centralWidget().count()-1, QtGui.QIcon(panel.PATH_ICON))
	print(wnd_main.centralWidget().tabIcon(wnd_main.centralWidget().count()-1))

app.exec()