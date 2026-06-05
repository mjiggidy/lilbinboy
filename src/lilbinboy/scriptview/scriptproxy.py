from PySide6 import QtCore
import avbutils

from ..binview  import binviewitemtypes


class BSScriptViewProxyModel(QtCore.QAbstractProxyModel):
	"""Adds a placeholder frame column"""

	ADDITIONAL_COLUMNS = 1
	DEFAULT_ITEM_FLAGS = QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled

	def __init__(self, /, parent:QtCore.QObject):

		super().__init__(parent)

		self._additional_header = binviewitemtypes.BSBinViewColumnInfo(
			field_id     = avbutils.bins.BinColumnFieldIDs.Frame,
			format_id    = avbutils.bins.BinColumnFormat.Frame,
			display_name = "",
			is_hidden    = False
		)

	def setSourceModel(self, sourceModel:QtCore.QAbstractItemModel):

		if self.sourceModel() == sourceModel:
			return
		
		if self.sourceModel() is not None:
			self.sourceModel().disconnect(self)

		sourceModel.dataChanged             .connect(self.sourceDataChanged)
		sourceModel.headerDataChanged       .connect(self.sourceHeaderDataChanged)

		sourceModel.columnsAboutToBeInserted.connect(self.sourceColumnsAboutToBeInserted)
		sourceModel.columnsInserted         .connect(self.columnsInserted)
		sourceModel.columnsAboutToBeRemoved .connect(self.sourceColumnsAboutToBeRemoved)
		sourceModel.columnsRemoved          .connect(self.columnsRemoved)

		sourceModel.rowsAboutToBeInserted   .connect(self.sourceRowsAboutToBeInserted)
		sourceModel.rowsInserted            .connect(self.rowsInserted)
		sourceModel.rowsAboutToBeRemoved    .connect(self.sourceRowsAboutToBeRemoved)
		sourceModel.rowsRemoved             .connect(self.rowsRemoved)

		sourceModel.layoutAboutToBeChanged  .connect(self.layoutAboutToBeChanged)
		sourceModel.layoutChanged           .connect(self.layoutChanged)

		sourceModel.modelAboutToBeReset     .connect(self.modelAboutToBeReset)
		sourceModel.modelReset              .connect(self.modelReset)

		return super().setSourceModel(sourceModel)
	
	# Source model mapping
	
	@QtCore.Slot(QtCore.Qt.Orientation, int, int)
	def sourceHeaderDataChanged(self, orientation:QtCore.Qt.Orientation, first:int, last:int):
		self.headerDataChanged.emit(orientation, first + self.ADDITIONAL_COLUMNS, last + self.ADDITIONAL_COLUMNS)
	
	@QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex, list)
	def sourceDataChanged(self, topLeft:QtCore.QModelIndex, bottomRight:QtCore.QModelIndex, roles:list[QtCore.Qt.ItemDataRole]):
		self.dataChanged.emit(self.mapFromSource(topLeft), self.mapFromSource(bottomRight), roles)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceColumnsAboutToBeInserted(self, parent:QtCore.QModelIndex, first:int, last:int):
		self.beginInsertColumns(QtCore.QModelIndex(), first + self.ADDITIONAL_COLUMNS, last + self.ADDITIONAL_COLUMNS)
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceColumnsAboutToBeRemoved(self, parent:QtCore.QModelIndex, first:int, last:int):
		self.beginRemoveColumns(QtCore.QModelIndex(), first + self.ADDITIONAL_COLUMNS, last + self.ADDITIONAL_COLUMNS)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceRowsAboutToBeInserted(self, parent:QtCore.QModelIndex, first:int, last:int):
		self.beginInsertRows(QtCore.QModelIndex(), first, last)
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def sourceRowsAboutToBeRemoved(self, parent:QtCore.QModelIndex, first:int, last:int):
		self.beginRemoveRows(QtCore.QModelIndex(), first, last)

	def mapFromSource(self, sourceIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:

		if not sourceIndex.isValid() or not self.sourceModel():
			return QtCore.QModelIndex()

		return self.index(sourceIndex.row(), sourceIndex.column() + self.ADDITIONAL_COLUMNS, QtCore.QModelIndex())
	
	def mapToSource(self, proxyIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if not proxyIndex.isValid() or not self.sourceModel():
			return QtCore.QModelIndex()
		
		if proxyIndex.column() < self.ADDITIONAL_COLUMNS:
			return QtCore.QModelIndex()
		
		return self.sourceModel().index(proxyIndex.row(), proxyIndex.column() - self.ADDITIONAL_COLUMNS, QtCore.QModelIndex())
	

	# Proxy model modifications

	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		return QtCore.QModelIndex()

	def columnCount(self, /, parent:QtCore.QModelIndex):

		if parent.isValid() or not self.sourceModel():
			return 0

		return self.sourceModel().columnCount(QtCore.QModelIndex()) + self.ADDITIONAL_COLUMNS
	
	def rowCount(self, /, parent:QtCore.QModelIndex):

		if parent.isValid() or not self.sourceModel():
			return 0

		return self.sourceModel().rowCount(QtCore.QModelIndex())
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex):

		# NOTE TO SELF: Surprised this needs to be reimplemented...?

		if parent.isValid() or not self.sourceModel():
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column)
	
	def data(self, proxyIndex:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):

		if not proxyIndex.isValid() or not self.sourceModel():
			return None

		if role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
			return QtCore.Qt.AlignmentFlag.AlignTop
		
		if proxyIndex.column() < self.ADDITIONAL_COLUMNS:
			
			# Return any of my special lil' binitemtypes
			if int(role) > int(QtCore.Qt.ItemDataRole.UserRole):	
				return self.sourceModel().index(proxyIndex.row(), 0, QtCore.QModelIndex()).data(role)
			else:
				return None

		return self.mapToSource(proxyIndex).data(role)
	
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, /, role:QtCore.Qt.ItemDataRole):
		
		if not self.sourceModel() or orientation != QtCore.Qt.Orientation.Horizontal:
			return None
		
		if section < self.ADDITIONAL_COLUMNS:
			return self._additional_header.data(role)
		
		return self.sourceModel().headerData(section - self.ADDITIONAL_COLUMNS, orientation, role)
	
	def flags(self, proxyIndex:QtCore.QModelIndex):

		if not proxyIndex.isValid() or not self.sourceModel():
			return QtCore.Qt.ItemFlag.NoItemFlags
		
		if proxyIndex.column() < self.ADDITIONAL_COLUMNS:
			return self.DEFAULT_ITEM_FLAGS
		
		return self.mapToSource(proxyIndex).flags()