"""
Main app controller
"""
import logging, typing
import qtlogrelay
from   PySide6 import QtCore, QtGui, QtWidgets
from   os import PathLike

from ..storage import storagemodel

from ..binviewprovider import binviewsources

from . import settings, config
from ..managers import windows, software_updates
from ..widgets  import mainwindow, settingswindow
from ..logs   import logmodels, logwidget
from ..res      import translations
from ..binview  import binviewitemtypes
from ..storage import storagemodel

BIN_VIEW_PATH = "binviews"

class BSMainApplication(QtWidgets.QApplication):
	"""Main application"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setApplicationName(config.BSApplicationConfig.APPLICATION_NAME)
		self.setApplicationVersion(config.BSApplicationConfig.APPLICATION_VERSION.toString())

		self.setOrganizationName(config.BSApplicationConfig.ORGANIZATION_NAME)
		self.setOrganizationDomain(config.BSApplicationConfig.ORGANIZATION_DOMAIN)
		
		self.setDesktopFileName(self.organizationDomain() + "." + self.applicationName())
		self.setStyle(config.BSApplicationConfig.UI_THEME)

		self._path_local_storage   = self._getLocalStorage(
			QtCore.QStandardPaths.writableLocation(config.BSApplicationConfig.APPLICATION_STORAGE_PATH)
		)
		
		self._man_settings = settings.BSSettingsManager(
			format   = QtCore.QSettings.Format.IniFormat,
			basepath = self._path_local_storage
		)

		self._man_binwindows       = windows.BSWindowManager()
		self._man_software_updates = software_updates.BSUpdatesManager()

		self._qt_log_handler       = qtlogrelay.QtLogRelayHandler()
		self._qt_log_model         = logmodels.BSLogDataModel()
		self._setupLogging()

		self._disable_updates_counter = 0
		
		self._wnd_log_viewer       = None
		self._wnd_settings         = None
		self._wnd_software_updates = None
		
		self._setupLocalization()

		#self._setupApplicationMenu()

#		self._man_binview_storage = providerstorage.BSBinViewStorageManager(base_path=self._path_local_storage)
#		self._man_binview_storage.setRefreshInterval(providerstorage.DEFAULT_REFRESH_RATE_MSEC)

		self._setupSignals()

		# Restore user settings for session
		self._man_software_updates.setAutoCheckEnabled(self._man_settings.softwareUpdateAutocheckEnabled())

		self._bin_view_storage_model = storagemodel.BSFileSystemModel(parent=self)

		self._setupBinViewStorage()

		if self._man_settings.showFirstRunMessage():

			self._man_settings.setShowFirstRunMessage(False)

			dev_message = QtWidgets.QMessageBox()
			dev_message.setOption(QtWidgets.QMessageBox.Option.DontUseNativeDialog)
			dev_message.setWindowTitle(self.tr("Bless This Mess"))
			dev_message.setIcon(QtWidgets.QMessageBox.Icon.Information)
			dev_message.setTextFormat(QtCore.Qt.TextFormat.RichText)
			dev_message.setText("Welcome to Binspector: The Pre-Alpha Nightmare!")

			dev_message.setInformativeText(
			"""
				<p>Binspector is still under heavy development and is feature-incomplete.  There will be things that don't work so great.  
				Most things, in fact.  Kinda <em>everything</em> is a mess right now, really.  Just so you know what's goin' on.
				</p>
				<p>
				Although Binspector is a read-only program and will never modify your Avid bin files, use this development build at your own risk.
				</p>
				<p>
				If you encounter any bugs that you'd really like me to prioritize, please report them to <strong><code>michael@glowingpixel.com</code></strong>.
				</p>
				<hr/>
				<p>Please consider supporting development on Ko-Fi:<br/><strong><code>https://ko-fi.com/lilbinboy</code></strong></p>
				"""
			)
			dev_message.exec()

		
	def _setupSignals(self):

		self._man_binwindows.windowGeometryWatcher().sig_window_geometry_changed.connect(self._man_settings.setLastWindowGeometry)

		self._man_software_updates.sig_newReleaseAvailable.connect(self.showUpdatesWindow)
		self._man_software_updates.sig_autoCheckChanged.connect(self._man_settings.setSoftwareUpdateAutocheckEnabled)

	def _setupApplicationMenu(self):
		"""Setup global menu"""

		raise DeprecationWarning("I don't think we doin this")
		# Setup default menu bar/actions (for macOS when no bin windows are open)
		# NOTE: This is currently clumsy and weird.  I'll uh, come back to this

		self.setQuitOnLastWindowClosed(False)

		from ..managers import actions
		from ..widgets import menus

		self._actionmanager   = actions.ActionsManager()
		self._default_menubar = menus.DefaultMenuBar(self._actionmanager)

		self._actionmanager.newWindowAction().triggered.connect(self.createMainWindow)
		self._actionmanager.fileBrowserAction().triggered.connect(lambda: self.createMainWindow(show_file_browser=True))
		self._actionmanager.showSettingsWindow().triggered.connect(self.showSettingsWindow)
		self._actionmanager.quitApplicationAction().triggered.connect(self.exit)

	def _setupBinViewStorage(self):


		path_binviews = QtCore.QDir(self._path_local_storage).filePath(BIN_VIEW_PATH)
		logging.getLogger(__name__).debug("Setting up binview storage provider at %s", QtCore.QDir.toNativeSeparators(path_binviews))

		if not QtCore.QFileInfo(path_binviews).isDir():

			logging.getLogger(__name__).debug("Creating non-existing dir: %s", QtCore.QDir.toNativeSeparators(path_binviews))
			
			if not QtCore.QDir().mkdir(path_binviews):
				logging.getLogger(__name__).error("Could not create directory for binview storage at %s: ", path_binviews)

		self._bin_view_storage_model.setFilter(
			QtCore.QDir.Filter.Files | \
			QtCore.QDir.Filter.NoDotAndDotDot
		)

		self._bin_view_storage_model.setNameFilters(
			["*.json"]
		)

		self._bin_view_storage_model.setNameFilterDisables(False)
		
		self._bin_view_storage_model.setRootPath(
			QtCore.QDir(self._path_local_storage).filePath(BIN_VIEW_PATH)
		)


	def _getLocalStorage(self, local_path:PathLike|None=None):
		"""Setup local storage for user data"""

		local_storage = QtCore.QDir(
			local_path or 
			QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.AppDataLocation)
		)
		
#		self._path_local_storage = local_path or QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.AppDataLocation)
#		print("Got local_storage", local_storage)
		if not QtCore.QDir().mkpath(local_storage.path()):
			raise OSError(
				self.tr("Cannot set up local storage path at {local_storage_path}").format(local_storage_path=local_storage)
			)
		
		# NOTE: Logging not set up at this point lol but hey man you know
		logging.getLogger(__name__).debug("Set up local storage at location %s", local_storage)

		return local_storage
		
	def _setupLogging(self, subdir_name:str="logs"):
		"""Setup logging config and handlers"""
		
		#logging.basicConfig(level=logging.DEBUG)
		
		logging.basicConfig(level=logging.ERROR)
		logging.getLogger("binspector.binfilters").setLevel(logging.DEBUG)
		logging.getLogger("binspector.siftwidget").setLevel(logging.DEBUG)

		base_dir = QtCore.QDir(QtCore.QDir(self._path_local_storage).filePath(subdir_name))

		if not QtCore.QDir().mkpath(base_dir.path()):
			raise OSError(
				self.tr("Cannot set up log storage path at {local_storage_path}").format(local_storage_path=base_dir)
			)

		file_formatter = logging.Formatter("\t".join([
			"%(levelname)s",
			"%(asctime)s",
			"%(name)s",
			"%(message)s"
		]))

		# File handler
		from logging import handlers
		file_handler = handlers.RotatingFileHandler(
			filename    = base_dir.filePath(config.BSApplicationConfig.LOG_FILE_NAME),
			maxBytes    = 1_000_000,
			backupCount = 5,
		)
		file_handler.setFormatter(file_formatter)
		file_handler.setLevel(logging.NOTSET)
		logging.getLogger().addHandler(file_handler)

		# QtLog Handler
		self._qt_log_handler.logEventReceived.connect(self._qt_log_model.addLogRecord, QtCore.Qt.ConnectionType.QueuedConnection)
		logging.getLogger().addHandler(self._qt_log_handler)

		logging.getLogger(__name__).debug("Well hello.  I've missed you.")

#	def _setupSettingsManager(self):
#		"""Get all set up with the user settings"""
#		
#		self._man_settings = settings.BSSettingsManager(
#			format   = QtCore.QSettings.Format.IniFormat,
#			basepath = self._path_local_storage
#		)

	def _setupLocalization(self):
		"""Install localizations if available"""
		
		translator_userlang = QtCore.QTranslator()

		if translator_userlang.load(QtCore.QLocale(), "bs", ".", ":/translations"):
			self.installTranslator(translator_userlang)
			logging.getLogger(__name__).debug("Installed translation for user lang %s", QtCore.QLocale().name())

		else:
			logging.getLogger(__name__).debug("Falling back to default translation for user lang %s", QtCore.QLocale().name())	

	def localStoragePath(self) -> PathLike[str]:
		"""Get the local user storage path"""

		return self._path_local_storage.path()
	
	def showLocalStorage(self):
		"""Open local user storage folder"""

		QtGui.QDesktopServices.openUrl(
			QtCore.QUrl.fromLocalFile(self._path_local_storage.path())
		)
	
	def settingsManager(self) -> settings.BSSettingsManager:
		return self._man_settings
	
	def updatesManager(self) -> software_updates.BSUpdatesManager:
		return self._man_software_updates
	
	@QtCore.Slot()
	@QtCore.Slot(bool)
	def createMainWindow(self, is_first_window:bool=False) -> mainwindow.BSMainWindow:
		"""Create a main window"""

		# At launch: No last window, but position stored in settings?  Recall saved position.
		if not self._man_binwindows.lastActiveBinWindow() and self._man_settings.lastWindowGeometry():
			start_geo = self._man_settings.lastWindowGeometry()
		
		# Otherwise get next geo from window manager
		else:
			start_geo = self._man_binwindows.nextWindowGeometry(relative_to=self._man_binwindows.lastActiveBinWindow())
		
		window:mainwindow.BSMainWindow = self._man_binwindows.addWindow(mainwindow.BSMainWindow())

		window.setGeometry(start_geo)

		#window.setActionsManager(actions.ActionsManager(window))
		#window.setSettings(self._settingsManager.settings("bs_main"))
		
		# Connect signals/slots
		# TODO: Probably connect this directly to managers, like binViewManager below
		# The window shouldn't have to care much about emitting all these signals, I don't think
		window.sig_request_new_window        .connect(self.createMainWindow)
		window.sig_request_quit_application  .connect(self.closeProgram)
		window.sig_request_show_settings     .connect(self.showSettingsWindow)
		window.sig_request_show_log_viewer   .connect(self.showLogWindow)
		window.sig_request_show_user_folder  .connect(self.showLocalStorage)
		window.sig_request_visit_discussions .connect(lambda: QtGui.QDesktopServices.openUrl("https://github.com/mjiggidy/binspector/discussions/"))
		window.sig_request_visit_donations   .connect(lambda: QtGui.QDesktopServices.openUrl("https://ko-fi.com/lilbinboy/"))
		window.sig_request_check_updates     .connect(self.showUpdatesWindow)
		window.sig_bin_changed               .connect(self._man_settings.setLastBinPath)
#		window.sig_request_export_bin_view   .connect(self.exportBinView)
#		window.sig_request_delete_bin_view   .connect(self.deleteBinView)

		# Restore Toggle Settings
		window.binContentsWidget().setBinColumnFiltersDisabled(self._man_settings.allColumnsVisible())
		window.binContentsWidget().sig_bin_view_enabled.connect(lambda enabled: self._man_settings.setAllColumnsVisible(not enabled))
		
		window.binViewManager().setAllItemsVisible(self._man_settings.allItemsVisible())
		window.binViewManager().sig_all_items_toggled.connect(self._man_settings.setAllItemsVisible)

		window.appearanceManager().setUseSystemAppearance(self._man_settings.useSystemAppearance())
		window.appearanceManager().sig_use_system_appearance_toggled.connect(self._man_settings.setUseSystemAppearance)
		#window.appearanceManager().sig_bin_appearance_toggled.connect(self._man_settings.setUseSystemAppearance)

		window.binContentsWidget().frameView()._overlay_ruler._setEnabled(self._man_settings.showFrameRuler())
		window.binContentsWidget().frameView()._overlay_ruler.sig_enabled_changed.connect(self._man_settings.setShowFrameRuler)

		window.binContentsWidget().frameView()._overlay_map._setEnabled(self._man_settings.showFrameMap())
		window.binContentsWidget().frameView()._overlay_map.sig_enabled_changed.connect(self._man_settings.setShowFrameMap)

		window.binContentsWidget().frameView()._background_painter.setEnabled(self._man_settings.showFrameGrid())
		window.binContentsWidget().frameView()._background_painter.sig_enabled_changed.connect(self._man_settings.setShowFrameGrid)

		window.setMobQueueSize(self._man_settings.mobQueueSize())
		window.setUseAnimation(self._man_settings.useFancyProgressBar())
		window.setUseSavedColumnWidths(self._man_settings.useSavedColumnWidths())
		
		window.binContentsWidget().setBottomScrollbarScaleFactor(self._man_settings.bottomScrollbarScale())
		window.binContentsWidget().setItemPadding(self._man_settings.listItemPadding())

		window.binLoadingSignalManger().sig_begin_loading.connect(self.setUpdateCheckDisabled)
		window.binLoadingSignalManger().sig_done_loading.connect(self.setUpdateCheckEnabled)

		window.binViewProviderModel().setStorageModel(self._bin_view_storage_model)

#		window.binContentsWidget().siftFilter().setLiveSiftEnabled(self._man_settings.useLiveSift())
#		window.binContentsWidget().siftFilter().sig_live_sift_enabled.connect(self._man_settings.setUseLiveSift)

		window.setUseSiftCriteriaFromBin(self._man_settings.useSiftCriteria())

#		window.binViewProviderModel().addStoredBinViewSources(self._man_binview_storage.lastBinViews())
#		self._man_binview_storage.sig_binviews_added.connect(window.binViewProviderModel().addStoredBinViewSources)
#		self._man_binview_storage.sig_binviews_removed.connect(window.binViewProviderModel().removeBinViewSources)


		logging.getLogger(__name__).debug("Created %s", window.winId())
		
		window.show()
		window.raise_()
		window.activateWindow()

		# Startup behavior
		startup_behavior = self._man_settings.startupBehavior()

		if is_first_window:

			if startup_behavior == settings.BSStartupBehavior.LAST_BIN:

				if QtCore.QFileInfo(self._man_settings.lastBinPath() or "").isFile():

					logging.getLogger(__name__).debug("Opening last bin at startup: %s", self._man_settings.lastBinPath())
					window.loadBinFromPath(self._man_settings.lastBinPath())
				
				else:
					logging.getLogger(__name__).error("Not opening last bin because it doesn't exist: %s", self._man_settings.lastBinPath())

			elif startup_behavior == settings.BSStartupBehavior.SHOW_BROWSER:

				logging.getLogger(__name__).debug("Showing file browser at startup")
				window.showFileBrowser(
					self._man_settings.lastBinPath() or QtCore.QDir.homePath()
				)

		return window
	
#	@QtCore.Slot(object)
#	def exportBinView(self, binview_info:binviewitemtypes.BSBinViewInfo):
#
#		try:
#			print("Would totally export here")
#			#output_path = self._man_binview_storage.writeStoredBinView(binview_info)
#		
#		except Exception as e:
#
#			logging.getLogger(__name__).error("Error exporting binview %s: %s", binview_info.name, str(e))
#
#			wnd_err = QtWidgets.QMessageBox()
#			wnd_err.setWindowTitle("Error exporting bin view")
#			wnd_err.setText("Could not export this bin view")
#			wnd_err.setInformativeText(f"{e}<br/><hr/>Please report any unexpected errors to <a href=\"michael@glowingpixel.com\">michael@glowingpixel.com</a>")
#			wnd_err.setIcon(QtWidgets.QMessageBox.Icon.Warning)
#			wnd_err.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
#			wnd_err.exec()
#
#		else:
#			logging.getLogger(__name__).info("Bin view \"%s\" was saved to %s", binview_info.name, output_path)

#	@QtCore.Slot(object)
#	def deleteBinView(self, binview_source:binviewsources.BSBinViewSourceFile):
#
#		try:
#			print("Would totally delete here")
#			#self._man_binview_storage.deleteStoredBinView(binview_source)
#		
#		except Exception as e:
#
#			logging.getLogger(__name__).error("Error deleting binview %s: %s", binview_source.name(), str(e))
#
#			wnd_err = QtWidgets.QMessageBox()
#			wnd_err.setWindowTitle("Error deleting bin view")
#			wnd_err.setText("Could not delete the bin view from storage")
#			wnd_err.setInformativeText(f"{e}<br/><hr/>Please report any unexpected errors to <a href=\"michael@glowingpixel.com\">michael@glowingpixel.com</a>")
#			wnd_err.setIcon(QtWidgets.QMessageBox.Icon.Warning)
#			wnd_err.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
#			wnd_err.exec()
#
#		else:
#			logging.getLogger(__name__).info("Bin view \"%s\" was deleted from %s", binview_source.name(), binview_source.path())
	
	@QtCore.Slot()
	@QtCore.Slot(bool)
	def setUpdateCheckEnabled(self, is_enabled:bool=True):

		self._man_software_updates.setEnabled(bool(is_enabled))

		self._disable_updates_counter = max(self._disable_updates_counter + (-1 if is_enabled else 1), 0)

		logging.getLogger(__name__).debug("_disable_updates_counter = %s", self._disable_updates_counter)

		if self._disable_updates_counter:
			self._man_software_updates.setDisabled()
		else:
			self._man_software_updates.setEnabled()

	
	@QtCore.Slot()
	@QtCore.Slot(bool)
	def setUpdateCheckDisabled(self, is_disabled:bool=True):

		self.setUpdateCheckEnabled(not bool(is_disabled))
	
	@QtCore.Slot()
	def showLogWindow(self):

		if not self._wnd_log_viewer:

			self._wnd_log_viewer = logwidget.BSLogViewerWidget()
			self._wnd_log_viewer.setWindowTitle("Log Viewer")
			self._wnd_log_viewer.setWindowFlag(QtCore.Qt.WindowType.Tool)

			start_geo = self.activeWindow().geometry().translated(QtCore.QPoint(100,100)) if self.activeWindow() else self._wnd_log_viewer.geometry()
			start_geo.setSize(QtCore.QSize(900,200))
			self._wnd_log_viewer.setGeometry(start_geo)
			
			self._wnd_log_viewer.setAttribute(QtCore.Qt.WA_DeleteOnClose)
			self._wnd_log_viewer.destroyed.connect(lambda: setattr(self, "_wnd_log_viewer", None))
			
			self._wnd_log_viewer.treeView().setModel(self._qt_log_model)

		if self._wnd_log_viewer.isMinimized():
			self._wnd_log_viewer.showNormal()
		else:
			self._wnd_log_viewer.show()

		self._wnd_log_viewer.raise_()
		self._wnd_log_viewer.activateWindow()

	
	@QtCore.Slot()
	def showUpdatesWindow(self):

		from ..widgets import software_updates
		
		# Create window if it's not already open
		if not self._wnd_software_updates:

			self._wnd_software_updates = software_updates.BSCheckForUpdatesWindow()
			
			self._wnd_software_updates.setWindowFlag(QtCore.Qt.WindowType.Tool)
			self._wnd_software_updates.setUpdateManager(self.updatesManager())
			self._wnd_software_updates.setAttribute(QtCore.Qt.WA_DeleteOnClose)
			
			# Release dat ref
			self._wnd_software_updates.destroyed.connect(lambda: setattr(self, "_wnd_software_updates", None))

		# Check for updates at window launch if an update hasn't already been found
		if self._man_software_updates.latestReleaseInfo() is None:
			self._man_software_updates.checkForUpdates()
		else:
			logging.getLogger(__name__).debug("Latest release info = %s", self._man_software_updates.latestReleaseInfo())

		if self._wnd_software_updates.isMinimized():
			self._wnd_software_updates.showNormal()
		else:
			self._wnd_software_updates.show()

		self._wnd_software_updates.raise_()
		self._wnd_software_updates.activateWindow()

	@QtCore.Slot()
	def showSettingsWindow(self):

		if not self._wnd_settings:
			
			self._wnd_settings = settingswindow.BSSettingsPanel()

			self._wnd_settings.setWindowTitle(f"{self.applicationDisplayName()} Settings")
			self._wnd_settings.setWindowFlag(QtCore.Qt.WindowType.Tool)
			self._wnd_settings.setAttribute(QtCore.Qt.WA_DeleteOnClose)
			
			self._wnd_settings.destroyed.connect(lambda: setattr(self, "_wnd_settings", None))

			self._wnd_settings.sig_use_animations_changed.connect(self._man_settings.setUseFancyProgressBar)
			self._wnd_settings.sig_use_animations_changed.connect(lambda use_animation: [w.setUseAnimation(use_animation) for w in self._man_binwindows.windows()])

			self._wnd_settings.sig_use_column_widths_changed.connect(self._man_settings.setUseSavedColumnWidths)
			self._wnd_settings.sig_use_column_widths_changed.connect(lambda use_col_widths: [w.setUseSavedColumnWidths(use_col_widths) for w in self._man_binwindows.windows()])

#			self._wnd_settings.sig_use_live_sift_changed.connect(self._man_settings.setUseLiveSift)
			
			self._wnd_settings.sig_use_sift_settings_changed.connect(self._man_settings.setUseSiftCriteria)
			self._wnd_settings.sig_use_sift_settings_changed.connect(lambda use_sift: [w.setUseSiftCriteriaFromBin(use_sift) for w in self._man_binwindows.windows()])

			self._wnd_settings.sig_mob_queue_size_changed.connect(self._man_settings.setMobQueueSize)
			self._wnd_settings.sig_startup_behavior_changed.connect(self._man_settings.setStartupBehavior)
			self._wnd_settings.sig_mob_queue_size_changed.connect(lambda queue_size: [w.setMobQueueSize(queue_size) for w in self._man_binwindows.windows()])
			self._wnd_settings.sig_item_padding_changed.connect(lambda padding: [w.binContentsWidget().setItemPadding(padding) for w in self._man_binwindows.windows()])
			self._wnd_settings.sig_item_padding_changed.connect(self._man_settings.setListItemPadding)
			
			# TODO: Hacky
			self._wnd_settings.sig_scrollbar_scale_changed.connect(lambda s: [w.binContentsWidget().setBottomScrollbarScaleFactor(s) for w in self._man_binwindows.windows()])
			self._wnd_settings.sig_scrollbar_scale_changed.connect(self._man_settings.setBottomScrollbarScale)

			# Settings Temp
			self._wnd_settings.setUseAnimations(self._man_settings.useFancyProgressBar())
			self._wnd_settings.setUseSavedColumnWidths(self._man_settings.useSavedColumnWidths())
			self._wnd_settings.setBottomScrollBarScale(self._man_settings.bottomScrollbarScale())
			self._wnd_settings.setMobQueueSize(self._man_settings.mobQueueSize())
			self._wnd_settings.setStartupBehavior(self._man_settings.startupBehavior())
			self._wnd_settings.setListItemPadding(self._man_settings.listItemPadding())
			self._wnd_settings.setLiveSiftEnabled(self._man_settings.useLiveSift())
			self._wnd_settings.setUseSiftSettingsFromBin(self._man_settings.useSiftCriteria())

		if self._wnd_settings.isMinimized():
			self._wnd_settings.showNormal()
		else:
			self._wnd_settings.show()
			
		self._wnd_settings.raise_()
		self._wnd_settings.activateWindow()
	
	@QtCore.Slot()
	def closeProgram(self):
		"""Binspect no more"""

		self.closeAllWindows()

		#logging.getLogger(__name__).debug("Thank you for everything.  I love you.")