from __future__ import annotations
import dataclasses, enum, typing

import avb, avbutils

from PySide6 import QtCore

DEFAULT_NONPRINTABLE_CHAR = '⬥'
"""Some bin columns produce a non-printable \x07 character.  Replace those with this for display only."""

class BSBinViewColumnInfoRole(enum.IntEnum):
	"""View item data roles available for a given column (extends `QtCore.Qt.ItemDataRole`)"""

	# NOTE: This is good I'mma stick with this.
	# Replaces anything from old view models / binitemtypes whatever

	DisplayNameRole = QtCore.Qt.ItemDataRole.DisplayRole
	"""Formatted name displayed on the bin column header"""

	IconRole        = QtCore.Qt.ItemDataRole.DecorationRole
	"""Data expected by a `BSIconProvider`"""

	ToolTipRole     = QtCore.Qt.ItemDataRole.ToolTipRole
	"""Tool tip data"""
	
	RawColumnInfo   = QtCore.Qt.ItemDataRole.UserRole
	"""Full `BSBinViewColumnInfo` object"""

	FieldNameRole   = QtCore.Qt.ItemDataRole.UserRole + 1
	"""Raw Field Name"""
	
	FieldIdRole     = QtCore.Qt.ItemDataRole.UserRole + 2
	"""Bin column field identifier"""

	FormatIdRole    = QtCore.Qt.ItemDataRole.UserRole + 3
	"""Bin column data format identifier"""

	IsHiddenRole    = QtCore.Qt.ItemDataRole.UserRole + 4
	"""Bin column visibility"""

	_SentinelRole    = QtCore.Qt.ItemDataRole.UserRole + 5
	"""Empty role to indicate the last offset from `QtCore.Qt.ItemDataRole.UserRole"""

@dataclasses.dataclass
class BSBinViewInfo:
	"""BinView View Item Data"""

	name:str
	columns:list[BSBinViewColumnInfo]

	@classmethod
	def from_binview(cls, binview:avb.bin.BinViewSetting) -> typing.Self:

		columns = []

		for col in binview.columns:
			try:
				columns.append(BSBinViewColumnInfo.from_column(col))
			except ValueError as e:
#				print("Passing value error: ", e)
				continue

		return cls(
			name    = binview.name,
			columns = columns
		)

@dataclasses.dataclass()
class BSBinViewColumnInfo:
	"""BinView Column Data"""

	field_id     :avbutils.bins.BinColumnFieldIDs
	"""Column identifier"""

	format_id    :avbutils.bins.BinColumnFormat
	"""Data format represented by this column"""

	display_name :str
	"""Column name for header"""

	is_hidden    :bool
	"""Column is hidden"""

	_data_roles  :dict[BSBinViewColumnInfoRole, typing.Any] = dataclasses.field(init=False)
	"""View Item Data Roles for `QAbstractItemModel` access via `.data()`"""

	def __post_init__(self):
		self._refresh_data_roles()

	def _build_tooltip(self):
		
		return QtCore.QCoreApplication.instance().tr(
			"""
			<table>
				<tr>
					<td><strong>Field:</strong></td><td>{field_id} ({field_name})</td>
				</tr>
				<tr>
					<td><strong>Format:</strong></td><td>{data_format_id} ({data_format})</td>
				</tr>
				<tr>
					<td><strong>Hidden:</strong></td><td>{is_hidden}</td>
				</tr>
			</table>
			"""
		).format(field_name=self.display_name, field_id=self.field_id.value, data_format=self.format_id, data_format_id=self.format_id.value, is_hidden=self.is_hidden)

	def _refresh_data_roles(self):

		self._data_roles = {
			BSBinViewColumnInfoRole.DisplayNameRole:    self._sanitize_display_name(self.display_name),
			BSBinViewColumnInfoRole.ToolTipRole:        self._build_tooltip(),
			BSBinViewColumnInfoRole.FieldIdRole:        self.field_id,
			BSBinViewColumnInfoRole.FieldNameRole:      self.display_name,
			BSBinViewColumnInfoRole.FormatIdRole:       self.format_id,
			BSBinViewColumnInfoRole.IsHiddenRole:       self.is_hidden,
			BSBinViewColumnInfoRole.RawColumnInfo:      self,
		}

	@staticmethod
	def _sanitize_display_name(name:str):
		"""Format the display name for column headers"""

		return "".join(c if c.isprintable() else DEFAULT_NONPRINTABLE_CHAR for c in name)
		

	def data(self, role:BSBinViewColumnInfoRole) -> typing.Any:
		return self._data_roles.get(role, None)
	
	def setData(self, value:typing.Any, role:BSBinViewColumnInfoRole):

		# NOTE: I think `self._data_roles` is updated for free since it's refs?
		# TODO: Verify
		# NOTE: Nope.

		if role == BSBinViewColumnInfoRole.DisplayNameRole:
			self.display_name = value

		elif role == BSBinViewColumnInfoRole.FieldIdRole:
			self.field_id = value

		elif role == BSBinViewColumnInfoRole.FormatIdRole:
			self.format_id = value
		
		elif role == BSBinViewColumnInfoRole.IsHiddenRole:
			self.is_hidden = value
		
		self._refresh_data_roles()

	def to_json_dict(self) -> dict[str, typing.Any]:
		"""Export a JSON-ready dict of this column"""

		return {
			"field_id": self.field_id.name,
			"format_id": self.format_id.name,
			"display_name": self.display_name,
			"is_hidden": self.is_hidden
		}

	@classmethod
	def from_column(cls, bin_column_info:dict) -> typing.Self:

		return cls(
			field_id     = avbutils.bins.BinColumnFieldIDs(bin_column_info["type"]),
			format_id    = avbutils.bins.BinColumnFormat(bin_column_info["format"]),
			display_name = str(bin_column_info["title"]),
			is_hidden    = bool(bin_column_info["hidden"]),
		)