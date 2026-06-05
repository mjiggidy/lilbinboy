
import typing
from PySide6 import QtCore
from avbutils import bins

from . import binitemtypes

type BSBinItemModelEntry = dict[bins.BinColumnFieldIDs, binitemtypes.BSAbstractViewItem]
"""Each bin item in the model is a dict of BinColumnFieldID and respective view item pairs"""

class BSBinItemModel(QtCore.QAbstractItemModel):
	"""Single-column item model for bin items"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._bin_items:list[binitemtypes.BSBinItemInfo] = []

	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:
		"""Number of bin items"""
		
		return 0 if parent.isValid() else len(self._bin_items)

	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		"""Column count for model (returns `1` for flat model)"""

		return 0 if parent.isValid() else 1
	
	def hasChildren(self, /, parent:QtCore.QModelIndex) -> bool:
		"""Model is flat and has no children"""
		
		return not parent.isValid()
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Model is flat, children have no parents"""
		
		return QtCore.QModelIndex()
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if parent.isValid():
			return QtCore.QModelIndex()
		
		if not column < self.columnCount(parent) or not row < self.rowCount(parent):
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column)
	
	def data(self, index:QtCore.QModelIndex, /, role:binitemtypes.BSBinItemDataRoles) -> typing.Any:
		
		if not index.isValid():
			return None
		
		bin_item = self._bin_items[index.row()]
		
		# Map specialized BinItemDataRoles to their avbutils counterparts

		if role == binitemtypes.BSBinItemDataRoles.ItemNameRole:
			return bin_item.view_items.get(bins.BinColumnFieldIDs.Name).raw_data()
				
		elif role == binitemtypes.BSBinItemDataRoles.ClipColorRole:
			return bin_item.view_items.get(bins.BinColumnFieldIDs.Color).raw_data()
		
		elif role == binitemtypes.BSBinItemDataRoles.ItemTypesRole:
			return bin_item.view_items.get(bins.BinColumnFieldIDs.BinItemIcon).raw_data()
		
		elif role == binitemtypes.BSBinItemDataRoles.ViewItemsRole:
			return bin_item.view_items
		
		elif role == binitemtypes.BSBinItemDataRoles.MobID:
			return bin_item.mob_id
		
		elif role == binitemtypes.BSBinItemDataRoles.FrameCoordinatesRole:
			return bin_item.frame_coordinates
		
		elif role == binitemtypes.BSBinItemDataRoles.FrameThumbnailRole:
			return bin_item.keyframe_offset
		
		elif role == binitemtypes.BSBinItemDataRoles.TimecodeRangeRole:
			return bin_item.primary_timecode

#		NOTE: I don't remember why this would be here and it would need work anyway
#
#		elif role == QtCore.Qt.ItemDataRole.DisplayRole:
#			if bin_item.view_items.get(bins.BinColumnFieldIDs.Name) is not None:
#				return bin_item.view_items.get(bins.BinColumnFieldIDs.Name).data(QtCore.Qt.ItemDataRole.DisplayRole)
#			else:
#				return str(bin_item)
			
		else:
			return None

		
#		elif role == binitemtypes.BSBinItemDataRoles.ScriptNotesRole:
#			# NOTE: Maybe rethink
#			return self._getUserColumnItem(index, user_column_name="Comments", role=QtCore.Qt.ItemDataRole.DisplayRole)

	@QtCore.Slot(object)
	def addBinItem(self, bin_item:BSBinItemModelEntry):
		"""Add a bin item and its properties to the model"""

		self.addBinItems([bin_item])

	@QtCore.Slot(object)
	def addBinItems(self, bin_items:typing.Iterable[BSBinItemModelEntry]):
		"""Add bin items and their properties to the model"""

		start_row = self.rowCount(QtCore.QModelIndex())
		end_row   = start_row + len(bin_items)-1

		self.beginInsertRows(QtCore.QModelIndex(), start_row, end_row)

		self._bin_items.extend(bin_items)

		self.endInsertRows()

	@QtCore.Slot()
	def clear(self):
		"""Clear and reset the bin items model"""

		self.beginResetModel()
		
		self._bin_items = []
		
		self.endResetModel()