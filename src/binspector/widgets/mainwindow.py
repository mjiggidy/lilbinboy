import logging, typing, dataclasses
from os import PathLike

from PySide6 import QtCore, QtGui, QtWidgets

from ..siftwidget import siftwidget

from ..binviewprovider import binviewsources, providermodel

from ..core import icon_registry, renaming

from ..binwidget import binwidget
from ..binitems import binitemsmodel, binitemtypes
from ..binview import binviewmodel, binviewitemtypes
from ..managers import actions, binproperties, appearance
from ..widgets import menus, toolboxes, buttons, about, overlaywidget
from ..core import binloader, icon_engines, icon_providers
from ..binvieweditor import editorwidget
from ..binfilters.siftfilter import sifters

DEFAULT_FIND_IN_BIN_REFRESH_INTERVAL_MSEC:int = 500

class BSMainWindow(QtWidgets.QMainWindow):
	"""Main window for BinSpectre 👻"""

	sig_request_new_window        = QtCore.Signal()
	sig_request_quit_application  = QtCore.Signal()
	sig_request_show_user_folder  = QtCore.Signal()
	sig_request_show_log_viewer   = QtCore.Signal()
	sig_request_show_settings     = QtCore.Signal()
	sig_request_check_updates     = QtCore.Signal()
	sig_request_visit_discussions = QtCore.Signal()
	sig_request_visit_donations   = QtCore.Signal()
	
	sig_request_export_bin_view   = QtCore.Signal(object)
	"""Export the bin view"""

	sig_request_delete_bin_view   = QtCore.Signal(object)
	"""Export the bin view"""

	sig_bin_changed               = QtCore.Signal(str)
	"""Window is loading a new bin"""

	def __init__(self):

		super().__init__()

		self._bin_item_model  = binitemsmodel.BSBinItemModel()
		self._bin_view_model   = binviewmodel.BSBinViewModel()

		self._settings         = QtCore.QSettings()
		self._man_actions      = actions.ActionsManager(self)	# NOTE: Investigate ownership

		# Define managers

		self._binview_provider = providermodel.BSBinViewProviderModel()

		self._find_in_bin_timer = QtCore.QTimer(parent=self, singleShot=True, interval=DEFAULT_FIND_IN_BIN_REFRESH_INTERVAL_MSEC)
		self._find_in_bin_timer.timeout.connect(lambda: self._bin_widget.setSearchText(self._bin_widget.topWidgetBar().searchBox().text()))
#		self._last_search_text = ""



		self._man_binview      = binproperties.BSBinViewManager()
#		self._man_siftsettings = binproperties.BSBinSiftSettingsManager()
		self._man_appearance   = appearance.BSBinAppearanceSettingsManager()
#		self._man_sorting      = binproperties.BSBinSortingPropertiesManager()
		self._man_bindisplay   = binproperties.BSBinDisplaySettingsManager()
#		self._man_viewmode     = binproperties.BSBinViewModeManager()

		# Define signals
		self._queue_size       = 500  # Mobs to batch-load
		self._use_animation    = True # Use animated progress bar
		self._use_sift         = True 
		self._sigs_binloader   = binloader.BSBinViewLoader.Signals()

		# Define animators
		self._anim_progress    = QtCore.QPropertyAnimation(parent=self)
		self._time_last_chunk  = QtCore.QElapsedTimer()
		self._time_last_load   = QtCore.QElapsedTimer()

		# Define widgets
		self._bin_widget       = binwidget.BSBinContentsWidget(bin_items_model=self._bin_item_model, bin_view_model=self._bin_view_model)

		self._tool_bindisplay  = toolboxes.BSBinDisplaySettingsView(icon_registry=icon_registry.BIN_ITEM_TYPE_ICON_REGISTRY)
		self._dock_bindisplay  = QtWidgets.QDockWidget(self.tr("Bin Display Settings"))
		
		self._tool_sifting     = siftwidget.BSSiftSettingsWidget(sift_filter_model=self._bin_widget.siftFilter())
		self._dock_sifting     = QtWidgets.QDockWidget(self.tr("Sift Settings"))

		self._tool_appearance  = toolboxes.BSBinAppearanceSettingsView()
		self._dock_appearance  = QtWidgets.QDockWidget(self.tr("Font & Colors"))


		self._tool_binview     = editorwidget.BSBinViewColumnEditor(bin_view_model=self._bin_view_model, bin_view_provider=self._binview_provider)
		self._dock_binview     = QtWidgets.QDockWidget(self.tr("Bin View Settings"))

		#self._tool_columneditor = editorwidget.BSBinViewColumnEditor()
		#self._tool_columneditor.show()

#		self._btn_toolbox_bindisplay = buttons.BSActionPushButton(show_text=False)
#		self._btn_toolbox_appearance = buttons.BSActionPushButton(show_text=False)
#		self._btn_toolbox_sifting    = buttons.BSActionPushButton(show_text=False)
#		self._btn_toolbox_binview    = buttons.BSActionPushButton(show_text=False)

		self._drag_drop_overlay = overlaywidget.BSDragDropOverlayWidget(parent=self._bin_widget, is_visible=False)

		# The rest
		
		self.setMenuBar(menus.BinWindowMenuBar(self._man_actions))
		self.setupWidgets()
		self.setupDock()
		self.setupActions()
		self.setupSignals()


	def setupWidgets(self):
		"""Configure general widget placement and config"""
		
		self.setCentralWidget(self._bin_widget)
		self.setAcceptDrops(True)

		self._dock_bindisplay.setWidget(self._tool_bindisplay)
		self._dock_sifting.setWidget(self._tool_sifting)
		self._dock_appearance.setWidget(self._tool_appearance)
		self._dock_binview.setWidget(self._tool_binview)
		
		self._dock_bindisplay.hide()
		self._dock_sifting.hide()
		self._dock_appearance.hide()
		self._dock_binview.hide()

#		self._bin_widget.setBinModel(self._man_binitems.viewModel())
		
		#self._tool_binview.setModel(self._man_binview.viewModel())

		#self._main_bincontents.frameView().setScene(self._man_binitems.frameScene())

		# Top binbarboy
		topbar = self._bin_widget.topWidgetBar()
		
		topbar.setOpenBinAction(self._man_actions.fileBrowserAction())
		topbar.setReloadBinAction(self._man_actions._act_reloadcurrent)
		topbar.setStopLoadAction(self._man_actions._act_stopcurrent)
		
		topbar.setViewModeListAction(self._man_actions.viewBinAsList())
		topbar._btn_viewmode_list.setIconEngine(icon_providers.getPalettedIconEngine(self._man_actions._act_view_list))

		topbar.setViewModeFrameAction(self._man_actions.viewBinAsFrame())
		topbar._btn_viewmode_frame.setIconEngine(icon_providers.getPalettedIconEngine(self._man_actions._act_view_frame))

		topbar.setViewModeScriptAction(self._man_actions.viewBinAsScript())
		topbar._btn_viewmode_script.setIconEngine(icon_providers.getPalettedIconEngine(self._man_actions._act_view_script))

		topbar.binViewSelector().setModel(self._binview_provider)

		self._anim_progress.setTargetObject(topbar.progressBar())
		self._anim_progress.setPropertyName(QtCore.QByteArray.fromStdString("value"))
		self._anim_progress.setEasingCurve(QtCore.QEasingCurve.Type.Linear)

		grp = QtWidgets.QSizeGrip(self._bin_widget.textView())
		self._bin_widget.textView().setCornerWidget(grp)

		self._bin_widget.setShowColumnEditorAction(self._man_actions._act_toggle_binview_settings)
		
		# Apply Bin Settings Toggles
		for act_toggle in reversed(self._man_actions.toggleBinSettingsActionGroup().actions()):	
			
			btn = buttons.BSPalettedActionPushButton(act_toggle, show_text=False, icon_engine=icon_providers.getPalettedIconEngine(act_toggle))
			btn.setIconSize(QtCore.QSize(8,8))
			btn.setFixedSize(QtCore.QSize(
				*[self._bin_widget.scrollbarScaler().scrollbarSize()] * 2,
			))
			self._bin_widget.scrollbarScaler().sig_size_changed.connect(
				lambda s, b=btn: b.setFixedSize(QtCore.QSize(s,s))
			)
			
			self._bin_widget.textView().addScrollBarWidget(btn, QtCore.Qt.AlignmentFlag.AlignLeft)

		# Frame View Toggles
		btn = buttons.BSPalettedActionPushButton(self._man_actions._act_toggle_sys_appearance, show_text=False, icon_engine=icon_providers.getPalettedIconEngine(self._man_actions._act_toggle_sys_appearance))
		btn.setIconSize(QtCore.QSize(8,8))
		btn.setFixedSize(QtCore.QSize(
			*[self._bin_widget.scrollbarScaler().scrollbarSize()] * 2,
		))
		self._bin_widget.scrollbarScaler().sig_size_changed.connect(
			lambda s, b=btn: b.setFixedSize(QtCore.QSize(s,s))
		)

		self._bin_widget.frameView().addScrollBarWidget(btn, QtCore.Qt.AlignmentFlag.AlignLeft)

		btn = buttons.BSPalettedActionPushButton(self._man_actions._act_toggle_show_all_items, show_text=False, icon_engine=icon_engines.BSPalettedSvgIconEngine(":/icons/gui/toggle_frame_showall.svg"))
		btn.setIconSize(QtCore.QSize(8,8))
		btn.setFixedSize(QtCore.QSize(
			*[self._bin_widget.scrollbarScaler().scrollbarSize()] * 2,
		))
		self._bin_widget.scrollbarScaler().sig_size_changed.connect(
			lambda s, b=btn: b.setFixedSize(QtCore.QSize(s,s))
		)

		self._bin_widget.frameView().addScrollBarWidget(btn, QtCore.Qt.AlignmentFlag.AlignLeft)

		for act_toggle in self._bin_widget.frameView().actions().overlayActions().actions(): #lol

			btn = buttons.BSPalettedActionPushButton(act_toggle, show_text=False, icon_engine=icon_providers.getPalettedIconEngine(act_toggle))
			btn.setIconSize(QtCore.QSize(8,8))
			btn.setFixedSize(QtCore.QSize(
				*[self._bin_widget.scrollbarScaler().scrollbarSize()] * 2,
			))
			self._bin_widget.scrollbarScaler().sig_size_changed.connect(
				lambda s, b=btn: b.setFixedSize(QtCore.QSize(s,s))
			)
			
			self._bin_widget.frameView().addScrollBarWidget(btn, QtCore.Qt.AlignmentFlag.AlignLeft)			


		
	def setupDock(self):
		"""Add and prepare the dock"""
		
		self.addDockWidget(QtCore.Qt.DockWidgetArea.NoDockWidgetArea, self._dock_binview)
		self._dock_binview.setFloating(True)
		self.addDockWidget(QtCore.Qt.DockWidgetArea.NoDockWidgetArea, self._dock_bindisplay)
		self._dock_bindisplay.setFloating(True)
		self.addDockWidget(QtCore.Qt.DockWidgetArea.NoDockWidgetArea, self._dock_sifting)
		self._dock_sifting.setFloating(True)
		self.addDockWidget(QtCore.Qt.DockWidgetArea.NoDockWidgetArea, self._dock_appearance)
		self._dock_appearance.setFloating(True)

	def setupActions(self):
		"""Add applicable actions"""

		self.addActions(self._man_actions.applicationActionsGroup().actions())
		self.addActions(self._man_actions.fileActionsGroup().actions())
		self.addActions(self._man_actions.windowActionsGroup().actions())
		
		self.addActions(self._man_actions.showBinSettingsActionGroup().actions())
		self.addActions(self._man_actions.viewModesActionGroup().actions())

		self.addActions(self._man_actions.toggleBinSettingsActionGroup().actions())

		self._man_actions._act_reloadcurrent.setVisible(False)
		self._man_actions._act_reloadcurrent.setEnabled(False)
		self._man_actions._act_stopcurrent  .setVisible(False)
		self._man_actions._act_stopcurrent  .setEnabled(False)
		
	def setupSignals(self):
		"""Connect signals and slots"""

		# Window/File Actions
		self._man_actions._act_filebrowser.triggered         .connect(self.showFileBrowser)
		self._man_actions._act_newwindow.triggered           .connect(self.sig_request_new_window)
		self._man_actions._act_closewindow.triggered         .connect(self.close)
		self._man_actions._act_quitapplication.triggered     .connect(self.sig_request_quit_application)
		self._man_actions._act_show_about.triggered          .connect(self.showAboutBox)

		self._man_actions._act_reloadcurrent.triggered       .connect(lambda: self.loadBinFromPath(self.windowFilePath()))
		self._man_actions._act_stopcurrent.triggered         .connect(self._sigs_binloader.requestStop)

		self._man_actions._act_check_updates.triggered       .connect(self.sig_request_check_updates)
		self._man_actions._act_open_discussions.triggered    .connect(self.sig_request_visit_discussions)
		self._man_actions._act_open_donations.triggered      .connect(self.sig_request_visit_donations)

		# Toolbox Toggle Actions
		# NOTE: Dock widgets have a toggleViewAction() butuhhhhh
		self._man_actions.showBinDisplaySettings().toggled   .connect(self._dock_bindisplay.setVisible)
		self._dock_bindisplay.visibilityChanged              .connect(self._man_actions.showBinDisplaySettings().setChecked)

		self._man_actions.showBinAppearanceSettings().toggled.connect(self._dock_appearance.setVisible)
		self._dock_appearance.visibilityChanged              .connect(self._man_actions.showBinAppearanceSettings().setChecked)

		self._man_actions.showBinSiftSettings().toggled      .connect(self._dock_sifting.setVisible)
		self._dock_sifting.visibilityChanged                 .connect(self._man_actions.showBinSiftSettings().setChecked)

		self._man_actions.showBinViewSettings().toggled      .connect(self._dock_binview.setVisible)
		self._dock_binview.visibilityChanged                 .connect(self._man_actions.showBinViewSettings().setChecked)

		# User debuggy-type tools
		# NOTE: Have application instance hook directly into window.actionsManager()?
		# NOTE FROM FUTURE SELF: ^^ what?
		# NOTE FROM DISTANT FUTURE SELF: Maybe have the QApplication instance set up the window's action manager on creation? lol dunno tho
		self._man_actions.showUserFolder().triggered         .connect(self.sig_request_show_user_folder)
		self._man_actions.showLogViewer().triggered          .connect(self.sig_request_show_log_viewer)
		self._man_actions.showSettingsWindow().triggered     .connect(self.sig_request_show_settings)

		# Bin Settings Toolboxes
		self._man_bindisplay.sig_bin_display_changed         .connect(self._tool_bindisplay.setFlags)
		self._man_bindisplay.sig_bin_display_changed         .connect(self._bin_widget.itemDisplayFilter().setAcceptedItemTypes)
		self._tool_bindisplay.sig_flags_changed              .connect(self._man_bindisplay.setBinDisplayFlags)

		# Appearance to binwidget
		self._man_appearance.sig_active_font_changed          .connect(self._bin_widget.setBinFont)
		self._man_appearance.sig_palette_changed             .connect(self._bin_widget.setBinPalette)
		
		# Appearance to toolbox
		self._man_appearance.sig_bin_font_changed            .connect(self._tool_appearance.setBinFont)
		self._man_appearance.sig_bin_colors_changed          .connect(self._tool_appearance.setBinColors)
		self._man_appearance.sig_window_rect_changed         .connect(self._tool_appearance.setBinRect)
		self._man_appearance.sig_was_iconic_changed          .connect(self._tool_appearance.setWasIconic)

		# Toolbox to Appearance
		self._tool_appearance.sig_font_changed               .connect(self._man_appearance.setBinFont)
		self._tool_appearance.sig_colors_changed             .connect(self._man_appearance.setBinColors)

		# Bin loader signals
		self._sigs_binloader.sig_begin_loading               .connect(self.prepareForBinLoading)
		self._sigs_binloader.sig_done_loading                .connect(self.cleanupAfterBinLoading)
		self._sigs_binloader.sig_got_exception               .connect(self.binLoadException)
		self._sigs_binloader.sig_aborted_loading             .connect(self.cleanupPartialBin)
		
		self._sigs_binloader.sig_got_mob_count               .connect(self.gotMobCount)
		self._sigs_binloader.sig_got_mobs                    .connect(self.addBinItems, QtCore.Qt.ConnectionType.BlockingQueuedConnection) # These fellas pile up
 
		self._sigs_binloader.sig_got_display_mode            .connect(self._bin_widget.setViewMode)
		self._sigs_binloader.sig_got_bin_display_settings    .connect(self._man_bindisplay.setBinDisplayFlags)
		self._sigs_binloader.sig_got_view_settings           .connect(self._bin_view_model.setBinViewInfo)
		self._sigs_binloader.sig_got_text_column_widths      .connect(self._bin_widget.setTextColumnWidthsFromBin)
		self._sigs_binloader.sig_got_frame_mode_scale        .connect(self._bin_widget.frameView().setZoom)
		self._sigs_binloader.sig_got_script_mode_scale       .connect(self._bin_widget.scriptView().setFrameScale)
		self._sigs_binloader.sig_got_sift_settings           .connect(self.setSiftCriteriaFromBin)
		self._sigs_binloader.sig_got_bin_appearance_settings .connect(self._man_appearance.setAppearanceSettings)
#		self._sigs_binloader.sig_got_sort_settings           .connect(self._man_binview.setDefaultSortColumns)
#		self._sigs_binloader.sig_got_mobs                    .connect(self.updateLoadingBar, QtCore.Qt.ConnectionType.BlockingQueuedConnection)

		# Sift Settings
		self._tool_sifting.sig_criteria_set                  .connect(self._bin_widget.siftFilter().setSiftCriteria)
		self._tool_sifting.sig_live_sift_enabled             .connect(self._bin_widget.siftFilter().setLiveSiftEnabled)
		self._bin_widget.siftFilter().sig_live_sift_enabled  .connect(self._tool_sifting.setLiveSiftEnabled)
		self._bin_widget.siftFilter().sig_criteria_changed   .connect(self._tool_sifting.setCriteria)

		# Bin Contents Toolbars
		self._bin_widget.topWidgetBar().searchBox().textChanged.connect(self.userChangedSearchText)

		# Bin View Modes
		# TODO: Something about this feels circular compared to the other stuff I've been doing
		self._bin_widget.sig_view_mode_changed                  .connect(lambda  vm: self._man_actions.viewModesActionGroup().actions()[int(vm)].setChecked(True))
		self._man_actions._actgrp_view_mode.triggered           .connect(lambda act: self._bin_widget.setViewMode(self._man_actions._actgrp_view_mode.actions().index(act)))

		# Bin Settings Toggles
		self._man_actions._act_toggle_show_all_columns.toggled  .connect(self._bin_widget.setBinColumnFiltersDisabled)
		self._bin_widget.sig_bin_view_enabled                   .connect(lambda enabled: self._man_actions._act_toggle_show_all_columns.setChecked(not enabled))
		
		self._man_actions._act_toggle_show_all_items.toggled    .connect(self._man_binview.setAllItemsVisible)
		self._man_binview.sig_all_items_toggled                 .connect(self._man_actions._act_toggle_show_all_items.setChecked)
		self._man_binview.sig_bin_filters_toggled               .connect(self._bin_widget.setBinItemFiltersEnabled)

		self._man_actions._act_toggle_sys_appearance.toggled    .connect(self._man_appearance.setUseSystemAppearance)
		self._man_appearance.sig_use_system_appearance_toggled  .connect(self._man_actions._act_toggle_sys_appearance.setChecked)


		# Bin View Provider
		self._bin_view_model.sig_bin_view_info_set              .connect(self.activeBinViewChanged)
		self._bin_view_model.sig_bin_view_modified              .connect(lambda bv: self.activeBinViewChanged(bv, True))
		
		# Bin View Editor
		self._tool_binview.sig_focus_column_requested           .connect(self._bin_widget.focusBinColumn)

		self._tool_binview.sig_bin_view_source_selected                .connect(self.binViewSourceSelected)
		self._bin_widget.binViewSelector().sig_binview_source_selected .connect(self.binViewSourceSelected)


	##
	## Getters & Setters
	##

	@QtCore.Slot(str)
	def userChangedSearchText(self, search_text:str):
		"""User changed "Find In Bin" text, throttle via """

		if not self._find_in_bin_timer.isActive():
			self._find_in_bin_timer.start()

	def binViewProviderModel(self) -> providermodel.BSBinViewProviderModel:

		return self._binview_provider

	@QtCore.Slot()
	def addBinItems(self, bin_items:list[binitemtypes.BSBinItemInfo]):

		self.updateLoadingBar(bin_items)
		self._bin_item_model.addBinItems(bin_items)
			
	def actionsManager(self) -> actions.ActionsManager:
		return self._man_actions

	def binViewManager(self) -> binproperties.BSBinViewManager:
		return self._man_binview
	
#	def siftSettingsManager(self) -> binproperties.BSBinSiftSettingsManager:
#		return self._man_siftsettings
	
	def appearanceManager(self) -> appearance.BSBinAppearanceSettingsManager:
		return self._man_appearance
	
#	def sortingManager(self) -> binproperties.BSBinSortingPropertiesManager:
#		return self._man_sorting
	
	def binLoadingSignalManger(self) -> binloader.BSBinViewLoader.Signals:
		return self._sigs_binloader
	
	def binContentsWidget(self) -> binwidget.BSBinContentsWidget:
		return self._bin_widget

	@QtCore.Slot(int)
	def setMobQueueSize(self, queue_size:int):
		self._queue_size = queue_size

	def mobQueueSize(self) -> int:
		return self._queue_size
	
	@QtCore.Slot(bool)
	def setUseSiftCriteriaFromBin(self, use_sift:bool):
		self._use_sift = use_sift
	
	@QtCore.Slot(bool)
	def setUseAnimation(self, use_animation:bool):
		self._use_animation = use_animation
	
	def useAnimation(self) -> bool:
		"""Use fancy animated progress bar"""

		return self._use_animation
	
	@QtCore.Slot(bool)
	def setUseSavedColumnWidths(self, use_col_widths:bool):

		self._bin_widget.setUseSavedBinColumnWidths(use_col_widths)
	
	##
	## Slots
	##

	@QtCore.Slot(object)
	def binViewSourceSelected(self, binview_source:binviewsources.BSAbstractBinViewSource):
		"""User selected a bin view"""

		try:
		
			binview_info = binview_source.binViewInfo()
		
		except Exception as e:

#			print(repr(e))

			if isinstance(e, FileNotFoundError):
				err_informative = self.tr(
					"The file <code>{file_name}</code> does not appear to exist.\n\nIf this error continues, please try restarting the application."
				).format_map(
					{"file_name": QtCore.QFileInfo(binview_source.path()).fileName()}
				)

			elif isinstance(binview_source, binviewsources.BSBinViewSourceFile):
				err_informative = self.tr(
					"The file <code>{file_name}</code> does not appear to be a valid bin view file.\n\nYou may wish to remove it from your user folder."
				).format_map(
					{"file_name": QtCore.QFileInfo(binview_source.path()).fileName()}
				)
			
			else:
				err_informative = self.tr(
					"The bin view <strong>{binview_name} does not appear to be valid."
				).format_map(
					{"binview_name": binview_source.name()}
				)

			wnd_error_message = QtWidgets.QMessageBox(parent=self)
			wnd_error_message.setIcon(QtWidgets.QMessageBox.Icon.Warning)
			
			wnd_error_message.setText(self.tr("Could Not Load Bin View"))
			wnd_error_message.setInformativeText(err_informative)
			wnd_error_message.setDetailedText(str(e))

			wnd_error_message.exec()
			
		else:
			self._bin_view_model.setBinViewInfo(binview_info)

	@QtCore.Slot(object)
	def activeBinViewChanged(self, binview_info:binviewitemtypes.BSBinViewInfo, is_modified:bool=False):
		"""BinViewModel informs that the bin view has been set"""


		unique_name = None


		if is_modified:
			
			# If this is a modified view, check for an already-existing, already-modified view and inherit the name
			for bvs in self._binview_provider.sessionBinViewSources():

				if bvs.name() == binview_info.name:
					
					if bvs.isModified():
						unique_name = bvs.name()
					else:
						break
			
			# Nothing like that found, so build a unique name for the modified view
			if not unique_name:

				other_binview_names = \
					set(s.name() for s in self._binview_provider.sessionBinViewSources() if s.name() != binview_info.name) |\
					set(s.name() for s in self._binview_provider.storedBinViewSources())
				
				unique_name = renaming.make_unique_name(binview_info.name, other_binview_names, index_padding=1)
		

		# For setting a non-modified active bin view, just go with the original name
		# NOTE: Won't do unique session names if I ever do multiple session bins I dunno
		unique_name = unique_name or binview_info.name

		self._binview_provider.clearSessionViewSources()
		
		if unique_name != binview_info.name:

			binview_info = dataclasses.replace(binview_info, name=unique_name)
			self._bin_view_model.setBinViewName(unique_name)

		# Otherwise, confirm name collision and give a new name
		
		binview_source = binviewsources.BSBinViewSourceBin(binview_info, is_modified)
		self._binview_provider.addSessionBinViewSource(binview_source)

#		self._bin_widget.topWidgetBar()._cmb_binviews.setCurrentIndex(0)


	@QtCore.Slot(str)
	def prepareForBinLoading(self, bin_path:str):
		"""Bin load is about to begin. Prepare UI elements."""

		
		logging.getLogger(__name__).info("Begin loading %s", bin_path)
		
		self._time_last_load.start()

		self._man_actions._act_filebrowser.setEnabled(False)
		
		self._man_actions._act_reloadcurrent.setEnabled(False)
		self._man_actions._act_reloadcurrent.setVisible(False)

		self._man_actions._act_stopcurrent.setEnabled(True)
		self._man_actions._act_stopcurrent.setVisible(True)
		
		self._bin_item_model.clear()
		self._bin_widget.siftFilter().setLiveSiftEnabled(False)
		self._bin_widget.siftFilter().resetSiftCriteria()
		
		self._bin_widget.topWidgetBar().progressBar().setFormat(self.tr("Loading bin properties..."))
		self._bin_widget.topWidgetBar().progressBar().show()

		# NOTE: Disabling autosize for now, big ol' overhead during load
		self._bin_widget.textView().header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
#		self._bin_widget.textView().header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

		self._bin_widget.textView().header().setSectionsMovable(False)
# self._bin_widget.textView().model().setDynamicSortFilter(False)
		
		self.setCursor(QtCore.Qt.CursorShape.BusyCursor)
		self.setWindowFilePath(bin_path)

	@QtCore.Slot(object)
	def updateLoadingBar(self, mobs_list:list):
		"""Update/animate the progress"""

		if self._use_animation:

			last_duration     = self._time_last_chunk.restart() if self._time_last_chunk.isValid() else 5_000
			adjusted_duration = round(last_duration * (len(mobs_list)/self._queue_size))

			self._anim_progress.stop()
			self._anim_progress.setStartValue(self._anim_progress.targetObject().value())
			#self._anim_progress.setEndValue(min(self._anim_progress.targetObject().value() + self._queue_size, self._anim_progress.targetObject().maximum()))
			self._anim_progress.setEndValue((self._anim_progress.endValue() or 0) + len(mobs_list))
			self._anim_progress.setDuration(adjusted_duration)
			
			if not self._time_last_chunk.isValid():
				self._time_last_chunk.start()

			self._anim_progress.start()
		else:
			self._bin_widget.topWidgetBar().progressBar().setValue(self._bin_widget.topWidgetBar().progressBar().value() + len(mobs_list))

	@QtCore.Slot(object)
	def setSiftCriteriaFromBin(self, criteria:list[list[sifters.BSAbstractSifter]]):

		if not self._use_sift:
			return
#		print("** FROM BIN, GOT ", criteria)
		self.binContentsWidget().siftFilter().setSiftCriteria(criteria)
		logging.getLogger(__name__).debug("Loaded sift settings from bin: %s", repr(criteria))
	
	@QtCore.Slot()
	def cleanupAfterBinLoading(self):
		"""A bin has finished loading.  Reset UI elements."""

		# NOTE: If I really wanna tween the last of the progress,
		# I could do something like below. But is it necessary?
		# PROBABLY NOT.
		#self._anim_progress.finished.connect(self.cleanupProgressBar)

		# NOTE: Otherwise, I'm just resetting everything immediately which I think is the way to go
		self._anim_progress.stop()
		self._anim_progress.setEndValue(0)
		self._time_last_chunk.invalidate()


		self._bin_widget.topWidgetBar().progressBar().setMaximum(0)
		self._bin_widget.topWidgetBar().progressBar().setValue(0)
		self._bin_widget.topWidgetBar().progressBar().hide()

		# Enabling sorting also performs a sort... sooo
		# Set invalid sort column first, per the docs
		# TODO: Set as stored sort column if available from the bin
#		self._bin_widget.textView().header().setSortIndicator(-1, QtCore.Qt.SortOrder.AscendingOrder)
		#self._bin_widget.textView().setSortingEnabled(True)
		
		self._man_actions._act_reloadcurrent.setEnabled(True)
		self._man_actions._act_reloadcurrent.setVisible(True)

		self._man_actions._act_stopcurrent.setEnabled(False)
		self._man_actions._act_stopcurrent.setVisible(False)

		self._man_actions._act_filebrowser.setEnabled(True)

		self.sig_bin_changed.emit(self.windowFilePath())
		

		self._bin_widget.textView().header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		self._bin_widget.textView().header().setSectionsMovable(True)
		self.unsetCursor()
		QtWidgets.QApplication.instance().alert(self)

		total_load_time = self._time_last_load.elapsed()
		self._time_last_load.invalidate()
		
		logging.getLogger(__name__).info("Finished loading %s in %s seconds (queuesize=%s, fancy=%s)", self.windowFilePath(), round(total_load_time/1000,2), self._queue_size, self._use_animation)

	@QtCore.Slot()
	@QtCore.Slot(str)
	def cleanupPartialBin(self, message:str|None=None):
		"""Do any cleanup for a cancelled bin load"""

		
		logging.getLogger(__name__).warning("Aborted loading bin")
		
		if message:
			QtWidgets.QMessageBox.critical(self, self.tr("Bin Not Loaded"), message)

	@QtCore.Slot(object)
	def binLoadException(self, exception:Exception):
		
		logging.getLogger(__name__).error("Error during bin load: %s", str(exception))
	
	@QtCore.Slot()
	@QtCore.Slot(object)
	def showFileBrowser(self, initial_path:PathLike|None=None):
		"""Show the file browser to select a bin"""

		file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
			parent=self,
			caption = self.tr("Choose an Avid bin..."),
			filter=self.tr("Avid Bin (*.avb);;All Files (*)"),
			dir=initial_path or self.windowFilePath()
		)

		self.activateWindow()
		
		if file_path:
			self.loadBinFromPath(file_path)

	@QtCore.Slot(object)
	def loadBinFromPath(self, bin_path:PathLike):
		"""Load a bin from the given path"""

		QtCore.QThreadPool.globalInstance().start(
			binloader.BSBinViewLoader(bin_path, self._sigs_binloader, self._queue_size)
		)

	@QtCore.Slot()
	def showAboutBox(self):
		"""Show the About thing"""

		dlg_about = about.BSAboutDialog()
		dlg_about.exec()

	@QtCore.Slot()
	def cleanupSignals(self):
		"""Disconnect from worker signals on close"""

		
		logging.getLogger(__name__).debug("Cleaning up signals")
		
		self._sigs_binloader.requestStop()
		self._sigs_binloader.disconnect(self)

	@QtCore.Slot(int)
	def gotMobCount(self, mob_count:int):

		self._bin_widget.topWidgetBar().progressBar().setMaximum(mob_count)
		self._bin_widget.topWidgetBar().progressBar().setFormat(self.tr("Loading %v of %m mobs", "%v=current_count; %m=total_count"))

	def closeEvent(self, event):
		
		self.cleanupSignals()
		
		return super().closeEvent(event)
	
	def dragEnterEvent(self, event:QtGui.QDragEnterEvent):

		if not event.mimeData().hasUrls():

			event.ignore()
			return False

		self._drag_drop_overlay.show()
		
		event.accept()
		return True
	
	def dropEvent(self, event:QtGui.QDropEvent):

		for file_path in map(lambda u: QtCore.QDir.toNativeSeparators(u.toLocalFile()), event.mimeData().urls()):

			self.loadBinFromPath(file_path)
			
		self._drag_drop_overlay.hide()
		event.accept()
		return True
	
	def dragLeaveEvent(self, event:QtGui.QDragLeaveEvent):

		self._drag_drop_overlay.hide()
		
		event.accept()
		return True
	
#	@QtCore.Slot(object)
#	@QtCore.Slot(object, str)
#	def exportBinView(self, binview_info:binviewitemtypes.BSBinViewInfo, with_name:str|None=None):
#		"""Export the current binview"""
#
#		if with_name:
#			binview_info = dataclasses.replace(binview_info, name=with_name)
#
#		self.sig_request_export_bin_view.emit(binview_info)

#	@QtCore.Slot(str)
#	def deleteBinView(self, binview_name:str):
#
#		for binview_info in self._binview_provider.storedBinViewSources():
#
#			if binview_info.name() == binview_name:
#				self.sig_request_delete_bin_view.emit(binview_info)
#
