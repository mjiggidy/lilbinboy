import dataclasses, pathlib, re
from PySide6 import QtWidgets, QtGui, QtCore
from timecode import Timecode
from ...lbb_common import LBUtilityTab
from . import dlg_marker, logic_trt, model_trt

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

class TRTThreadedSignals(QtCore.QObject):
	sig_got_bin_info = QtCore.Signal(logic_trt.BinInfo)

class TRTThreadedBinGetter(QtCore.QRunnable):

	def __init__(self, bin_path:str):
		super().__init__()
		self._bin_path = bin_path
		self._signals = TRTThreadedSignals()

	def signals(self) -> TRTThreadedSignals:
		return self._signals

	def run(self):
		self.signals().sig_got_bin_info.emit(logic_trt.get_latest_stats_from_bins([self._bin_path])[0])
	

class TRTListItem(QtWidgets.QTreeWidgetItem):
	"""A TRTListItem"""

	HEAD_TRIM = Timecode("8:00")
	TAIL_TRIM = Timecode("4:00")
	
	def __init__(self, reel_info:logic_trt.ReelInfo):


		super().__init__(QtWidgets.QTreeWidgetItem.ItemType.UserType)

		# Icon
		#self.setData(0, QtCore.Qt.ItemDataRole.DisplayRole, )

		self.setData(1, QtCore.Qt.ItemDataRole.DisplayRole, str(reel_info.sequence_name))

		# Full duration
		self.setTextAlignment(2, QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		self.setData(2, QtCore.Qt.ItemDataRole.DisplayRole, str(reel_info.duration_total).lstrip("0:"))
		self.setData(2, QtCore.Qt.ItemDataRole.FontRole, QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont))
		self.setData(2, QtCore.Qt.ItemDataRole.InitialSortOrderRole, reel_info.duration_total.frame_number)


		# LFOA F+F
		tc_lfoa = reel_info.duration_total - self.TAIL_TRIM - 1 # -1?  Hmmmm....
		ff = str(tc_lfoa.frame_number//16) + "+" + str(tc_lfoa.frame_number%16).zfill(2)
		self.setTextAlignment(3, QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		self.setData(3, QtCore.Qt.ItemDataRole.DisplayRole, ff)
		self.setData(3, QtCore.Qt.ItemDataRole.FontRole, QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont))

		# Date modified
		self.setData(4, QtCore.Qt.ItemDataRole.TextAlignmentRole, QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		self.setData(4, QtCore.Qt.ItemDataRole.FontRole, QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont))
		self.setData(4, QtCore.Qt.ItemDataRole.DisplayRole, str(reel_info.date_modified))

		# Trimmed duration
		tc_trimmed = reel_info.duration_total - self.HEAD_TRIM - self.TAIL_TRIM
		self.setTextAlignment(5, QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		self.setData(5, QtCore.Qt.ItemDataRole.DisplayRole, str(tc_trimmed).lstrip("0:"))
		self.setData(5, QtCore.Qt.ItemDataRole.FontRole, QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont))
		self.setData(5, QtCore.Qt.ItemDataRole.InitialSortOrderRole, tc_trimmed.frame_number)

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

		self._add_demo_summary_items()

	def _add_demo_summary_items(self):
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
	sig_marker_preset_editor_requested = QtCore.Signal()

	def __init__(self):

		super().__init__()

		self.setTitle("Sequence Trimming")

		self.setLayout(QtWidgets.QGridLayout())

		self._from_head = LBSpinBoxTC()
		self._from_tail = LBSpinBoxTC()

		self._icon_mark_in  = QtWidgets.QLabel(pixmap=QtGui.QPixmap(self.PATH_MARK_IN).scaledToHeight(16, QtCore.Qt.TransformationMode.SmoothTransformation))
		self._icon_mark_out = QtWidgets.QLabel(pixmap=QtGui.QPixmap(self.PATH_MARK_OUT).scaledToHeight(16, QtCore.Qt.TransformationMode.SmoothTransformation))

		# Trim from Head / Duration
		self.layout().addWidget(self._icon_mark_in, 0, 0)
		self.layout().addWidget(self._from_head, 0, 1)
		self.layout().addWidget(QtWidgets.QLabel("From Head"), 0, 2)
		self.layout().addItem(QtWidgets.QSpacerItem(0,2, QtWidgets.QSizePolicy.Policy.MinimumExpanding),0,3)
		
		# Trim from Head / Marker
		self._from_head_marker = LBMarkerPresetComboBox()
		self.layout().addWidget(QtWidgets.QCheckBox(), 1, 0)
		self.layout().addWidget(self._from_head_marker, 1, 1)
		self.layout().addWidget(QtWidgets.QLabel("Or FFOA Locator", buddy=self._from_head), 1, 2)

		# Trim from Tail / Duration
		self.layout().addWidget(QtWidgets.QLabel("From Tail", alignment=QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter, buddy=self._from_tail), 0, 4)
		self.layout().addWidget(self._from_tail, 0, 5)
		self.layout().addWidget(self._icon_mark_out, 0, 6)

		# Trim from Tail / Marker
		self._from_tail_marker = LBMarkerPresetComboBox()
		self.layout().addWidget(QtWidgets.QLabel("Or LFOA Locator", alignment=QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter), 1, 4)
		self.layout().addWidget(self._from_tail_marker, 1, 5)
		self.layout().addWidget(QtWidgets.QCheckBox(), 1, 6)

		self._from_head.sig_timecode_changed.connect(self.sig_head_trim_changed)
		self._from_tail.sig_timecode_changed.connect(self.sig_tail_trim_changed)

		self._from_head_marker.sig_edit_marker_presets.connect(self.sig_marker_preset_editor_requested)
		self._from_tail_marker.sig_edit_marker_presets.connect(self.sig_marker_preset_editor_requested)
	
	@QtCore.Slot(Timecode)
	def set_head_trim(self, timecode:Timecode):
		self._from_head.setTimecode(timecode)

	@QtCore.Slot(Timecode)
	def set_tail_trim(self, timecode:Timecode):
		self._from_tail.setTimecode(timecode)
	
	@QtCore.Slot(dict)
	def set_marker_presets(self, marker_presets:dict[str, model_trt.LBMarkerPreset]):
		"""Update FFOA and LFOA marker combo boxes"""
		self._from_head_marker.setMarkerPresets(marker_presets)
		self._from_tail_marker.setMarkerPresets(marker_presets)


class LBMarkerPresetComboBox(QtWidgets.QComboBox):

	sig_edit_marker_presets = QtCore.Signal()
	"""Request the editor"""
	
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		self.currentIndexChanged.connect(self.updateToolTip)
		self.currentIndexChanged.connect(self.checkIfEditorRequested)
	
	def setMarkerPresets(self, marker_presets:dict[str, model_trt.LBMarkerPreset]):

		current_selection = self.currentText()
		self.clear()

		for preset_name, preset_data in marker_presets.items():
			self.addItem(model_trt.LBMarkerIcon(preset_data.color), preset_name, preset_data)

		self.insertSeparator(len(marker_presets))
		self.addItem("Add/Edit...")

		self.setCurrentText(current_selection)
	
	@QtCore.Slot(int)
	def checkIfEditorRequested(self, index:int):
		if self.currentData() is None:
			self.sig_edit_marker_presets.emit()

	@QtCore.Slot(int)
	def updateToolTip(self, index:int):
		self.setToolTip(self.formatForToolTip(self.currentData()) if self.currentData() else "No Preset Chosen")
	
	def formatForToolTip(self, marker_preset:model_trt.LBMarkerPreset) -> str:

		return "Color: {color}; Comment: {comment}; Author: {author}".format(
			color = marker_preset.color or "(Any)",
			comment = ("\"" + marker_preset.comment + "\"") if marker_preset.comment else "(Any)",
			author = ("\"" + marker_preset.author + "\"") if marker_preset.author else "(Any)",
		)

class LBSpinBoxTC(QtWidgets.QSpinBox):

	PAT_VALID_TEXT = re.compile(r"^(\d+:){0,3}\d+$")
	PAT_INTER_TEXT = re.compile(r"^(\d+:?){1,4}$")

	sig_timecode_changed = QtCore.Signal(Timecode)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		self._rate = 24
		self._allow_negative = False
		self.valueChanged.connect(lambda: self.sig_timecode_changed.emit(self.timecode()))
	
	@QtCore.Slot()
	def setRate(self, rate:int):
		self._rate = rate
		self.updateMaximumTC()
		self.sig_timecode_changed.emit(self.timecode())

	@QtCore.Slot()
	def updateMaximumTC(self):
		self.setMaximum(Timecode("100:00:00:00", rate=self.rate()).frame_number)
		self.setMinimum(Timecode("-100:00:00:00", rate=self.rate()).frame_number if self.allowNegative() else Timecode(0, rate=self.rate()).frame_number)

	def validate(self, input:str, pos:int) -> bool:

		# Allow for one '-' if negative is allowed, by stripping it off for validation
		if self.allowNegative() and input.startswith("-"):
			input = input[1:]

		if self.__class__.PAT_VALID_TEXT.match(input):
			return QtGui.QValidator.State.Acceptable 
		elif self.__class__.PAT_INTER_TEXT.match(input):
			return QtGui.QValidator.State.Intermediate
		elif input == "":
			return QtGui.QValidator.State.Intermediate 
		else:
			return QtGui.QValidator.State.Invalid
	
	@QtCore.Slot(Timecode)
	def setTimecode(self, timecode:Timecode):
		self.setRate(timecode.rate)
		self.setValue(timecode.frame_number)
	
	def setAllowNegative(self, allow:bool):
		if allow != self.allowNegative():
			self._allow_negative = allow
			self.updateMaximumTC()

	def allowNegative(self) -> bool:
		return self._allow_negative
	
	def timecode(self) -> Timecode:
		return Timecode(self.value(), rate=self.rate())

	def rate(self) -> int:
		return self._rate
	
	def textFromValue(self, val:int) -> str:
		return str(Timecode(val, rate=self.rate()))
	
	def valueFromText(self, text:str) -> int:
		return Timecode(text, rate=self.rate()).frame_number

class LBTRTCalculator(LBUtilityTab):
	"""TRT Calculator"""

	PATH_ICON = __file__+"../../../../res/icon_trt.png"

	sig_modelchanged = QtCore.Signal()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


		self.setLayout(QtWidgets.QVBoxLayout())

		self._pool = QtCore.QThreadPool()

		self._model = model_trt.TRTModel()
		self.list_trts = model_trt.TRTTreeView()
		self.trt_summary = TRTSummary()
		self.list_viewmodel = model_trt.TRTViewModel(self.model())
		
		self.list_trts.setModel(model_trt.TRTViewSortModel())
		self.list_trts.model().setSortRole(QtCore.Qt.ItemDataRole.InitialSortOrderRole)

		self._marker_presets = QtCore.QSettings().value("lbb/marker_presets", dict())

		self.prog_loading = TRTBinLoadingProgressBar()

		self.list_viewmodel.set_headers([
			model_trt.TRTTreeViewHeaderColor("","sequence_color"),
			model_trt.TRTTreeViewHeaderItem("Sequence Name","sequence_name"),
			model_trt.TRTTreeViewHeaderDuration("Full Duration","duration_total"),
			model_trt.TRTTreeViewHeaderDuration("Trimmed Duration","duration_trimmed"),
			model_trt.TRTTreeViewHeaderDuration("LFOA", "lfoa"),
			model_trt.TRTTreeViewHeaderDateTime("Date Modified","date_modified"),
			model_trt.TRTTreeViewHeaderPath("From Bin","bin_path"),
			model_trt.TRTTreeViewHeaderBinLock("Bin Lock","bin_lock"),

		])

		self.list_trts.model().setSourceModel(self.list_viewmodel)

		self.list_trts.sig_add_bins.connect(self.set_bins)

		self.btn_add_bins = QtWidgets.QPushButton("Add From Bins...")
		self.btn_refresh_bins = QtWidgets.QPushButton()
		self.btn_clear_bins = QtWidgets.QPushButton()
		

		self.trt_trims = TRTControlsTrims()

		self.trt_trims.sig_head_trim_changed.connect(self.model().setTrimFromHead)
		self.trt_trims.sig_tail_trim_changed.connect(self.model().setTrimFromTail)

		self.trim_total = LBSpinBoxTC()
		self.trim_total.setAllowNegative(True)
		self.trim_total.setTimecode(Timecode(QtCore.QSettings().value("trt/trim_total",0), rate=QtCore.QSettings().value("trt/rate",24)))
		self.trim_total.sig_timecode_changed.connect(self.model().setTrimTotal)

		self.model().setTrimFromHead(Timecode(QtCore.QSettings().value("trt/trim_head",0), rate=QtCore.QSettings().value("trt/rate",24)))
		self.model().setTrimFromTail(Timecode(QtCore.QSettings().value("trt/trim_tail",0), rate=QtCore.QSettings().value("trt/rate",24)))

		self.trt_trims.set_head_trim(self.model().trimFromHead())
		self.trt_trims.set_tail_trim(self.model().trimFromTail())

		self._setupWidgets()
		self.trt_trims.sig_head_trim_changed.connect(self.save_trims)
		self.trt_trims.sig_tail_trim_changed.connect(self.save_trims)
		self.trim_total.sig_timecode_changed.connect(self.save_trims)

		self._model.sig_data_changed.connect(self.update_summary)
		self._model.sig_data_changed.connect(self.list_trts.fit_headers)
		self._model.sig_data_changed.connect(self.update_control_buttons)
		self._model.sig_data_changed.connect(self.save_bins)

		self.list_trts.fit_headers()

		self.set_bins(QtCore.QSettings().value("trt/bin_paths",[]))

		self._marker_icons = model_trt.LBMarkerIcons()
		
		self.wnd_marker = dlg_marker.TRTMarkerMaker(self)
		for marker in self._marker_icons:
			self.wnd_marker.addMarker(marker)
		
		self.wnd_marker.sig_save_preset.connect(self.save_marker_preset)
		self.wnd_marker.exec()

		self.update_marker_presets()
		self.trt_trims.sig_marker_preset_editor_requested.connect(self.wnd_marker.exec)
	
	@QtCore.Slot(str, model_trt.LBMarkerPreset)
	def save_marker_preset(self, preset_name:str, marker_preset:model_trt.LBMarkerPreset):
		self._marker_presets.update({preset_name: marker_preset})
		QtCore.QSettings().setValue("lbb/marker_presets", self._marker_presets)
		self.update_marker_presets()
	
	def update_marker_presets(self):
		self.trt_trims.set_marker_presets(self._marker_presets)
		self.wnd_marker.set_marker_presets(self._marker_presets)

	def setModel(self, model:model_trt.TRTModel):
		self._model = model
		self.list_viewmodel.set_model(model)
	
	def model(self) -> model_trt.TRTModel:
		return self._model
	
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

		for path in paths:
			
			thread = TRTThreadedBinGetter(path)
			
			self.prog_loading.step_added()
			thread.signals().sig_got_bin_info.connect(self.model().add_sequence)
			thread.signals().sig_got_bin_info.connect(self.prog_loading.step_complete)

			self._pool.start(thread)
	
	def _setupWidgets(self):

		self.btn_add_bins.clicked.connect(self.choose_folder)
		self.btn_add_bins.setToolTip("Add the latest sequence(s) from one or more bins")
		self.btn_add_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
		#self.btn_add_bins.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Fixed))

		self.btn_refresh_bins.clicked.connect(self.refresh_bins)
		self.btn_refresh_bins.setToolTip("Reload the existing bins for updates")
		self.btn_refresh_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRefresh))

		self.list_trts.sig_remove_rows.connect(self.remove_bins)
		self.btn_clear_bins.clicked.connect(lambda: self.remove_bins(sorted(set([idx.row() for idx in self.list_trts.selectedIndexes()]), reverse=True)))
		self.btn_clear_bins.setToolTip("Clear the existing sequences")
		self.btn_clear_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditClear))

		ctrl_layout = QtWidgets.QHBoxLayout()

		ctrl_layout.addWidget(self.btn_add_bins)
		ctrl_layout.addWidget(self.prog_loading)
		ctrl_layout.addWidget(self.btn_refresh_bins)
		ctrl_layout.addWidget(self.btn_clear_bins)
		self.layout().addLayout(ctrl_layout)
		
		self.layout().addWidget(self.list_trts)
		
		self.layout().addWidget(self.trt_summary)
		self.layout().addWidget(self.trt_trims)

		grp_totaltrim = QtWidgets.QGroupBox()
		grp_totaltrim.setLayout(QtWidgets.QHBoxLayout())
		grp_totaltrim.layout().addWidget(self.trim_total)

		self.layout().addWidget(grp_totaltrim)

	
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
		files,_ = QtWidgets.QFileDialog.getOpenFileNames(caption="Choose Avid bins for calcuation...", filter="Avid Bins (*.avb)")
		
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

			