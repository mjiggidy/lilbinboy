from PySide6 import QtWidgets, QtGui, QtCore
import importlib.metadata
from lilbinboy import lbb_common, lbb_features

try:
	__version__ =importlib.metadata.version("lilbinboy")
except importlib.metadata.PackageNotFoundError:
	__version__ = "Mystery!"

class Config:
	APP_NAME   = "Lil' Bin Boy"
	APP_STYLE  = "Fusion"
	APP_VERSION = __version__
	ORG_NAME   = "GlowingPixel"
	ORG_DOMAIN = "glowingpixel.com"

def main():
	app = QtWidgets.QApplication()

	app.setStyle(Config.APP_STYLE)
	# TODO: macOS Translucent background
	#surface_format = QtGui.QSurfaceFormat()
	#surface_format.setAlphaBufferSize(8)
	#QtGui.QSurfaceFormat.setDefaultFormat(surface_format)
	#wnd_main.setAttribute(QtCore.Qt.WA_TranslucentBackground)

	main_icon = QtGui.QIcon()
	main_icon.addFile(":/app/icons/icon_16.png", QtCore.QSize(16,16))
	main_icon.addFile(":/app/icons/icon_24.png", QtCore.QSize(24,24))
	main_icon.addFile(":/app/icons/icon_32.png", QtCore.QSize(32,32))
	main_icon.addFile(":/app/icons/icon_64.png", QtCore.QSize(64,64))
	main_icon.addFile(":/app/icons/icon_128.png", QtCore.QSize(128,128))
	main_icon.addFile(":/app/icons/icon_256.png", QtCore.QSize(256,256))

	app.setOrganizationName(Config.ORG_NAME)
	app.setOrganizationDomain(Config.ORG_DOMAIN)
	app.setApplicationName(Config.APP_NAME)
	app.setApplicationVersion(Config.APP_VERSION)
	app.setWindowIcon(main_icon)
	app_settings = QtCore.QSettings()

	# Setup main window
	wnd_main = lbb_common.wnd_main.LBMainWindow()
	wnd_main.setWindowTitle(app.applicationName())
	wnd_main.setGeometry(app_settings.value("main/window_geometry", QtCore.QRect()))
	wnd_main.sig_resized.connect(lambda rect: app_settings.setValue("main/window_geometry", rect))

	wnd_main.show()

	# Setup main window
	mnu_file = wnd_main.menuBar().addMenu("&File")

	act_quit = QtGui.QAction("Quit")
	act_quit.setMenuRole(QtGui.QAction.MenuRole.ApplicationSpecificRole)
	act_quit.triggered.connect(wnd_main.close)
	act_quit.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ApplicationExit))
	mnu_file.addAction(act_quit)

	wnd_main.menuBar().addMenu("&Edit")
	mnu_tools = wnd_main.menuBar().addMenu("&Tools")

	act_datalocation = QtGui.QAction("Open Data Storage Location...")
	act_datalocation.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.AppDataLocation))))
	act_datalocation.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FolderOpen))
	mnu_tools.addAction(act_datalocation)


	mnu_help = QtWidgets.QMenu("&Help")

	act_wiki = QtGui.QAction("Lil' Bin Boy Wiki...")
	act_wiki.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/mjiggidy/lilbinboy/wiki")))
	mnu_help.addAction(act_wiki)

	act_updates = QtGui.QAction("Check For Updates...")
	act_updates.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/mjiggidy/lilbinboy/releases")))
	mnu_help.addAction(act_updates)

	mnu_help.addSeparator()
	

	act_aboutbox = QtGui.QAction("About Lil' Bin Boy...")
	act_aboutbox.setMenuRole(QtGui.QAction.MenuRole.AboutRole)
	act_aboutbox.triggered.connect(lambda: lbb_common.wnd_about.LBAboutWindow(wnd_main).exec())
	act_aboutbox.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.HelpAbout))
	mnu_help.addAction(act_aboutbox)
	
	wnd_main.menuBar().addMenu(mnu_help)

	# Add feature tabs
	for name, panel in lbb_features.features.items():
		wnd_main.tabs.addTab(panel(), str(name))
		wnd_main.tabs.setTabIcon(wnd_main.tabs.count()-1, QtGui.QIcon(panel.PATH_ICON))

	# Coming soon...
	wnd_main.tabs.addTab(QtWidgets.QWidget(), str("Bin Snitch"))
	wnd_main.tabs.addTab(QtWidgets.QWidget(), str("Attic Scrounger"))
	wnd_main.tabs.addTab(QtWidgets.QWidget(), str("Batch Bin"))
	wnd_main.tabs.addTab(QtWidgets.QWidget(), str("Porta-Nexis"))

	app.exec()