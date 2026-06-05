from ..binitems import binitemtypes
from ..binview import binviewitemtypes

#from . import textviewmodel, proxyfilters

import avbutils
from PySide6 import QtCore

#class BSBTextViewSortFilterProxyModelDEPRECATED(QtCore.QSortFilterProxyModel):
#	"""The New One For The New Thing"""
#
#	sig_bin_view_enabled  = QtCore.Signal(bool)
#	"""Bin view has been toggled on (`True`) or off (`False`)"""
#
#	def __init__(self, *args, text_view_model:textviewmodel.BSBinCompositeModel|None=None, **kwargs):
#
#		super().__init__(*args, **kwargs)
#
#		self.setDynamicSortFilter(False)
#		self.setSortRole(QtCore.Qt.ItemDataRole.InitialSortOrderRole)
#		
#		self._sort_collator = QtCore.QCollator()
#		self._sort_collator.setNumericMode(True)
#		self._sort_collator.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
#
#		self._item_filters_enabled     = True
#		self._column_filters_enabled   = True
#		
#		self._filter_bin_display_items = proxyfilters.BSBinItemDisplayFilter()
#		self._filter_find_in_bin       = proxyfilters.BSFindInBinFilter()
#
#		if text_view_model:
#			self.setSourceModel(text_view_model)
#
#	def setSourceModel(self, sourceModel:textviewmodel.BSBinCompositeModel):
#
#		if self.sourceModel() == sourceModel:
#			return
#		
#		if self.sourceModel():
#			self.sourceModel().disconnect(self)
#
##		if not isinstance(sourceModel, textviewmodel.BSTextViewModel):
##			raise ValueError(f"Source model must be `BSTextViewModel`; got {repr(sourceModel)}")
#		
#		sourceModel.headerDataChanged.connect(self.binColumnDataChanged)
##		sourceModel.modelReset.connect(lambda: self.sort(-1))	# Start unsorted/"script order"
#		
#		super().setSourceModel(sourceModel)
#
#	@QtCore.Slot(QtCore.Qt.Orientation, int, int)
#	def binColumnDataChanged(self, orientation:QtCore.Qt.Orientation, first:int, last:int):
#		
#		# NOTE: Scheduled for deprecation in Qt 6.13
#		# self.invalidateColumnsFilter()
#
#		# NOTE: The neue way, but I don't like it
#		# I feel weird calling `begin` AFTER the data has changed
#
#		self.beginFilterChange()
#		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Columns)
#
#	@QtCore.Slot(object)
#	def setBinDisplayItemTypes(self, types:avbutils.BinDisplayItemTypes):
#		
#		if types != self._filter_bin_display_items.acceptedItemTypes():
#
#			self.beginFilterChange()
#			self._filter_bin_display_items.setAcceptedItemTypes(types)
#			self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)
#
#	def binDisplayItemTypes(self) -> avbutils.BinDisplayItemTypes:
#		
#		return self._filter_bin_display_items.acceptedItemTypes()
#	
#	@QtCore.Slot(bool)
#	def setBinItemFiltersEnabled(self, filters_enabled:bool):
#
#		if not self._item_filters_enabled != filters_enabled:
#			return
#
#		self.beginFilterChange()
#		self._item_filters_enabled = filters_enabled
#		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)
#
#	def binItemFiltersEnabled(self) -> bool:
#
#		return self._item_filters_enabled
#	
#	def binColumnFiltersEnabled(self) -> bool:
#
#		return self._column_filters_enabled
#
#	@QtCore.Slot(bool)
#	def setBinColumnFiltersEnabled(self, filters_enabled:bool):
#
#		if not self._column_filters_enabled != filters_enabled:
#			return
#		
#		print("KK")
#
#		self.beginFilterChange()
#		self._column_filters_enabled = filters_enabled
#		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Columns)
#
#		self.sig_bin_view_enabled.emit(filters_enabled)
#
#	@QtCore.Slot(bool)
#	def setBinColumnFiltersDisabled(self, filters_disabled:bool):
#		"""Convenience method to bypass filters"""
#
#		self.setBinColumnFiltersEnabled(not filters_disabled)
#
#	@QtCore.Slot(object)
#	def setSiftOptions(self, sift_options:object):
#		"""TODO"""
#
#	@QtCore.Slot(bool)
#	def setSiftEnabled(self, is_enabled:bool):
#		"""TODO"""
#
#	@QtCore.Slot(str)
#	def setSearchText(self, search_text:str):
#
#		if self._filter_find_in_bin.searchText() == search_text:
#			return
#		
#		self.beginFilterChange()
#		self._filter_find_in_bin.setSearchText(search_text)
#		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)
#
#	###
#
#	def lessThan(self, source_left:QtCore.QModelIndex, source_right:QtCore.QModelIndex) -> bool:
#
#		#sort_role = self.sortRole()
#		sort_role = QtCore.Qt.ItemDataRole.InitialSortOrderRole
#
#		return self._sort_collator.compare(
#			source_left.data(sort_role),
#			source_right.data(sort_role)
#		) <= 0
#
#	@QtCore.Slot(QtCore.QModelIndex, int, QtCore.QModelIndex, int)
#	def moveColumn(self, sourceParent:QtCore.QModelIndex, col_start:int, destinationParent:QtCore.QModelIndex, col_dest:int) -> bool:
#
#		# Need to map the logical proxy columns here to logical source columns
#		# But without a row available, indexes come back as invalid
#
#		source_col_start = self.mapToSourceColumn(col_start)
#		source_col_end   = self.mapToSourceColumn(col_dest)
#
##		source_start_name = self.sourceModel().headerData(source_col_start, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole)
##		source_start_end  = self.sourceModel().headerData(source_col_end-1, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole) if source_col_end > 0 else "<<FRONT>>"
##		print(f"Proxy model wants to move {source_start_name} to before {source_start_end}")
#		
#		return self.sourceModel().moveColumn(QtCore.QModelIndex(), source_col_start, QtCore.QModelIndex(), source_col_end)
#
#	def mapToSourceColumn(self, proxy_column:int) -> int|None:
#		"""Map a logical column to its parent model column"""
#
#		visible_source_columns = []
#		
#		for source_col in range(self.sourceModel().columnCount(QtCore.QModelIndex())):
#			
#			if len(visible_source_columns) > proxy_column:
#				return visible_source_columns[-1]
#			
#			elif self.filterAcceptsColumn(source_col, QtCore.QModelIndex()):
#				visible_source_columns.append(source_col)
#
#		# I guess just go to the end man I dunno
#		return self.sourceModel().columnCount(QtCore.QModelIndex())
#		raise ValueError(f"Could not map proxy column {proxy_column} to source model")
#
#
#	def filterAcceptsColumn(self, source_column:int, source_parent:QtCore.QModelIndex) -> bool:
#
#		# Allow all if filters are not enabled
#		if not self._column_filters_enabled:
#			return True
#		
#		return not self.sourceModel().headerData(source_column, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)
#	
#	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex):
#
#		# Allow all if filters are not enabled
#		if not self._item_filters_enabled:
#			return True
#		
#		return all([
#			self._filter_bin_display_items.filterAcceptsItem(self, source_row, source_parent),
#			self._filter_find_in_bin.filterAcceptsItem(self, source_row, source_parent)
#		])