from PySide6 import QtWidgets, QtCore, QtGui
from . import lbb_common, lbb_features, Config
#from .lbb_common import resources
import pathlib

def main():
	app = QtWidgets.QApplication()

	app.setStyle(Config.APP_STYLE)
	# TODO: macOS Translucent background
	#surface_format = QtGui.QSurfaceFormat()
	#surface_format.setAlphaBufferSize(8)
	#QtGui.QSurfaceFormat.setDefaultFormat(surface_format)
	#wnd_main.setAttribute(QtCore.Qt.WA_TranslucentBackground)

	app.setOrganizationName(Config.ORG_NAME)
	app.setOrganizationDomain(Config.ORG_DOMAIN)
	app.setApplicationName(Config.APP_NAME)
	app.setWindowIcon(QtGui.QPixmap(":/app/icons/icon_256.png"))
	app_settings = QtCore.QSettings()

	# Setup main window
	wnd_main = lbb_common.LBMainWindow()
	wnd_main.setWindowTitle(app.applicationName())
	wnd_main.setGeometry(app_settings.value("main/window_geometry", QtCore.QRect()))
	wnd_main.sig_resized.connect(lambda rect: app_settings.setValue("main/window_geometry", rect))

	wnd_main.show()

	# Setup main window
	wnd_main.menuBar().addMenu("&File")
	wnd_main.menuBar().addMenu("&Edit")
	wnd_main.menuBar().addMenu("&Tools")

	mnu_help = QtWidgets.QMenu("&Help")
	act_aboutbox = QtGui.QAction("About Lil' Bin Boy...")
	act_aboutbox.setMenuRole(QtGui.QAction.MenuRole.AboutRole)
	act_aboutbox.triggered.connect(lambda: lbb_common.LBAboutWindow(wnd_main).exec())
	mnu_help.addAction(act_aboutbox)
	
	wnd_main.menuBar().addMenu(mnu_help)

	# Add feature tabs
	for name, panel in lbb_features.features.items():
		wnd_main.tabs.addTab(panel(), str(name))
		wnd_main.tabs.setTabIcon(wnd_main.tabs.count()-1, QtGui.QIcon(panel.PATH_ICON))

	# Coming soon...
	wnd_main.tabs.addTab(QtWidgets.QWidget(), str("Binlocker"))
	wnd_main.tabs.addTab(QtWidgets.QWidget(), str("Continuity Maker"))
	wnd_main.tabs.addTab(QtWidgets.QWidget(), str("Bin Config"))

	app.exec()

if __name__ == "__main__":
	import multiprocessing
	multiprocessing.freeze_support()
	main()