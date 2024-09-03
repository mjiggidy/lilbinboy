import dataclasses, pathlib
from PySide6 import QtWidgets, QtGui, QtCore
from timecode import Timecode
from ...lbb_common import LBUtilityTab
from . import logic_trt


class TRTModelColumn(QtCore.QObject):
	def __init__(self, header_text:str):

		super().__init__()
		self.header_text = str(header_text)
	
	def header_data(self, role:QtCore.Qt.ItemDataRole=QtCore.Qt.ItemDataRole.DisplayRole):

		if role==QtCore.Qt.ItemDataRole.DisplayRole:
			return self.header_text
	
	def __str__(self):
		return self.header_text

class TRTDurationColumn(TRTModelColumn):

	def header_data(self, role:QtCore.Qt.ItemDataRole=QtCore.Qt.ItemDataRole.DisplayRole):
		if role==QtCore.Qt.ItemDataRole.DisplayRole:
			return self.header_text
	
	def item_data(self, item:Timecode, role:QtCore.Qt.ItemDataRole=QtCore.Qt.ItemDataRole.DisplayRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return str(item).lstrip("0:")
		elif role == QtCore.Qt.ItemDataRole.FontRole:
			return QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont)


class TRTModel(QtCore.QAbstractItemModel):

	def __init__(self):
		"""Create and setup a new model"""
		super().__init__()

		self._datastruct:list[logic_trt.ReelInfo] = []
		self._headers = [
			TRTModelColumn(""),
			TRTModelColumn("Sequence Name"),
			TRTDurationColumn("Full Duration"),
			TRTModelColumn("LFOA"),
			TRTModelColumn("Date Modified"),
			TRTDurationColumn("Trimmed Duration"),
			TRTModelColumn("Bin Lock"),
		]
		
		# Typically a list of data here
		# Typically a dict of header keys and values here
	
	def index(self, row:int, column:int, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> QtCore.QModelIndex:
		"""Returns the index of the item in the model specified by the given row, column and parent index."""

		if parent.isValid():
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column, self._datastruct[row])
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Returns the parent of the model item with the given index. If the item has no parent, an invalid QModelIndex is returned."""
		return  QtCore.QModelIndex()

	def rowCount(self, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Returns the number of rows under the given parent. When the parent is valid it means that is returning the number of children of parent."""
		return 0 if parent.isValid() else len(self._datastruct)
	
	def columnCount(self, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Returns the number of columns for the children of the given parent."""
		return 0 if parent.isValid() else len(self._headers)

	def data(self, index:QtCore.QModelIndex, role:QtCore.Qt.ItemDataRole=QtCore.Qt.ItemDataRole.DisplayRole) -> str:
		"""Returns the data stored under the given role for the item referred to by the index."""
		col = self._headers[index.column()]
		if str(col) == "Full Duration":
			return col.item_data(self._datastruct[index.row()].reel.duration_total)

	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, role:QtCore.Qt.ItemDataRole=QtCore.Qt.ItemDataRole.DisplayRole) -> str:
		"""Returns the data for the given role and section in the header with the specified orientation."""
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self._headers[section].header_data(role)

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

class TRTList(QtWidgets.QTreeView):
	"""TRT Readout"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setColumnWidth(0, 24)
		self.setColumnWidth(1, 128)
		self.setAlternatingRowColors(True)
		self.setIndentation(0)
		self.setSortingEnabled(True)
		self.sortByColumn(1, QtCore.Qt.SortOrder.AscendingOrder)


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

		self.model_trts = TRTModel()
		self.list_trts = TRTList()
		self.list_trts.setModel(self.model_trts)
		self.btn_browser = QtWidgets.QPushButton("Choose Bins...")
		self._setupWidgets()

		#self.get_sequence_info(pathlib.Path("/Users/mjordan/dev/lilbinboy/example_projects/SNL/01_EDITS").glob("*.avb"))

	def get_sequence_info(self, paths):

		summaries = logic_trt.get_latest_stats_from_bins(paths)
		self.model_trts._datastruct = summaries

	def _setupWidgets(self):

		self.btn_browser.clicked.connect(self.choose_folder)
		self.layout().addWidget(self.btn_browser)
		
		self.layout().addWidget(self.list_trts)
		
		self.layout().addWidget(TRTSummary())
		self.layout().addWidget(TRTControlsTrims())
	
	def set_bins(self, bin_paths: list[str]):

		self.model_trts.beginResetModel()
		self.get_sequence_info(pathlib.Path(x) for x in bin_paths)
		self.model_trts.endResetModel()

	
	def choose_folder(self):
		files,_ = QtWidgets.QFileDialog.getOpenFileNames(caption="Choose Avid bins for calcuation...", filter="Avid Bin (*.avb)")
		
		if not files:
			return
		
		self.set_bins(files)