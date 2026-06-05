import typing, dataclasses
from PySide6 import QtCore
import avbutils

from ..binview import binviewitemtypes
from ..binitems import binitemtypes
from ..binfilters.siftfilter.sifters import rangesifter
from ..binfilters.siftfilter import siftproxymodel


class BSSiftRangesModel(QtCore.QAbstractListModel):
	"""Present sift-able ranges, based on bin column visibility"""

	def __init__(self, *args, sift_filter_model:siftproxymodel.BSBinSiftFilterProxyModel|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._sift_filter_model       = sift_filter_model or siftproxymodel.BSBinSiftFilterProxyModel()
		self._available_range_fields  = self.gatherRecognizedFields()
		self._setupSiftFilterModel()

	def setSiftFilterModel(self, sift_filter_model:siftproxymodel.BSBinSiftFilterProxyModel):

		if self._sift_filter_model == sift_filter_model:
			return

		self._sift_filter_model.disconnect(self)
		self._sift_filter_model = sift_filter_model
		
		self._setupSiftFilterModel()

		self.reset()

	def _setupSiftFilterModel(self):

		self._sift_filter_model.columnsInserted         .connect(self.siftFilterAddedColumns)
		self._sift_filter_model.columnsAboutToBeRemoved .connect(self.siftFilterRemovingColumns)
		self._sift_filter_model.layoutChanged           .connect(self.reset)
		self._sift_filter_model.modelReset              .connect(self.reset)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def siftFilterAddedColumns(self, parent:QtCore.QModelIndex, first:int, last:int):

		if parent.isValid():
			return
		
		adding_field_ids = self.gatherRecognizedFields(first, last)

		if not adding_field_ids:
			return
		
		new_row_first = len(self._available_range_fields)
		new_row_last  = new_row_first + len(adding_field_ids) - 1
		
		self.beginInsertRows(QtCore.QModelIndex(), new_row_first, new_row_last)
		self._available_range_fields.extend(adding_field_ids)
		self.endInsertRows()

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def siftFilterRemovingColumns(self, parent:QtCore.QModelIndex, first:int, last:int):

		if parent.isValid():
			return
		
		removing_field_ids = self.gatherRecognizedFields(first, last)

		if not removing_field_ids:
			return
		
		for field_id in removing_field_ids:

			# TODO: Coalesce (is that a/the word) into ranges
			# EDIT: OH HAHA IT WAS THE WORD, AND I EVEN SPELLED IT CORRECTLY

			idx = self._available_range_fields.index(field_id)

			self.beginRemoveRows(QtCore.QModelIndex(), idx, idx)
			del self._available_range_fields[idx]
			self.endRemoveRows()

	def mapToColumnIndex(self, index:QtCore.QModelIndex) -> int|None:
		"""Map a given index back to the sift model column index it references"""

		if not index.isValid():
			return

		field_id = self._available_range_fields[index.row()]

		for col in range(self._sift_filter_model.columnCount(QtCore.QModelIndex())):

			if field_id == self._sift_filter_model.headerData(col, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole):
				return col
			
		return None

	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:

		if parent.isValid():
			return 0
		
		return len(self._available_range_fields)
	
	@QtCore.Slot()
	def reset(self):

		self.beginResetModel()
		self._available_range_fields = self.gatherRecognizedFields()
		self.endResetModel()

	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole) -> typing.Any:

		if not index.isValid():
			return

		field_id       = self._available_range_fields[index.row()]
		range_info     = self.rangeInfoForColumnDependency(field_id)
		

		if not range_info:
			print("Well that's odd")
			return
		
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return range_info.range_name
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return range_info.range_role
		
		elif role == QtCore.Qt.ItemDataRole.ToolTipRole:

			src_column_idx = self.mapToColumnIndex(index)

			if src_column_idx is None:
				return

			format_id   = self._sift_filter_model.headerData(src_column_idx, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.FormatIdRole)
			format_name = avbutils.bins.BinColumnFormat(format_id).name
			
			return self.tr("Sift based on {format_type} range").format(format_type=format_name)

###


	def gatherRecognizedFields(self, first:int=0, last:int|None=None) -> list[avbutils.bins.BinColumnFieldIDs]:
		"""Gather fields that trigger range availability.  If `last` is not provided, it'll just do 'em all."""


		available_columns_count = self._sift_filter_model.columnCount(QtCore.QModelIndex())

		if not available_columns_count:
			return []

		last = last or available_columns_count - 1

		if not last < available_columns_count:
			raise ValueError("Last column index exceeds last available") # lol i dunno
		
		if not first <= last:
			raise ValueError(f"First index {first=} proceeds last index {last=}.  It shouldn't tho.  So...")

		new_cols = []
		for col in range(first, last+1):

			field_id = self._sift_filter_model.headerData(col, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)

			if field_id == avbutils.bins.BinColumnFieldIDs.User:
				continue

			if self.rangeInfoForColumnDependency(field_id):
				new_cols.append(field_id)
		
		return new_cols

	def rangeInfoForColumnDependency(self, field_id:avbutils.bins.BinColumnFieldIDs) -> rangesifter.BSSiftRangeInfo|None:
		"""For a given field id, get its range info thing (or `None`)"""

		return rangesifter.SIFT_RANGE_COLUMN_DEPENDENCIES.get(field_id)
	
####

class BSSiftRangesProxyModelDEPRECATED(QtCore.QSortFilterProxyModel):
	"""Present sift-able ranges, based on bin column visibility"""

	def __init__(self, *args, **kwargs):

		raise NotImplementedError

		super().__init__(*args, **kwargs)

		self._sort_collator = QtCore.QCollator()
		self._sort_collator.setNumericMode(True)
		self._sort_collator.setLocale(QtCore.QLocale.system())
		self._sort_collator.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)

		self.setSortRole(QtCore.Qt.ItemDataRole.DisplayRole)
		self.setDynamicSortFilter(True)
		self.sort(0, QtCore.Qt.SortOrder.AscendingOrder)

	def rangeInfoForColumnDependency(self, field_id:avbutils.bins.BinColumnFieldIDs) -> rangesifter.BSSiftRangeInfo|None:

		return rangesifter.SIFT_RANGE_COLUMN_DEPENDENCIES.get(field_id)

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex) -> bool:

		if source_parent.isValid():
			return False

		field_id:avbutils.bins.BinColumnFormat = self.sourceModel()\
			.index(source_row, 0, QtCore.QModelIndex())\
			.data(binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
		
		return bool(self.rangeInfoForColumnDependency(field_id))
	
	def lessThan(self, source_left:QtCore.QModelIndex, source_right:QtCore.QModelIndex):
		
		return self._sort_collator.compare(
			source_left .data(self.sortRole()),
			source_right.data(self.sortRole()),
		)

	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:
		return super().columnCount(QtCore.QModelIndex())
	
	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		return 1
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole) -> typing.Any:

		if not self.sourceModel():
			return
		
		field_id:avbutils.bins.BinColumnFormat = self.sourceModel().headerData(
			index.row(),
			QtCore.Qt.Orientation.Horizontal,
			binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole
		)

		range_trigger = self.rangeInfoForColumnDependency(field_id)

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return range_trigger.range_name
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return range_trigger.range_role
		
		elif role == QtCore.Qt.ItemDataRole.ToolTipRole:

			format_name = avbutils.bins.BinColumnFormat(
				self.mapToSource(index).data(
					binviewitemtypes.BSBinViewColumnInfoRole.FormatIdRole
				)).name
			
			return self.tr("Sift based on {format_type} range").format(format_type=format_name)
		
		#return super().data(index, role)