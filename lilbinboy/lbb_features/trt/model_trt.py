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
	
	def header_data(self, role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole):
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.name()
		
		elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
			return QtGui.Qt.AlignmentFlag.AlignRight
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return self.field()

class TRTModel(QtCore.QObject):

	sig_data_changed = QtCore.Signal()

	def __init__(self, bin_info_list:list[logic_trt.BinInfo]=None):
		super().__init__()

		self._data = bin_info_list or []

		# TODO: Deal with
		self._fps = 24
		self._trim_head = Timecode("8:00", rate=self._fps)
		self._trim_tail = Timecode("4:00", rate=self._fps)
	
	def sequence_count(self) -> int:
		return len(self._data)
	
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
			"lfoa": str((reel_info.duration_total - self._trim_tail).frame_number // 16) + "+" + str((reel_info.duration_total - self._trim_tail).frame_number % 16).zfill(2),
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