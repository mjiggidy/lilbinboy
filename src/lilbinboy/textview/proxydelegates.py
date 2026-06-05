"""
Manage display delegates
"""

from __future__ import annotations
import typing
import avbutils

from PySide6 import QtCore, QtWidgets

from ..binwidget import itemdelegates

from ..binitems import binitemtypes
from ..binview import binviewitemtypes

if typing.TYPE_CHECKING:
	from PySide6 import QtGui

type FormatLookupDict = dict[avbutils.BinColumnFormat, itemdelegates.BSGenericItemDelegate]
"""Key/Val Lookup For Delegate Lookup"""

type FieldLookupDict = dict[int, itemdelegates.BSGenericItemDelegate]
"""Key/Val Lookup For Particular Field Lookups"""

class BSBinColumnProxyDelegate(QtWidgets.QStyledItemDelegate):
	"""Proxy delegate looks up the real delegate from a provider when pressed for info"""

	def __init__(self, delegate_provider:BSBinColumnDelegateProvider|None=None):

		super().__init__(parent=delegate_provider)

	def delegateProvider(self) -> BSBinColumnDelegateProvider:
		"""The looker-upper of the actual delegates"""

		return self.parent()

	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex|QtCore.QPersistentModelIndex):
		"""Paint from the REAL delegate. Not... not whatever THIS is."""

		return self.parent().delegateForColumn(index.column()).paint(painter, option, index)
	
	def sizeHint(self, option, index) -> QtCore.QSize:
		"""Size hint for the bin column delegate"""

		return self.parent().delegateForColumn(index.column()).sizeHint(option, index)

class BSBinColumnDelegateProvider(QtCore.QObject):
	"""
	Item delegate provider for binwidget treeview columns.
	Allows delegate lookup based generic field type or bespoke individual fields
	"""

	sig_view_changed                  = QtCore.Signal(object)
	sig_default_item_delegate_changed = QtCore.Signal(object)

	sig_field_delegate_changed        = QtCore.Signal(int, object)
	"""(`FieldID`, `NewDelegate`)"""

	sig_format_delegate_changed       = QtCore.Signal(int, object)
	"""(`FormatID`, `NewDelegate`)"""

	def __init__(self,
		view:QtWidgets.QAbstractItemView,
		*args,
		default_delegate:itemdelegates.BSGenericItemDelegate|None=None,
		unique_delegates_per_field:FieldLookupDict|None=None,
		delegates_per_format:FormatLookupDict|None=None,
	):

		super().__init__(parent=view)

		self._view = view
		self._default_item_delegate = default_delegate or itemdelegates.BSGenericItemDelegate(parent=self.parent())

		# Cached instances -- TODO: Combine this with registry
		self._format_delegates       :FormatLookupDict = delegates_per_format       or dict()
		self._unique_field_delegates :FieldLookupDict  = unique_delegates_per_field or dict()

	def itemView(self) -> QtWidgets.QAbstractItemView:
		"""The view for which the delegates will be used"""

		return self._view
	
	def setDefaultItemDelegate(self, delegate:itemdelegates.BSGenericItemDelegate):
		"""Set the view's default item delegate (convenience for view's `setItemDelegate()` method)"""

		if self._default_item_delegate == delegate:
			return
		
		self._default_item_delegate = delegate
		self.sig_default_item_delegate_changed.emit(delegate)

	def defaultItemDelegate(self, index:QtCore.QModelIndex|None=None) -> itemdelegates.BSGenericItemDelegate:
		"""Return the view's default item delegate (convenience passthrough for view's `itemDelegate()` method)"""

		return self._default_item_delegate
	
	def setDelegateForFormat(self, column_format_id:avbutils.bins.BinColumnFormat, delegate:itemdelegates.BSGenericItemDelegate):
		"""Set the item delegate for a given format"""

		if column_format_id in self._format_delegates and self._format_delegates[column_format_id] == delegate:
			return

		self._format_delegates[column_format_id] = delegate

		self.sig_format_delegate_changed.emit(column_format_id, delegate)

	def setUniqueDelegateForField(self, column_field_id:int, delegate:itemdelegates.BSGenericItemDelegate):
		"""Set the item delegate for a given field"""

		if column_field_id in self._unique_field_delegates and self._unique_field_delegates[column_field_id] == delegate:
			return

		self._unique_field_delegates[column_field_id] = delegate
		self.sig_field_delegate_changed.emit(column_field_id, delegate)
	
	def unsetUniqueDelegateForField(self, column_field_id:int):
		"""Revert to default delegate for a field, if a unique delegate is set"""

		if column_field_id in self._unique_field_delegates:
			del self._unique_field_delegates[column_field_id]
	
	def delegateForFormat(self, format:avbutils.bins.BinColumnFormat) -> itemdelegates.BSGenericItemDelegate|None:
		"""Return the delegate for the given `avbutils.bins.BinColumnFormat"""

		return self._format_delegates.get(format, None)
	
	def delegateForField(self, field:int) -> itemdelegates.BSGenericItemDelegate|None:
		"""Return the delegate for the given `avbutils.bins.BIN_COLUMN_ROLES`"""

		# Return default delegate instance if unknown
		return self._unique_field_delegates.get(field, None)
	
	def setDelegateForColumn(self, logical_column_index:int, item_delegate:itemdelegates.BSGenericItemDelegate):
		"""Set a delegate given the logical column index of the view's model"""

		# Field ID from column
		model       = self._view.model()
		orientation = QtCore.Qt.Orientation.Horizontal

		# TODO: See if no-model-set condition can be dealt with better
		if model is None:
			return

		field  = model.headerData(logical_column_index, orientation, binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
		format = model.headerData(logical_column_index, orientation, binviewitemtypes.BSBinViewColumnInfoRole.FormatIdRole)

		if self._view.itemDelegateForColumn(logical_column_index) == item_delegate:
			return
		
		self.setUniqueDelegateForField(field, item_delegate)
		
	def delegateForColumn(self,
		logical_column_index:int,
		*args,
		orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal,
	) -> itemdelegates.BSGenericItemDelegate:
		"""Provide a delegate for a given logical column index of the view's model"""

		model  = self._view.model()

		# TODO: See if no-model-set condition can be dealt with better
		if model is None:
			return self._default_item_delegate

		field  = model.headerData(logical_column_index, orientation, binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
		format = model.headerData(logical_column_index, orientation, binviewitemtypes.BSBinViewColumnInfoRole.FormatIdRole)

		if field_delegate := self.delegateForField(field):
			return field_delegate
		
		elif format_delegate := self.delegateForFormat(format):
			return format_delegate
		
		else:
			return self._default_item_delegate

	def delegates(self) -> set[itemdelegates.BSGenericItemDelegate]:
		"""Get all known item delegate instances"""

		return set(list(self._format_delegates.values()) + list(self._unique_field_delegates.values()) + [self._default_item_delegate])