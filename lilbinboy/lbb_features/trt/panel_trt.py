import dataclasses, pathlib, re
from PySide6 import QtWidgets, QtGui, QtCore
from timecode import Timecode
from ...lbb_common import LBUtilityTab, LBSpinBoxTC
from . import dlg_marker, logic_trt, model_trt, treeview_trt, markers_trt, trims_trt

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


class TRTThreadedBinGetter(QtCore.QRunnable):

	class TRTThreadedSignals(QtCore.QObject):
		sig_got_bin_info = QtCore.Signal(logic_trt.BinInfo)

	def __init__(self, bin_path:str):
		super().__init__()
		self._bin_path = bin_path
		self._signals = self.TRTThreadedSignals()

	def signals(self) -> TRTThreadedSignals:
		return self._signals

	def run(self):
		self.signals().sig_got_bin_info.emit(logic_trt.get_latest_stats_from_bins([self._bin_path])[0])

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

	def __init__(self):

		super().__init__()

		self.setContentsMargins(0,0,0,0)
		self.setLayout(QtWidgets.QHBoxLayout())

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

class TRTSummary(QtWidgets.QGroupBox):

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
			"""Demo info for now"""
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
		self._treeview_model = model_trt.TRTViewModel(self.model())
		
		# Declare top controls
		self.btn_add_bins = QtWidgets.QPushButton("Add From Bins...")
		self.btn_refresh_bins = QtWidgets.QPushButton()
		self.btn_clear_bins = QtWidgets.QPushButton()
		
		# Stacked widget to toggle between progress bar and bin/sequence mode
		self.lay_top_stack = QtWidgets.QStackedLayout()
		self.prog_loading = TRTBinLoadingProgressBar()
		self.bin_mode = TRTModeSelection()

		# Declare main treeview
		self.list_trts = treeview_trt.TRTTreeView()
		self.trt_summary = TRTSummary()

		# Declare trims
		self.trt_trims = trims_trt.TRTControlsTrims()
		self.trim_total = LBSpinBoxTC()



		self._setupSignals()
		self._setupModels()
		self._setupWidgets()

		self.model().setSequenceSelectionMode(QtCore.QSettings().value("trt/sequence_selection_mode", model_trt.SequenceSelectionMode.ONE_SEQUENCE_PER_BIN))

		self.set_bins(QtCore.QSettings().value("trt/bin_paths",[]))


	def _setupModels(self):
		"""Configure the important data"""

		self.model().setTrimFromHead(Timecode(QtCore.QSettings().value("trt/trim_head",0), rate=QtCore.QSettings().value("trt/rate",24)))
		self.model().setTrimFromTail(Timecode(QtCore.QSettings().value("trt/trim_tail",0), rate=QtCore.QSettings().value("trt/rate",24)))
		
		self.model().set_marker_presets(QtCore.QSettings().value("lbb/marker_presets", dict()))

		self.model().set_active_head_marker_preset_name(QtCore.QSettings().value("trt/trim_marker_preset_head"))
		self.model().set_active_tail_marker_preset_name(QtCore.QSettings().value("trt/trim_marker_preset_tail"))

		# TODO: Load in from user settings
		self._treeview_model.set_headers([
			treeview_trt.TRTTreeViewHeaderColor("","sequence_color"),
			treeview_trt.TRTTreeViewHeaderItem("Sequence Name","sequence_name"),
			treeview_trt.TRTTreeViewHeaderDuration("Full Duration","duration_total"),
			treeview_trt.TRTTreeViewHeaderDuration("Trimmed Duration","duration_trimmed"),
			treeview_trt.TRTTreeViewHeaderDuration("LFOA", "lfoa"),
			treeview_trt.TRTTreeViewHeaderDateTime("Date Modified","date_modified"),
			treeview_trt.TRTTreeViewHeaderPath("From Bin","bin_path"),
			treeview_trt.TRTTreeViewHeaderBinLock("Bin Lock","bin_lock"),

		])


	def _setupWidgets(self):
		"""Setup the widgets and add them to the layout"""

		# Setup top controls
		ctrl_layout = QtWidgets.QHBoxLayout()
		
		self.btn_add_bins.setToolTip("Add the latest sequence(s) from one or more bins")
		self.btn_add_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
		ctrl_layout.addWidget(self.btn_add_bins)

		
		#ctrl_layout.addWidget(self.prog_loading)
		self.lay_top_stack.addWidget(self.prog_loading)
		self.lay_top_stack.addWidget(self.bin_mode)

		
		ctrl_layout.addLayout(self.lay_top_stack)

		self.btn_refresh_bins.setToolTip("Reload the existing bins for updates")
		self.btn_refresh_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRefresh))
		ctrl_layout.addWidget(self.btn_refresh_bins)

		self.btn_clear_bins.setToolTip("Clear the existing sequences")
		self.btn_clear_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditClear))
		ctrl_layout.addWidget(self.btn_clear_bins)

		self.layout().addLayout(ctrl_layout)

		# Set up main treeview
		self.list_trts.setModel(self._treeview_model)

		self.layout().addWidget(self.list_trts)
		self.layout().addWidget(self.trt_summary)

		
		# Set up sequence trim controls
		self.layout().addWidget(self.trt_trims)

		
		# Set up total trim controls
		# TODO: Better
		grp_totaltrim = QtWidgets.QGroupBox()
		grp_totaltrim.setLayout(QtWidgets.QHBoxLayout())
		self.trim_total.setAllowNegative(True)
		grp_totaltrim.layout().addWidget(self.trim_total)
		self.layout().addWidget(grp_totaltrim)
	
	def _setupSignals(self):
		"""Connect signals and slots"""

		self.model().sig_sequence_selection_mode_changed.connect(self.bin_mode.setSequenceSelectionMode)
		self.model().sig_sequence_selection_mode_changed.connect(lambda mode: QtCore.QSettings().setValue("trt/sequence_selection_mode", mode))

		self.model().sig_data_changed.connect(self.update_summary)
		self.model().sig_data_changed.connect(self.list_trts.fit_headers)
		self.model().sig_data_changed.connect(self.update_control_buttons)
		self.model().sig_data_changed.connect(self.save_bins)
		
		#self.model().sig_trims_changed.connect(lambda: self.trt_trims.set_head_trim(self.model().trimFromHead()))
		#self.model().sig_trims_changed.connect(lambda: self.trt_trims.set_tail_trim(self.model().trimFromTail()))
		self.model().sig_trims_changed.connect(self.save_trims)

		self.model().sig_marker_presets_model_changed.connect(self.trt_trims.set_marker_presets)
		self.model().sig_head_marker_preset_changed.connect(self.save_head_trim_marker_preset)
		self.model().sig_head_marker_preset_changed.connect(self.trt_trims.set_head_marker_preset_name)
		self.model().sig_tail_marker_preset_changed.connect(self.save_tail_trim_marker_preset)
		self.model().sig_tail_marker_preset_changed.connect(self.trt_trims.set_tail_marker_preset_name)

		# Swap between progress bar and bin mode selection depending on if the progress bar is active
		self.prog_loading.sig_progress_started.connect(lambda: self.lay_top_stack.setCurrentWidget(self.prog_loading))
		self.prog_loading.sig_progress_completed.connect(lambda: self.lay_top_stack.setCurrentWidget(self.bin_mode))
		self.bin_mode.sig_sequence_selection_mode_changed.connect(self.model().setSequenceSelectionMode)
		
		self.list_trts.sig_add_bins.connect(self.set_bins)
		self.list_trts.sig_remove_rows.connect(self.remove_bins)
		
		self.btn_add_bins.clicked.connect(self.choose_folder)
		self.btn_refresh_bins.clicked.connect(self.refresh_bins)
		self.btn_clear_bins.clicked.connect(lambda: self.remove_bins(self.list_trts.selectedRows()))

		self.trt_trims.sig_head_trim_changed.connect(self.model().setTrimFromHead)
		self.trt_trims.sig_tail_trim_changed.connect(self.model().setTrimFromTail)
		
		self.trim_total.sig_timecode_changed.connect(self.save_trims)
		self.trim_total.sig_timecode_changed.connect(self.model().setTrimTotal)

		self.trt_trims.sig_head_trim_marker_preset_chosen.connect(self.model().set_active_head_marker_preset_name)
		self.trt_trims.sig_tail_trim_marker_preset_chosen.connect(self.model().set_active_tail_marker_preset_name)

		self.trt_trims.sig_marker_preset_editor_requested.connect(self.show_marker_maker_dialog)
		
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
		
		for marker in markers_trt.LBMarkerIcons():
			wnd_marker.addMarker(marker)
		wnd_marker.setMarkerPresets(self.model().marker_presets())

		self.model().sig_marker_presets_model_changed.connect(wnd_marker.setMarkerPresets)
		wnd_marker.sig_save_preset.connect(self.save_marker_preset)
		wnd_marker.sig_delete_preset.connect(self.remove_marker_preset)

		return bool(wnd_marker.exec())

	@QtCore.Slot(str)
	def save_head_trim_marker_preset(self, preset_name:str):
		QtCore.QSettings().setValue("trt/trim_marker_preset_head", preset_name)
		print("Head", preset_name)

	@QtCore.Slot(str)
	def save_tail_trim_marker_preset(self, preset_name:str):
		QtCore.QSettings().setValue("trt/trim_marker_preset_tail", preset_name)		
		print("Tail", preset_name)

	def setModel(self, model:model_trt.TRTDataModel):
		self._data_model = model
		self._treeview_model.setDataModel(model)
	
	def model(self) -> model_trt.TRTDataModel:
		return self._data_model
	
	def save_bins(self):
		settings = QtCore.QSettings()
		settings.setValue("trt/bin_paths", [str(b.path) for b in self.model().data()])
	
	def save_trims(self):
		settings = QtCore.QSettings()
		settings.setValue("trt/trim_head", str(self.model().trimFromHead()))
		settings.setValue("trt/trim_tail", str(self.model().trimFromTail()))
		settings.setValue("trt/trim_total", str(self.model().trimTotal()))
		settings.setValue("trt/rate", self.model().rate())

	def get_sequence_info(self, paths):

		last_bin = ""

		for path in paths:
			
			thread = TRTThreadedBinGetter(path)
			
			self.prog_loading.step_added()
			thread.signals().sig_got_bin_info.connect(self.model().add_bin)
			thread.signals().sig_got_bin_info.connect(self.prog_loading.step_complete)

			self._pool.start(thread)

			last_bin = str(path)
		
		# Save last bin path if it's a good 'un
		if last_bin:
			QtCore.QSettings().setValue("trt/last_bin", last_bin)
	
	def set_bins(self, bin_paths: list[str]):

		#self.list_trts.clear()
		self.get_sequence_info(pathlib.Path(x) for x in bin_paths)
		self.save_bins()
	
	def refresh_bins(self):
		pass

	def remove_bins(self, selected:list[int]):

		# Remove selection
		if selected:
			[self.model().remove_sequence(idx) for idx in selected]
			self.save_bins()

		# Or remove everything if nothing is selected
		elif QtWidgets.QMessageBox.warning(self,
			"Clearing Current Sequences",
			"This will clear the existing sequences.  Are you sure?",
			QtWidgets.QMessageBox.StandardButton.Ok, QtWidgets.QMessageBox.StandardButton.Cancel) == QtWidgets.QMessageBox.StandardButton.Ok:

			self.model().clear()
			self.save_bins()
	
	def choose_folder(self):
		last_bin_path = QtCore.QSettings().value("trt/last_bin")
		print(last_bin_path)
		files,_ = QtWidgets.QFileDialog.getOpenFileNames(caption="Choose Avid bins for calcuation...", dir=last_bin_path, filter="Avid Bins (*.avb)")
		
		if not files:
			return
		
		self.set_bins(files)

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