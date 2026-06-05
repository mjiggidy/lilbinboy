import typing

import avbutils
from PySide6 import QtCore

from ..siftmatchtypes import BSSiftMatchTypes
from . import BSAbstractSifter

class BSAnyColumnSifter(BSAbstractSifter):
	"""Sift items for specified text in any column"""

	def __init__(
		self,
		sift_string:str = "",
		match_type :BSSiftMatchTypes = BSSiftMatchTypes.Contains,
		data_role  :QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole
	):

		super().__init__(
			sift_string = sift_string,
			match_type  = match_type,
			data_role   = data_role
		)

	def sifterAcceptsIndex(self, index:QtCore.QModelIndex) -> bool:

		if not index.isValid() or not self._sift_string:
			return True
		
		# Pre-determine the match type before we go a-spinnin through columns
		
		if self._match_type == BSSiftMatchTypes.BeginsWith:				
			sift_matches_string = lambda sift_string, source_data: source_data.startswith(sift_string)
		
		elif self._match_type == BSSiftMatchTypes.Contains:				
			sift_matches_string = lambda sift_string, source_data: sift_string in source_data

		elif self._match_type == BSSiftMatchTypes.MatchesExactly:
			sift_matches_string = lambda sift_string, source_data: sift_string == source_data
			
		# Prep for case-insensitivity
		sift_string = self._sift_string
		
		if not self.caseSensitive():
			sift_string = sift_string.casefold()
		
		for item_index in self.filter_columns(index):

			source_data = item_index.data(self._data_role)

			# Skip empty values
			if not source_data:
				continue
			
			# Prep for case-insensitivity
			if not self.caseSensitive():
				source_data = source_data.casefold()
			
			# Return True if we hit it
			if sift_matches_string(sift_string, source_data):
				return True
					
		return False
		
	def filter_columns(self, index:QtCore.QModelIndex) -> typing.Generator[QtCore.QModelIndex, None, None]:
		"""Filter columns considered for sift"""

		yield from (index.siblingAtColumn(col) for col in range(index.model().columnCount(QtCore.QModelIndex())))
	
	def caseSensitive(self) -> bool:

		return False