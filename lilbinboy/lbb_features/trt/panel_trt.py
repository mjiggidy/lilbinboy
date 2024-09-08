import dataclasses, pathlib
from PySide6 import QtWidgets, QtGui, QtCore
from timecode import Timecode
from ...lbb_common import LBUtilityTab
from . import logic_trt, model_trt

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
				label="Total F+F",
				value="0+00"
			))

			self.add_summary_item(TRTSummaryItem(
				label="Total Runtime",
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

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setTitle("Trimming")

class LBTRTCalculator(LBUtilityTab):
	"""TRT Calculator"""

	sig_modelchanged = QtCore.Signal()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


		self.setLayout(QtWidgets.QGridLayout())

		self._model = model_trt.TRTModel()
		self.list_trts = model_trt.TRTTreeView()
		self.trt_summary = TRTSummary()
		
		self.list_viewmodel = model_trt.TRTViewModel(self.model())
		
		self.list_trts.setModel(model_trt.TRTViewSortModel())
		self.list_trts.model().setSortRole(QtCore.Qt.ItemDataRole.InitialSortOrderRole)

		self.list_viewmodel.set_headers([
			model_trt.TRTTreeViewHeaderItem("","icon"),
			model_trt.TRTTreeViewHeaderItem("Sequence Name","sequence_name"),
			model_trt.TRTTreeViewHeaderDuration("Full Duration","duration_total"),
			model_trt.TRTTreeViewHeaderDuration("Trimmed Duration","duration_trimmed"),
			model_trt.TRTTreeViewHeaderDuration("LFOA", "lfoa"),
			model_trt.TRTTreeViewHeaderDateTime("Date Modified","date_modified"),
			model_trt.TRTTreeViewHeaderItem("Bin Lock","bin_lock"),

		])

		self.list_trts.model().setSourceModel(self.list_viewmodel)

		self.btn_add_bins = QtWidgets.QPushButton("Add Bins...")
		
		self._model.sig_data_changed.connect(self.update_summary)
		
		self._setupWidgets()

	def setModel(self, model:model_trt.TRTModel):
		self._model = model
		self.list_viewmodel.set_model(model)
	
	def model(self) -> model_trt.TRTModel:
		return self._model

	def get_sequence_info(self, paths):
		self.model().set_data(logic_trt.get_latest_stats_from_bins(paths))
	
	def _setupWidgets(self):

		self.btn_add_bins.clicked.connect(self.choose_folder)
		self.btn_add_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))

		self.layout().addWidget(self.btn_add_bins)
		
		self.layout().addWidget(self.list_trts)
		
		self.layout().addWidget(self.trt_summary)
		self.layout().addWidget(TRTControlsTrims())
	
	def set_bins(self, bin_paths: list[str]):

		#self.list_trts.clear()
		self.get_sequence_info(pathlib.Path(x) for x in bin_paths)
	
	def choose_folder(self):
		files,_ = QtWidgets.QFileDialog.getOpenFileNames(caption="Choose Avid bins for calcuation...", filter="Avid Bins (*.avb)")
		
		if not files:
			return
		
		self.set_bins(files)

	def update_summary(self):
		self.trt_summary.add_summary_item(TRTSummaryItem(label="Sequences", value=self.model().sequence_count()))
		self.trt_summary.add_summary_item(TRTSummaryItem(label="Total F+F", value=self.model().total_lfoa()))
		self.trt_summary.add_summary_item(TRTSummaryItem(label="Total Runtime",  value=self.model().total_runtime()))
		