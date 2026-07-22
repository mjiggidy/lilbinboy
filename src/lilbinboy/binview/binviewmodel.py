from __future__ import annotations
import typing, enum, logging
from PySide6 import QtCore

from . import binviewitemtypes

class BSBinViewModificationHint(enum.Enum):
	"""Type of bin view modification"""

	BinViewColumnsAdded      = enum.auto()
	"""Bin view column(s) were added"""

	BinViewColumnsRemoved    = enum.auto()
	"""Bin view column(s) were removed"""
	
	BinViewColumnsMoved      = enum.auto()
	"""Bin view column(s) were rearranged"""

	BinViewColumnDataChanged = enum.auto()
	"""Bin view column(s) data modified in place (renamed, hidden)"""


class BSBinViewModel(QtCore.QAbstractItemModel):
	"""Main Bin View Model"""

	DEFAULT_BIN_VIEW_NAME     = "NoNameSet"

	sig_bin_view_name_changed = QtCore.Signal(str)
	
	sig_bin_view_info_set     = QtCore.Signal(object)
	"""The model has been set via setBinViewInfo"""

	sig_bin_view_modified     = QtCore.Signal(object, object)
	"""The current binview has been modified from its source"""

	def __init__(self, /, bin_view:binviewitemtypes.BSBinViewInfo|None=None, parent:QtCore.QObject|None=None):
		
		super().__init__(parent)

		self._bin_view_name:str = bin_view.name if bin_view else self.DEFAULT_BIN_VIEW_NAME
		self._bin_view_columns:list[binviewitemtypes.BSBinViewColumnInfo] = bin_view.columns if bin_view else []

		self._is_modified:bool = False
	
	@QtCore.Slot(object)
	def setBinViewInfo(self, bin_view_info:binviewitemtypes.BSBinViewInfo):
		"""Set the bin view model from a `BSBinViewInfo`"""

		self.beginResetModel()
		self._bin_view_name    = bin_view_info.name
		self._bin_view_columns = bin_view_info.columns
		self._is_modified      = False
		self.endResetModel()
		
		self.sig_bin_view_info_set.emit(self.binViewInfo())
		self.sig_bin_view_name_changed.emit(bin_view_info.name)
	
	def binViewInfo(self) -> binviewitemtypes.BSBinViewInfo:
		"""Get the bin view info for the current model"""

		return binviewitemtypes.BSBinViewInfo(
			name        = self.binViewName(),
			columns     = self._bin_view_columns
		)

	@QtCore.Slot(str)
	def setBinViewName(self, name:str):

		if self._bin_view_name == name:
			return
		
		self._bin_view_name = name
		self.sig_bin_view_name_changed.emit(name)
		
	def binViewName(self) -> str:

		return self._bin_view_name
	
	# TODO: Consolidate these addBinColumn(s) methods (or: why did I do it this way...?)

	def addBinColumn(self, bin_column:binviewitemtypes.BSBinViewColumnInfo, row:int|None=None):

		if row is not None:

			self.beginInsertRows(QtCore.QModelIndex(), row, row)
			self._bin_view_columns.insert(row, bin_column)

		else:

			self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount())
			self._bin_view_columns.append(bin_column)
		
		self.endInsertRows()
		# NOTE: insertRows() emits sig_bin_view_modified

	def addBinColumns(self, bin_columns:typing.Iterable[binviewitemtypes.BSBinViewColumnInfo], row:int|None=None):

		bin_columns = list(bin_columns)

		if row:

			self.beginInsertRows(QtCore.QModelIndex(), row, row+len(bin_columns)-1)
			self._bin_view_columns[row:row] = bin_columns

		else:

			self.beginInsertRows(QtCore.QModelIndex(), self.rowCount(), self.rowCount()+len(bin_columns)-1)
			self._bin_view_columns.extend(bin_columns)
		
		self.endInsertRows()
		# NOTE: insertRows() emits sig_bin_view_modified

	def binColumns(self) -> list[binviewitemtypes.BSBinViewColumnInfo]:

		return self._bin_view_columns


	###


	def parent(self, child_index:QtCore.QModelIndex) -> QtCore.QModelIndex:

		return QtCore.QModelIndex()
	
	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:

		if parent.isValid():
			return 0

		return len(self._bin_view_columns)
	
	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:

		if parent.isValid():
			return 0
		
		return 1
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:

		if parent.isValid():
			return  QtCore.QModelIndex()
		
		return self.createIndex(row, column)
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):

		return self._bin_view_columns[index.row()].data(role)
	
	def setData(self, index:QtCore.QModelIndex, value:typing.Any, /, role:binviewitemtypes.BSBinViewColumnInfoRole):
		
		item = self._bin_view_columns[index.row()]

		if value == item.data(role):
			return False
		
		item.setData(value, role)
		self.dataChanged.emit(index, index)

		self._is_modified = True
		self.sig_bin_view_modified.emit(self.binViewInfo(), BSBinViewModificationHint.BinViewColumnDataChanged)

		return True
	
#	def removeRow(self, row:int, /, parent:QtCore.QModelIndex) -> bool:
#		"""Remove a given row (convience for `self.removeRows()`)"""
#		
#		if parent.isValid():
#			return False
#		
#		print(f"Source model says remove row {row}: {self.index(row, 0, parent).data(QtCore.Qt.ItemDataRole.DisplayRole)}")
#		
#		self.removeRows(row, 1, parent)
	
	@QtCore.Slot(int, int, QtCore.QModelIndex)
	def removeRows(self, row:int, count:int, /, parent:QtCore.QModelIndex):
		"""Remove given rows"""

		if count < 1 or parent.isValid():
			return False

#		for bin_column_index in range(row, row + count):
#			print(f"Data model removing row {bin_column_index}: {self.index(bin_column_index, 0, parent).data(QtCore.Qt.ItemDataRole.DisplayRole)}")

		self.beginRemoveRows(parent, row, row + count-1)
		del self._bin_view_columns[row:row+count]
		self.endRemoveRows()

		self._is_modified = True
		self.sig_bin_view_modified.emit(self.binViewInfo(), BSBinViewModificationHint.BinViewColumnsRemoved)

		return True
	
	@QtCore.Slot(int, int, QtCore.QModelIndex)
	def insertRows(self, row:int, count:int, /, parent:QtCore.QModelIndex):

		import avbutils
		
		self.beginInsertRows(parent, row, row + count-1)

		self._bin_view_columns.append(binviewitemtypes.BSBinViewColumnInfo(
			field_id = avbutils.bins.BinColumnFieldIDs.User,
			format_id = avbutils.bins.BinColumnFormat.UserText,
			display_name = "New User Column",
			is_hidden = False
		))

		self.endInsertRows()

		self._is_modified = True
		self.sig_bin_view_modified.emit(self.binViewInfo(), BSBinViewModificationHint.BinViewColumnsAdded)

		return True
	
	def moveRows(self, sourceParent:QtCore.QModelIndex, sourceRow:int, count:int, destinationParent:QtCore.QModelIndex, destinationChild:int):
		
#		print(f"Hey I got {sourceRow=} {count=} {destinationChild=}")
		
		logging.getLogger(__name__).debug("Begin move rows")
		self.beginMoveRows(sourceParent, sourceRow, sourceRow + count-1, destinationParent, destinationChild)

		# NOTE: This confuses me every time I look at it.  Imanita do better here.
		# That said, it DOES work lol
		
		# Pull out the range of column items and remove them from the master list
		moving_rows = self._bin_view_columns[sourceRow: sourceRow+count]
		del self._bin_view_columns[sourceRow: sourceRow+count]

		# If destination is after the removed items, adjust the destination for the amount removed since that'll throw off the destination
		destinationChild = destinationChild - count if sourceRow < destinationChild else destinationChild

		# Insert at the adjusted destination
		self._bin_view_columns[destinationChild:destinationChild] = moving_rows

		logging.getLogger(__name__).debug("End move rows")
		self.endMoveRows()

		# NOTE: I think this all works at this point from any entry point

		self._is_modified = True
		self.sig_bin_view_modified.emit(self.binViewInfo(), BSBinViewModificationHint.BinViewColumnsMoved)
		
		return True
	
	def sort(self, role:binviewitemtypes.BSBinViewColumnInfoRole, /, order:QtCore.Qt.SortOrder):
		"""REDEFINED SORT ROLE: Accepts `BSBinViewColumnInfoRole` instead of a column index, since this is a flat list"""

		self.layoutAboutToBeChanged.emit()

		self._bin_view_columns.sort(
			key=lambda c: c.data(role),
			reverse=(order == QtCore.Qt.SortOrder.DescendingOrder)
		)
		
		self.layoutChanged.emit()
		self.sig_bin_view_modified.emit(self.binViewInfo(), BSBinViewModificationHint.BinViewColumnDataChanged)
		#return super().sort(column, order)
	
#	def dropMimeData(self, data, action, row, column, parent):
#		print("Huh")
#		return True
#		return super().dropMimeData(data, action, row, column, parent)