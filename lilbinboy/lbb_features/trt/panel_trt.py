import dataclasses, pathlib
from PySide6 import QtWidgets, QtGui, QtCore
from timecode import Timecode
from ...lbb_common import LBUtilityTab
from . import logic_trt

class TRTListItem(QtWidgets.QTreeWidgetItem):
	"""A TRTListItem"""
	
	def __init__(self, reel_info:logic_trt.ReelInfo):


		super().__init__(QtWidgets.QTreeWidgetItem.ItemType.UserType)

		# Icon
		#self.setData(0, QtCore.Qt.ItemDataRole.DisplayRole, )

		self.setData(1, QtCore.Qt.ItemDataRole.DisplayRole, str(reel_info.sequence_name))

		self.setTextAlignment(2, QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		self.setData(2, QtCore.Qt.ItemDataRole.DisplayRole, str(reel_info.duration_total).lstrip("0:"))
		self.setData(2, QtCore.Qt.ItemDataRole.FontRole, QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont))
		self.setData(2, QtCore.Qt.ItemDataRole.InitialSortOrderRole, reel_info.duration_total.frame_number)

		# LFOA F+F
		ff = str(reel_info.duration_total.frame_number//16) + "+" + str(reel_info.duration_total.frame_number%16).zfill(2)
		self.setTextAlignment(3, QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		self.setData(3, QtCore.Qt.ItemDataRole.DisplayRole, ff)
		self.setData(3, QtCore.Qt.ItemDataRole.FontRole, QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont))

		self.setData(4, QtCore.Qt.ItemDataRole.TextAlignmentRole, QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		self.setData(4, QtCore.Qt.ItemDataRole.FontRole, QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont))
		self.setData(4, QtCore.Qt.ItemDataRole.DisplayRole, str(reel_info.date_modified))

@dataclasses.dataclass(frozen=True)
class TRTSummaryItem():
	"""Item to display in a `TRTSummary` bar"""

	label:str
	"""The label for this item"""

	value:str
	"""The value of this item"""

class TRTList(QtWidgets.QTreeWidget):
	"""TRT Readout"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setHeaderLabels([
			"",
			"Sequence Name",
			"Full Duration",
			"LFOA",
			"Date Modified",
			"Bin Lock"
		])

		self.setColumnWidth(0, 24)
		self.setColumnWidth(1, 128)
		self.setAlternatingRowColors(True)
		self.setIndentation(0)
		self.setSortingEnabled(True)
		self.sortByColumn(1, QtCore.Qt.SortOrder.AscendingOrder)

		#self._add_demo_sequence_info()
	
	def add_sequence_info(self, sequence_info:logic_trt.ReelInfo):

		duration_head = Timecode("8:00")
		duration_tail = Timecode("4:00")

		tc_trimmed = sequence_info.duration_total - duration_head - duration_tail
		tc_lfoa  = sequence_info.duration_total - duration_tail
		str_lfoa = str(tc_lfoa.frame_number // 16) + "+" + str(tc_lfoa.frame_number % 16).zfill(2)
		self.addTopLevelItem(TRTListItem(sequence_info))

	def _add_demo_sequence_info(self):


		self.addTopLevelItems([
			TRTListItem(["", "JW4 REEL 1 v24.3.1", "00:17:40:12", "1602+11", "2023-01-27 08:59:22",""]),
			TRTListItem(["", "JW4 REEL 2 v24.0.87", "00:20:48:18", "1885+01", "2023-01-21 11:13:13",""]),
			TRTListItem(["", "JW4 REEL 3 v24.5.8", "00:20:07:21", "1823+12", "2023-01-20 15:39:15",""]),
			TRTListItem(["", "JW4 REEL 4 v24.3", "00:10:41:02", "973+09", "2023-01-21 11:29:19",""]),
			TRTListItem(["", "JW4 REEL 5 v24.3.39", "00:20:38:04", "1869+03", "2023-01-19 22:05:27",""]),
		])


class TRTSummary(QtWidgets.QGroupBox):

	_fnt_label = QtGui.QFont()
	_fnt_value = QtGui.QFont()

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.__class__._fnt_label.setCapitalization(QtGui.QFont.Capitalization.AllUppercase)
		self.__class__._fnt_label.setPointSizeF(8)

		self.__class__._fnt_value.setBold(True)
		self.__class__._fnt_value.setPointSizeF(14)

		self.setLayout(QtWidgets.QGridLayout())
		self.layout().setHorizontalSpacing(24)

		self._add_demo_summary_items()

	def _add_demo_summary_items(self):
			"""Demo info for now"""
			self.add_summary_item(TRTSummaryItem(
				label="Sequences",
				value="6"
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
				value="29208+04"
			))

			self.add_summary_item(TRTSummaryItem(
				label="Total Runtime",
				value="01:02:33:04"
			))
	
	def add_summary_item(self, item:TRTSummaryItem):

		lbl_value = QtWidgets.QLabel(item.value)
		lbl_value.setFont(self.__class__._fnt_value)
		lbl_value.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
		lbl_value.setTextInteractionFlags(QtGui.Qt.TextInteractionFlag.TextSelectableByMouse|QtGui.Qt.TextInteractionFlag.TextSelectableByKeyboard)

		lbl_label = QtWidgets.QLabel(item.label)
		lbl_label.setFont(self.__class__._fnt_label)
		lbl_label.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
		lbl_label.setBuddy(lbl_value)
		
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

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QGridLayout())

		self.list_trts = TRTList()
		self.btn_browser = QtWidgets.QPushButton("Choose Bins...")
		self._setupWidgets()

		self.get_sequence_info(pathlib.Path("/Users/mjordan/dev/lilbinboy/example_projects/SNL/01_EDITS").glob("*.avb"))

	def get_sequence_info(self, paths):

		summaries = logic_trt.get_latest_stats_from_bins(paths)
		for summary in summaries:
			self.list_trts.add_sequence_info(summary.reel)
	
	def _setupWidgets(self):

		self.btn_browser.clicked.connect(self.choose_folder)
		self.layout().addWidget(self.btn_browser)
		
		self.layout().addWidget(self.list_trts)
		
		self.layout().addWidget(TRTSummary())
		self.layout().addWidget(TRTControlsTrims())
	
	def set_bins(self, bin_paths: list[str]):

		self.list_trts.clear()
		self.get_sequence_info(pathlib.Path(x) for x in bin_paths)
	
	def choose_folder(self):
		files,_ = QtWidgets.QFileDialog.getOpenFileNames(caption="Choose Avid bins for calcuation...", filter="Avid Bin (*.avb)")
		
		if not files:
			return
		
		self.set_bins(files)