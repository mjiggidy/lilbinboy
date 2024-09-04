from PySide6 import QtCore, GtGui, QtWidgets
from timecode import Timecode
from . import logic_trt

class TRTTreeViewHeaderItem(QtCore.QObject):

	def __init__(self, text:str, key:str):

		super().__init__()

		self._text = str(text)
		self._key  = str(key)
	
	def data(self, role:QtCore.Qt.ItemDataRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self._text
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return self._key

class TRTModel(QtCore.QObject):

	sig_data_changed = QtCore.Signal()

	def __init__(self, bin_info_list:list[logic_trt.BinInfo]):
		super().__init__(self)

		self._data = bin_info_list

		# TODO: Deal with
		self._fps = 24
		self._trim_head = Timecode("8:00", self._fps)
		self._trim_tail = Timecode("4:00", self._fps)
	
	def set_data(self, bin_info_list:list[logic_trt.BinInfo]):
		self._data = bin_info_list
		self.sig_data_changed()
	
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
	

class TRTTreeView(QtWidgets.QTreeWidget):
	"""TRT Readout"""
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setColumnWidth(0, 24)
		self.setColumnWidth(1, 128)
		self.setAlternatingRowColors(True)
		self.setIndentation(0)
		self.setSortingEnabled(True)
		self.sortByColumn(1, QtCore.Qt.SortOrder.AscendingOrder)