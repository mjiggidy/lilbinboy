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

class LBBApplication(QtWidgets.QApplication):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setStyle(Config.APP_STYLE)


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

		self.setOrganizationName(Config.ORG_NAME)
		self.setOrganizationDomain(Config.ORG_DOMAIN)
		self.setApplicationName(Config.APP_NAME)
		self.setApplicationVersion(Config.APP_VERSION)
		self.setWindowIcon(main_icon)
		app_settings = QtCore.QSettings()

		# Setup main window
		self.wnd_main = lbb_common.wnd_main.LBMainWindow()
		self.wnd_main.setWindowTitle(self.applicationName())
		self.wnd_main.setGeometry(app_settings.value("main/window_geometry", QtCore.QRect()))
		#self.wnd_main.sig_resized.connect(lambda rect: app_settings.setValue("main/window_geometry", rect))

		self._windowmanager = lbb_common.windowmanager.WindowManager(self.wnd_main, app_settings, "main")

		self.wnd_main.show()

		# Setup main window
		self.mnu_file = self.wnd_main.menuBar().addMenu("&File")

		self.act_quit = QtGui.QAction("Quit")
		self.act_quit.setMenuRole(QtGui.QAction.MenuRole.ApplicationSpecificRole)
		self.act_quit.triggered.connect(self.wnd_main.close)
		self.act_quit.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ApplicationExit))
		self.mnu_file.addAction(self.act_quit)

		self.wnd_main.menuBar().addMenu("&Edit")
		self.mnu_tools = self.wnd_main.menuBar().addMenu("&Tools")

		self.act_datalocation = QtGui.QAction("Open Data Storage Location...")
		self.act_datalocation.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.AppDataLocation))))
		self.act_datalocation.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FolderOpen))
		self.mnu_tools.addAction(self.act_datalocation)


		self.mnu_help = QtWidgets.QMenu("&Help")

		self.act_wiki = QtGui.QAction("Lil' Bin Boy Wiki...")
		self.act_wiki.triggered.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl("https://github.com/mjiggidy/lilbinboy/wiki")))
		self.mnu_help.addAction(self.act_wiki)

		self.act_updates = QtGui.QAction("Check For Updates...")
		self.act_updates.setMenuRole(QtGui.QAction.MenuRole.ApplicationSpecificRole)
		self.act_updates.triggered.connect(self.showCheckForUpdatesWindow)
		self.mnu_help.addAction(self.act_updates)

		self.mnu_help.addSeparator()
		

		self.act_aboutbox = QtGui.QAction("About Lil' Bin Boy...")
		self.act_aboutbox.setMenuRole(QtGui.QAction.MenuRole.AboutRole)
		self.act_aboutbox.triggered.connect(lambda: lbb_common.wnd_about.LBAboutWindow(self.wnd_main).exec())
		self.act_aboutbox.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.HelpAbout))
		self.mnu_help.addAction(self.act_aboutbox)
		
		self.wnd_main.menuBar().addMenu(self.mnu_help)

		# Add feature tabs
		for name, panel in lbb_features.features.items():
			self.wnd_main.tabs.addTab(panel(), str(name))
			self.wnd_main.tabs.setTabIcon(self.wnd_main.tabs.count()-1, QtGui.QIcon(panel.PATH_ICON))

		# Check for Updates
		self.updateManager = lbb_common.wnd_checkforupdates.LBUpdateManager()
		self.updateManager.setReleasesUrl(QtCore.QUrl(app_settings.value("main/updates_manager/releases_url", lbb_common.wnd_checkforupdates.URL_RELEASES)))
		self.updateManager.setCooldownInterval(int(app_settings.value("main/updates_manager/cooldown_interval_msec", 30 * 1000)))
		self.updateManager.setAutoCheckInterval(int(app_settings.value("main/updates_manager/autocheck_interval_msec", 30 * 60 * 1000)))
		self.updateManager.setAutoCheckEnabled(bool(app_settings.value("main/updates_manager/autocheck_enabled", True)))
		self.updateManager.sig_autoCheckChanged.connect(lambda is_enabled: app_settings.setValue("main/updates_manager/autocheck_enabled", is_enabled))
		self.updateManager.sig_newReleaseAvailable.connect(self.showCheckForUpdatesWindow)
		self.wnd_check = None


		# Coming soon...
		self.wnd_main.tabs.addTab(QtWidgets.QWidget(), str("Bin Snitch"))
		self.wnd_main.tabs.addTab(QtWidgets.QWidget(), str("Attic Scrounger"))
		self.wnd_main.tabs.addTab(QtWidgets.QWidget(), str("Batch Bin"))
		self.wnd_main.tabs.addTab(QtWidgets.QWidget(), str("Porta-Nexis"))

	@QtCore.Slot()
	def showCheckForUpdatesWindow(self):
		"""Show the "Check For Updates" window"""

		if self.wnd_check is None:
			# Create new window if it wasn't visible
			self.wnd_check = lbb_common.wnd_checkforupdates.LBCheckForUpdatesWindow(parent=self.wnd_main)
			self.wnd_check.setUpdateManager(self.updateManager)

			# Unset instance once closed
			self.wnd_check.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose)
			self.wnd_check.destroyed.connect(lambda: setattr(self, "wnd_check", None))


		# Check for updates on window open, unless a new release is already known
		if self.updateManager.latestReleaseInfo() is None:
			self.updateManager.checkForUpdates()
			
		self.wnd_check.show()
		

def main():
	app = LBBApplication()



	app.exec()