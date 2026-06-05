from __future__ import annotations
import typing, enum, datetime, os, dataclasses
import avbutils, avb
from timecode import Timecode, TimecodeRange
from PySide6 import QtCore, QtGui, QtWidgets
from functools import singledispatch

#from binspector.binitems import binitemtypes

@dataclasses.dataclass(frozen=True)
class BSBinItemInfo:
	"""Bin item info for a given mob"""

	mob_id            :avb.mobid.MobID
	item_type         :avbutils.bins.BinDisplayItemTypes
	tracks            :set[avb.trackgroups.Track]
	primary_timecode  :TimecodeRange|None
	clip_color        :avbutils.compositions.ClipColor|None
	name              :str
	frame_coordinates :tuple[int,int]
	keyframe_offset   :int
	view_items        :dict[int,BSAbstractViewItem|dict[str,BSAbstractViewItem]] # Field ID -> ViewItem or 40 -> dict[term,def]

class BSBinItemDataRoles(enum.IntEnum):
	"""Item Data Roles for Bin Items (extends `QtCore.Qt.ItemDataRole`)"""

	ItemNameRole         = QtCore.Qt.ItemDataRole.UserRole + 1
	"""Bin item name"""

	ItemTypesRole        = enum.auto()
	"""Bin item types under which this is categorized"""

	ClipColorRole        = enum.auto()
	"""Clip color assigned to this item, if any"""

	FrameCoordinatesRole = enum.auto()
	"""Scene coordinates for this thumbnail in Frame View Mode"""

	FrameThumbnailRole   = enum.auto()
	"""Relative frame offset for thumbnail"""

	ScriptNotesRole      = enum.auto()
	"""Data for Script View Mode extended comment"""
	
	ViewItemsRole        = enum.auto()
	"""Return the view item dict"""

	MobID                = enum.auto()
	"""The MobID"""

	TimecodeRangeRole    = enum.auto()
	"""The primary timecode range for this item"""

	FilmTCRangeRole      = enum.auto()
	"""Film TC range"""

	SoundTCRole          = enum.auto()
	"""In-Out frame offset range"""

	AuxTC1RangeRole      = enum.auto()
	"""Timecode range"""

	AuxTC2RangeRole      = enum.auto()
	"""Timecode range"""

	AuxTC3RangeRole     = enum.auto()
	"""Timecode range"""

	AuxTC4RangeRole      = enum.auto()
	"""Timecode range"""

	AuxTC5RangeRole      = enum.auto()
	"""Timecode range"""

	InkNumberRangeRole   = enum.auto()
	"""Ink number range"""

	AuxInkNumberRangeRole= enum.auto()
	"""Ink number range"""

	KNRangeRole          = enum.auto()
	"""In-Out frame offset range"""

	TCMarkInOutRangeRole = enum.auto()
	"""In-Out frame offset range"""

	KNMarkInOutRangeRole = enum.auto()
	"""In-Out keycode offset range"""







	

class BSAbstractViewItem:
	"""An abstract view item for bin item models"""

	def __init__(self, raw_data:typing.Any, icon:QtGui.QIcon|None=None, tooltip:QtWidgets.QToolTip|str|None=None):

		self._data = raw_data
		self._icon = icon
		self._tooltip = tooltip

		self._data_roles = {}
		self._prepare_data()
	
	def _prepare_data(self):
		"""Precalculate them datas for all them roles"""
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:          self.to_string(self._data),
			QtCore.Qt.ItemDataRole.ToolTipRole:          self._tooltip if self._tooltip is not None else repr(self._data),
			QtCore.Qt.ItemDataRole.DecorationRole:       self._icon,
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: self.to_string(self._data),	# QCollator just compares strings
			QtCore.Qt.ItemDataRole.UserRole:             self,
		})
	def raw_data(self) -> typing.Any:
		"""Get the original data for this item in its original format"""
		return self._data

	def data(self, role:QtCore.Qt.ItemDataRole) -> typing.Any:
		"""Get item data for a given role.  By default, returns the raw data as a string."""
		return self._data_roles.get(role, None)
	
	def setData(self, role:QtCore.Qt.ItemDataRole, data:typing.Any):
		"""Override data for a particular role"""
		self._data_roles[role] = data
	
	def itemData(self) -> dict[QtCore.Qt.ItemDataRole, typing.Any]:
		"""Get all item data roles"""
		return self._data_roles
	
	def to_json(self) -> str:
		"""Format as JSON object"""
		return self.data(QtCore.Qt.ItemDataRole.DisplayRole)
	
	@classmethod
	def to_string(cls, data:typing.Any) -> str:
		return str(data)
	
class BSStringViewItem(BSAbstractViewItem):
	"""A standard string"""

	def _prepare_data(self):
		super()._prepare_data()

		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole: self.format_single_line(self.to_string(self._data)),
		})

	def format_single_line(self, input_string:str):
		
		output_string = ""
		
		for c in input_string:
			if not c.isprintable():
				return output_string + "…"
			output_string += c
		
		return output_string

class BSEnumViewItem(BSAbstractViewItem):
	"""Represents an Enum"""

	def __init__(self, raw_data:enum.Enum, *args, **kwargs):
		super().__init__(raw_data, *args, **kwargs)

	def _prepare_data(self):
		super()._prepare_data()

		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DecorationRole:       self._data,
			QtCore.Qt.ItemDataRole.DisplayRole:          self._data.name.replace("_", " ").title(),
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: self.to_string(self._data.value),
		})
	
class BSNumericViewItem(BSAbstractViewItem):
	"""A numeric value"""

	STRING_PADDING:int = 0
	"""Left-side padding for string formatting"""

	def __init__(self, raw_data:int, *args, **kwargs):
		super().__init__(raw_data, *args, **kwargs)

	def _prepare_data(self):
		super()._prepare_data()

		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:          self.to_string(self._data),
			#QtCore.Qt.ItemDataRole.InitialSortOrderRole: self._data,
			QtCore.Qt.ItemDataRole.FontRole:             QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont).family(),
			QtCore.Qt.ItemDataRole.TextAlignmentRole:    QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter,
		})
	
	def to_json(self) -> int:
		return self.data(QtCore.Qt.ItemDataRole.UserRole) # NOTE to self: need to change this to access item's _data
	
	@classmethod
	def to_string(cls, data):
		return super().to_string(data).rjust(cls.STRING_PADDING)

class BSPathViewItem(BSAbstractViewItem):
	"""A file path"""

	def __init__(self, raw_data:str|QtCore.QFileInfo):
		super().__init__(QtCore.QFileInfo(raw_data))
	
	def _prepare_data(self):
		super()._prepare_data()

		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:          self._data.fileName(),
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: self._data.fileName(),
			QtCore.Qt.ItemDataRole.DecorationRole:       QtWidgets.QFileIconProvider().icon(self._data),
			QtCore.Qt.ItemDataRole.ToolTipRole:          QtCore.QDir.toNativeSeparators(self._data.absoluteFilePath()),
		})
	
	def to_json(self) -> str:
		return QtCore.QDir.toNativeSeparators(self.data(QtCore.Qt.ItemDataRole.UserRole).absoluteFilePath())

class BSDateTimeViewItem(BSAbstractViewItem):
	"""A datetime entry"""

	def __init__(self, raw_data:datetime.datetime, format_string:QtCore.Qt.DateFormat|str=QtCore.Qt.DateFormat.TextDate):
		
		self._format_string = format_string
		
		super().__init__(QtCore.QDateTime(raw_data).toLocalTime())
	
	def setFormatString(self, format_string:str):
		"""Set the datetime formatting string used by strftime"""
		self._format_string = format_string
		self._data_roles.update()
	
	def formatString(self) -> str:
		"""The datetime formatting string used by strftime"""
		return self._format_string

	def _prepare_data(self):
		super()._prepare_data()
	
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:          self._data.toString(self._format_string),
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: str(self._data.toMSecsSinceEpoch()),
			QtCore.Qt.ItemDataRole.TextAlignmentRole:    QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter,
		})
	
	def to_json(self) -> dict:
		return {
			"type": "datetime",
			"timestamp": self.data(QtCore.Qt.ItemDataRole.UserRole).timestamp(),
			"formatted": self.data(QtCore.Qt.ItemDataRole.DisplayRole)
		}

class BSTimecodeViewItem(BSNumericViewItem):
	"""A timecode"""

	def __init__(self, raw_data:Timecode, *args, **kwargs):
		if not isinstance(raw_data, Timecode):
			raise TypeError("Data must be an instance of `Timecode`")
		super().__init__(raw_data, *args, **kwargs)
	
	def _prepare_data(self):
		super()._prepare_data()
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: str(self._data.frame_number),
		})
	
	def to_json(self) -> dict:
		tc = self.data(QtCore.Qt.ItemDataRole.UserRole)
		return {
			"type": "timecode",
			"frames": tc.frame_number,
			"rate": tc.rate,
			"formatted": self.data(QtCore.Qt.ItemDataRole.DisplayRole).strip()
		}

class BSDurationViewItem(BSTimecodeViewItem):
	"""A duration (hh:mm:ss:ff), a subset of timecode"""

	def _prepare_data(self):
		super()._prepare_data()
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole: self.to_string(self._data),
		})
	
	@classmethod
	def to_string(cls, data):

		tc_str = str(data)
		is_neg =tc_str.startswith("-")
		
		# Get the index of the last separator
		leading_chars = 1
		sep = ":"
		idx_last_sep = tc_str.rfind(sep) - leading_chars
		pre, post = tc_str[:idx_last_sep], tc_str[idx_last_sep:]
		pre = pre.lstrip("-00" + sep)

		return f"{'-' if is_neg else ''}{pre}{post}".rjust(cls.STRING_PADDING)

class BSFeetFramesViewItem(BSNumericViewItem):
	"""A frame offset described in feet & frames (f+ff)"""

	def __init__(self, raw_data:int, *args, **kwargs):

		if not isinstance(raw_data, int):
			raise TypeError(f"Data must be an integer (not {type(raw_data)})")
		super().__init__(raw_data, *args, **kwargs)

	def _prepare_data(self):
		super()._prepare_data()
	
	def to_json(self) -> dict:
		return {
			"type":      "feet_frames",
			"format":    "35mm",
			"perfs":     4,
			"frames":    self.data(QtCore.Qt.ItemDataRole.UserRole),
			"formatted": self.data(QtCore.Qt.ItemDataRole.DisplayRole).strip()
		}
	
	@classmethod
	def to_string(cls, data):
		return str(str(data // 16) + "+" + str(data % 16).zfill(2)).rjust(cls.STRING_PADDING)

class BSClipColorViewItem(BSAbstractViewItem):
	"""A clip color"""

	def __init__(self, raw_data:avbutils.ClipColor|QtGui.QRgba64|None, *args, **kwargs):

		if isinstance(raw_data, avbutils.ClipColor):
			raw_data = QtGui.QColor.fromRgba64(*raw_data.as_rgb16())
		elif isinstance(raw_data, QtGui.QRgba64):
			raw_data = QtGui.QColor.fromRgba64(raw_data)
		elif raw_data is None:
			raw_data = QtGui.QColor()
		elif not isinstance(raw_data, QtGui.QColor):
			raise TypeError(f"Data must be a QColor object (got {type(raw_data)})")
		
		super().__init__(raw_data, *args, **kwargs)
	
	def _prepare_data(self):
		# Not calling super, would be weird

		self._data_roles.update({
			#QtCore.Qt.ItemDataRole.UserRole: self._data,
			#QtCore.Qt.ItemDataRole.BackgroundRole: self._data,
			QtCore.Qt.ItemDataRole.DecorationRole:self._data,
			QtCore.Qt.ItemDataRole.ToolTipRole: f"R: {self._data.red()} G: {self._data.green()} B: {self._data.blue()}" if self._data.isValid() else QtCore.QCoreApplication.instance().tr("No Color"),
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: self.to_string(self._data.getRgb())
		})
	
	def to_json(self) -> dict|None:

		color = self.raw_data()
		
		if not color.isValid():
			return None
		
		color_64 = color.rgba64()

		return {
			"type": "color",
			"rgb16": [color_64.red(), color_64.green(), color_64.blue()],
			"rgb8": [color.red(), color.green(), color.blue()],
			"hex": self.data(QtCore.Qt.ItemDataRole.UserRole).name()
		}

class BSMarkerViewItem(BSAbstractViewItem):
	"""Marker column"""

	def __init__(self, raw_data:avbutils.MarkerInfo, *args, **kwargs):

		super().__init__(raw_data, *args, **kwargs)
		self._prepare_data()
	
	def _prepare_data(self):
		
		super()._prepare_data()
		
		marker_color = QtGui.QColor(self._data.color.name) if self._data is not None else QtGui.QColor()
		
		marker_info:avbutils.markers.MarkerInfo = self._data
		
		tooltip = QtCore.QCoreApplication.instance().tr(
			"""
			<table>
				<tr>
					<td><b>Color:</b></td><td>{marker_color}</td>
				</tr>
				<tr>
					<td><b>Comment:</b></td><td>{comment}</td>
				</tr>
				<tr>
					<td><b>User:</b></td><td>{user}</td>
				</tr>
				<tr>
					<td><b>Track:</b></td><td>{track}</td>
				</tr>
				<tr>
					<td><b>Frame Offset:</b></td><td>{offset}</td>
				</tr>
			</table>
			""").format(
				marker_color=marker_info.color.value,
				comment=marker_info.comment,
				user=marker_info.user,
				track=marker_info.track_label,
				offset=marker_info.frm_offset
			) if self._data else QtCore.QCoreApplication.instance().tr("No Marker")
		
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole: None,
			QtCore.Qt.ItemDataRole.DecorationRole: marker_color,
			QtCore.Qt.ItemDataRole.ToolTipRole: tooltip,
		})

class BSBinLockViewItem(BSAbstractViewItem):
	"""Bin lock info"""

	# Note: For now I think we'll do a string, but want to expand this later probably
	def __init__(self, raw_data:avbutils.LockInfo, *args, **kwargs):
		super().__init__(raw_data, *args, **kwargs)

	def _prepare_data(self):
		super()._prepare_data()
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:    self._data.name if self._data else "",
			QtCore.Qt.ItemDataRole.DecorationRole: QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.SystemLockScreen if self._data else None)
		})
	
	def to_json(self) -> str|None:
		return self.data(QtCore.Qt.ItemDataRole.DisplayRole) or None

@singledispatch
def get_viewitem_for_item(item:typing.Any) -> BSAbstractViewItem:
	"""Return the most suitable view item for a given item"""
	return BSStringViewItem(item)

@get_viewitem_for_item.register
def _(item:BSAbstractViewItem):
	return item

@get_viewitem_for_item.register
def _(item:str):
	return BSStringViewItem(item)

@get_viewitem_for_item.register
def _(item:int|float):
	return BSNumericViewItem(item)

@get_viewitem_for_item.register
def _(item:enum.Enum):
	return BSEnumViewItem(item)

@get_viewitem_for_item.register
def _(item:os.PathLike):
	return BSPathViewItem(item)

@get_viewitem_for_item.register
def _(item:str):
	return BSStringViewItem(item)

@get_viewitem_for_item.register
def _(item:datetime.datetime):
	return BSDateTimeViewItem(item)

@get_viewitem_for_item.register
def _(item:Timecode):
	return BSTimecodeViewItem(item)

@get_viewitem_for_item.register
def _(item:avbutils.markers.MarkerInfo):
	return BSMarkerViewItem(item)
