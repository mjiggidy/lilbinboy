import enum, typing

from PySide6 import QtCore
from . import abstractfiltermodel
from ..binview import binviewitemtypes

from ..utils import clumper

import avbutils

class BSBinViewFilterOptions(enum.IntFlag):
	"""Bin View Filter Option Flags"""

	ShowHidden  = enum.auto()
	ShowVisible = enum.auto()
	ShowAll     = ShowHidden|ShowVisible

class BSBinViewFilterRole(enum.IntEnum):

	IsPermanentlyVisibleRole = binviewitemtypes.BSBinViewColumnInfoRole._SentinelRole + 1
	"""Is this item meant to be permanently visible / un-hide-able"""

class BSBinViewFilterProxyModel(abstractfiltermodel.BSAbstractBinSortFilterProxyModel):

	DEFAULT_FILTER_OPTIONS      = BSBinViewFilterOptions.ShowVisible
	DEFAULT_PERMANENT_FIELD_IDS = [avbutils.bins.BinColumnFieldIDs.Name, avbutils.bins.BinColumnFieldIDs.BinItemIcon]

	sig_permanent_field_ids_changed = QtCore.Signal(object)

	def __init__(self,
		*args,
		bin_columns_model:QtCore.QAbstractItemModel|None = None,
		bin_view_options :BSBinViewFilterOptions|None = None,
		permanent_fields :typing.Iterable[avbutils.bins.BinColumnFieldIDs]|None = None,
		is_enabled       :bool = True,
		**kwargs
	):
		
		super().__init__(*args, is_enabled=is_enabled, **kwargs)

		self._bin_view_options    = bin_view_options or self.DEFAULT_FILTER_OPTIONS
		self._permanent_field_ids = set(permanent_fields or self.DEFAULT_PERMANENT_FIELD_IDS)

		if bin_columns_model:
			self.setSourceModel(bin_columns_model)

	@QtCore.Slot(object)
	def setBinViewOptions(self, bin_view_options:BSBinViewFilterOptions):
		"""Set which bin columns to accept"""
		
		if self._bin_view_options == bin_view_options:
			return
		
		self.beginFilterChange()
		self._bin_view_options = bin_view_options
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)

	def binViewOptions(self) -> BSBinViewFilterOptions:
		"""Which bin columns are accepted"""

		return self._bin_view_options
	
	def permanentFieldIDs(self) -> list[avbutils.bins.BinColumnFieldIDs]:
		"""A list of field IDs to remain permanently visible"""

		return list(self._permanent_field_ids)
	
	def setPermanentFieldIDs(self, field_ids:typing.Iterable[avbutils.bins.BinColumnFieldIDs]):
		"""Set the list of field IDs to remain permanently visible in this binview filter"""
		
		field_ids = set(field_ids)

		if self._permanent_field_ids == field_ids:
			return
		
		self.beginFilterChange()
		self._permanent_field_ids = field_ids
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)

		self.sig_permanent_field_ids_changed.emit(self.permanentFieldIDs())
			
	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:
		
		if not self.isEnabled():
			return True
		
		is_permanent_field = self.indexIsPermanentItem(self.sourceModel().index(source_row, 0, source_parent))
		is_hidden          = self.sourceModel().index(source_row, 0, source_parent).data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole) and not is_permanent_field
		
		if is_hidden:
			return self._bin_view_options & BSBinViewFilterOptions.ShowHidden
		
		else:
			return self._bin_view_options & BSBinViewFilterOptions.ShowVisible
		
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole) -> typing.Any:
		
		if role == binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole:

			# Column is only truly hidden if it's not set as a permanent field here
			return self.mapToSource(index).data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole) and not self.indexIsPermanentItem(index)
		
		if role == BSBinViewFilterRole.IsPermanentlyVisibleRole:
			
			return self.indexIsPermanentItem(index)
		
		return super().data(index, role)
	
	def setData(self, index, value, /, role = ...):
		
		if role == binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole and self.indexIsPermanentItem(index):

			# NOTE: Think about if I actually want to allow the value to change or not.
			# For now, this causes actual "item hidden" data to be hard-coded to False via this proxy
			# which updates item tooltips and such to show state=visible at all times, beyond just 
			# filtering out the rows themselves
			value = False
		
		return super().setData(index, value, role)
	
	def setEnabled(self, is_enabled:bool):
		
		if self._is_enabled == is_enabled:
			return
		
		self.beginFilterChange()
		self._is_enabled = is_enabled
		self.endFilterChange(QtCore.QSortFilterProxyModel.Direction.Rows)
		
		self.sig_filter_toggled.emit(is_enabled)

	def moveRows(self, sourceParent:QtCore.QModelIndex, sourceRow:int, count:int, destinationParent:QtCore.QModelIndex, destinationChild:int) -> bool:
		
		if sourceParent.isValid() or destinationParent.isValid():
			return False

		# NOTE TO SELF ABOUT ALLA THIS:
		# 
		# Clumps moving up from below the destination push down the indexes of any remaining under-clumps by the moving clump's length
		# 
		# Clumps moving down from above the destination pull up the destination index by the moving clump's length.
		# 
		# ALSO, want to move any hidden rows within the clump.  So first and last clump indexes should be used as a range for the count, 
		# rather than relying on the number of indexes in the clump, if that makes any sense to me later.


		mapped_source_row_first = self.mapToSource(self.index(sourceRow, 0, QtCore.QModelIndex())).row()
		mapped_source_row_last  = self.mapToSource(self.index(sourceRow+count-1, 0, QtCore.QModelIndex())).row()
		mapped_destination_row  = self.mapToSource(self.index(destinationChild-1, 0, QtCore.QModelIndex())).row() + 1

		# NOTE ABOUT THE ABOVE: Want to move the visible column to JUST UNDER its left-neighboring visible column, so
		# getting the proxy index of the left neighbor, mapping it back to source (all columns), and adding one to put it after that
		# If destinationChild=0, I think that maps to invalid index -1, +1 = 0 so I think that's okay.

		mapped_count = mapped_source_row_last - mapped_source_row_first + 1

		return self.sourceModel().moveRows(QtCore.QModelIndex(), mapped_source_row_first, mapped_count, QtCore.QModelIndex(), mapped_destination_row)
	
	def sort(self,  role:binviewitemtypes.BSBinViewColumnInfoRole, /, order:QtCore.Qt.SortOrder):
		"""REDEFINED SORT ROLE: Accepts `BSBinViewColumnInfoRole` instead of a column index, since this is a flat list"""
		
		if not self.sourceModel():
			return
		
		self.sourceModel().sort(role, order)
		
	def indexIsPermanentItem(self, index:QtCore.QModelIndex) -> bool:
		"""
		Does this index reference an item that is permanent?\n
		NOTE: This does not map back to source.
		"""
	
		return index.data(
			binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole
		) in self._permanent_field_ids