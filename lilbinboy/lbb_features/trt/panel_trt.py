import dataclasses, pathlib, re
from PySide6 import QtWidgets, QtGui, QtCore
from timecode import Timecode
from concurrent import futures
from ...lbb_common import LBUtilityTab, LBSpinBoxTC, LBTimelineView
from . import dlg_choose_columns, dlg_marker, logic_trt, model_trt, treeview_trt, markers_trt, trims_trt, dlg_sequence_selection, dlg_choose_columns, exporters_trt

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
	
	def __init__(self, bin_paths:list[str]):
		super().__init__()
		self._bin_paths = bin_paths
		self._signals = self.TRTThreadedSignals()
	
	def signals(self) -> TRTThreadedSignals:
		return self._signals
	
	def run(self):
		with futures.ProcessPoolExecutor(max_workers=6) as executor:
			bin_futures = {executor.submit(logic_trt.get_timelines_from_bin, bin_path) : bin_path for bin_path in self._bin_paths}
			for bin_future in futures.as_completed(bin_futures):
				try:
					timeline_info_list = bin_future.result()
					self.signals().sig_got_bin_info.emit(timeline_info_list)
				except Exception as e:
					print("Didn't load " + bin_futures[bin_future] + ": " + str(e))
					self.signals().sig_had_error.emit(bin_futures[bin_future], e)


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

@dataclasses.dataclass(frozen=True)
class TRTSummaryItem():
	"""Item to display in a `TRTSummary` bar"""

	label:str
	"""The label for this item"""

	value:str
	"""The value of this item"""

class TRTModeSelection(QtWidgets.QGroupBox):
	"""Select how sequences are chosen from bins"""

	sig_sequence_selection_mode_changed = QtCore.Signal(model_trt.SequenceSelectionMode)
	sig_sequence_selection_settings_requested = QtCore.Signal()

	def __init__(self):

		super().__init__()

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
		self.layout().addWidget(self._btn_one_sequence_config)

		self.layout().addStretch()

		self._rdo_all_sequence.setText("All Sequences In Bin")
		self.layout().addWidget(self._rdo_all_sequence)

		self.layout().addStretch()

		self._btn_group.buttonClicked.connect(self.selectionChanged)
		self._btn_one_sequence_config.clicked.connect(self.sig_sequence_selection_settings_requested)
	
	@QtCore.Slot(QtWidgets.QAbstractButton)
	def selectionChanged(self, button:QtWidgets.QAbstractButton):

		if button == self._rdo_one_sequence:
			self.sig_sequence_selection_mode_changed.emit(model_trt.SequenceSelectionMode.ONE_SEQUENCE_PER_BIN)
		elif button == self._rdo_all_sequence:
			self.sig_sequence_selection_mode_changed.emit(model_trt.SequenceSelectionMode.ALL_SEQUENCES_PER_BIN)
		else:
			print("Weird selection mode")
	
	@QtCore.Slot(model_trt.SequenceSelectionMode)
	def setSequenceSelectionMode(self, mode:model_trt.SequenceSelectionMode):

		print("Setting to ", mode)
		
		if mode is model_trt.SequenceSelectionMode.ONE_SEQUENCE_PER_BIN:
			self._rdo_one_sequence.setChecked(True)
		elif mode is model_trt.SequenceSelectionMode.ALL_SEQUENCES_PER_BIN:
			self._rdo_all_sequence.setChecked(True)

class TRTSummary(QtWidgets.QWidget):

	_fnt_label = QtGui.QFont()
	_fnt_value = QtGui.QFont()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._summary_items = dict()

		self.__class__._fnt_label.setCapitalization(QtGui.QFont.Capitalization.AllUppercase)
		self.__class__._fnt_label.setPointSizeF(8)

		self.__class__._fnt_value.setBold(True)
		self.__class__._fnt_value.setPointSizeF(18)

		self.setLayout(QtWidgets.QGridLayout())
		self.layout().setHorizontalSpacing(24)

		self._add_initial_summary_items()

	def _add_initial_summary_items(self):
			"""Initial info for now"""

			self.add_summary_item(TRTSummaryItem(
				label="Sequences",
				value="0"
			))

			self.add_summary_item(TRTSummaryItem(
				label="Locked",
				value="0"
			))

			self.add_summary_item(TRTSummaryItem(
				label="FPS",
				value="24"
			))

			self.layout().addItem(QtWidgets.QSpacerItem(1,1, QtWidgets.QSizePolicy.Policy.MinimumExpanding), 1, self.layout().columnCount())

			self.add_summary_item(TRTSummaryItem(
				label="Total Running Length",
				value="0+00"
			))

			self.add_summary_item(TRTSummaryItem(
				label="Total Running Time",
				value="00:00:00:00"
			))
	
	def add_summary_item(self, item:TRTSummaryItem):

		if str(item.label) in self._summary_items:
			label, value = self._summary_items[str(item.label)]
			value.setText(str(item.value))
		
		else:
			
			lbl_value = QtWidgets.QLabel(str(item.value))
			lbl_value.setFont(self.__class__._fnt_value)
			lbl_value.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
			lbl_value.setTextInteractionFlags(QtGui.Qt.TextInteractionFlag.TextSelectableByMouse|QtGui.Qt.TextInteractionFlag.TextSelectableByKeyboard)

			lbl_label = QtWidgets.QLabel(str(item.label))
			lbl_label.setFont(self.__class__._fnt_label)
			lbl_label.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
			lbl_label.setBuddy(lbl_value)

			self._summary_items.update({
				str(item.label): (lbl_label, lbl_value)
			})
			
			self.layout().addWidget(lbl_value, 0, self.layout().columnCount())
			self.layout().addWidget(lbl_label, 1, self.layout().columnCount()-1)


class LBTRTCalculator(LBUtilityTab):
	"""TRT Calculator"""

	PATH_ICON = __file__+"../../../../res/icon_trt.png"

	sig_modelchanged = QtCore.Signal()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


		self.setLayout(QtWidgets.QVBoxLayout())

		self._pool = QtCore.QThreadPool()

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
		self.list_trts = treeview_trt.TRTTreeView()
		self.trt_summary = TRTSummary()

		# Longplay Layout
		self.view_longplay = LBTimelineView()

		# Declare trims
		self.trt_trims = trims_trt.TRTControlsTrims()
		self.trim_total = LBSpinBoxTC()



		self._setupSignals()
		self._setupWidgets()
		self._loadInitial()




	def _loadInitial(self):
		"""Load initial data from preferences (or defaults)"""
		
		self.model().setRate(int(QtCore.QSettings().value("trt/rate", 24)))

		self.model().setSequenceSelectionMode(QtCore.QSettings().value("trt/sequence_selection_mode", model_trt.SequenceSelectionMode.ONE_SEQUENCE_PER_BIN))
		
		self.model().set_marker_presets(QtCore.QSettings().value("lbb/marker_presets", dict()))

		self.model().setTrimFromHead(Timecode(QtCore.QSettings().value("trt/trim_head",0), rate=self.model().rate()))
		self.model().setTrimFromTail(Timecode(QtCore.QSettings().value("trt/trim_tail",0), rate=self.model().rate()))
		self.model().setTrimTotal(Timecode(QtCore.QSettings().value("trt/trim_total",0), rate=self.model().rate()))
		
		self.model().set_active_head_marker_preset_name(QtCore.QSettings().value("trt/trim_marker_preset_head"))
		self.model().set_active_tail_marker_preset_name(QtCore.QSettings().value("trt/trim_marker_preset_tail"))

		self.setColumnsHidden(QtCore.QSettings().value("trt/columns_hidden", []))
		
		self.add_bins_from_paths(QtCore.QSettings().value("trt/bin_paths",[]))

	def _setupWidgets(self):
		"""Setup the widgets and add them to the layout"""

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

		grp_summaries = QtWidgets.QGroupBox()
		grp_summaries.setLayout(QtWidgets.QVBoxLayout())
		grp_summaries.layout().setContentsMargins(0,0,0,0)
		grp_summaries.layout().addWidget(self.trt_summary)

		self.layout().addWidget(grp_summaries)


		
		# Set up sequence trim controls
		self.layout().addWidget(self.trt_trims)

		self.layout().addWidget(QtWidgets.QPushButton("Export TSV", clicked=self.export_tsv))

	
	def _setupSignals(self):
		"""Connect signals and slots"""

		# Bin/sequence loading mode
		self.model().sig_data_changed.connect(self.update_summary)
		self.model().sig_sequence_selection_mode_changed.connect(self.sequenceSelectionModeChanged)

		# Data model has changed
		self.model().sig_data_changed.connect(self.update_control_buttons)

		self.model().sig_sequence_added.connect(self.sequenceAdded)
		self.model().sig_sequence_removed.connect(self.sequenceRemoved)

		# Data model bins have changed
		self.model().sig_bins_changed.connect(self.save_bins)

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

		# Hook in to the sort/filter model to update the LP timeline view
		self.list_trts.model().layoutChanged.connect(self.update_lp_layout)
		self.model().sig_data_changed.connect(self.update_lp_layout)
		#print(self.list_trts.model().data(0,1))
		
		# Top control buttons
		self.btn_add_bins.clicked.connect(self.choose_folder)
		self.btn_refresh_bins.clicked.connect(self.refresh_bins)
		self.btn_clear_bins.clicked.connect(lambda: self.remove_bins(self.list_trts.selectedRows()))

		# Trim timecode spinners
		self.trt_trims.sig_head_trim_changed.connect(self.model().setTrimFromHead)
		self.trt_trims.sig_tail_trim_changed.connect(self.model().setTrimFromTail)
		self.trt_trims.sig_total_trim_changed.connect(self.model().setTrimTotal)
		
		# Trim marker preset controls
		self.trt_trims.sig_head_trim_marker_preset_chosen.connect(self.model().set_active_head_marker_preset_name)
		self.trt_trims.sig_tail_trim_marker_preset_chosen.connect(self.model().set_active_tail_marker_preset_name)
		self.trt_trims.sig_marker_preset_editor_requested.connect(self.show_marker_maker_dialog)
		
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
		self.model().setSequenceSelectionProcess(process)

	#
	# Marker matching presets methods
	#

	@QtCore.Slot(str, markers_trt.LBMarkerPreset)
	def save_marker_preset(self, preset_name:str, marker_preset:markers_trt.LBMarkerPreset):
		presets = self.model().marker_presets()
		presets.update({preset_name: marker_preset})
		self.model().set_marker_presets(presets)
		
		QtCore.QSettings().setValue("lbb/marker_presets", self.model().marker_presets())

	
	@QtCore.Slot(str)
	def remove_marker_preset(self, preset_name:str):
		presets = self.model().marker_presets()
		presets.pop(preset_name, None)
		self.model().set_marker_presets(presets)

		QtCore.QSettings().setValue("lbb/marker_presets", self.model().marker_presets())
	
	@QtCore.Slot()
	def show_marker_maker_dialog(self) -> bool:
		wnd_marker = dlg_marker.TRTMarkerMaker(self)
		
		# Add valid marker colors
		for marker in markers_trt.LBMarkerIcons():
			wnd_marker.addMarkerColor(marker)

		# Set current marker presets
		wnd_marker.setMarkerPresets(self.model().marker_presets())

		# Setup signals & slots
		self.model().sig_marker_presets_model_changed.connect(wnd_marker.setMarkerPresets)
		
		wnd_marker.sig_save_preset.connect(self.save_marker_preset)
		wnd_marker.sig_delete_preset.connect(self.remove_marker_preset)
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
		QtCore.QSettings().setValue("trt/trim_marker_preset_head", preset_name)

	@QtCore.Slot(str)
	def trimTailMarkerChanged(self, preset_name:str):
		self.trt_trims.set_tail_marker_preset_name(preset_name)
		self.updateSequenceInfo()
		QtCore.QSettings().setValue("trt/trim_marker_preset_tail", preset_name)

	@QtCore.Slot(int)
	def saveRate(self, rate:int):
		QtCore.QSettings().setValue("trt/rate", rate)
	
	def trimHeadTCChanged(self, tc:Timecode):
		self.trt_trims.set_head_trim(tc)
		self.updateSequenceInfo()
		QtCore.QSettings().setValue("trt/trim_head", str(tc))

	def trimTailTCChanged(self, tc:Timecode):
		self.trt_trims.set_tail_trim(tc)
		self.updateSequenceInfo()
		QtCore.QSettings().setValue("trt/trim_tail", str(tc))
	
	def trimTotalTCChanged(self, tc:Timecode):
		self.trt_trims.set_total_trim(tc)
		self.view_longplay.setTotalAdjust(tc.frame_number)
		QtCore.QSettings().setValue("trt/trim_total", str(tc))

		# TODO: Misplaced this little guy?
	#
	# Data model methods
	#

	def setModel(self, model:model_trt.TRTDataModel):
		self._data_model = model
		self._treeview_model.setDataModel(model)
	
	def model(self) -> model_trt.TRTDataModel:
		return self._data_model

	def save_bins(self):
		settings = QtCore.QSettings()

		unique_bin_paths = list(set([QtCore.QFileInfo(timeline.bin_path).absoluteFilePath() for timeline in self.model().data()]))

		settings.setValue("trt/bin_paths", unique_bin_paths)
	
	@QtCore.Slot(logic_trt.TimelineInfo)
	def sequenceAdded(self, bin_info: logic_trt.TimelineInfo):
		"""Model reports that a sequence has been added"""

		view_item = self.model().item_to_dict(bin_info)
		self._treeview_model.addSequenceInfo(view_item)
		self.list_trts.fit_headers()
	
	@QtCore.Slot(int)
	def sequenceRemoved(self, idx:int):
		self._treeview_model.removeSequenceInfo(idx)
	
	def add_bins_from_paths(self, paths:list[str]):

		
		last_bin = paths[-1] if paths else []

		thread = TRTThreadedMulticoreAbomination(paths)
		thread.signals().sig_got_bin_info.connect(self.model().add_timelines_from_bin)
		thread.signals().sig_got_bin_info.connect(self.prog_loading.step_complete)
		thread.signals().sig_had_error.connect(self.prog_loading.step_complete)

		for _ in range(len(paths)):
			self.prog_loading.step_added()
		
		self._pool.start(thread)

		# Save last bin path if it's a good 'un
		if last_bin:
			QtCore.QSettings().setValue("trt/last_bin", last_bin)
	
	def updateSequenceInfo(self):

		for idx, bin_info in enumerate(self._data_model.data()):
			view_item = self.model().item_to_dict(bin_info)
			self._treeview_model.updateSequenceInfo(idx, view_item)
	
	def refresh_bins(self):
		pass

	def remove_bins(self, selected:list[int]):

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

		menu = QtWidgets.QMenu(self.list_trts.header())
		action_showchooser = QtGui.QAction("Choose visible columns...")
		action_showchooser.triggered.connect(self.showColumnChooserWindow)
		menu.addAction(action_showchooser)
		menu.exec(menu.parent().mapToGlobal(pos))
	
	def showColumnChooserWindow(self, *args):
		wnd_choosecolumns = dlg_choose_columns.TRTChooseColumnsDialog(self.list_trts)
		
		for idx, header in enumerate(self._treeview_model.headers()):
			wnd_choosecolumns.addColumn(header, is_hidden=not self.list_trts.model().filterAcceptsColumn(idx, QtCore.QModelIndex()))
		wnd_choosecolumns.sig_columns_chosen.connect(self.processColumnChooserSelection)
		wnd_choosecolumns.exec()
	
	@QtCore.Slot(list)
	def processColumnChooserSelection(self, idx_visible:list[int]):
		"""Columns hidden/shown were chosen"""

		# Boy this is really backwards, but basically,
		# Getting SELECTED column indexes, and then taking
		# the field names of the inverse of that
		# Note to self: Sorry, self.

		# Somtimes the indexes come in as strings ugh
		idx_visible = [int(x) for x in list(idx_visible)]
		
		fields_hidden = []

		for idx, header in enumerate(self._treeview_model.headers()):
			if idx not in idx_visible:
				fields_hidden.append(header.field())
		
		self.setColumnsHidden(fields_hidden)
		
	
	@QtCore.Slot(list)
	def setColumnsHidden(self, fields:list[str]):
		"""Set hidden columns in proxy view, by field name"""
		self.list_trts.model().setHiddenFields(fields)
		QtCore.QSettings().setValue("trt/columns_hidden", fields)
	
	def choose_folder(self):
		last_bin_path = QtCore.QSettings().value("trt/last_bin")
		files,_ = QtWidgets.QFileDialog.getOpenFileNames(caption="Choose Avid bins for calcuation...", dir=last_bin_path, filter="Avid Bins (*.avb);;All Files (*)")
		
		if not files:
			return
		
		self.add_bins_from_paths(files)

	@QtCore.Slot()
	def update_summary(self):
		self.trt_summary.add_summary_item(TRTSummaryItem(label="Locked", value=self.model().locked_bin_count()))
		self.trt_summary.add_summary_item(TRTSummaryItem(label="Sequences", value=self.model().sequence_count()))
		self.trt_summary.add_summary_item(TRTSummaryItem(label="Total Running Length", value=self.model().total_lfoa()))
		self.trt_summary.add_summary_item(TRTSummaryItem(label="Total Running Time",  value=self.model().total_runtime()))
	
	@QtCore.Slot()
	def update_control_buttons(self):
		enabled = bool(list(self.model().data()))
		self.btn_clear_bins.setEnabled(enabled)
		self.btn_refresh_bins.setEnabled(enabled)
	
	@QtCore.Slot(model_trt.SequenceSelectionMode)
	def sequenceSelectionModeChanged(self, mode:model_trt.SequenceSelectionMode):
		self.bin_mode.setSequenceSelectionMode(mode)
		QtCore.QSettings().setValue("trt/sequence_selection_mode", mode)

	@QtCore.Slot()
	def update_lp_layout(self):
		
		unsorted_durs:list[tuple[str,int]] = []

		for row_idx in range(self.list_trts.model().rowCount()):
			
			# NOTE on the try:
			# Need to test this further -- at one point I messed this up
			try:
				prx_index = self.list_trts.model().index(row_idx, 0, QtCore.QModelIndex())
				main_index = self.list_trts.model().mapToSource(prx_index)

				mapped_idx = main_index.row()

				bin_info = self.model().data()[mapped_idx]
				bin_dict = self.model().item_to_dict(bin_info)
				unsorted_durs.append((bin_dict.get("sequence_name").data(QtCore.Qt.ItemDataRole.UserRole), bin_dict.get("duration_trimmed").data(QtCore.Qt.ItemDataRole.UserRole).frame_number))
			except Exception as e:
				print(f"Proxy out of sync with data ({self.list_trts.model().rowCount()} vs {len(self._data_model.data())})")
		
		self.view_longplay.setItems(unsorted_durs)

	#
	# Exporters
	#
	def export_tsv(self):

		exporters_trt.export_tab_delimited(self.list_trts.model(), "out.tsv")