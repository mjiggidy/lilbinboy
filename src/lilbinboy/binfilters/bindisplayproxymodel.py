from PySide6 import QtCore
from ..binitems import binitemtypes
from . import abstractfiltermodel

import avbutils

DEFAULT_ITEM_TYPES = avbutils.bins.BinDisplayItemTypes.default_items()

class BSBinDisplayFilterProxyModel(abstractfiltermodel.BSAbstractBinSortFilterProxyModel):
	"""Bin display item filter"""

	sig_item_types_changed = QtCore.Signal(object)

	def __init__(self, *args, bin_items_model:QtCore.QAbstractItemModel|None = None,  accepted_item_types:avbutils.bins.BinDisplayItemTypes|None = None, **kwargs):

		super().__init__(*args, **kwargs)

		self._accepted_item_types = accepted_item_types or DEFAULT_ITEM_TYPES

		if bin_items_model:
			self.setSourceModel(bin_items_model)


	@QtCore.Slot(object)
	def setAcceptedItemTypes(self, bin_item_types:avbutils.bins.BinDisplayItemTypes):

		if self._accepted_item_types == bin_item_types:
			return
		
		self.beginFilterChange()
		self._accepted_item_types = bin_item_types
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)

		self.sig_item_types_changed.emit(bin_item_types)

	def acceptedItemTypes(self) -> avbutils.bins.BinDisplayItemTypes:

		return self._accepted_item_types
	
	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:

		if not self._is_enabled:
			return True
		
		source_index   = self.sourceModel().index(source_row, 0, source_parent)
#		print("Got here")
		bin_item_types = source_index.data(binitemtypes.BSBinItemDataRoles.ItemTypesRole)

#		print(self._accepted_item_types)

		return bin_item_types in self._accepted_item_types
	
	@QtCore.Slot(bool)
	def setEnabled(self, is_enabled:bool):

		if self._is_enabled == is_enabled:
			return

		self.beginFilterChange()
		self._is_enabled = is_enabled
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)
		
		self.sig_filter_toggled.emit(is_enabled)