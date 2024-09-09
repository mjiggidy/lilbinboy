from PySide6 import QtCore, QtGui, QtWidgets
from timecode import Timecode
from . import logic_trt


class TRTTreeViewHeaderItem(QtCore.QObject):

	def __init__(self, text:str, key:str):

		super().__init__()

		self._text = str(text)
		self._key  = str(key)

	def header_data(self, role:QtCore.Qt.ItemDataRole=QtCore.Qt.ItemDataRole.DisplayRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.name()
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return self.field()
	
	def item_data(self, bin_dict:dict, role:QtCore.Qt.ItemDataRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return str(bin_dict.get(self.field(), ""))
		
		if role == QtCore.Qt.ItemDataRole.InitialSortOrderRole:
			return bin_dict.get(self.field(),"")
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return bin_dict
	
	def name(self) -> str:
		return self._text
	
	def field(self) -> str:
		return self._key

class TRTTreeViewHeaderDuration(TRTTreeViewHeaderItem):

	def item_data(self, bin_dict:dict, role:QtCore.Qt.ItemDataRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return str(bin_dict.get(self.field(), "")).lstrip("0:")
		
		elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
			return QtGui.Qt.AlignmentFlag.AlignRight | QtGui.Qt.AlignmentFlag.AlignVCenter
		
		elif role == QtCore.Qt.ItemDataRole.FontRole:
			return QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont)
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return bin_dict
		
		elif role == QtCore.Qt.ItemDataRole.InitialSortOrderRole:
			return int(bin_dict.get("duration_total",""))
	
	def header_data(self, role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole):
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.name()
		
		elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
			return QtGui.Qt.AlignmentFlag.AlignRight
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return self.field()
		
class TRTTreeViewHeaderIcon(TRTTreeViewHeaderItem):

	def item_data(self, bin_dict:dict, role:QtCore.Qt.ItemDataRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return ""
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return bin_dict
		
		elif role == QtCore.Qt.ItemDataRole.InitialSortOrderRole:
			return 0
		
		elif role == QtCore.Qt.ItemDataRole.DecorationRole:
			return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FolderOpen)
	
	def header_data(self, role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole):
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.name()
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return self.field()
		
class TRTTreeViewHeaderBinLock(TRTTreeViewHeaderItem):

	def item_data(self, bin_dict:dict, role:QtCore.Qt.ItemDataRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return ""
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return bin_dict
		
		elif role == QtCore.Qt.ItemDataRole.InitialSortOrderRole:
			return 0
		
		elif role == QtCore.Qt.ItemDataRole.DecorationRole:
			return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.SystemLockScreen)
	
	def header_data(self, role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole):
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.name()
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return self.field()
		
class TRTTreeViewHeaderDateTime(TRTTreeViewHeaderItem):

	def item_data(self, bin_dict:dict, role:QtCore.Qt.ItemDataRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return str(bin_dict.get(self.field(), ""))
		
		elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
			return QtGui.Qt.AlignmentFlag.AlignRight | QtGui.Qt.AlignmentFlag.AlignVCenter
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return bin_dict
		
		elif role == QtCore.Qt.ItemDataRole.InitialSortOrderRole:
			return int(bin_dict.get(self.field()).timestamp())
	
	def header_data(self, role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole):
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.name()
		
		elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
			return QtGui.Qt.AlignmentFlag.AlignRight
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return self.field()

class TRTModel(QtCore.QObject):

	sig_data_changed = QtCore.Signal()

	LFOA_PERFS_PER_FOOT = 16

	def __init__(self, bin_info_list:list[logic_trt.BinInfo]=None):
		super().__init__()

		self._data = bin_info_list or []

		# TODO: Deal with
		self._fps = 24
		self._trim_head = Timecode("8:00", rate=self._fps)
		self._trim_tail = Timecode("3:00", rate=self._fps)
	
	def sequence_count(self) -> int:
		"""Number of sequences being considered"""
		return len(self._data)
	
	def bin_count(self) -> int:
		"""Number of individual bins involved in this"""
		return len(set(b.path for b in self._data))
	
	def total_runtime(self) -> Timecode:
		
		trt = Timecode(0, rate=self._fps)

		for bin_info in self._data:
			reel_info = bin_info.reel
			trt += reel_info.duration_total - self._trim_head_amount(reel_info) - self._trim_tail_amount(reel_info)
		
		return trt
	
	def rate(self) -> int:
		return self._fps
	
	def setRate(self, rate:int) -> int:
		self._fps = rate
		self.sig_data_changed.emit()
	
	def trimFromHead(self) -> Timecode:
		return self._trim_head
	
	def setTrimFromHead(self, timecode:Timecode):
		self._trim_head = timecode
		self.sig_data_changed.emit()
	
	def trimFromTail(self) -> Timecode:
		return self._trim_tail
	
	def setTrimFromTail(self, timecode:Timecode):
		self._trim_tail = timecode
		self.sig_data_changed.emit()
	
	def total_lfoa(self) -> str:
		trt = self.total_runtime()
		return self.tc_to_lfoa(trt)
	
	def tc_to_lfoa(self, tc:Timecode) -> str:
		zpadding = len(str(self.LFOA_PERFS_PER_FOOT))
		return str(tc.frame_number // 16) + "+" + str(tc.frame_number % self.LFOA_PERFS_PER_FOOT).zfill(zpadding)
		
	def _trim_head_amount(self, reel_info:logic_trt.ReelInfo) -> Timecode:
		# TODO: Implement markers; indiciate if it was Marker or head trim
		return self._trim_head
	
	def _trim_tail_amount(self, reel_info:logic_trt.ReelInfo) -> Timecode:
		# TODO: Implement markers; indiciate if it was Marker or tail trim
		return self._trim_tail

	
	def set_data(self, bin_info_list:list[logic_trt.BinInfo]):
		self._data = bin_info_list
		self.sig_data_changed.emit()
	
	def item_to_dict(self, index:int):
		
		bin_info = self._data[index]
		reel_info = bin_info.reel

		return {
			"sequence_name": reel_info.sequence_name,
			"duration_total": reel_info.duration_total,
			"duration_trimmed": reel_info.duration_total - self._trim_head - self._trim_tail,
			"head_trimmed": self._trim_head,
			"tail_trimmed": self._trim_tail,
			"lfoa": self.tc_to_lfoa(reel_info.duration_total - self._trim_tail - 1), # TODO: Think through the -1 but I think it makes sense being zero-based instead of 1-based for durations? Like, LFOA may be on 0+00 but that means it's 0+01 frame long
			"date_modified": reel_info.date_modified,
			"bin_path": bin_info.path,
			"bin_lock": bin_info.lock
		}
	

class TRTViewModel(QtCore.QAbstractItemModel):
	
	def __init__(self, trt_model:TRTModel, headers_list:list[TRTTreeViewHeaderItem]=None):
		"""Create and setup a new model"""
		super().__init__()

		self.set_model(trt_model)
		self._headers = headers_list or []

		self.model().sig_data_changed.connect(self.modelReset)
		
		# Typically a list of data here
		# Typically a dict of header keys and values here
	
	def set_model(self, trt_model:TRTModel):
		self._model = trt_model
		self.modelReset.emit()
	
	def model(self) -> TRTModel:
		return self._model
	
	def set_headers(self, headers:list[TRTTreeViewHeaderItem]):
		self._headers = headers
		self.headerDataChanged.emit(QtCore.Qt.Orientation.Horizontal, 0, len(self._headers)-1)
	
	def index(self, row:int, column:int, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> QtCore.QModelIndex:
		"""Returns the index of the item in the model specified by the given row, column and parent index."""
		return self.createIndex(row, column, self.model().item_to_dict(row))
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Returns the parent of the model item with the given index. If the item has no parent, an invalid QModelIndex is returned."""
		return QtCore.QModelIndex()

	def rowCount(self, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Returns the number of rows under the given parent. When the parent is valid it means that is returning the number of children of parent."""
		if parent.isValid():
			return 0
		else:
			return self.model().sequence_count()
	
	def columnCount(self, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Returns the number of columns for the children of the given parent."""
		return len(self._headers)

	def data(self, index:QtCore.QModelIndex, role:int=QtCore.Qt.ItemDataRole.DisplayRole) -> QtCore.QObject:
		"""Returns the data stored under the given role for the item referred to by the index."""
		header = self._headers[index.column()]
		return header.item_data(self.model().item_to_dict(index.row()), role)

	def headerData(self, section:int, orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal, role:int=QtCore.Qt.ItemDataRole.DisplayRole) -> QtCore.QObject:
		"""Returns the data for the given role and section in the header with the specified orientation."""
		return self._headers[section].header_data(role)
	
class TRTViewSortModel(QtCore.QSortFilterProxyModel):
	pass

class TRTTreeView(QtWidgets.QTreeView):
	"""TRT Readout"""
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setColumnWidth(0, 24)
		self.setColumnWidth(1, 128)
		self.setAlternatingRowColors(True)
		self.setIndentation(0)
		self.setSortingEnabled(True)
		self.sortByColumn(1, QtCore.Qt.SortOrder.AscendingOrder)