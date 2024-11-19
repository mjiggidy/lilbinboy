
import enum
import avbutils
from datetime import datetime
from PySide6 import QtCore, QtGui
from timecode import Timecode
from . import logic_trt, treeview_trt, markers_trt

class SequenceSelectionMode(enum.Enum):
	"""Modes for choosing sequences from a bin"""

	ONE_SEQUENCE_PER_BIN  = 0,
	"""Select only one sequence from a given bin"""

	ALL_SEQUENCES_PER_BIN = 1
	"""Select all sequences from a given bin"""


class TRTDataModel(QtCore.QObject):

	sig_bins_changed = QtCore.Signal()
	"""Bins (sequnces?) were added or removed"""

	sig_sequence_added = QtCore.Signal(logic_trt.BinInfo)
	"""BinInfo for a new bin added"""
	sig_sequence_removed = QtCore.Signal(int)
	"""Row index for a sequence removed"""

	sig_data_changed  = QtCore.Signal()

	sig_head_trim_tc_changed = QtCore.Signal(Timecode)
	sig_tail_trim_tc_changed = QtCore.Signal(Timecode)
	sig_trims_changed = QtCore.Signal()

	sig_sequence_selection_mode_changed = QtCore.Signal(SequenceSelectionMode)

	sig_marker_presets_model_changed = QtCore.Signal(dict)
	sig_head_marker_preset_changed   = QtCore.Signal(str)
	sig_tail_marker_preset_changed   = QtCore.Signal(str)

	#LFOA_PERFS_PER_FOOT = 8 # 35.8
	LFOA_PERFS_PER_FOOT = 16 # 35.4
	#LFOA_PERFS_PER_FOOT = 21 # 35.3
	#LFOA_PERFS_PER_FOOT = 32 # 35.2
	#LFOA_PERFS_PER_FOOT = 40 # 16.40
	#LFOA_PERFS_PER_FOOT = 20 # 16.20
	#LFOA_PERFS_PER_FOOT = 8 # 65.15
	#LFOA_PERFS_PER_FOOT = 12 # 65.10
	#LFOA_PERFS_PER_FOOT = 15 # 65.8
	#LFOA_PERFS_PER_FOOT = 24 # 65.5
	#LFOA_PERFS_PER_FOOT = 8 # Vista - 8 perfs but 2 perfs per frame - goes 0, 2, 4, 6


	# TODO: Not a great place for these probably
	MAX_8b = (1 << 8) - 1
	"""Maximum 8-bit value"""
	MAX_16b = (1 << 16) - 1
	"""Maximum 16-bit value"""

	def __init__(self, bin_info_list:list[logic_trt.BinInfo]=None):
		super().__init__()

		self._data = bin_info_list or []
		self._marker_presets = dict()

		# TODO: Deal with
		self._fps = 24
		self._trim_head = Timecode("8:00", rate=self._fps)
		self._trim_tail = Timecode("4:00", rate=self._fps)
		self._trim_total = Timecode(0, rate=self._fps)
		self._adjust_total = Timecode(0, rate=self._fps)

		# Settings
		self._sequence_selection_mode = SequenceSelectionMode.ONE_SEQUENCE_PER_BIN

		# Marker presets
		self._head_marker_preset_name = None
		self._tail_marker_preset_name = None
	
	def sequence_count(self) -> int:
		"""Number of sequences being considered"""
		return len(self._data)
	
	def setSequenceSelectionMode(self, mode:SequenceSelectionMode):
		self._sequence_selection_mode = mode
		print(mode)
		self.sig_sequence_selection_mode_changed.emit(mode)
	
	def bin_count(self) -> int:
		"""Number of individual bins involved in this"""
		return len(set(b.path for b in self._data))
	
	def total_runtime(self) -> Timecode:
		
		trt = Timecode(0, rate=self._fps)

		for bin_info in self._data:
			reel_info = bin_info.reel
			trt += reel_info.duration_total - self._trim_head_amount(reel_info) - self._trim_tail_amount(reel_info)
		
		return max(Timecode(0, rate=self.rate()), trt + self.trimTotal())
	
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
		self.sig_head_trim_tc_changed.emit(self.trimFromHead())
		self.sig_trims_changed.emit()
	
	def trimFromTail(self) -> Timecode:
		return self._trim_tail
	
	def setTrimFromTail(self, timecode:Timecode):
		self._trim_tail = timecode
		
		self.sig_data_changed.emit()
		self.sig_tail_trim_tc_changed.emit(self.trimFromTail())
		self.sig_trims_changed.emit()

	def trimTotal(self) -> Timecode:
		return self._trim_total

	def setTrimTotal(self, timecode:Timecode):
		self._trim_total = timecode
		self.sig_data_changed.emit()
		self.sig_trims_changed.emit()
	
	def total_lfoa(self) -> str:
		trt = self.total_runtime()
		return self.tc_to_lfoa(trt)
	
	def locked_bin_count(self) -> int:
		return len([x for x in self.data() if x.lock is not None])
	
	def tc_to_lfoa(self, tc:Timecode) -> str:
		zpadding = len(str(self.LFOA_PERFS_PER_FOOT))
		#tc = max(tc, Timecode(0, rate=self.rate()))
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
		self.sig_bins_changed.emit()
	
	def set_marker_presets(self, marker_presets:dict[str, markers_trt.LBMarkerPreset]):
		self._marker_presets = marker_presets

		# TODO: Try this
		if self.activeHeadMarkerPresetName() and self.activeHeadMarkerPresetName() not in self.marker_presets():
			self.set_active_head_marker_preset_name(None)
		if self.activeTailMarkerPresetName() and self.activeTailMarkerPresetName() not in self.marker_presets():
			self.set_active_tail_marker_preset_name(None)

		self.sig_marker_presets_model_changed.emit(self.marker_presets())

	def activeHeadMarkerPresetName(self) -> str|None:
		"""Active head marker preset name"""
		return self._head_marker_preset_name
	
	def activeHeadMarkerPreset(self) -> markers_trt.LBMarkerPreset|None:
		"""Active head marker preset, or None"""
		return self.marker_presets().get(self.activeHeadMarkerPresetName(), None)
	
	def activeTailMarkerPresetName(self) -> str|None:
		"""Active tail marker preset name"""
		return self._tail_marker_preset_name
	
	def activeTailMarkerPreset(self) -> markers_trt.LBMarkerPreset|None:
		"""Active tail marker preset"""
		return self.marker_presets().get(self.activeTailMarkerPresetName(), None)
	
	@QtCore.Slot(str)
	def set_active_head_marker_preset_name(self, marker_preset_name:str|None):
		"""User has set a head marker preset"""
		
		if not marker_preset_name or marker_preset_name in self.marker_presets():
			self._head_marker_preset_name = marker_preset_name or None
			self.sig_head_marker_preset_changed.emit(self._head_marker_preset_name)
		else:
			print("Got weird one:", marker_preset_name, str(type(marker_preset_name)))

	@QtCore.Slot(str)
	def set_active_tail_marker_preset_name(self, marker_preset_name:str|None):
		"""User has set a tail marker preset"""
		
		if not marker_preset_name or marker_preset_name in self.marker_presets():
			self._tail_marker_preset_name = marker_preset_name or None
			self.sig_tail_marker_preset_changed.emit(self._tail_marker_preset_name)
		else:
			print("Noo", marker_preset_name)

	
	def marker_presets(self) -> dict[str, markers_trt.LBMarkerPreset]:
		return self._marker_presets
	
	def add_bin(self, bin_info:logic_trt.BinInfo):
		self._data.append(bin_info)
		self.sig_sequence_added.emit(bin_info)
		self.sig_bins_changed.emit()
		self.sig_data_changed.emit()
	
	def remove_sequence(self, index:int):
		try:
			del self._data[index]
		except Exception as e:
			print(f"Didn't remove because {e}")
		
		self.sig_sequence_removed.emit(index)
		
		self.sig_bins_changed.emit()
		self.sig_data_changed.emit()

	def clear(self):
		self.set_data([])
	
	def data(self):
		return iter(self._data)
	
	#
	# Item To Dict Methods
	#
	
	def getSequenceName(self, sequence_info:logic_trt.ReelInfo) -> str:
		return sequence_info.sequence_name
	
	def getSequenceColor(self, sequence_info:logic_trt.ReelInfo) -> QtGui.QRgba64|None:
		return QtGui.QRgba64.fromRgba64(*sequence_info.sequence_color.as_rgb16(), sequence_info.sequence_color.max_16b()) if sequence_info.sequence_color else None
	
	def getSequenceStartTimecode(self, sequence_info:logic_trt.ReelInfo) -> Timecode:
		return sequence_info.sequence_tc_range.start
	
	def getSequenceTotalDuration(self, sequence_info:logic_trt.ReelInfo) -> Timecode:
		return sequence_info.duration_total
	
	def getSequenceTrimmedDuration(self, sequence_info:logic_trt.ReelInfo) -> Timecode:
		return max(Timecode(0, rate=self.rate()), sequence_info.duration_total - self._trim_head - self._trim_tail)
	
	def getSequenceTrimFromHead(self, sequence_info:logic_trt.ReelInfo) -> Timecode:
		
		if self.activeHeadMarkerPreset():
			matched_marker = self.matchMarkersToPreset(self.activeHeadMarkerPreset(), sorted(sequence_info.markers, key=lambda m: m.frm_offset))
			if matched_marker:
				return Timecode(matched_marker.frm_offset, rate=self.rate())

		return self.trimFromHead()
	
	def getSequenceTrimFromTail(self, sequence_info:logic_trt.ReelInfo) -> Timecode:
		
		if self.activeTailMarkerPreset():
			matched_marker = self.matchMarkersToPreset(self.activeTailMarkerPreset(), sorted(sequence_info.markers, key=lambda m: m.frm_offset, reverse=True))
			if matched_marker:
				return Timecode(matched_marker.frm_offset, rate=self.rate())
		
		return self.trimFromTail()
	
	def getSequenceFFOATimecode(self, sequence_info:logic_trt.ReelInfo) -> Timecode:
		return self.getSequenceStartTimecode(sequence_info) + self.trimFromHead()
	
	def getSequenceLFOATimecode(self, sequence_info:logic_trt.ReelInfo) -> Timecode:
		return self.getSequenceTotalDuration(sequence_info) - self.getSequenceTrimFromTail(sequence_info) - 1
	
	def getSequenceDateModified(self, sequence_info:logic_trt.ReelInfo) -> datetime:
		return sequence_info.date_modified
	
	def matchMarkersToPreset(self, marker_preset:markers_trt.LBMarkerPreset, marker_list:list[avbutils.MarkerInfo]) -> avbutils.MarkerInfo:

		for marker_info in marker_list:
			if marker_preset.color is not None and marker_info.color.value != marker_preset.color:
				continue
			if marker_preset.comment is not None and marker_info.comment != marker_preset.comment:
				continue
			if marker_preset.author is not None and marker_info.user != marker_preset.author:
				continue
			return marker_info
		return None
	

	
	
	def item_to_dict(self, bin_info:logic_trt.BinInfo):
		
		sequence_info = bin_info.reel

		#if self.activeHeadMarkerPreset():
		#	marker_match = self.matchMarkersToPreset(marker_preset=self.activeHeadMarkerPreset(), marker_list=sorted(sequence_info.markers, key=lambda m: m.frm_offset))
		#	if marker_match:
		#		print(f"MARKER MATCHED:", self.getSequenceStartTimecode(sequence_info) + marker_match)

		return {
			"sequence_name": 	treeview_trt.TRTStringItem(self.getSequenceName(sequence_info)),
			"sequence_color": 	treeview_trt.TRTClipColorItem(self.getSequenceColor(sequence_info)),
			"sequence_start_tc":treeview_trt.TRTTimecodeItem(self.getSequenceStartTimecode(sequence_info)),
			"duration_total": 	treeview_trt.TRTDurationItem(self.getSequenceTotalDuration(sequence_info)),
			"duration_trimmed": treeview_trt.TRTDurationItem(self.getSequenceTrimmedDuration(sequence_info)),
			"head_trimmed": 	treeview_trt.TRTDurationItem(self.getSequenceTrimFromHead(sequence_info)),
			"tail_trimmed": 	treeview_trt.TRTDurationItem(self.getSequenceTrimFromTail(sequence_info)),
			"ffoa_tc":			treeview_trt.TRTTimecodeItem(self.getSequenceFFOATimecode(sequence_info)),
			"ffoa_ff":			treeview_trt.TRTFeetFramesItem(self.tc_to_lfoa(self.getSequenceFFOATimecode(sequence_info))),
			"lfoa_tc":			treeview_trt.TRTTimecodeItem(self.getSequenceLFOATimecode(sequence_info)),
			"lfoa_ff": 			treeview_trt.TRTFeetFramesItem(self.tc_to_lfoa(self.getSequenceLFOATimecode(sequence_info))), # TODO: Need a an AbstractItem type for this
			"date_modified": 	treeview_trt.TRTStringItem(self.getSequenceDateModified(sequence_info)),	# TODO: Need an Item type fro this
			"bin_path": 		treeview_trt.TRTPathItem(bin_info.path),
			"bin_lock": 		treeview_trt.TRTBinLockItem(bin_info.lock)
		}
	

class TRTViewModel(QtCore.QAbstractItemModel):
	
	def __init__(self, headers_list:list[treeview_trt.TRTTreeViewHeaderItem]=None):
		"""Create and setup a new model"""
		super().__init__()

		self._data:list[dict[str, treeview_trt.TRTAbstractItem]] = []
		self._headers:list[treeview_trt.TRTTreeViewHeaderItem]   = headers_list or []

		self.setHeaderItems([
			treeview_trt.TRTTreeViewHeaderItem("","sequence_color", display_delegate=treeview_trt.TRTClipColorDisplayDelegate()),
			treeview_trt.TRTTreeViewHeaderItem("Sequence Name","sequence_name"),
			treeview_trt.TRTTreeViewHeaderItem("Full Duration","duration_total"),
			treeview_trt.TRTTreeViewHeaderItem("Trimmed Duration","duration_trimmed"),
			treeview_trt.TRTTreeViewHeaderItem("Trimmed From Head", "head_trimmed"),
			treeview_trt.TRTTreeViewHeaderItem("Trimmed From Tail", "tail_trimmed"),
			treeview_trt.TRTTreeViewHeaderItem("Sequence Start", "sequence_start_tc"),
			treeview_trt.TRTTreeViewHeaderItem("FFOA (F+F)", "ffoa_ff"),
			treeview_trt.TRTTreeViewHeaderItem("FFOA (TC)", "ffoa_tc"),
			treeview_trt.TRTTreeViewHeaderItem("LFOA (F+F)", "lfoa_ff"),
			treeview_trt.TRTTreeViewHeaderItem("LFOA (TC)", "lfoa_tc"),
			treeview_trt.TRTTreeViewHeaderItem("Date Modified","date_modified"),
			treeview_trt.TRTTreeViewHeaderItem("From Bin","bin_path"),
			treeview_trt.TRTTreeViewHeaderItem("Bin Lock","bin_lock"),
		])
	
	def setSequenceInfoList(self, trt_data:list[dict[str,treeview_trt.TRTAbstractItem]]):
		self.beginResetModel()
		self._data = trt_data
		self.endResetModel()
	
	def addSequenceInfo(self, sequence_info:dict[str, treeview_trt.TRTAbstractItem]):
		self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
		self._data.append(sequence_info)
		self.endInsertRows()
	
	@QtCore.Slot(int)
	def removeSequenceInfo(self, idx:int):
		self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
		del self._data[idx]
		self.endRemoveRows()
	
	def sequenceInfoList(self) -> list[dict[str, treeview_trt.TRTAbstractItem]]:
		return self._data
	
	def setHeaderItems(self, headers:list[treeview_trt.TRTTreeViewHeaderItem]):
		self._headers = headers
		self.headerDataChanged.emit(QtCore.Qt.Orientation.Horizontal, 0, len(self._headers)-1)
	
	def index(self, row:int, column:int, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> QtCore.QModelIndex:
		"""Returns the index of the item in the model specified by the given row, column and parent index."""
		header = self._headers[column]
		return self.createIndex(row, column, header.field())
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Returns the parent of the model item with the given index. If the item has no parent, an invalid QModelIndex is returned."""
		return QtCore.QModelIndex()

	def rowCount(self, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Returns the number of rows under the given parent. When the parent is valid it means that is returning the number of children of parent."""
		if parent.isValid():
			return 0
		else:
			return len(self.sequenceInfoList())
	
	def columnCount(self, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Returns the number of columns for the children of the given parent."""
		return len(self._headers)

	def data(self, index:QtCore.QModelIndex, role:int=QtCore.Qt.ItemDataRole.DisplayRole) -> QtCore.QObject:
		"""Returns the data stored under the given role for the item referred to by the index."""

		#item:treeview_trt.TRTAbstractItem = index.data()
		#return item.data(role)

		field = self._headers[index.column()].field()
		item  = self._data[index.row()]
		#print(field, item)
		return item.get(field).data(role)

	def headerData(self, section:int, orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal, role:int=QtCore.Qt.ItemDataRole.DisplayRole) -> QtCore.QObject:
		"""Returns the data for the given role and section in the header with the specified orientation."""
		return self._headers[section].header_data(role)
	
	def headers(self) -> list[treeview_trt.TRTTreeViewHeaderItem]:
		return self._headers
	
class TRTViewSortModel(QtCore.QSortFilterProxyModel):
	
	def lessThan(self, left_idx:QtCore.QModelIndex, right_idx:QtCore.QModelIndex) -> bool:
		"""Reimplemented sort function to use InitialSortOrderRole"""
		return left_idx.data(QtCore.Qt.ItemDataRole.InitialSortOrderRole) < right_idx.data(QtCore.Qt.ItemDataRole.InitialSortOrderRole)