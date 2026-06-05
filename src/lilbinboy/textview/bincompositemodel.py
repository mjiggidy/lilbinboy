"""TextViewModel to combine Item Model and View Models"""
import typing
from PySide6 import QtCore

from ..binitems import binitemsmodel, binitemtypes
from ..binview import binviewmodel, binviewitemtypes

import avbutils

class BSBinCompositeModel(QtCore.QAbstractItemModel):
	"""Combine bin items model with bin view model for a nice table-y text view"""

	def __init__(self, *args, item_model:QtCore.QAbstractItemModel, view_model:QtCore.QAbstractItemModel, **kwargs):
		
		super().__init__(*args, **kwargs)

		self._item_model = item_model
		self._view_model = view_model

		self._setupViewModel()
		self._setupItemModel()

	def _setupItemModel(self):

		self._item_model.rowsAboutToBeInserted.connect(self.binItemsAboutToBeInserted)
		self._item_model.rowsInserted.connect(self.binItemsInserted)

		self._item_model.rowsAboutToBeMoved.connect(self.binItemsAboutToBeMoved)
		self._item_model.rowsMoved.connect(self.binItemsMoved)
		
		self._item_model.rowsAboutToBeRemoved.connect(self.binItemsAboutToBeRemoved)
		self._item_model.rowsRemoved.connect(self.binItemsRemoved)

		self._item_model.layoutAboutToBeChanged.connect(self.binItemLayoutAboutToChange)
		self._item_model.layoutChanged.connect(self.binItemLayoutChanged)

		self._item_model.modelAboutToBeReset.connect(self.beginResetModel)
		self._item_model.modelReset.connect(self.endResetModel)

	def _setupViewModel(self):

		self._view_model.rowsAboutToBeInserted.connect(self.binColumnsAboutToBeInserted)
		self._view_model.rowsInserted.connect(self.binColumnsInserted)

		self._view_model.rowsAboutToBeMoved.connect(self.binColumnsAboutToBeMoved)
		self._view_model.rowsMoved.connect(self.binColumnsMoved)

		self._view_model.rowsAboutToBeRemoved.connect(self.binColumnsAboutToBeRemoved)
		self._view_model.rowsRemoved.connect(self.binColumnsRemoved)

		self._view_model.layoutAboutToBeChanged.connect(self.binColumnLayoutAboutToChange)
		self._view_model.layoutChanged.connect(self.binColumnLayoutChanged)

		self._view_model.modelAboutToBeReset.connect(self.beginResetModel)
		self._view_model.modelReset.connect(self.endResetModel)

		self._view_model.dataChanged.connect(self.binColumnDataChanged)
		#self._view_model.dataChanged.connect(print)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binItemsAboutToBeInserted(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):

		self.beginInsertRows(QtCore.QModelIndex(), row_start, row_end)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binItemsInserted(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):
		
		self.endInsertRows()

	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def binItemsAboutToBeMoved(self, sourceParent:QtCore.QModelIndex, sourceStart:int, sourceEnd:int, destinationParent:QtCore.QModelIndex, destinationRow:int):

		self.beginMoveRows(QtCore.QModelIndex(), sourceStart, sourceEnd, QtCore.QModelIndex(), destinationRow)
	
	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def binItemsMoved(self, sourceParent:QtCore.QModelIndex, sourceStart:int, sourceEnd:int, destinationParent:QtCore.QModelIndex, destinationRow:int):

		self.endMoveRows()

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binItemsAboutToBeRemoved(self, parent:QtCore.QModelIndex, start:int, end:int):
		
		self.beginRemoveRows(QtCore.QModelIndex(), start, end)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binItemsRemoved(self, parent:QtCore.QModelIndex, start:int, end:int):
		
		self.endRemoveRows()

	@QtCore.Slot()
	def binItemLayoutAboutToChange(self):

		self.layoutAboutToBeChanged.emit()

	@QtCore.Slot()
	def binItemLayoutChanged(self):

		self.layoutChanged.emit()


	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binColumnsAboutToBeInserted(self, parent:QtCore.QModelIndex, col_start:int, col_end:int):

		self.beginInsertColumns(QtCore.QModelIndex(), col_start, col_end)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binColumnsInserted(self, parent:QtCore.QModelIndex, col_start:int, col_end:int):
		
		self.endInsertColumns()

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binColumnsAboutToBeRemoved(self, parent:QtCore.QModelIndex, start:int, end:int):
		
		self.beginRemoveColumns(QtCore.QModelIndex(), start, end)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binColumnsRemoved(self, parent:QtCore.QModelIndex, start:int, end:int):
		
		self.endRemoveColumns()

	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def binColumnsAboutToBeMoved(self, sourceParent:QtCore.QModelIndex, sourceStart:int, sourceEnd:int, destinationParent:QtCore.QModelIndex, destinationRow:int):
		#print("BIN")

		source_name = self.headerData(sourceStart, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole)
		dest_name   = self.headerData(destinationRow-1, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole) if destinationRow > 0 else "<<FRONT>>"

#		print(f"Text view model knows it's about to move {source_name} to before {dest_name}")

		# NOTE: I THINK it's ok?

		self.beginMoveColumns(QtCore.QModelIndex(), sourceStart, sourceEnd, QtCore.QModelIndex(), destinationRow)
	
	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def binColumnsMoved(self, sourceParent:QtCore.QModelIndex, sourceStart:int, sourceEnd:int, destinationParent:QtCore.QModelIndex, destinationRow:int):

		self.endMoveColumns()

#	def moveColumn(self, sourceParent:QtCore.QModelIndex, sourceColumn:int, destinationParent:QtCore.QModelIndex, destinationColumn:int) -> bool:
#
#		# TODO: Roll into `moveColumns()`
#		
#		column_to_move = self.headerData(sourceColumn, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole)
#		column_before  = self.headerData(destinationColumn - 1, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole) if destinationColumn > 0 else "<<FRONT>>"
##		print(f"Text view model got move {column_to_move=} {sourceColumn=} to after {column_before=} {destinationColumn=}")
#
#		# NOTE: Good at this point, save for dragging-to-last-position stuff
#
#		return self.binViewModel().moveRow(QtCore.QModelIndex(), sourceColumn, QtCore.QModelIndex(), destinationColumn)
#		#return super().moveColumn(sourceParent, sourceColumn, destinationParent, destinationChild)

	def moveColumns(self, sourceParent:QtCore.QModelIndex, sourceColumn:int, count:int, destinationParent:QtCore.QModelIndex, destinationColumn:int) -> bool:
		"""Re-order visible bin columns.  Comes in from QHeaderView drags."""

#		column_to_move = self.headerData(sourceColumn, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole)
#		column_before  = self.headerData(destinationColumn - 1, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole) if destinationColumn > 0 else "<<FRONT>>"
#		print(f"Composite model got move column {column_to_move=} {sourceColumn=} to after {column_before=} {destinationColumn=}")

		return self.binViewModel().moveRows(
			QtCore.QModelIndex(),
			sourceColumn,
			count,
			QtCore.QModelIndex(),
			destinationColumn
		)


	@QtCore.Slot()
	def binColumnLayoutAboutToChange(self):

		# NOTE: Bin View Model reports these as a vertical change since they're listed as rows
		# doing a translation to Horizontal here

		self.layoutAboutToBeChanged.emit()

	@QtCore.Slot()
	def binColumnLayoutChanged(self):

		self.layoutChanged.emit()

	@QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex, object)
	def binColumnDataChanged(self, topLeft:QtCore.QModelIndex, bottomRight:QtCore.QModelIndex, roles:typing.Sequence[QtCore.Qt.ItemDataRole]):
		"""Bin column data was changed"""

		self.headerDataChanged.emit(QtCore.Qt.Orientation.Horizontal, topLeft.row(), bottomRight.row())


	def setBinItemModel(self, item_model:QtCore.QAbstractItemModel):
		"""Set the bin item model"""

		if self._item_model == item_model:
			return
		
		self._item_model.disconnect(self)

		self.beginResetModel()
		
		self._item_model = item_model
		self._setupItemModel()

		self.endResetModel()

	def binItemModel(self) -> QtCore.QAbstractItemModel:
		"""The current bin items model"""

		return self._item_model

	def setBinViewModel(self, view_model:QtCore.QAbstractItemModel):
		"""Set the bin column view model"""

		if self._view_model == view_model:
			return
		
		self._view_model.disconnect(self)

		self.beginResetModel()
		
		self._view_model = view_model
		self._setupViewModel()

		self.endResetModel()

	def binViewModel(self) -> QtCore.QAbstractItemModel:

		return self._view_model


	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:
		"""Get bin item count"""
		
		if parent.isValid():
			return 0
		
		return self._item_model.rowCount(QtCore.QModelIndex())
	
	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		"""Get bin view column count"""
		
		if parent.isValid():
			return 0
		
		return self._view_model.rowCount(QtCore.QModelIndex())
	
	def hasChildren(self, /, parent:QtCore.QModelIndex) -> bool:
		
		return not parent.isValid()
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		return QtCore.QModelIndex()
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if parent.isValid():
			return QtCore.QModelIndex()
		
		if not row < self._item_model.rowCount(QtCore.QModelIndex()):
			import logging
			logging.getLogger(__name__).error("Got bad row index %s (row count=%s)", row, int(self._item_model.rowCount(QtCore.QModelIndex())))
			return QtCore.QModelIndex()		
		
		elif not column < self._view_model.rowCount(QtCore.QModelIndex()):
			import logging
			logging.getLogger(__name__).error("Got bad column index %s (column count=%s)", column, int(self._view_model.rowCount(QtCore.QModelIndex())))
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column)
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):

		#print(f"AKSI INGRG FOR DATAERS {index=} {role=}")
		#return "NO HAHA"
		
		# NOTE: Need to figure out best way to return original data roles
		# This is eh
		if role > QtCore.Qt.ItemDataRole.UserRole:
			return self._item_model.data(self._item_model.index(index.row(), 0, QtCore.QModelIndex()), role)

		bin_item = self._item_model.data(self._item_model.index(index.row(), 0, QtCore.QModelIndex()), binitemtypes.BSBinItemDataRoles.ViewItemsRole)
		
		# Determine which field we need for this column
		field_id   = self._view_model.data(self._view_model.index(index.column(), 0, QtCore.QModelIndex()), binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
		field_name = self._view_model.data(self._view_model.index(index.column(), 0, QtCore.QModelIndex()), binviewitemtypes.BSBinViewColumnInfoRole.FieldNameRole)

		# No info for requested field ID
		if field_id not in bin_item:
			return None
		
		# One of the user fields requested
		elif field_id == avbutils.bins.BinColumnFieldIDs.User:

			# Get column name and look it up in user fields
			user_fields = bin_item[field_id]
			
			if field_name in user_fields:
				return user_fields[field_name].data(role)

		# Return standard field data
		else:
			return bin_item[field_id].data(role)
	
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, /, role:QtCore.Qt.ItemDataRole) -> typing.Any:
		
		if not orientation == QtCore.Qt.Orientation.Horizontal:
			return None
		
		return self._view_model.data(self._view_model.index(section, 0, QtCore.QModelIndex()), role)
	
	def setHeaderData(self, section:int, orientation:QtCore.Qt.Orientation, value:typing.Any, /, role:binviewitemtypes.BSBinViewColumnInfoRole) -> bool:

		if orientation != QtCore.Qt.Orientation.Horizontal:
			return False
		
#		print("Text view model tryna set section value to ", value)

		return self._view_model.setData(self._view_model.index(section, 0, QtCore.QModelIndex()), value, role)