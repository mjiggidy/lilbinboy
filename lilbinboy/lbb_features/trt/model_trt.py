
import enum
import avbutils
from datetime import datetime
from PySide6 import QtCore, QtGui, QtWidgets
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

	sig_sequence_added = QtCore.Signal(logic_trt.TimelineInfo)
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

	def __init__(self, bin_info_list:list[logic_trt.TimelineInfo]=None):
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
			trt += self.getSequenceTrimmedDuration(bin_info)
		
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
		locked = 0
		unique_bins = set()

		for timeline in self._data:
			if timeline.bin_path in unique_bins:
				continue
			unique_bins.add(timeline.bin_path)
			if timeline.bin_lock:
				locked += 1

		return locked
	
	def tc_to_lfoa(self, tc:Timecode) -> str:
		zpadding = len(str(self.LFOA_PERFS_PER_FOOT))
		#tc = max(tc, Timecode(0, rate=self.rate()))
		return str(tc.frame_number // 16) + "+" + str(tc.frame_number % self.LFOA_PERFS_PER_FOOT).zfill(zpadding)
		
	def _trim_head_amount(self) -> Timecode:
		# TODO: Implement markers; indiciate if it was Marker or head trim
		return self._trim_head
	
	def _trim_tail_amount(self) -> Timecode:
		# TODO: Implement markers; indiciate if it was Marker or tail trim
		return self._trim_tail

	
	def set_data(self, bin_info_list:list[logic_trt.TimelineInfo]):
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
			self.sig_data_changed.emit()
		else:
			print("Got weird one:", marker_preset_name, str(type(marker_preset_name)))

	@QtCore.Slot(str)
	def set_active_tail_marker_preset_name(self, marker_preset_name:str|None):
		"""User has set a tail marker preset"""
		
		if not marker_preset_name or marker_preset_name in self.marker_presets():
			self._tail_marker_preset_name = marker_preset_name or None
			self.sig_tail_marker_preset_changed.emit(self._tail_marker_preset_name)
			self.sig_data_changed.emit()
		else:
			print("Noo", marker_preset_name)

	
	def marker_presets(self) -> dict[str, markers_trt.LBMarkerPreset]:
		return self._marker_presets
	
	#
	# Actual bin/timeline data model stuff here
	#
	
	def add_timelines_from_bin(self, bin_info:list[logic_trt.TimelineInfo]):
		"""Given all timelines in a bin, add it depending on the SequenceSelection mode"""

		if not bin_info:
			# TODO: Think about doing something with the interface or like... you know
			return

		if self._sequence_selection_mode is SequenceSelectionMode.ALL_SEQUENCES_PER_BIN:
			for timeline_info in bin_info:
				self.add_sequence(timeline_info)
		
		else:
			self.add_sequence(sorted(bin_info, key=lambda timeline: timeline.date_modified, reverse=True)[0])
			

	def add_sequence(self, sequence_info:logic_trt.TimelineInfo):
		self._data.insert(0, sequence_info)
		self.sig_sequence_added.emit(sequence_info)
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
		for _ in range(len(self.data())):
			self.remove_sequence(0)
	
	def data(self):
		return self._data
	
	#
	# Item To Dict Methods
	#
	
	def getSequenceName(self, sequence_info:logic_trt.TimelineInfo) -> str:
		return sequence_info.timeline_name
	
	def getSequenceColor(self, sequence_info:logic_trt.TimelineInfo) -> QtGui.QRgba64|None:
		return QtGui.QRgba64.fromRgba64(*sequence_info.timeline_color.as_rgb16(), sequence_info.timeline_color.max_16b()) if sequence_info.timeline_color else None
	
	def getSequenceStartTimecode(self, sequence_info:logic_trt.TimelineInfo) -> Timecode:
		return sequence_info.timeline_tc_range.start
	
	def getSequenceTotalDuration(self, sequence_info:logic_trt.TimelineInfo) -> Timecode:
		return sequence_info.timeline_tc_range.duration
	
	def getSequenceTrimmedDuration(self, sequence_info:logic_trt.TimelineInfo) -> Timecode:
		return max(Timecode(0, rate=self.rate()), self.getSequenceTotalDuration(sequence_info) - self.getSequenceTrimFromHead(sequence_info) - self.getSequenceTrimFromTail(sequence_info))
	
	def getSequenceTrimFromHead(self, sequence_info:logic_trt.TimelineInfo) -> Timecode:
		
		if self.activeHeadMarkerPreset():
			matched_marker = self.matchMarkersToPreset(self.activeHeadMarkerPreset(), sorted(sequence_info.markers, key=lambda m: m.frm_offset))
			if matched_marker:
				return Timecode(matched_marker.frm_offset, rate=self.rate())

		return self.trimFromHead()
	
	def getSequenceTrimFromTail(self, sequence_info:logic_trt.TimelineInfo) -> Timecode:
		
		if self.activeTailMarkerPreset():
			matched_marker = self.matchMarkersToPreset(self.activeTailMarkerPreset(), sorted(sequence_info.markers, key=lambda m: m.frm_offset, reverse=True))
			if matched_marker:
				return Timecode(matched_marker.frm_offset, rate=self.rate())
		
		return self.trimFromTail()
	
	def getSequenceFFOATimecode(self, sequence_info:logic_trt.TimelineInfo) -> Timecode:
		return self.getSequenceStartTimecode(sequence_info) + self.getSequenceTrimFromHead(sequence_info)
	
	def getSequenceLFOATimecode(self, sequence_info:logic_trt.TimelineInfo) -> Timecode:
		return self.getSequenceStartTimecode(sequence_info) + self.getSequenceTotalDuration(sequence_info) - self.getSequenceTrimFromTail(sequence_info) - 1
	
	def getSequenceFFOAFeetFrames(self, sequence_info:logic_trt.TimelineInfo) -> str:
		return self.tc_to_lfoa(self.getSequenceTrimFromHead(sequence_info))
	
	def getSequenceLFOAFeetFrames(self, sequence_info:logic_trt.TimelineInfo) -> str:
		return self.tc_to_lfoa(self.getSequenceTotalDuration(sequence_info) - self.getSequenceTrimFromTail(sequence_info) -1)
	
	def getSequenceDateModified(self, sequence_info:logic_trt.TimelineInfo) -> datetime:
		return sequence_info.date_modified
	
	def getSequenceDateCreated(self, sequence_info:logic_trt.TimelineInfo) -> datetime:
		return sequence_info.date_created
	
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
	

	
	
	def item_to_dict(self, timeline_info:logic_trt.TimelineInfo):

		return {
			"sequence_name": 	treeview_trt.TRTStringItem(self.getSequenceName(timeline_info)),
			"sequence_color": 	treeview_trt.TRTClipColorItem(self.getSequenceColor(timeline_info)),
			"sequence_start_tc":treeview_trt.TRTTimecodeItem(self.getSequenceStartTimecode(timeline_info)),
			"duration_total": 	treeview_trt.TRTDurationItem(self.getSequenceTotalDuration(timeline_info)),
			"duration_trimmed": treeview_trt.TRTDurationItem(self.getSequenceTrimmedDuration(timeline_info)),
			"head_trimmed": 	treeview_trt.TRTDurationItem(self.getSequenceTrimFromHead(timeline_info)),
			"tail_trimmed": 	treeview_trt.TRTDurationItem(self.getSequenceTrimFromTail(timeline_info)),
			"ffoa_tc":			treeview_trt.TRTTimecodeItem(self.getSequenceFFOATimecode(timeline_info)),
			"ffoa_ff":			treeview_trt.TRTFeetFramesItem(self.getSequenceFFOAFeetFrames(timeline_info)),
			"lfoa_tc":			treeview_trt.TRTTimecodeItem(self.getSequenceLFOATimecode(timeline_info)),
			"lfoa_ff": 			treeview_trt.TRTFeetFramesItem(self.getSequenceLFOAFeetFrames(timeline_info)), # TODO: Need a an AbstractItem type for this
			"date_modified": 	treeview_trt.TRTStringItem(self.getSequenceDateModified(timeline_info)),	# TODO: Need an Item type fro this
			"date_created":		treeview_trt.TRTStringItem(self.getSequenceDateCreated(timeline_info)),
			"bin_path": 		treeview_trt.TRTPathItem(timeline_info.bin_path),
			"bin_lock": 		treeview_trt.TRTBinLockItem(timeline_info.bin_lock)
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
			treeview_trt.TRTTreeViewHeaderItem("Date Created","date_created"),
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

	def updateSequenceInfo(self, idx:int, sequence_info:dict[str, treeview_trt.TRTAbstractItem]):
		idx_start = self.index(idx, 2)
		idx_end = self.index(idx, self.columnCount()-1)
		self._data[idx] = sequence_info
		self.dataChanged.emit(idx_start, idx_end)
	
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