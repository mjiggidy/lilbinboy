import dataclasses, pathlib, re
from PySide6 import QtWidgets, QtGui, QtCore
from timecode import Timecode
from ...lbb_common import LBUtilityTab, LBSpinBoxTC
from . import dlg_marker, logic_trt, model_trt, treeview_trt, markers_trt

class TRTBinLoadingProgressBar(QtWidgets.QProgressBar):

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
	

class TRTControls(QtWidgets.QGroupBox):
	"""TRT Control Abstract"""

class TRTControlsTrims(TRTControls):

	PATH_MARK_IN = str(pathlib.Path(__file__+"../../../../res/icon_mark_in.svg").resolve())
	PATH_MARK_OUT = str(pathlib.Path(__file__+"../../../../res/icon_mark_out.svg").resolve())

	sig_head_trim_changed = QtCore.Signal(Timecode)
	sig_tail_trim_changed = QtCore.Signal(Timecode)

	sig_head_trim_marker_preset_changed = QtCore.Signal(str)
	sig_tail_trim_marker_preset_changed = QtCore.Signal(str)

	sig_use_head_marker_changed = QtCore.Signal(bool)
	sig_use_tail_marker_changed = QtCore.Signal(bool)

	sig_marker_preset_editor_requested = QtCore.Signal()

	def __init__(self):

		super().__init__()

		self.setTitle("Sequence Trimming")

		self.setLayout(QtWidgets.QGridLayout())

		self._from_head = LBSpinBoxTC()
		self._from_tail = LBSpinBoxTC()

		self._use_head_marker = QtWidgets.QCheckBox()
		self._use_tail_marker = QtWidgets.QCheckBox()

		self._from_head_marker = markers_trt.LBMarkerPresetComboBox()
		self._from_tail_marker = markers_trt.LBMarkerPresetComboBox()

		self._icon_mark_in  = QtWidgets.QLabel(pixmap=QtGui.QPixmap(self.PATH_MARK_IN).scaledToHeight(16, QtCore.Qt.TransformationMode.SmoothTransformation))
		self._icon_mark_out = QtWidgets.QLabel(pixmap=QtGui.QPixmap(self.PATH_MARK_OUT).scaledToHeight(16, QtCore.Qt.TransformationMode.SmoothTransformation))

		# Trim from Head / Duration
		self.layout().addWidget(self._icon_mark_in, 0, 0)
		self.layout().addWidget(self._from_head, 0, 1)
		self.layout().addWidget(QtWidgets.QLabel("From Head"), 0, 2)
		self.layout().addItem(QtWidgets.QSpacerItem(0,2, QtWidgets.QSizePolicy.Policy.MinimumExpanding),0,3)
		
		# Trim from Head / Marker
		self.layout().addWidget(self._use_head_marker, 1, 0)
		self.layout().addWidget(self._from_head_marker, 1, 1)
		self._from_head_marker.setEnabled(False)
		self.layout().addWidget(QtWidgets.QLabel("Or FFOA Locator", buddy=self._from_head), 1, 2)

		# Trim from Tail / Duration
		self.layout().addWidget(QtWidgets.QLabel("From Tail", alignment=QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter, buddy=self._from_tail), 0, 4)
		self.layout().addWidget(self._from_tail, 0, 5)
		self.layout().addWidget(self._icon_mark_out, 0, 6)

		# Trim from Tail / Marker
		self.layout().addWidget(QtWidgets.QLabel("Or LFOA Locator", alignment=QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter), 1, 4)
		self.layout().addWidget(self._from_tail_marker, 1, 5)
		self._from_tail_marker.setEnabled(False)
		self.layout().addWidget(self._use_tail_marker, 1, 6)

		self._from_head.sig_timecode_changed.connect(self.sig_head_trim_changed)
		self._from_tail.sig_timecode_changed.connect(self.sig_tail_trim_changed)

		self._use_head_marker.checkStateChanged.connect(lambda: self._from_head_marker.setEnabled(self._use_head_marker.isChecked()))
		self._use_head_marker.checkStateChanged.connect(lambda: self.sig_use_head_marker_changed.emit(self._use_head_marker.isChecked()))
		self._use_tail_marker.checkStateChanged.connect(lambda: self._from_tail_marker.setEnabled(self._use_tail_marker.isChecked()))
		self._use_tail_marker.checkStateChanged.connect(lambda: self.sig_use_tail_marker_changed.emit(self._use_tail_marker.isChecked()))

		self._from_head_marker.sig_marker_preset_editor_requested.connect(self.sig_marker_preset_editor_requested)
		self._from_head_marker.sig_marker_preset_changed.connect(self.sig_head_trim_marker_preset_changed)
		
		self._from_tail_marker.sig_marker_preset_editor_requested.connect(self.sig_marker_preset_editor_requested)
		self._from_tail_marker.sig_marker_preset_changed.connect(self.sig_tail_trim_marker_preset_changed)
	
	@QtCore.Slot(Timecode)
	def set_head_trim(self, timecode:Timecode):
		self._from_head.setTimecode(timecode)

	@QtCore.Slot(Timecode)
	def set_tail_trim(self, timecode:Timecode):
		self._from_tail.setTimecode(timecode)
	
	@QtCore.Slot(dict)
	def set_marker_presets(self, marker_presets:dict[str, markers_trt.LBMarkerPreset]):
		"""Update FFOA and LFOA marker combo boxes"""

		if not marker_presets:
			self._use_head_marker.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._use_tail_marker.setCheckState(QtCore.Qt.CheckState.Unchecked)

		self._from_head_marker.setMarkerPresets(marker_presets)
		self._from_tail_marker.setMarkerPresets(marker_presets)

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
		self.prog_loading = TRTBinLoadingProgressBar()
		
		# Declare main treeview
		self.list_trts = treeview_trt.TRTTreeView()
		self.trt_summary = TRTSummary()

		# Declare trims
		self.trt_trims = TRTControlsTrims()
		self.trim_total = LBSpinBoxTC()



		self._setupModels()
		self._setupWidgets()
		self._setupSignals()


		self.set_bins(QtCore.QSettings().value("trt/bin_paths",[]))

		self.update_marker_presets()

	def _setupModels(self):
		"""Configure the important data"""

		self.model().setTrimFromHead(Timecode(QtCore.QSettings().value("trt/trim_head",0), rate=QtCore.QSettings().value("trt/rate",24)))
		self.model().setTrimFromTail(Timecode(QtCore.QSettings().value("trt/trim_tail",0), rate=QtCore.QSettings().value("trt/rate",24)))
		self.model().set_marker_presets(QtCore.QSettings().value("lbb/marker_presets", dict()))

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

		ctrl_layout.addWidget(self.prog_loading)

		self.btn_refresh_bins.setToolTip("Reload the existing bins for updates")
		self.btn_refresh_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRefresh))
		ctrl_layout.addWidget(self.btn_refresh_bins)

		self.btn_clear_bins.setToolTip("Clear the existing sequences")
		self.btn_clear_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditClear))
		ctrl_layout.addWidget(self.btn_clear_bins)

		self.layout().addLayout(ctrl_layout)

		# Set up main treeview
		self.list_trts.setModel(self._treeview_model)


		#self.list_trts.model().setSourceModel(self._treeview_model)
		#self.list_trts.model().setSortRole(QtCore.Qt.ItemDataRole.InitialSortOrderRole)

		self.layout().addWidget(self.list_trts)
		self.layout().addWidget(self.trt_summary)

		
		# Set up sequence trim controls
		self.trt_trims.set_head_trim(self.model().trimFromHead())
		self.trt_trims.set_tail_trim(self.model().trimFromTail())
		self.layout().addWidget(self.trt_trims)

		
		# Set up total trim controls
		# TODO: Better
		grp_totaltrim = QtWidgets.QGroupBox()
		grp_totaltrim.setLayout(QtWidgets.QHBoxLayout())
		self.trim_total.setAllowNegative(True)
		self.trim_total.setTimecode(Timecode(QtCore.QSettings().value("trt/trim_total",0), rate=QtCore.QSettings().value("trt/rate",24)))
		grp_totaltrim.layout().addWidget(self.trim_total)
		self.layout().addWidget(grp_totaltrim)
	
	def _setupSignals(self):
		"""Connect signals and slots"""

		self._data_model.sig_data_changed.connect(self.update_summary)
		self._data_model.sig_data_changed.connect(self.list_trts.fit_headers)
		self._data_model.sig_data_changed.connect(self.update_control_buttons)
		self._data_model.sig_data_changed.connect(self.save_bins)
		self._data_model.sig_trims_changed.connect(self.save_trims)

		self.list_trts.sig_add_bins.connect(self.set_bins)
		self.list_trts.sig_remove_rows.connect(self.remove_bins)
		
		self.btn_add_bins.clicked.connect(self.choose_folder)
		self.btn_refresh_bins.clicked.connect(self.refresh_bins)
		self.btn_clear_bins.clicked.connect(lambda: self.remove_bins(self.list_trts.selectedRows()))

		self.trt_trims.sig_use_head_marker_changed.connect(self.toggled_head_trim_marker)
		self.trt_trims.sig_use_tail_marker_changed.connect(self.toggled_tail_trim_marker)
		self.trt_trims.sig_head_trim_changed.connect(self.model().setTrimFromHead)
		self.trt_trims.sig_head_trim_marker_preset_changed.connect(self.set_head_trim_marker_preset)
		self.trt_trims.sig_tail_trim_changed.connect(self.model().setTrimFromTail)
		self.trt_trims.sig_tail_trim_marker_preset_changed.connect(self.set_tail_trim_marker_preset)
		
		self.trim_total.sig_timecode_changed.connect(self.save_trims)
		self.trim_total.sig_timecode_changed.connect(self.model().setTrimTotal)

		self.trt_trims.sig_marker_preset_editor_requested.connect(self.show_marker_maker_dialog)
		
	@QtCore.Slot(str, markers_trt.LBMarkerPreset)
	def save_marker_preset(self, preset_name:str, marker_preset:markers_trt.LBMarkerPreset):
		presets = self.model().marker_presets()
		presets.update({preset_name: marker_preset})
		self.model().set_marker_presets(presets)
		
		QtCore.QSettings().setValue("lbb/marker_presets", self.model().marker_presets())
		self.update_marker_presets()
	
	@QtCore.Slot(str)
	def remove_marker_preset(self, preset_name:str):
		print("Removed", self.model().marker_presets().pop(preset_name, None))
		QtCore.QSettings().setValue("lbb/marker_presets", self.model().marker_presets())
		self.update_marker_presets()
	
	@QtCore.Slot()
	def show_marker_maker_dialog(self) -> bool:
		wnd_marker = dlg_marker.TRTMarkerMaker(self)
		
		for marker in markers_trt.LBMarkerIcons():
			wnd_marker.addMarker(marker)
		wnd_marker.set_marker_presets(self.model().marker_presets())
		
		wnd_marker.sig_save_preset.connect(self.save_marker_preset)
		wnd_marker.sig_delete_preset.connect(self.remove_marker_preset)
		
		wnd_marker.finished.connect(self.update_marker_presets)

		return bool(wnd_marker.exec())
	
	def update_marker_presets(self):
		self.trt_trims.set_marker_presets(self.model().marker_presets())

	@QtCore.Slot(bool)
	def toggled_head_trim_marker(self, is_enabled:bool):
		"""Opted to use a head marker... or not!!"""

		# Make sure at least one marker is defined
		if is_enabled and not self.model().marker_presets():
			self.show_marker_maker_dialog()
		

	@QtCore.Slot(bool)
	def toggled_tail_trim_marker(self, is_enabled:bool):
		"""Opted to use a tail marker... or not!!"""

		# Make sure at least one marker is defined
		if is_enabled and not self.model().marker_presets():
			self.show_marker_maker_dialog()
	
	@QtCore.Slot(str)
	def set_head_trim_marker_preset(self, preset_name:str):
		print("Head", preset_name)

	@QtCore.Slot(str)
	def set_tail_trim_marker_preset(self, preset_name:str):
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
			thread.signals().sig_got_bin_info.connect(self.model().add_sequence)
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