import enum

from ..binview import binviewitemtypes
from ..binfilters import binviewproxymodel
from PySide6 import QtCore, QtGui

import avbutils

class BSBinViewColumnEditorFeature(enum.IntEnum):
	"""Editor column features"""

	GripperColumn     = enum.auto()
	NameColumn        = enum.auto()
	DataFormatColumn  = enum.auto()
	VisibilityColumn  = enum.auto()
	DeleteColumn      = enum.auto()

class BSBinViewColumnEditorProxyModel(QtCore.QAbstractProxyModel):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._editor_features:list[BSBinViewColumnEditorFeature] = [
			BSBinViewColumnEditorFeature.DataFormatColumn,
			BSBinViewColumnEditorFeature.NameColumn,
			BSBinViewColumnEditorFeature.DeleteColumn,
			BSBinViewColumnEditorFeature.VisibilityColumn,
		]

	###

	def setSourceModel(self, sourceModel:QtCore.QAbstractItemModel):
		
		if self.sourceModel() == sourceModel:
			return
		
		if self.sourceModel():
			self.sourceModel().disconnect(self)

		sourceModel.rowsAboutToBeRemoved.connect(self.sourceModelAboutToRemoveRows)
		sourceModel.rowsRemoved.connect(self.sourceModelRemovedRows)

		sourceModel.rowsAboutToBeInserted.connect(self.sourceModelAboutToInsertRows)
		sourceModel.rowsInserted.connect(self.sourceModelInsertedRows)

		sourceModel.rowsAboutToBeMoved.connect(self.sourceModelAboutToMoveRows)
		sourceModel.rowsMoved.connect(self.sourceModelMovedRows)

		sourceModel.modelAboutToBeReset.connect(self.sourceModelAboutToReset)
		sourceModel.modelReset.connect(self.sourceModelReset)

		sourceModel.layoutChanged.connect(self.layoutChanged)
		sourceModel.dataChanged.connect(self.sourceModelDataChanged)
		
		super().setSourceModel(sourceModel)

#		print("Source set", sourceModel)

	### Source Model Malarky

	@QtCore.Slot()
	def sourceModelAboutToReset(self):

		self.beginResetModel()

	@QtCore.Slot()
	def sourceModelReset(self):

		self.endResetModel()

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceModelAboutToRemoveRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):

		if parent.isValid():
			return
		
		self.beginRemoveRows(QtCore.QModelIndex(), row_start, row_end)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceModelRemovedRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):

		if parent.isValid():
			return
		
		self.endRemoveRows()

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceModelAboutToInsertRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):
		
		if parent.isValid():
			return
		
		self.beginInsertRows(QtCore.QModelIndex(), row_start, row_end)
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceModelInsertedRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int):

		if parent.isValid():
			return
		
		self.endInsertRows()

	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def sourceModelAboutToMoveRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int, destination:QtCore.QModelIndex, dest_row:int):

		if parent.isValid():
			return

		self.beginMoveRows(QtCore.QModelIndex(), row_start, row_end, QtCore.QModelIndex(), dest_row)

	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
	def sourceModelMovedRows(self, parent:QtCore.QModelIndex, row_start:int, row_end:int, destination:QtCore.QModelIndex, dest_row:int):

		if parent.isValid():
			return

		self.endMoveRows()

	@QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex, list)
	def sourceModelDataChanged(self, topLeft:QtCore.QModelIndex, bottomRight:QtCore.QModelIndex, roles:list[QtCore.Qt.ItemDataRole]):

		self.dataChanged.emit(
			self.index(topLeft.row(), 0, QtCore.QModelIndex()),
			self.index(bottomRight.row(), self.columnCount(QtCore.QModelIndex()) - 1, QtCore.QModelIndex())
		)

	def mapToSource(self, proxyIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:

		if not proxyIndex.isValid() or not self.sourceModel():
			return QtCore.QModelIndex()
		
		return self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex())
	
	def mapFromSource(self, sourceIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:

		if not sourceIndex.isValid() or not self.sourceModel():
			return QtCore.QModelIndex()
		
		return self.index(sourceIndex.row(), 0, QtCore.QModelIndex())

	### Model Malarky

	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		return 0 if parent.isValid() else len(self._editor_features)
	
	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:

		if not self.sourceModel() or parent.isValid():
			return 0
		
		return self.sourceModel().rowCount(QtCore.QModelIndex())
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		return QtCore.QModelIndex()
	
	def hasChildren(self, /, parent:QtCore.QModelIndex) -> bool:
		return False
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex):

		if parent.isValid():
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column)
	
	def data(self, proxyIndex:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):

		if not self.sourceModel() or not proxyIndex.isValid():
			return
		
		editor_feature = self._editor_features[proxyIndex.column()]

		if editor_feature == BSBinViewColumnEditorFeature.NameColumn:

			if self.sourceModel().index(proxyIndex.row(), 0).data(binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole) == avbutils.bins.BinColumnFieldIDs.BinItemIcon\
			   and role == QtCore.Qt.ItemDataRole.DisplayRole:
				
				return self.tr("[Icon]")

			return self.sourceModel().index(proxyIndex.row(), 0).data(role)

		elif editor_feature == BSBinViewColumnEditorFeature.DataFormatColumn:
			
			data_format:avbutils.bins.BinColumnFormat = self.sourceModel().index(proxyIndex.row(), 0).data(binviewitemtypes.BSBinViewColumnInfoRole.FormatIdRole)

			if role == QtCore.Qt.ItemDataRole.DisplayRole:
				return None
			
			if role == QtCore.Qt.ItemDataRole.ToolTipRole:

				return self.tr("<strong>Column Data Format</strong><br/>{data_format_name}")\
					.format(data_format_name = data_format.name.title())
			
			elif role == QtCore.Qt.ItemDataRole.UserRole:

				return self.sourceModel().index(proxyIndex.row(), 0).data(binviewitemtypes.BSBinViewColumnInfoRole.FormatIdRole)
			
		elif editor_feature == BSBinViewColumnEditorFeature.VisibilityColumn:

			is_permanently_visible = self.sourceModel().index(proxyIndex.row(), 0).data(binviewproxymodel.BSBinViewFilterRole.IsPermanentlyVisibleRole)
			is_hidden              = self.sourceModel().index(proxyIndex.row(), 0).data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

			if role == QtCore.Qt.ItemDataRole.ToolTipRole:

				if is_permanently_visible:

					return self.tr("<strong>Permanent Column</strong><br/>This column cannot be hidden")
					
				else:
					return self.tr("<strong>Toggle Column Visibility</strong><br/>This column is currently {is_hidden}.  Click to toggle visiblity of this, and any other selected columns")\
					.format(is_hidden = self.tr("hidden", "Referring to column visibility") if is_hidden else self.tr("visible",  "Referring to column visibility"))
			
			elif role == QtCore.Qt.ItemDataRole.UserRole:
				return not self.sourceModel().index(proxyIndex.row(), 0).data(binviewproxymodel.BSBinViewFilterRole.IsPermanentlyVisibleRole)
			
		elif editor_feature == BSBinViewColumnEditorFeature.DeleteColumn:

			is_deletable = self._columnCanBeDeletedIsThatCorrectPlease(
				self.sourceModel().index(proxyIndex.row(), 0).data(binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
			)

#			if role == QtCore.Qt.ItemDataRole.DecorationRole:
#				# Allow delete if user field
#				return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditClear) if is_deletable else QtGui.QIcon()
			
			if role == QtCore.Qt.ItemDataRole.ToolTipRole and is_deletable:
				return self.tr("<strong>Delete User Column</strong><br/>Permanently remove {column_name}, and any other selected user columns, from this bin view")\
					.format(column_name = proxyIndex.siblingAtColumn(1).data(QtCore.Qt.ItemDataRole.DisplayRole))
			
			if role == QtCore.Qt.ItemDataRole.UserRole:

				return is_deletable

	
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, /, role:QtCore.Qt.ItemDataRole):

		if orientation != QtCore.Qt.Orientation.Horizontal:
			return
		
		editor_feature = self._editor_features[section]

		if role == QtCore.Qt.ItemDataRole.UserRole:
			return editor_feature
		
#		if role == QtCore.Qt.ItemDataRole.DisplayRole:
#			return editor_feature.name
	
	def flags(self, index:QtCore.QModelIndex):
		
		flags = \
			QtCore.Qt.ItemFlag.ItemIsEnabled | \
			QtCore.Qt.ItemFlag.ItemIsSelectable | \
			QtCore.Qt.ItemFlag.ItemNeverHasChildren

		# Allow dropping between items (invalid indexes)
		if not index.isValid():
			return QtCore.Qt.ItemFlag.ItemIsDropEnabled
		
#		editor_feature = self._editor_features[index.column()]

		# Column Name Edididable if user field and we're talkin bout the name column here
#		if editor_feature == BSBinViewColumnEditorFeature.NameColumn \
#		   and self.mapToSource(index).data(binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole) == avbutils.bins.BinColumnFieldIDs.User:
#			flags |= QtCore.Qt.ItemFlag.ItemIsEditable
		
		return flags | QtCore.Qt.ItemFlag.ItemIsDragEnabled
	
	### Draggityy Droppity Mimeity businesses

	def supportedDragActions(self) -> QtCore.Qt.DropAction:
		return QtCore.Qt.DropAction.MoveAction
	
	def supportedDropActions(self)-> QtCore.Qt.DropAction:
		return QtCore.Qt.DropAction.MoveAction
	
	def mimeTypes(self):
		return ["application/x-qabstractitemmodeldatalist"]
	
	def canDropMimeData(self, data:QtCore.QMimeData, action:QtCore.Qt.DropAction, row:int, column:int, parent:QtCore.QModelIndex):
		# Only allow drops *between* items
		# (Pairs with flags() returning ItemFalgs.ItemAcceptsDrops for invalid QModelIndexes)
		return not parent.isValid()

	def moveRows(self, sourceParent:QtCore.QModelIndex, sourceRow:int, count:int, destinationParent:QtCore.QModelIndex, destinationChild:int):

		if sourceParent.isValid() or destinationParent.isValid():
			return False

		return self.sourceModel().moveRows(
			QtCore.QModelIndex(),
			sourceRow,
			count,
			QtCore.QModelIndex(),
			destinationChild
		)
	
	def removeRows(self, row, count, /, parent = ...):

		if not self.sourceModel() or parent.isValid():
			return
		
		return self.sourceModel().removeRows(row, count, QtCore.QModelIndex())

#	def removeRow(self, row:int, /, parent:QtCore.QModelIndex) -> bool:
#		
#		if not self.sourceModel() or parent.isValid():
#			return
#		
#		return self.sourceModel().removeRow(row, QtCore.QModelIndex())
	
	def insertRows(self, row:int, count:int, /, parent:QtCore.QModelIndex) -> bool:
		"""Forward row inserts to the source model"""

		if parent.isValid() or not self.sourceModel():
			return False
		
		return self.sourceModel().insertRows(row, count, QtCore.QModelIndex())
	
	def sort(self, role:binviewitemtypes.BSBinViewColumnInfoRole, /, order = ...):
		"""REDEFINED SORT ROLE: Accepts `BSBinViewColumnInfoRole` instead of a column index, since this is a flat list"""

		return super().sort(role, order)
	
	def dropMimeData(self, data:QtCore.QMimeData, action:QtCore.Qt.DropAction, row:int, column:int, parent:QtCore.QModelIndex) -> bool:

		# Accept drop-to-move-column actions
		if action == QtCore.Qt.DropAction.MoveAction and data.hasFormat("application/x-qabstractitemmodeldatalist"):
			return True
	
		return super().dropMimeData(data, action, row, column, parent)
	
	### Helper junk

	def _columnCanBeDeletedIsThatCorrectPlease(self, field_id:avbutils.bins.BinColumnFieldIDs) -> bool:

		return field_id == avbutils.bins.BinColumnFieldIDs.User