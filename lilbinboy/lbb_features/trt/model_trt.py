
import enum
import avbutils
from datetime import datetime, timezone
from PySide6 import QtCore, QtGui
from timecode import Timecode, TimecodeRange
from lilbinboy.lbb_features.trt import logic_trt, markers_trt, wdg_sequence_treeview

class SequenceSelectionMode(enum.Enum):
	"""Modes for choosing sequences from a bin"""

	ONE_SEQUENCE_PER_BIN  = "Single"
	"""Select only one sequence from a given bin"""

	ALL_SEQUENCES_PER_BIN = "All"
	"""Select all sequences from a given bin"""


class SingleSequenceSelectionProcess:
	"""Data for selecting a single sequence"""

	class AbstractSequenceFilter:
		def validate(self, timeline_info:logic_trt.TimelineInfo) -> bool:
			"""Test the timeline against the filter"""
			pass

	class NameContainsFilter(AbstractSequenceFilter):
		"""Sequence name contains..."""
		def __init__(self, name:str):
			# TODO: Maybe list of names, and AND or OR
			self._name = str(name)
		
		def name(self) -> str:
			return self._name
		
		def validate(self, timeline_info:logic_trt.TimelineInfo) -> bool:
			return self._name.lower() in timeline_info.timeline_name.lower()
	
	class ClipColorFilter(AbstractSequenceFilter):
		"""Clip color is set to..."""
		def __init__(self, colors:list[QtGui.QColor]):
			self._colors = colors
		
		def colors(self) -> list[QtGui.QColor]:
			return self._colors
		
		def validate(self, timeline_info:logic_trt.TimelineInfo) -> bool:
			return QtGui.QColor.fromRgba64(*timeline_info.timeline_color.as_rgba16()) in self._colors if timeline_info.timeline_color else False
		

	SORT_COLUMNS = ["Name", "Start Timecode", "Creation Date", "Modified Date"]

	def __init__(self):
		self._sort_column:str = "Name"
		self._sort_direction:str = "Descending"
		self._filters:list["AbstractSequenceFilter"] = []

	def sortColumn(self) -> str:
		return self._sort_column
	
	def setSortColumn(self, column:str):
		if column not in self.SORT_COLUMNS:
			raise ValueError(f"Column {column} is not a valid column")
		self._sort_column = str(column)
	
	def sortDirection(self) -> QtCore.Qt.SortOrder:
		return self._sort_direction
	
	def setSortDirection(self, direction:QtCore.Qt.SortOrder):
		self._sort_direction = QtCore.Qt.SortOrder(direction)

	def filters(self) -> list[AbstractSequenceFilter]:
		"For now, filters will just b"
		return self._filters
	
	def setFilters(self, filters:list[AbstractSequenceFilter]):
		self._filters = filters
	
	def getSingleSequence(self, timelines:list[logic_trt.TimelineInfo]) -> logic_trt.TimelineInfo|None:
		"""Get a seequence based on this process"""

		# Sort first
		sort_reversed = self.sortDirection() == QtCore.Qt.SortOrder.DescendingOrder
		
		if self.sortColumn() == "Name":
			timelines_sorted = sorted(timelines, reverse=sort_reversed, key=lambda t: avbutils.human_sort(t.timeline_name))
		elif self.sortColumn() == "Start Timecode":
			timelines_sorted = sorted(timelines, reverse=sort_reversed, key=lambda t: t.timeline_tc_range.start)
		elif self.sortColumn() == "Creation Date":
			timelines_sorted = sorted(timelines, reverse=sort_reversed, key=lambda t: t.date_created)
		elif self.sortColumn() == "Modified Date":
			timelines_sorted = sorted(timelines, reverse=sort_reversed, key=lambda t: t.date_modified)
		else:
			raise KeyError(f"No sort method defined for ", self.sortColumn())
		
		#if not self.filters():
		#	return timelines_sorted[0]
		
		# Do filters
		for t in timelines_sorted:
			if all(f.validate(t) for f in self.filters()):
				return t
		
		return None
		


class TRTDataModel(QtCore.QObject):

	class CalculatedTimelineInfo:
		"""Cached and calculated timeline info based on current trims, etc"""

		def __init__(self, timeline_info:logic_trt.TimelineInfo):
			
			self._timeline_info = timeline_info

			# Basic info interpreted to Qt objects
			self._clip_color = QtGui.QColor.fromRgba64(*self._timeline_info.timeline_color.as_rgb16(), self._timeline_info.timeline_color.max_16b()) if self._timeline_info.timeline_color else QtGui.QColor()
			self._date_modified = QtCore.QDateTime(self._timeline_info.date_modified.astimezone(timezone.utc))
			self._date_created = QtCore.QDateTime(self._timeline_info.date_created.astimezone(timezone.utc))
			self._bin_file_path = QtCore.QFileInfo(self._timeline_info.bin_path)

			# User settings
			self._global_ffoa = Timecode(0, rate=self._timeline_info.timeline_tc_range.rate)
			self._global_lfoa = Timecode(0, rate=self._timeline_info.timeline_tc_range.rate)

			self._marker_ffoa = None
			self._marker_lfoa = None

			# Calculated from user settings
			self._active_ffoa_offset = self._global_ffoa
			self._active_lfoa_offset = self._global_lfoa

			self._timecode_trimmed = self._timeline_info.timeline_tc_range

		def timelineName(self) -> str:
			"""Timeline name"""
			return self._timeline_info.timeline_name
		
		def binFilePath(self) -> QtCore.QFileInfo:
			"""Bin file path"""
			return self._bin_file_path
		
		def binLockInfo(self) -> avbutils.LockInfo|None:
			"""Bin lock info if available"""
			return self._timeline_info.bin_lock
		
		def timelineColor(self) -> QtGui.QColor:
			"""Timeline clip color"""
			return self._clip_color
		
		def timelineTimecodeExtents(self) -> TimecodeRange:
			"""Full timecode extents of the timeline (without trims)"""
			return self._timeline_info.timeline_tc_range
		
		def timelineTimecodeTrimmed(self) -> TimecodeRange:
			"""Trimmed timecode range (FFOA -> LFOA)"""
			return self._timecode_trimmed
		
		def timelineDateModified(self) -> QtCore.QDateTime:
			"""Timeline date modified"""
			return self._date_modified
		
		def timelineDateCreated(self) -> QtCore.QDateTime:
			"""Timeline date created"""
			return self._date_created

		def markerFFOA(self) -> avbutils.MarkerInfo|None:
			"""Matched marker currently in use for FFOA (or `None`)"""
			return self._marker_ffoa
		
		def markerLFOA(self) -> avbutils.MarkerInfo|None:
			"""Matched marker currently in use for LFOA (or `None`)"""
			return self._marker_lfoa
		
		def ffoaOffset(self) -> Timecode:
			"""Duration from head to FFOA"""
			return self._active_ffoa_offset
		
		def lfoaOffset(self) -> Timecode:
			"""Duration from LFOA to tail"""
			return self._active_lfoa_offset
		
		# Setters & Dynamic stuff
		def setGlobalFFOA(self, ffoa:Timecode):
			"""Default FFOA offset used "globally" for each timeline unless a marker match overrides this"""
			
			if ffoa.rate != self._timecode_trimmed.rate:
				raise ValueError("FFOA duration rate must match the timeline's timecode rate")
			
			self._global_ffoa = ffoa
			self._updateFFOAOffset()

		def setGlobalLFOA(self, lfoa:Timecode):
			"""Default LFOA offset used "globally" for each timeline unless a marker match overrides this"""
			
			if lfoa.rate != self._timecode_trimmed.rate:
				raise ValueError("LFOA duration rate must match the timeline's timecode rate")
			
			self._global_lfoa = lfoa
			self._updateLFOAOffset()

		def findMarkerFFOAFromPreset(self, marker_preset:markers_trt.LBMarkerPreset):
			"""See if we can match us some of them marker for FFOA"""

			if marker_preset is None:
				self._marker_ffoa = None

			else:
				self._marker_ffoa = self._findMarkerFromPreset(
					marker_preset,
					sorted(self._timeline_info.markers, key=lambda m: m.frm_offset)
				)

			self._updateFFOAOffset()

			return self.markerFFOA()

		def findMarkerLFOAFromPreset(self, marker_preset:markers_trt.LBMarkerPreset):
			"""See if we can match us some of them marker for LFOA"""

			if marker_preset is None:
				self._marker_lfoa = None

			else:
				self._marker_lfoa = self._findMarkerFromPreset(
					marker_preset,
					sorted(self._timeline_info.markers, key=lambda m: m.frm_offset, reverse=True)
				)

			self._updateLFOAOffset()

			return self.markerLFOA()
		
		# Helpers
		def _updateFFOAOffset(self):
			"""Set the frame offset to the FFOA"""
			# Call this after any potential changes to FFOA criteria

			frame_offset = self.markerFFOA().frm_offset if self.markerFFOA() else self._global_ffoa.frame_number

			self._active_ffoa_offset = Timecode(frame_offset, rate=self._timecode_trimmed.rate)

			self._timecode_trimmed = TimecodeRange(
				start = self.timelineTimecodeExtents().start + frame_offset,
				end   = max(self._timecode_trimmed.end,self.timelineTimecodeExtents().start + frame_offset)
			)

		def _updateLFOAOffset(self):
			"""Set the frame offset to the FFOA"""
			# Call this after any potential changes to LFOA criteria

			frame_offset = (self.timelineTimecodeExtents().duration - self.markerLFOA().frm_offset - 1) if self.markerLFOA() else self._global_lfoa.frame_number

			self._active_lfoa_offset = Timecode(frame_offset, rate=self._timecode_trimmed.rate)

			#print("Set to", self._timecode_trimmed.start, "End", self.timelineTimecodeExtents().start + frame_offset)

			self._timecode_trimmed = TimecodeRange(
				start = self._timecode_trimmed.start,
				end   = max(self.timelineTimecodeExtents().end - frame_offset, self._timecode_trimmed.start)
			)

		@classmethod
		def _findMarkerFromPreset(self, marker_preset:markers_trt.LBMarkerPreset, marker_list:list[avbutils.MarkerInfo]):
			"""Match a marker to the given preset criteria"""

			for marker_info in marker_list:

				if marker_preset.color is not None and marker_info.color.value != marker_preset.color:
					continue
				if marker_preset.comment is not None and marker_preset.comment not in marker_info.comment:
					continue
				if marker_preset.author is not None and marker_preset.author not in marker_info.user:
					continue
				return marker_info
			
			return None


			
	sig_trt_changed = QtCore.Signal(Timecode)
	"""Something happen that affects TRT calculation"""

	sig_sequence_selection_mode_changed = QtCore.Signal(SequenceSelectionMode)
	"""User changed sequence selection mode"""
	sig_sequence_selection_process_changed = QtCore.Signal(SingleSequenceSelectionProcess)
	"""User changed sequence selection criteria"""

	sig_bins_changed = QtCore.Signal(list)
	"""Bins (sequnces?) were added or removed"""

	sig_sequence_added = QtCore.Signal(CalculatedTimelineInfo)
	"""BinInfo for a new bin added"""
	sig_sequence_removed = QtCore.Signal(int)
	"""Row index for a sequence removed"""

	sig_data_changed  = QtCore.Signal()

	sig_rate_changed = QtCore.Signal(int)
	"""Timecode rate has changed"""

	sig_head_trim_tc_changed = QtCore.Signal(Timecode)
	"""Global FFOA offset changed"""
	sig_tail_trim_tc_changed = QtCore.Signal(Timecode)
	"""Global LFOA offset changed"""
	sig_total_trim_tc_changed = QtCore.Signal(Timecode)
	"""Final adjustment changed"""

	sig_marker_presets_model_changed = QtCore.Signal(dict)
	"""Marker match criteria presets model has been updated"""
	sig_head_marker_preset_changed   = QtCore.Signal(str)
	"""User chose a head marker preset"""
	sig_tail_marker_preset_changed   = QtCore.Signal(str)
	"""User chose a tail marker preset"""

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


	def __init__(self):
		super().__init__()

		from typing import Self

		self._data:list[Self.CalculatedTimelineInfo] = []
		self._marker_presets:dict[str, markers_trt.LBMarkerPreset] = dict()

		# TODO: Deal with
		self._fps = 24
		self._trim_head    = Timecode("8:00", rate=self._fps)
		self._trim_tail    = Timecode("4:00", rate=self._fps)
		self._trim_total   = Timecode(0, rate=self._fps)
		self._adjust_total = Timecode(0, rate=self._fps)

		# Settings
		self._sequence_selection_mode    = SequenceSelectionMode.ONE_SEQUENCE_PER_BIN
		self._sequence_selection_process = SingleSequenceSelectionProcess()

		# Marker presets
		self._head_marker_preset_name = None
		self._tail_marker_preset_name = None
	
	#
	# Statz
	#
	def sequence_count(self) -> int:
		"""Number of sequences being considered"""
		return len(self._data)
	
	def bin_count(self) -> int:
		"""Number of individual bins involved in this"""
		return len(set(b.binFilePath() for b in self._data))
	
	def total_runtime(self) -> Timecode:
		"""Total running time"""
		trt = Timecode(0, rate=self._fps)

		for timeline_info in self._data:
			trt += timeline_info.timelineTimecodeTrimmed().duration
		
		return max(Timecode(0, rate=self.rate()), trt + self.trimTotal())

	def total_lfoa(self) -> str:
		"""Total running length (F+F)"""
		trt = self.total_runtime()
		return self.tc_to_lfoa(trt)
	
	def locked_bin_count(self) -> int:
		"""Bins that were locked while reading"""
		locked = 0
		unique_bins = set()

		for timeline in self._data:
			if timeline.binFilePath().absoluteFilePath() in unique_bins:
				continue
			unique_bins.add(timeline.binFilePath().absoluteFilePath())
			if timeline.binLockInfo():
				locked += 1

		return locked
	
	#
	# Modez
	#
	def sequenceSelectionMode(self) -> SequenceSelectionMode:
		return self._sequence_selection_mode

	def setSequenceSelectionMode(self, mode:SequenceSelectionMode):
		
		if mode is self.sequenceSelectionMode():
			return
		
		self._sequence_selection_mode = mode
		self.sig_sequence_selection_mode_changed.emit(mode)
	
	def sequenceSelectionProcess(self) -> SingleSequenceSelectionProcess:
		"""Process for selecting a single sequence from a bin"""
		return self._sequence_selection_process
	
	def setSequenceSelectionProcess(self, process:SingleSequenceSelectionProcess):
		"""Set the psrocess for selecting a single sequence from a bin"""
		if not isinstance(process, SingleSequenceSelectionProcess):
			raise TypeError("Not a valid Sequence Selection Process")
		self._sequence_selection_process = process
		
		self.sig_sequence_selection_process_changed.emit(self.sequenceSelectionProcess())
	
	def rate(self) -> int:
		return self._fps
	
	def setRate(self, rate:int) -> int:
		if rate < 1:
			print("No!  No!!!!")
			exit()
		self._fps = rate
		self.sig_rate_changed.emit(self.rate())
		self.sig_data_changed.emit()
	
	#
	#	Global FFOA/LFOA trims
	#
	def trimFromHead(self) -> Timecode:
		"""Default FFOA offset from head"""
		return self._trim_head
	
	def setTrimFromHead(self, timecode:Timecode):
		"""Specify the default FFOA offset from head"""
		self._trim_head = timecode
		

		for timeline in self.data():
			timeline.setGlobalFFOA(self.trimFromHead())

		self.sig_data_changed.emit()
		self.sig_head_trim_tc_changed.emit(self.trimFromHead())
		self.sig_trt_changed.emit(self.total_runtime())
	
	def trimFromTail(self) -> Timecode:
		"""Default LFOA offset from tail"""
		return self._trim_tail
	
	def setTrimFromTail(self, timecode:Timecode):
		"""Specify the default LFOA offset from tail"""
		self._trim_tail = timecode
		

		for timeline in self.data():
			timeline.setGlobalLFOA(self.trimFromTail())

		self.sig_data_changed.emit()
		self.sig_tail_trim_tc_changed.emit(self.trimFromTail())
		self.sig_trt_changed.emit(self.total_runtime())

	def trimTotal(self) -> Timecode:
		"""Final adjustment to the TRT (not reel-specific)"""
		return self._trim_total
	
	def trimTotalFF(self) -> str:
		"""Final adjustments to TRT in F+F"""
		return self.tc_to_lfoa(self.trimTotal())

	def setTrimTotal(self, timecode:Timecode):
		"""Specify final adjustments to the TRT (not reel-specific)"""
		self._trim_total = timecode
		self.sig_total_trim_tc_changed.emit(self.trimTotal())
		self.sig_data_changed.emit()

		self.sig_trt_changed.emit(self.total_runtime())
	

	
	# Helper
	def tc_to_lfoa(self, tc:Timecode) -> str:
		zpadding = len(str(self.LFOA_PERFS_PER_FOOT))
		#tc = max(tc, Timecode(0, rate=self.rate()))
		return str(tc.frame_number // 16) + "+" + str(tc.frame_number % self.LFOA_PERFS_PER_FOOT).zfill(zpadding)
	
	#
	#	Marker Match Criteria Presets
	#	
	def marker_presets(self) -> dict[str, markers_trt.LBMarkerPreset]:
		return self._marker_presets
	
	def set_marker_presets(self, marker_presets:dict[str, markers_trt.LBMarkerPreset]):
		self._marker_presets = marker_presets

		# TODO: Try this
		if self.activeHeadMarkerPresetName() and self.activeHeadMarkerPresetName() not in self.marker_presets():
			self.set_active_head_marker_preset_name(None)
		if self.activeTailMarkerPresetName() and self.activeTailMarkerPresetName() not in self.marker_presets():
			self.set_active_tail_marker_preset_name(None)

		# Maybe just re-apply to update?
		# NOTE: Checking for None here to avoid initial setup None-ifying(?) saved settings before they're restored
		if self.activeHeadMarkerPresetName():
			self.set_active_head_marker_preset_name(self.activeHeadMarkerPresetName())
		if self.activeTailMarkerPresetName():
			self.set_active_tail_marker_preset_name(self.activeTailMarkerPresetName())

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

			for timeline in self.data():
				timeline.findMarkerFFOAFromPreset(self.activeHeadMarkerPreset())

			self.sig_head_marker_preset_changed.emit(self._head_marker_preset_name)
			self.sig_data_changed.emit()

			self.sig_trt_changed.emit(self.total_runtime())
		else:
			print("Got weird one:", marker_preset_name, str(type(marker_preset_name)))

	@QtCore.Slot(str)
	def set_active_tail_marker_preset_name(self, marker_preset_name:str|None):
		"""User has set a tail marker preset"""
		
		if not marker_preset_name or marker_preset_name in self.marker_presets():
			self._tail_marker_preset_name = marker_preset_name or None

			for timeline in self.data():
				timeline.findMarkerLFOAFromPreset(self.activeTailMarkerPreset())

			self.sig_tail_marker_preset_changed.emit(self._tail_marker_preset_name)
			self.sig_data_changed.emit()

			self.sig_trt_changed.emit(self.total_runtime())
		else:
			print("Noo", marker_preset_name)

	

	
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
				self._add_sequence(self.CalculatedTimelineInfo(timeline_info))
		
		else:
			filtered_sequence = self.sequenceSelectionProcess().getSingleSequence(bin_info)
			if not filtered_sequence:
				return
			self._add_sequence(self.CalculatedTimelineInfo(filtered_sequence))
			

	def _add_sequence(self, sequence_info:CalculatedTimelineInfo):
		"""Add a sequence to the data model"""
		# NOTE: This should be called from add_timelines_from_bin

		# Set 'er up
		sequence_info.setGlobalFFOA(self.trimFromHead())
		sequence_info.setGlobalLFOA(self.trimFromTail())

		sequence_info.findMarkerFFOAFromPreset(self.activeHeadMarkerPreset())
		sequence_info.findMarkerLFOAFromPreset(self.activeTailMarkerPreset())

		self._data.insert(0, sequence_info)
		self.sig_sequence_added.emit(sequence_info)
		self.sig_bins_changed.emit(self.binsUsed())
		self.sig_data_changed.emit()

		self.sig_trt_changed.emit(self.total_runtime())

	def binsUsed(self) -> list[str]:
		"""Get a list of bins currently in use"""
		return list(set(sequence.binFilePath().absoluteFilePath() for sequence in self.data()))
	
	def remove_sequence(self, index:int):
		"""Remove a sequence from the data model"""
		try:
			del self._data[index]
		except Exception as e:
			print(f"Didn't remove because {e}")
		
		self.sig_sequence_removed.emit(index)
		
		self.sig_bins_changed.emit(self.binsUsed())
		self.sig_data_changed.emit()

		self.sig_trt_changed.emit(self.total_runtime())

	def clear(self):
		"""Remove ALL sequences from the data model ohohoohoo"""
		for _ in range(len(self.data())):
			self.remove_sequence(0)
	
	def data(self) -> list[CalculatedTimelineInfo]:
		"""All the data"""
		# TODO: Iterator or something?
		return self._data
	
	#
	# Item To Dict Methods
	#
	def item_to_dict(self, timeline_info:CalculatedTimelineInfo) -> dict[str, wdg_sequence_treeview.TRTAbstractItem]:

		_marker_icons = markers_trt.LBMarkerIcons()

		head_marker = timeline_info.markerFFOA()
		tail_marker = timeline_info.markerLFOA()

		head_icon = _marker_icons.ICONS.get(head_marker.color.value).pixmap(10,10) if head_marker else QtGui.QIcon(":/trt/icons/icon_mark_in.svg").pixmap(QtCore.QSize(10,10))
		head_tooltip = str(
			f"""
			<b>Matched FFOA Marker Criteria</b>
			<hr/>
			<b>Location</b>: {head_marker.track_label} @ {timeline_info.timelineTimecodeExtents().start + head_marker.frm_offset}<br/>
			<b>Color</b>: {head_marker.color.value}<br/>
			<b>Author</b>: {head_marker.user}<br/>
			<b>Comment</b>: {head_marker.comment}
			<hr/>
			<b>Date Created</b>: {head_marker.date_created}<br/>
			<b>Date Modified</b>: {head_marker.date_modified}
			"""
		) if head_marker else f"Using global Per-Sequence FFOA: {timeline_info.ffoaOffset()} from head"

		tail_icon = _marker_icons.ICONS.get(tail_marker.color.value).pixmap(10,10) if tail_marker else QtGui.QIcon(":/trt/icons/icon_mark_out.svg").pixmap(QtCore.QSize(10,10))
		tail_tooltip = str(
			f"""
			<b>Matched LFOA Marker Criteria</b>
			<hr/>
			<b>Location</b>: {tail_marker.track_label} @ {timeline_info.timelineTimecodeExtents().start + tail_marker.frm_offset}<br/>
			<b>Color</b>: {tail_marker.color.value}<br/>
			<b>Author</b>: {tail_marker.user}<br/>
			<b>Comment</b>: {tail_marker.comment}
			<hr/>
			<b>Date Created</b>: {tail_marker.date_created}<br/>
			<b>Date Modified</b>: {tail_marker.date_modified}
			"""
		) if tail_marker else f"Using global Per-Sequence LFOA value: {timeline_info.lfoaOffset()} from tail"


		# Prepare your anus

		return {
			"sequence_name":           wdg_sequence_treeview.TRTStringItem(timeline_info.timelineName()),
			"sequence_color":          wdg_sequence_treeview.TRTClipColorItem(timeline_info.timelineColor()),
			"sequence_start_tc":       wdg_sequence_treeview.TRTTimecodeItem(timeline_info.timelineTimecodeExtents().start),
			"duration_total_tc":       wdg_sequence_treeview.TRTDurationItem(timeline_info.timelineTimecodeExtents().duration),
			"duration_total_ff":       wdg_sequence_treeview.TRTFeetFramesItem(timeline_info.timelineTimecodeExtents().duration.frame_number),
			"duration_total_frames":   wdg_sequence_treeview.TRTNumericItem(timeline_info.timelineTimecodeExtents().duration.frame_number),
			"duration_trimmed_tc":     wdg_sequence_treeview.TRTDurationItem(timeline_info.timelineTimecodeTrimmed().duration),
			"duration_trimmed_ff":     wdg_sequence_treeview.TRTFeetFramesItem(timeline_info.timelineTimecodeTrimmed().duration.frame_number),
			"duration_trimmed_frames": wdg_sequence_treeview.TRTNumericItem(timeline_info.timelineTimecodeTrimmed().duration.frame_number),
			"head_trimmed_tc":         wdg_sequence_treeview.TRTDurationItem(timeline_info.ffoaOffset(), icon=head_icon, tooltip=head_tooltip),
			"head_trimmed_ff":         wdg_sequence_treeview.TRTFeetFramesItem(timeline_info.ffoaOffset().frame_number, icon=head_icon, tooltip=head_tooltip),
			"head_trimmed_frames":     wdg_sequence_treeview.TRTNumericItem(timeline_info.ffoaOffset().frame_number, icon=head_icon, tooltip=head_tooltip),
			"tail_trimmed_tc":         wdg_sequence_treeview.TRTDurationItem(timeline_info.lfoaOffset(), icon=tail_icon, tooltip=tail_tooltip),
			"tail_trimmed_ff":         wdg_sequence_treeview.TRTFeetFramesItem(timeline_info.lfoaOffset().frame_number, icon=tail_icon, tooltip=tail_tooltip),
			"tail_trimmed_frames":     wdg_sequence_treeview.TRTNumericItem(timeline_info.lfoaOffset().frame_number, icon=tail_icon, tooltip=tail_tooltip),
			"ffoa_tc":                 wdg_sequence_treeview.TRTTimecodeItem(timeline_info.timelineTimecodeTrimmed().start),
			"ffoa_ff":                 wdg_sequence_treeview.TRTFeetFramesItem(timeline_info.timelineTimecodeTrimmed().start.frame_number),
			"lfoa_tc":                 wdg_sequence_treeview.TRTTimecodeItem(timeline_info.timelineTimecodeTrimmed().end),
			"lfoa_ff":                 wdg_sequence_treeview.TRTFeetFramesItem(timeline_info.ffoaOffset().frame_number + timeline_info.timelineTimecodeTrimmed().duration.frame_number),
			"date_modified":           wdg_sequence_treeview.TRTDateTimeItem(timeline_info.timelineDateModified()),
			"date_created":            wdg_sequence_treeview.TRTDateTimeItem(timeline_info.timelineDateCreated()),
			"bin_path":                wdg_sequence_treeview.TRTPathItem(timeline_info.binFilePath()),
			"bin_lock":                wdg_sequence_treeview.TRTBinLockItem(timeline_info.binLockInfo())
		}
	

class TRTViewModel(QtCore.QAbstractItemModel):
	
	def __init__(self, headers_list:list[wdg_sequence_treeview.TRTTreeViewHeaderItem]=None):
		"""Create and setup a new model"""
		super().__init__()

		self._data:list[dict[str, wdg_sequence_treeview.TRTAbstractItem]] = []
		self._headers:list[wdg_sequence_treeview.TRTTreeViewHeaderItem] = []

		self.setHeaderItems([
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Sequence Color","sequence_color", show_label=False, is_frozen_header=True, display_delegate=wdg_sequence_treeview.TRTClipColorDisplayDelegate),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Sequence Name","sequence_name", is_frozen_header=True),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Full Duration (TC)","duration_total_tc", is_accumulating_value=True),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Full Duration (F+F)","duration_total_ff", is_accumulating_value=True),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Full Duration (Frames)","duration_total_frames", is_accumulating_value=True),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Trimmed Duration (TC)","duration_trimmed_tc", is_accumulating_value=True),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Trimmed Duration (F+F)","duration_trimmed_ff", is_accumulating_value=True),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Trimmed Duration (Frames)","duration_trimmed_frames", is_accumulating_value=True),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Trimmed From Head (TC)", "head_trimmed_tc", is_accumulating_value=True),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Trimmed From Head (F+F)", "head_trimmed_ff", is_accumulating_value=True),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Trimmed From Head (Frames)", "head_trimmed_frames", is_accumulating_value=True),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Trimmed From Tail (TC)", "tail_trimmed_tc", is_accumulating_value=True),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Trimmed From Tail (F+F)", "tail_trimmed_ff", is_accumulating_value=True),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Trimmed From Tail (Frames)", "tail_trimmed_frames", is_accumulating_value=True),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Sequence Start", "sequence_start_tc"),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("FFOA (F+F)", "ffoa_ff"),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("FFOA (TC)", "ffoa_tc"),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("LFOA (F+F)", "lfoa_ff"),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("LFOA (TC)", "lfoa_tc"),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Date Created","date_created"),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Date Modified","date_modified"),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("From Bin","bin_path"),
			wdg_sequence_treeview.TRTTreeViewHeaderItem("Bin Lock","bin_lock"),
		])
	
	def setSequenceInfoList(self, trt_data:list[dict[str,wdg_sequence_treeview.TRTAbstractItem]]):
		self.beginResetModel()
		self._data = trt_data
		self.endResetModel()
	
	def addSequenceInfo(self, sequence_info:dict[str, wdg_sequence_treeview.TRTAbstractItem]):
		self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
		self._data.insert(0, sequence_info)
		self.endInsertRows()

	def updateSequenceInfo(self, idx:int, sequence_info:dict[str, wdg_sequence_treeview.TRTAbstractItem]):
		idx_start = self.index(idx, 2) # Bout dat 2: Skipping sequence_color and sequence_name
		idx_end = self.index(idx, self.columnCount()-1)
		self._data[idx] = sequence_info
		self.dataChanged.emit(idx_start, idx_end)
	
	@QtCore.Slot(int)
	def removeSequenceInfo(self, idx:int):
		self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
		del self._data[idx]
		self.endRemoveRows()
	
	def sequenceInfoList(self) -> list[dict[str, wdg_sequence_treeview.TRTAbstractItem]]:
		return self._data
	
	def setHeaderItems(self, headers:list[wdg_sequence_treeview.TRTTreeViewHeaderItem]):
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

		field = self._headers[index.column()].field()
		item  = self._data[index.row()]

		return item.get(field).data(role)

	def headerData(self, section:int, orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal, role:int=QtCore.Qt.ItemDataRole.DisplayRole) -> QtCore.QObject:
		"""Returns the data for the given role and section in the header with the specified orientation."""
		if orientation == QtCore.Qt.Orientation.Horizontal:
			return self._headers[section].header_data(role)
		else:
			return None
	
	def headers(self) -> list[wdg_sequence_treeview.TRTTreeViewHeaderItem]:
		"""Return all `TRTTreeViewHeaderItem` objects in logical order"""
		return self._headers
	
class TRTViewSortModel(QtCore.QSortFilterProxyModel):
	"""Proxy model to ensure proper sorting"""

	def lessThan(self, left_idx:QtCore.QModelIndex, right_idx:QtCore.QModelIndex) -> bool:
		"""Reimplemented sort function to use InitialSortOrderRole"""
		return left_idx.data(self.sortRole()) < right_idx.data(self.sortRole())
	
	def headers(self) -> list[wdg_sequence_treeview.TRTTreeViewHeaderItem]:
		"""Header items in logical order"""
		return self.sourceModel().headers()