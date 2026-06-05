import typing

import avbutils
from PySide6 import QtCore

from . import BSAnyColumnSifter
from ..siftmatchtypes import BSSiftMatchTypes
from ....binview import binviewitemtypes

class BSSingleColumnSifter(BSAnyColumnSifter):
	"""Sift items for text in a  single specified column"""

	def __init__(
		self,
		sift_column_info:binviewitemtypes.BSBinViewColumnInfo,
		sift_string     :str                    = "",
		match_type      :BSSiftMatchTypes       = BSSiftMatchTypes.Contains,
		data_role       :QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole
	):
		
		self._sift_column_info = sift_column_info

		super().__init__(
			sift_string = sift_string,
			match_type  = match_type,
			data_role   = data_role
		)

	def filter_columns(self, index:QtCore.QModelIndex) -> typing.Generator[QtCore.QModelIndex, None, None]:
		"""Filter to just the column"""

		# Get sibling index for given header
		source_model  = index.model()

		for col in range(source_model.columnCount(QtCore.QModelIndex())):

			col_field_id = source_model.headerData(col, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
			col_name     = source_model.headerData(col, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole)

			if col_field_id == self._sift_column_info.field_id:

				# User col: Skip if display name also does not match
				if col_field_id == avbutils.bins.BinColumnFieldIDs.User and col_name != self._sift_column_info.display_name:
					continue

				yield index.siblingAtColumn(col)
				return

		raise ValueError(f"Column {self._sift_column_info} not found")
	
	def siftColumnInfo(self) -> binviewitemtypes.BSBinViewColumnInfo:
		"""The `BSBinViewColumnInfo` column for which to sift"""

		return self._sift_column_info