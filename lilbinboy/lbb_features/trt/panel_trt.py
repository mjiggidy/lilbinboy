import logging
from PySide6 import QtWidgets, QtGui, QtCore, QtSql
from timecode import Timecode
from concurrent import futures
from lilbinboy.lbb_common import LBUtilityTab, LBSpinBoxTC, LBTimelineView, LBSettingsManager
from lilbinboy.lbb_features.trt import dlg_choose_columns, dlg_marker, logic_trt, model_trt, markers_trt, dlg_sequence_selection, dlg_choose_columns, exporters_trt, wdg_sequence_treeview, wdg_sequence_trims, wdg_stats, hist_main
from .settings_keys import TRTSettingsKeys


class TRTBinLoadingProgressBar(QtWidgets.QProgressBar):

	sig_progress_started = QtCore.Signal()
	sig_progress_completed = QtCore.Signal()

	TIMEOUT_BEFORE_HIDE = 1000

	def __init__(self):
		super().__init__()

		# Hide timer but keep the space for it
		p = self.sizePolicy()
		p.setRetainSizeWhenHidden(True)
		self.setSizePolicy(p)
		
		# Setup timer to hide
		self._reset_timer = QtCore.QTimer()
		self._reset_timer.timeout.connect(self.reset)
		self._reset_timer.setSingleShot(True)
		
		self.reset()

		self.setFormat("Loading %v of %m bins...")
	
	@QtCore.Slot()
	def step_added(self):
		if self.isHidden():
			self.setHidden(False)
			self.sig_progress_started.emit()

		self._reset_timer.stop()
		self.setMaximum(self.maximum() + 1)
	
	@QtCore.Slot()
	def step_complete(self):
		self.setValue(self.value() + 1)
		if self.value() == self.maximum():
			self._reset_timer.start(self.TIMEOUT_BEFORE_HIDE)
	
	@QtCore.Slot()
	def reset(self):
		self.setRange(0,0)
		self.setValue(0)
		self.setHidden(True)
		self.sig_progress_completed.emit()

class TRTThreadedMulticoreAbomination(QtCore.QRunnable):
	"""I don't like this"""

	class TRTThreadedSignals(QtCore.QObject):
		sig_got_bin_info = QtCore.Signal(list)
		sig_had_error    = QtCore.Signal(str, Exception)
		sig_complete     = QtCore.Signal(bool)
	
	def __init__(self, bin_paths:list[str]):
		super().__init__()
		self._bin_paths = bin_paths
		self._signals = self.TRTThreadedSignals()
	
	def signals(self) -> TRTThreadedSignals:
		return self._signals
	
	def run(self):
		errors:list[Exception] = []
		with futures.ProcessPoolExecutor(max_workers=6) as executor:
			bin_futures = {executor.submit(logic_trt.get_timelines_from_bin, bin_path) : bin_path for bin_path in self._bin_paths}
			for bin_future in futures.as_completed(bin_futures):
				try:
					timeline_info_list = bin_future.result()
					self.signals().sig_got_bin_info.emit(timeline_info_list)
				except Exception as e:
					logging.getLogger(__name__).error("Didn't load %s: %s", bin_futures[bin_future], e)
					errors.append(e)
					self.signals().sig_had_error.emit(bin_futures[bin_future], e)
		self.signals().sig_complete.emit(bool(errors))


class TRTThreadedBinGetter(QtCore.QRunnable):
	"""The old one"""

	class TRTThreadedSignals(QtCore.QObject):
		sig_got_bin_info = QtCore.Signal(list)

	def __init__(self, bin_path:str):
		super().__init__()
		self._bin_path = bin_path
		self._signals = self.TRTThreadedSignals()

	def signals(self) -> TRTThreadedSignals:
		return self._signals

	def run(self):
		self.signals().sig_got_bin_info.emit(logic_trt.get_timelines_from_bin(self._bin_path))

class TRTModeSelection(QtWidgets.QFrame):
	"""Select how sequences are chosen from bins"""

	sig_sequence_selection_mode_changed = QtCore.Signal(model_trt.SequenceSelectionMode)
	sig_sequence_selection_settings_requested = QtCore.Signal()

	def __init__(self):

		super().__init__()

		self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
		self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
		self.updateStylesheet()

		#self.setSizePolicy(self.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.Maximum)

		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setContentsMargins(0,0,0,0)

		self._rdo_one_sequence = QtWidgets.QRadioButton()
		self._btn_one_sequence_config = QtWidgets.QPushButton()
		
		self._rdo_all_sequence = QtWidgets.QRadioButton()

		self._btn_group = QtWidgets.QButtonGroup()
		self._btn_group.addButton(self._rdo_one_sequence)
		self._btn_group.addButton(self._rdo_all_sequence)
		
		self.layout().addStretch()

		self._rdo_one_sequence.setText("One Sequence Per Bin")
		self.layout().addWidget(self._rdo_one_sequence)

		self._btn_one_sequence_config.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentProperties))
		self._btn_one_sequence_config.setIconSize(QtCore.QSize(8,8))
		self.layout().addWidget(self._btn_one_sequence_config)

		self.layout().addStretch()

		self._rdo_all_sequence.setText("All Sequences In Bin")
		self.layout().addWidget(self._rdo_all_sequence)

		self.layout().addStretch()

		self._btn_group.buttonClicked.connect(self.selectionChanged)
		self._btn_one_sequence_config.clicked.connect(self.sig_sequence_selection_settings_requested)
	
	def updateStylesheet(self):
		# I hate using CSS for this
		border_color = QtWidgets.QApplication.palette().color(QtGui.QPalette.ColorRole.Dark).name()
		background_color = QtWidgets.QApplication.palette().color(QtGui.QPalette.ColorRole.Midlight).name()
		self.setStyleSheet(f"QFrame {{ border-radius: 2px; border: 1px solid {border_color}; }}") # Ugh
	
	@QtCore.Slot(QtWidgets.QAbstractButton)
	def selectionChanged(self, button:QtWidgets.QAbstractButton):

		if button == self._rdo_one_sequence:
			self.sig_sequence_selection_mode_changed.emit(model_trt.SequenceSelectionMode.ONE_SEQUENCE_PER_BIN)
		elif button == self._rdo_all_sequence:
			self.sig_sequence_selection_mode_changed.emit(model_trt.SequenceSelectionMode.ALL_SEQUENCES_PER_BIN)
		else:
			logging.getLogger(__name__).error("Weird selection mode from button: %s", button)
	
	@QtCore.Slot(model_trt.SequenceSelectionMode)
	def setSequenceSelectionMode(self, mode:model_trt.SequenceSelectionMode):
		
		if mode is model_trt.SequenceSelectionMode.ONE_SEQUENCE_PER_BIN:
			self._rdo_one_sequence.setChecked(True)
		elif mode is model_trt.SequenceSelectionMode.ALL_SEQUENCES_PER_BIN:
			self._rdo_all_sequence.setChecked(True)


class LBTRTCalculator(LBUtilityTab):
	"""TRT Calculator"""

	PATH_ICON = __file__+"../../../../res/icon_trt.png"

	sig_modelchanged = QtCore.Signal()
	sig_export_requested = QtCore.Signal(str, str)

	def __init__(self, settings:QtCore.QSettings, *args, **kwargs):
		super().__init__(*args, **kwargs)


		self.setLayout(QtWidgets.QVBoxLayout())

		self._pool = QtCore.QThreadPool()
		self._settings = settings

		# Declare models
		self._data_model = model_trt.TRTDataModel()
		self._treeview_model = model_trt.TRTViewModel()
		
		# Declare top controls
		self.btn_add_bins = QtWidgets.QPushButton("Add From Bins...")
		self.btn_refresh_bins = QtWidgets.QPushButton()
		self.btn_clear_bins = QtWidgets.QPushButton()
		
		# Stacked widget to toggle between progress bar and bin/sequence mode
		self.stack_bin_loading = QtWidgets.QStackedWidget()
		self.prog_loading = TRTBinLoadingProgressBar()
		self.bin_mode = TRTModeSelection()

		# Declare main treeview
		self.list_trts = wdg_sequence_treeview.TRTTreeView()
		self.trt_summary = wdg_stats.TRTStatView()

		# Longplay Layout
		self.view_longplay = LBTimelineView()

		# Declare trims
		self.trt_trims = wdg_sequence_trims.TRTControlsTrims()
		self.trim_total = LBSpinBoxTC()

		# Export TSV/CSV/JSON
		self.actn_export_data = QtGui.QAction(self)
		self.btn_export_data = QtWidgets.QPushButton()

		self.btn_snapshots = QtWidgets.QPushButton()



		self._setupSignals()
		self._setupWidgets()
		self._loadInitial()


	def setSettingsManager(self, settings:QtCore.QSettings):
		# TODO: Never called?
		self._settings = settings
		logging.getLogger(__name__).debug("Settings manager set to %s", settings)
	
	def settingsManager(self) -> QtCore.QSettings:
		return self._settings

	def _loadInitial(self):
		"""Load initial data from preferences (or defaults)"""
		
		self.model().setRate(int(self.settingsManager().value(TRTSettingsKeys.LAST_RATE, 24)))

		
		try:
			seq_mode = model_trt.SequenceSelectionMode(self.settingsManager().value(TRTSettingsKeys.SEQ_SELECTION_MODE, model_trt.SequenceSelectionMode.ONE_SEQUENCE_PER_BIN.value))
		except ValueError:
			seq_mode = model_trt.SequenceSelectionMode.ONE_SEQUENCE_PER_BIN
		finally:
			self.model().setSequenceSelectionMode(seq_mode)
			self.bin_mode.setSequenceSelectionMode(self.model().sequenceSelectionMode())
		
		self.model().set_marker_presets(self.settingsManager().value(TRTSettingsKeys.MARKER_PRESETS_LIST, dict()))

		self.model().setTrimFromHead(Timecode(self.settingsManager().value(TRTSettingsKeys.TRIM_HEAD_DURATION,0), rate=self.model().rate()))
		self.model().setTrimFromTail(Timecode(self.settingsManager().value(TRTSettingsKeys.TRIM_TAIL_DURATION,0), rate=self.model().rate()))
		self.model().setTrimTotal(Timecode(self.settingsManager().value(TRTSettingsKeys.TRIM_TOTAL_DURATION,0), rate=self.model().rate()))
		
		self.model().set_active_head_marker_preset_name(self.settingsManager().value(TRTSettingsKeys.TRIM_HEAD_MARKER))
		self.model().set_active_tail_marker_preset_name(self.settingsManager().value(TRTSettingsKeys.TRIM_TAIL_MARKER))


		self.setFieldVisibility(self.settingsManager().value(TRTSettingsKeys.LIST_FIELDS_ORDER, [], type=list), self.settingsManager().value(TRTSettingsKeys.LIST_FIELDS_HIDDEN, [], type=list))
		
		try:
			sort_order = QtCore.Qt.SortOrder[self.settingsManager().value(TRTSettingsKeys.LIST_SORT_DIRECTION, QtCore.Qt.SortOrder.AscendingOrder.name)]
		except KeyError:
			sort_order = QtCore.Qt.SortOrder.AscendingOrder
		finally:			
			self.setSorting(
				sort_field = self.settingsManager().value(TRTSettingsKeys.LIST_SORT_FIELD, "sequence_name"),
				sort_order = sort_order
			)

		sequenceSelectionSettings = model_trt.SingleSequenceSelectionProcess()
		sequenceSelectionSettings.setSortColumn(self.settingsManager().value(TRTSettingsKeys.SEQ_SELECTION_COL_NAME,"Name"))
		
		
		try:
			sort_direction = QtCore.Qt.SortOrder[self.settingsManager().value(TRTSettingsKeys.SEQ_SELECTION_COL_DIRECTION, QtCore.Qt.SortOrder.AscendingOrder.name)]
		except KeyError:
			sort_direction = QtCore.Qt.SortOrder.AscendingOrder
		finally:
			sequenceSelectionSettings.setSortDirection(sort_direction)
			sequenceSelectionFilters = []

		for filter in self.settingsManager().value(TRTSettingsKeys.SEQ_SELECTION_FILTERS, None) or []:
			if filter.get("kind") == "name_contains":
				sequenceSelectionFilters.append(
					model_trt.SingleSequenceSelectionProcess.NameContainsFilter(filter.get("string",""))
				)
			elif filter.get("kind") == "clip_color":
				sequenceSelectionFilters.append(
					model_trt.SingleSequenceSelectionProcess.ClipColorFilter([QtGui.QColor.fromRgba64(*c) for c in filter.get("colors")])
				)
			else:
				logging.getLogger(__name__).error("Unknown filter: %s", filter)
		sequenceSelectionSettings.setFilters(sequenceSelectionFilters)
		self.model().setSequenceSelectionProcess(sequenceSelectionSettings)
			
		
		self.add_bins_from_paths(list(self.settingsManager().value(TRTSettingsKeys.BINS_LIST,[], type=list)))


	def _setupWidgets(self):
		"""Setup the widgets and add them to the layout"""

		# Actions!
		# NOTE: I dunno if this is really the way to go buuut like....
		self.actn_export_data.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentSaveAs))
		self.actn_export_data.setText("Export as...")
		self.actn_export_data.triggered.connect(self.promptForExport)
		self.actn_export_data.setShortcut(QtGui.QKeySequence.StandardKey.Save)
		#self.addAction(self.actn_export_data)

		self.btn_export_data.setText(self.actn_export_data.text())
		self.btn_export_data.setIcon(self.actn_export_data.icon())
		self.btn_export_data.clicked.connect(self.actn_export_data.triggered)
		self.btn_export_data.setShortcut(self.actn_export_data.shortcut())

		# Setup top controls
		ctrl_layout = QtWidgets.QHBoxLayout()

		
		self.btn_add_bins.setToolTip("Add the latest sequence(s) from one or more bins")
		self.btn_add_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
		ctrl_layout.addWidget(self.btn_add_bins)
		
		#ctrl_layout.addWidget(self.prog_loading)
		self.stack_bin_loading.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Maximum))
		self.stack_bin_loading.addWidget(self.prog_loading)
		self.stack_bin_loading.addWidget(self.bin_mode)
		self.stack_bin_loading.setCurrentWidget(self.bin_mode)

		ctrl_layout.addWidget(self.stack_bin_loading)

		self.btn_refresh_bins.setToolTip("Reload the existing bins for updates")
		self.btn_refresh_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRefresh))
		ctrl_layout.addWidget(self.btn_refresh_bins)

		self.btn_clear_bins.setToolTip("Clear the existing sequences")
		self.btn_clear_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditClear))
		ctrl_layout.addWidget(self.btn_clear_bins)

		self.layout().addLayout(ctrl_layout)

		# Set up main treeview
		self.list_trts.setModel(self._treeview_model)
		self.list_trts.header().setContextMenuPolicy(QtGui.Qt.ContextMenuPolicy.CustomContextMenu)
		self.list_trts.header().customContextMenuRequested.connect(self.showColumnChooserContextMenu)
		self.list_trts.fit_headers()
		self.layout().addWidget(self.list_trts)

		# Longplay view
		self.view_longplay.setItems([])
		self.layout().addWidget(self.view_longplay)

		# Summary
		grp_summaries = QtWidgets.QGroupBox()
		grp_summaries.setLayout(QtWidgets.QVBoxLayout())
		grp_summaries.layout().setContentsMargins(0,0,0,0)
		
		# Initial items
		self.trt_summary.add_stat_item(wdg_stats.TRTStatItem(
			label="Sequences",
			value="0"
		))

		self.trt_summary.add_stat_item(wdg_stats.TRTStatItem(
			label="Locked",
			value="0"
		))

		self.trt_summary.add_stat_item(wdg_stats.TRTStatItem(
			label="FPS",
			value="24"
		))

		self.trt_summary.add_spacer()

		self.trt_summary.add_stat_item(wdg_stats.TRTStatItem(
			label="Total Running Length",
			value="0+00"
		))

		self.trt_summary.add_stat_item(wdg_stats.TRTStatItem(
			label="Total Running Time",
			value="00:00:00:00"
		))
		
		grp_summaries.layout().addWidget(self.trt_summary)
		self.layout().addWidget(grp_summaries)

		lay_exporters = QtWidgets.QHBoxLayout()
		
		lay_exporters.addWidget(self.btn_export_data)
		self.btn_snapshots.setText("Show Snapshots...")
		self.btn_snapshots.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRestore))
		self.btn_snapshots.clicked.connect(self.historyViewerRequsted)
		lay_exporters.addWidget(self.btn_snapshots)

		self.layout().addLayout(lay_exporters)
		
		# Set up sequence trim controls
		self.layout().addWidget(self.trt_trims)

		
		
		#self.layout().addWidget()

	
	def _setupSignals(self):
		"""Connect signals and slots"""

		# Bin/sequence loading mode
		self.model().sig_trt_changed.connect(self.update_summary)
		self.model().sig_sequence_selection_mode_changed.connect(self.sequenceSelectionModeChanged)	# Single sequence vs all sequences
		self.model().sig_sequence_selection_process_changed.connect(self.singleSequenceSelectionProcessChanged) # Single sequence selection filters

		# Data model has changed
		self.model().sig_data_changed.connect(self.update_control_buttons)

		self.model().sig_sequence_added.connect(self.sequenceAdded)
		self.model().sig_sequence_removed.connect(self.sequenceRemoved)

		# Data model bins have changed
		self.model().sig_bins_changed.connect(self.saveBins)

		self.model().sig_rate_changed.connect(self.saveRate)
		
		# Trim timecode changed
		self.model().sig_head_trim_tc_changed.connect(self.trimHeadTCChanged)
		self.model().sig_tail_trim_tc_changed.connect(self.trimTailTCChanged)
		self.model().sig_total_trim_tc_changed.connect(self.trimTotalTCChanged)

		# Trim marker presets have changed
		self.model().sig_marker_presets_model_changed.connect(self.trt_trims.set_marker_presets)
		self.model().sig_head_marker_preset_changed.connect(self.trimHeadMarkerChanged)
		self.model().sig_tail_marker_preset_changed.connect(self.trimTailMarkerChanged)

		# Swap between progress bar and bin mode selection depending on if the progress bar is active
		self.prog_loading.sig_progress_started.connect(lambda: self.stack_bin_loading.setCurrentWidget(self.prog_loading))
		self.prog_loading.sig_progress_completed.connect(lambda: self.stack_bin_loading.setCurrentWidget(self.bin_mode))
		self.bin_mode.sig_sequence_selection_mode_changed.connect(self.model().setSequenceSelectionMode)
		self.bin_mode.sig_sequence_selection_settings_requested.connect(self.showSequenceSelectionSettings)


		
		# Treeview requests for add/remove bins (drag and drop or selection delete)
		self.list_trts.sig_bins_dragged_dropped.connect(self.add_bins_from_paths)
		self.list_trts.sig_remove_rows_requested.connect(self.remove_bins)
		
		
		#self.list_trts.header().sectionResized.connect(self.saveFieldVisibility)
		self.list_trts.header().sectionMoved.connect(self.saveFieldVisibility)
		#self.list_trts.header().sortIndicatorChanged.connect(self.saveSorting) 
		#self.list_trts.sig_field_order_changed.connect(self.saveFieldOrder)
		self.list_trts.sig_sorting_changed.connect(self.saveSorting)

		# Hook in to the sort/filter model to update the LP timeline view
		self.list_trts.model().layoutChanged.connect(self.update_lp_layout)
		self.model().sig_data_changed.connect(self.update_lp_layout)
		#print(self.list_trts.model().data(0,1))
		
		# Top control buttons
		self.btn_add_bins.clicked.connect(self.choose_folder)
		self.btn_refresh_bins.clicked.connect(lambda: self.refresh_bins(self.list_trts.selectedRows()))
		self.btn_clear_bins.clicked.connect(lambda: self.remove_bins(self.list_trts.selectedRows()))

		# Trim timecode spinners
		self.trt_trims.sig_head_trim_changed.connect(self.model().setTrimFromHead)
		self.trt_trims.sig_tail_trim_changed.connect(self.model().setTrimFromTail)
		self.trt_trims.sig_total_trim_changed.connect(self.model().setTrimTotal)
		
		# Trim marker preset controls
		self.trt_trims.sig_head_trim_marker_preset_chosen.connect(self.model().set_active_head_marker_preset_name)
		self.trt_trims.sig_tail_trim_marker_preset_chosen.connect(self.model().set_active_tail_marker_preset_name)
		self.trt_trims.sig_marker_preset_editor_requested.connect(self.show_marker_maker_dialog)

		# Exports
		self.sig_export_requested.connect(self.exportData)
		
		# Total adjustment spinner
		#self.trim_total.sig_timecode_changed.connect(self.save_trims)
		#self.trim_total.sig_timecode_changed.connect(self.model().setTrimTotal)
	

	#
	# Sequence selection methods
	#

	@QtCore.Slot()
	def showSequenceSelectionSettings(self):

		wnd_sss = dlg_sequence_selection.TRTSequenceSelection(self)
		wnd_sss.setInitialSortProcess(self.model().sequenceSelectionProcess())
		wnd_sss.sig_process_chosen.connect(self.setSequenceSelectionProcess)
		wnd_sss.exec()
	
	def setSequenceSelectionProcess(self, process:model_trt.SingleSequenceSelectionProcess):
		"""Dialog was closed with changes -- tell the model"""
		self.model().setSequenceSelectionProcess(process)
	
	def singleSequenceSelectionProcessChanged(self, process:model_trt.SingleSequenceSelectionProcess):
		"""Model has changed the selection process"""

		self.settingsManager().setValue(TRTSettingsKeys.SEQ_SELECTION_COL_NAME, process.sortColumn())
		self.settingsManager().setValue(TRTSettingsKeys.SEQ_SELECTION_COL_DIRECTION, process.sortDirection().name)

		filter_settings = []
		for filter in process.filters():
			
			if isinstance(filter, model_trt.SingleSequenceSelectionProcess.NameContainsFilter):
				filter_settings.append({
					"kind": "name_contains",
					"string": filter.name()
				})
			elif isinstance(filter, model_trt.SingleSequenceSelectionProcess.ClipColorFilter):
				filter_settings.append({
					"kind": "clip_color",
					"colors": [tuple([color.rgba64().red(), color.rgba64().green(), color.rgba64().blue(), color.rgba64().alpha()]) for color in filter.colors()]
				})
			else:
				logging.getLogger(__name__).error("Unknown filter: %s", filter)

		self.settingsManager().setValue(TRTSettingsKeys.SEQ_SELECTION_FILTERS, filter_settings)
		

		# Prompt for reload
		if not self.model().sequence_count() or not self.model().sequenceSelectionMode() is model_trt.SequenceSelectionMode.ONE_SEQUENCE_PER_BIN:
			return
		
		if QtWidgets.QMessageBox.question(self,
			"Sequence Selection Settings Changed",
			"Would you like to reload the existing bins with these new settings?") == QtWidgets.QMessageBox.StandardButton.Yes:

			# Getting the selection count here so refresh_bins() doesn't prompt about a "refresh-all"
			self.refresh_bins(list(range(self.model().sequence_count())))
		


	#
	# Marker matching presets methods
	#

	@QtCore.Slot(str, markers_trt.LBMarkerPreset)
	def save_marker_preset(self, preset_name:str, marker_preset:markers_trt.LBMarkerPreset):
		presets = self.model().marker_presets()
		presets.update({preset_name: marker_preset})
		self.model().set_marker_presets(presets)
		
		self.settingsManager().setValue(TRTSettingsKeys.MARKER_PRESETS_LIST, self.model().marker_presets())

	
	@QtCore.Slot(str)
	def remove_marker_preset(self, preset_name:str):
		presets = self.model().marker_presets()
		presets.pop(preset_name, None)
		self.model().set_marker_presets(presets)

		self.settingsManager().setValue(TRTSettingsKeys.MARKER_PRESETS_LIST, self.model().marker_presets())
	
	@QtCore.Slot()
	def show_marker_maker_dialog(self) -> bool:
		wnd_marker = dlg_marker.TRTMarkerMaker(self)
		
		# Add valid marker colors
		for marker in markers_trt.LBMarkerIcons():
			wnd_marker.addMarkerColor(marker)

		# Set current marker presets
		wnd_marker.setMarkerPresets(self.model().marker_presets())
		wnd_marker.setActiveFFOAMarkerPresetName(self.model().activeHeadMarkerPresetName())
		wnd_marker.setActiveLFOAMarkerPresetName(self.model().activeTailMarkerPresetName())

		# Setup signals & slots
		self.model().sig_marker_presets_model_changed.connect(wnd_marker.setMarkerPresets)
		self.model().sig_head_marker_preset_changed.connect(wnd_marker.setActiveFFOAMarkerPresetName)
		self.model().sig_tail_marker_preset_changed.connect(wnd_marker.setActiveLFOAMarkerPresetName)
		
		wnd_marker.sig_save_preset.connect(self.save_marker_preset)
		wnd_marker.sig_delete_preset.connect(self.remove_marker_preset)

		wnd_marker.sig_set_as_ffoa.connect(self.model().set_active_head_marker_preset_name)
		wnd_marker.sig_set_as_lfoa.connect(self.model().set_active_tail_marker_preset_name)

		wnd_marker.finished.connect(self.marker_maker_dialog_closed)

		return bool(wnd_marker.exec())
	
	@QtCore.Slot()
	def marker_maker_dialog_closed(self):
		"""Marker preset editor was closed, clean up"""

		# Reset TRT combo boxes?
		self.trt_trims.set_head_marker_preset_name(self.model().activeHeadMarkerPresetName())
		self.trt_trims.set_tail_marker_preset_name(self.model().activeTailMarkerPresetName())

	#
	# Trim methods
	#
	
	@QtCore.Slot(str)
	def trimHeadMarkerChanged(self, preset_name:str):
		self.trt_trims.set_head_marker_preset_name(preset_name)
		self.updateSequenceInfo()
		self.settingsManager().setValue(TRTSettingsKeys.TRIM_HEAD_MARKER, preset_name)

	@QtCore.Slot(str)
	def trimTailMarkerChanged(self, preset_name:str):
		self.trt_trims.set_tail_marker_preset_name(preset_name)
		self.updateSequenceInfo()
		self.settingsManager().setValue(TRTSettingsKeys.TRIM_TAIL_MARKER, preset_name)

	@QtCore.Slot(int)
	def saveRate(self, rate:int):
		self.settingsManager().setValue(TRTSettingsKeys.LAST_RATE, rate)
	
	def trimHeadTCChanged(self, tc:Timecode):
		self.trt_trims.set_head_trim(tc)
		self.updateSequenceInfo()
		self.settingsManager().setValue(TRTSettingsKeys.TRIM_HEAD_DURATION, str(tc))

	def trimTailTCChanged(self, tc:Timecode):
		self.trt_trims.set_tail_trim(tc)
		self.updateSequenceInfo()
		self.settingsManager().setValue(TRTSettingsKeys.TRIM_TAIL_DURATION, str(tc))
	
	def trimTotalTCChanged(self, tc:Timecode):
		self.trt_trims.set_total_trim(tc)
		self.view_longplay.setTotalAdjust(tc.frame_number)
		self.settingsManager().setValue(TRTSettingsKeys.TRIM_TOTAL_DURATION, str(tc))

	#
	# Data model methods
	#

	def setModel(self, model:model_trt.TRTDataModel):
		self._data_model = model
		self._treeview_model.setDataModel(model)
	
	def model(self) -> model_trt.TRTDataModel:
		return self._data_model

	@QtCore.Slot(list)
	def saveBins(self, bin_paths:list[str]):
		settings = self.settingsManager()

		settings.setValue(TRTSettingsKeys.BINS_LIST, bin_paths)
	
	@QtCore.Slot(model_trt.TRTDataModel.CalculatedTimelineInfo)
	def sequenceAdded(self, sequence_info: model_trt.TRTDataModel.CalculatedTimelineInfo):
		"""Model reports that a sequence has been added"""

		view_item = self.model().item_to_dict(sequence_info)
		self._treeview_model.addSequenceInfo(view_item)
		self.list_trts.fit_headers()
	
	@QtCore.Slot(int)
	def sequenceRemoved(self, idx:int):
		self._treeview_model.removeSequenceInfo(idx)

		# NOTE: I also have this in the treeview's `rowsRemoved` slot, but it doesn't seem to be called...
		if not self.model().sequence_count():
			self.list_trts.setStatus(self.list_trts.TRTTreeViewDisplayStatus.EMPTY)
	
	def add_bins_from_paths(self, paths:list[str]):
		"""Load in sequences from a list of Avid bin file paths"""
		if not paths:
			return 
		
		# Update Treeview status
		self.list_trts.beginLoadingSequences()
		
		last_bin = paths[-1] if paths else []

		thread = TRTThreadedMulticoreAbomination(paths)
		thread.signals().sig_got_bin_info.connect(self.model().add_timelines_from_bin)
		thread.signals().sig_got_bin_info.connect(self.prog_loading.step_complete)
		thread.signals().sig_had_error.connect(self.prog_loading.step_complete)
		thread.signals().sig_complete.connect(self.bin_loading_complete)

		for _ in range(len(paths)):
			self.prog_loading.step_added()
		
		self._pool.start(thread)

		# Save last bin path if it's a good 'un
		if last_bin:
			self.settingsManager().setValue(TRTSettingsKeys.LAST_BIN, last_bin)
	
	@QtCore.Slot(bool)
	def bin_loading_complete(self, had_errors:bool):
		"""Done loading bins"""

		self.list_trts.doneLoadingSequences()
		
		# TEST
		#self.formatSequenceInfoAsJSON()
	
	def updateSequenceInfo(self):

		for idx, bin_info in enumerate(self._data_model.data()):
			view_item = self.model().item_to_dict(bin_info)
			self._treeview_model.updateSequenceInfo(idx, view_item)
	
	@QtCore.Slot(list)
	def refresh_bins(self, selected:list[int]):
		
		if not selected and not QtWidgets.QMessageBox.warning(self,
			"Reloading All Bins",
			"This will clear all of the existing sequences and reload their bins.  Are you sure?",
			QtWidgets.QMessageBox.StandardButton.Ok, QtWidgets.QMessageBox.StandardButton.Cancel) == QtWidgets.QMessageBox.StandardButton.Ok:

			return
		
		selected = selected or list(range(self.model().sequence_count()))

		# Gather bin paths based on selection
		bin_paths = set()
		data = self.model().data()
		for idx in selected:
			bin_paths.add(data[idx].binFilePath().absoluteFilePath())
		
		# Add any others that have the same bin paths
		reload_indexes = []
		for idx, timeline_info in enumerate(data):
			if timeline_info.binFilePath().absoluteFilePath() in bin_paths:
				reload_indexes.append(idx)
		
		# Remove existing
		self.remove_bins(reload_indexes)

		# Add the bin paths again
		self.add_bins_from_paths(list(bin_paths))

	@QtCore.Slot(list)
	def remove_bins(self, selected:list[int]):

		selected.sort(reverse=True)

		# Remove selection
		if selected:
			[self.model().remove_sequence(idx) for idx in selected]

		# Or remove everything if nothing is selected
		elif QtWidgets.QMessageBox.warning(self,
			"Clearing Current Sequences",
			"This will clear the existing sequences.  Are you sure?",
			QtWidgets.QMessageBox.StandardButton.Ok, QtWidgets.QMessageBox.StandardButton.Cancel) == QtWidgets.QMessageBox.StandardButton.Ok:

			self.model().clear()

	#
	# Treeview show/hide columns
	#

	@QtCore.Slot(QtCore.QPoint)
	def showColumnChooserContextMenu(self, pos:QtCore.QPoint):
		"""Show the menu"""
		
		idx_logical_heading = self.list_trts.header().logicalIndexAt(pos)
		field = self._treeview_model.headers()[idx_logical_heading]
		title = field.name()
		section = field.field()

		title = self.list_trts.model().headerData(idx_logical_heading, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole)
		section = self.list_trts.model().headerData(idx_logical_heading, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

		logging.getLogger(__name__).debug("Right click on %s at %s", section, pos)


		menu = QtWidgets.QMenu(self.list_trts.header())

		visible_columns = self.list_trts.fieldOrder(include_hidden=False)

		action_showchooser = QtGui.QAction("Choose visible columns...")
		action_showchooser.triggered.connect(self.showColumnChooserWindow)
		
		logging.getLogger(__name__).debug("Got %i columns", len(visible_columns))

		if not field.isFrozenHeader() and len(visible_columns) > 1:
			action_hidecol = QtGui.QAction(f"Hide {title}")
			action_hidecol.triggered.connect(lambda: self.setFieldHidden(field, True))
			menu.addAction(action_hidecol)
			menu.addSeparator()

		menu.addAction(action_showchooser)
		menu.exec(menu.parent().mapToGlobal(pos))
	
	def showColumnChooserWindow(self, *args):
		wnd_choosecolumns = dlg_choose_columns.TRTChooseColumnsDialog(self.list_trts)
		
		for idx in range(self._treeview_model.columnCount()):
			header = self._treeview_model.headers()[idx]
			wnd_choosecolumns.addColumn(header, is_hidden=self.list_trts.isColumnHidden(idx))
		wnd_choosecolumns.sig_columns_chosen.connect(self.processColumnChooserSelection)
		wnd_choosecolumns.exec()

	@QtCore.Slot(wdg_sequence_treeview.TRTTreeViewHeaderItem, bool)
	def setFieldHidden(self, field:wdg_sequence_treeview.TRTTreeViewHeaderItem, is_hidden:bool=True):
		"""Given a field object, hide it from view"""

		# All fields, in logical order
		all_fields = self.list_trts.model().headers()
		idx_logical_field = [f.field() for f in all_fields].index(field.field())
		
		self.list_trts.setColumnHidden(idx_logical_field, is_hidden)
		self.saveFieldVisibility()
		
	
	@QtCore.Slot(list) 
	def processColumnChooserSelection(self, idx_visible:list[int]):
		"""Columns hidden/shown were chosen"""

		idx_visible = [int(x) for x in list(idx_visible)]

		for idx in range(self._treeview_model.columnCount()):
			self.list_trts.setColumnHidden(idx, idx not in idx_visible)
			self.list_trts.resizeColumnToContents(idx)
		
		self.saveFieldVisibility()

	@QtCore.Slot(list)
	def setFieldVisibility(self, field_order:list[str], fields_hidden:list[str]):
		"""Set the field order"""

		current_field_order:list[str] = []

		# First build a list of the current fields in visual position
		for vis_idx in range(self._treeview_model.columnCount()):
			logical_idx = self.list_trts.header().logicalIndex(vis_idx)
			current_field_order.append(self._treeview_model.headers()[logical_idx].field())
		
		# Move backwards through desired field order, move that field to the front
		for field in field_order[::-1]:

			# Skip any unknown/old fields
			if field not in current_field_order:
				continue
			
			# Move column to front and update our little inner model
			idx_curr = current_field_order.index(field)
			self.list_trts.header().moveSection(idx_curr, 0)
			current_field_order.insert(0, current_field_order.pop(idx_curr))

			# Set visibility
			self.list_trts.setColumnHidden(self.list_trts.header().logicalIndex(0), field in fields_hidden)
	
	@QtCore.Slot(list)
	def saveFieldVisibility(self):
		"""Save the field order and visibility of the Sequence TreeView"""

		fields_order: list[str] = []
		fields_hidden:list[str] = []
		
		for vis_idx in range(self._treeview_model.columnCount()):

			# Get the field name at visual index
			logical_idx = self.list_trts.header().logicalIndex(vis_idx)
			header_field = self._treeview_model.headers()[logical_idx].field()
			
			# Save its position
			fields_order.append(header_field)
			
			# Save its visibility
			if self.list_trts.isColumnHidden(logical_idx):
				fields_hidden.append(header_field)
		
		self.settingsManager().setValue(TRTSettingsKeys.LIST_FIELDS_ORDER,  fields_order)
		self.settingsManager().setValue(TRTSettingsKeys.LIST_FIELDS_HIDDEN, fields_hidden)
	
	def choose_folder(self):
		last_bin_path = self.settingsManager().value(TRTSettingsKeys.LAST_BIN)
		files,_ = QtWidgets.QFileDialog.getOpenFileNames(caption="Choose Avid bins for calcuation...", dir=last_bin_path, filter="Avid Bins (*.avb);;All Files (*)")
		
		if not files:
			return
		
		self.add_bins_from_paths(files)
	
	@QtCore.Slot(str, QtCore.Qt.SortOrder)
	def saveSorting(self, sort_field:str, sort_order:QtCore.Qt.SortOrder):
		self.settingsManager().setValue(TRTSettingsKeys.LIST_SORT_FIELD, sort_field)
		self.settingsManager().setValue(TRTSettingsKeys.LIST_SORT_DIRECTION, sort_order.name)
	
	@QtCore.Slot(str, QtCore.Qt.SortOrder)
	def setSorting(self, sort_field:str, sort_order:QtCore.Qt.SortOrder):
		self.list_trts.setSorting(sort_field, sort_order)

	@QtCore.Slot(Timecode)
	def update_summary(self):
		self.trt_summary.add_stat_item(wdg_stats.TRTStatItem(label="Locked", value=self.model().locked_bin_count()))
		self.trt_summary.add_stat_item(wdg_stats.TRTStatItem(label="Sequences", value=self.model().sequence_count()))
		self.trt_summary.add_stat_item(wdg_stats.TRTStatItem(label="Total Running Length", value=self.model().total_lfoa()))
		self.trt_summary.add_stat_item(wdg_stats.TRTStatItem(label="Total Running Time",  value=self.model().total_runtime()))

		### Ascending order: Use QtCore.SortOrder
	
	@QtCore.Slot()
	def update_control_buttons(self):
		enabled = bool(list(self.model().data()))
		self.btn_clear_bins.setEnabled(enabled)
		self.btn_refresh_bins.setEnabled(enabled)
	
	@QtCore.Slot(model_trt.SequenceSelectionMode)
	def sequenceSelectionModeChanged(self, mode:model_trt.SequenceSelectionMode):
		
		self.bin_mode.setSequenceSelectionMode(mode)
		self.settingsManager().setValue(TRTSettingsKeys.SEQ_SELECTION_MODE, mode.value)

		if not self.model().sequence_count():
			return

		if QtWidgets.QMessageBox.question(self,
			"Sequence Selection Settings Changed",
			"Would you like to reload the existing bins with these new settings?") == QtWidgets.QMessageBox.StandardButton.Yes:

			self.refresh_bins(list(range(self.model().sequence_count())))

	@QtCore.Slot()
	def update_lp_layout(self):
		"""Update the LP view to reflect current sequences in QTreeView order"""

		timeline_infos = self.sortedCalculatedTimelineInfo()
		unsorted_durs = [(t.timelineName(), t.timelineTimecodeTrimmed().duration.frame_number) for t in timeline_infos]
		self.view_longplay.setItems(unsorted_durs)

	#
	# Exporters
	#

	@QtCore.Slot()
	def promptForExport(self):
		"""Prompt user for data export settings"""

		formats = {
			"tsv" : "Tab Separated Values",
			"csv" : "Comma Separated Values",
			"json": "JSON Data",
		}

		available_filters = ";;".join([
			f"{desc} (*.{ext})" for ext, desc in formats.items()
		])

		last_export_path = QtCore.QFileInfo(self.settingsManager().value(TRTSettingsKeys.LAST_EXPORT, "."))
		path_file, filter = QtWidgets.QFileDialog.getSaveFileName(
			caption="Export data as...", 
			dir=last_export_path.filePath(),
			filter=available_filters
		)

		# Nevermind
		if not path_file:
			return
		
		# If user specified a known suffix in the filename, go with it
#		print("Got ", QtCore.QFileInfo(path_file).suffix())
		if QtCore.QFileInfo(path_file).suffix().lower() in formats.keys():
			self.sig_export_requested.emit(path_file, QtCore.QFileInfo(path_file).suffix())
			return

		# If they're doing something silly, check which filter they selected
		for format_suffix in formats:
			if format_suffix in filter:
				self.sig_export_requested.emit(path_file, format_suffix)
				return

	@QtCore.Slot(str,str)
	def exportData(self, path_file:str, file_format:str):
		
		try:
			if file_format in ["tsv","csv"]:
				exporters_trt.export_delimited(self.list_trts.model(), path_file, file_format)
			if file_format == "json":
				exporters_trt.export_json(self.formatSequenceInfoAsJSON(), path_file)
		except Exception as e:
			logging.getLogger(__name__).error("Problem exporting %s: %s:", file_format, e)
		else:
			self.settingsManager().setValue(TRTSettingsKeys.LAST_EXPORT, path_file)
	
	@QtCore.Slot()
	def historyViewerRequsted(self):

		path_db = QtCore.QDir(QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.AppDataLocation)).filePath("trt_db.db")
		QtCore.QDir().mkpath(QtCore.QFileInfo(path_db).absolutePath())
		
		if not QtCore.QDir().exists(QtCore.QFileInfo(path_db).absolutePath()):
			logging.getLogger(__name__).error("Didn't make the path to DB: %s", QtCore.QFileInfo(path_db).absolutePath())

		db = QtSql.QSqlDatabase.addDatabase("QSQLITE", "trt")
		db.setDatabaseName(QtCore.QFileInfo(path_db).absoluteFilePath())
		db.open()

		if not db.open():
			logging.getLogger(__name__).error("Couldn't open database at %s: %s", path_db, db.lastError().text())
		
		
		self.wnd_history = hist_main.TRTHistoryViewer(db, parent=self)
		
		# Set "Current" card to use the same sorted view as our main list_trts
		self.wnd_history.setLiveModel(self.list_trts.model()) # "Current" as in "Current Sequences in main Program"
		
		# Keep er real up to date real nice.  Keep er fed.  Real nice.
		self.wnd_history.setLiveRuntime(self.model().total_runtime())
		self.model().sig_trt_changed.connect(self.wnd_history.setLiveRuntime)

		self.wnd_history.setLiveTotalAdjustment(self.model().trimTotal())
		self.model().sig_total_trim_tc_changed.connect(self.wnd_history.setLiveTotalAdjustment)

		self.wnd_history.setLiveRate(self.model().rate())
		self.model().sig_rate_changed.connect(self.wnd_history.setLiveRate)
		
		# Just really try to delete this thing
		self.wnd_history.sig_is_closing.connect(self.wnd_history.deleteLater)
		
		self.wnd_history.show()

	def sortedCalculatedTimelineInfo(self) -> list[model_trt.TRTDataModel.CalculatedTimelineInfo]:
		"""Get calculated timeline info sorted by the `QTreeView`"""

		sorted_timeline_info:list[model_trt.TRTDataModel.CalculatedTimelineInfo] = []

		# From QTreeView rows, resolve the index for the original model
		for rownum in range(self.list_trts.model().rowCount()):
			src_row_num = self.list_trts.model().mapToSource(
				self.list_trts.model().index(rownum, 0, QtCore.QModelIndex())
			).row()
			sorted_timeline_info.append(self.model().data()[src_row_num])
		
		return sorted_timeline_info
			
	
	def formatSequenceInfoAsJSON(self) -> dict:
		"""TEST: Notes for pulling data"""

		# Get header order (and if they're displayed or not)
		
		# NOTE: Not returned in order, I don't think.  Should.
		headers_visible = self.list_trts.model().headers()
		headers_all     = self.list_trts.model().sourceModel().headers()
		headers_hidden  = [h for h in headers_all if h not in headers_visible]

		# Get index order and map to OG index for proper display order of original data
		sorted_timeline_info = self.sortedCalculatedTimelineInfo()
		
		gen_time = QtCore.QDateTime.currentDateTime()

		json_formatted = {
			"schema_version": 1,
			"total_runtime_tc": {
				"type":"timecode",
				"frames": self.model().total_runtime().frame_number,
				"rate": self.model().total_runtime().rate,
				"formatted": str(self.model().total_runtime()),
			},
			"total_runtime_ff": {
				"type": "feet_frames",
				"format": "35mm",
				"perfs": 4,
				"frames": self.model().total_runtime().frame_number,
				"formatted": self.model().total_lfoa()
			},
			"total_adjustment_tc": {
				"type": "timecode",
				"frames": self.model().trimTotal().frame_number,
				"rate": self.model().trimTotal().rate,
				"formatted": str(self.model().trimTotal())
			},
			"total_adjustment_ff": {
				"type": "feet_frames",
				"format": "35mm",
				"perfs": 4,
				"frames": self.model().trimTotal().frame_number,
				"formatted": self.model().trimTotalFF()
			},
			"datetime_output": {
				"type": "datetime",
				"timestamp": gen_time.toSecsSinceEpoch(),
				"formatted": gen_time.toLocalTime().toString("dd MMM yyyy hh:mm:ss AP")
			}
		}

		json_sequences:list[dict] = []

		for timeline_info in [self.model().item_to_dict(t) for t in sorted_timeline_info]:

			sequence_json = dict()
			for header in headers_all:
				sequence_json[header.field()] = timeline_info.get(header.field()).to_json()
			json_sequences.append(sequence_json)
		
		json_formatted["sequence_count"] = len(json_sequences)
		json_formatted["sequences"] = json_sequences

		return json_formatted