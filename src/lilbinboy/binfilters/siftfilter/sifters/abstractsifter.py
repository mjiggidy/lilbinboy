import abc, typing

from PySide6 import QtCore

from ....binview import binviewitemtypes
from .. import siftmatchtypes

import avb

class BSAbstractSifter(abc.ABC):
	"""An abstract sifter"""

	def __init__(self,
		sift_string:str                             = "",
		match_type :siftmatchtypes.BSSiftMatchTypes = siftmatchtypes.BSSiftMatchTypes.Contains,
		data_role  :QtCore.Qt.ItemDataRole          = QtCore.Qt.ItemDataRole.DisplayRole
	):

		self._sift_string = sift_string
		self._data_role   = data_role
		self._match_type  = match_type

	@abc.abstractmethod
	def sifterAcceptsIndex(self, index:QtCore.QModelIndex) -> bool:
		"""This sifter accepts the given index"""

	@abc.abstractmethod
	def isValid(self) -> bool:
		"""This filter is complete and should be used"""

	def siftString(self) -> str:
		"""The user string for which to sift"""

		return self._sift_string

	def matchType(self) -> siftmatchtypes.BSSiftMatchTypes:
		"""How to match the string"""

		return self._match_type
	
	def dataRole(self) -> QtCore.Qt.ItemDataRole:
		"""The model's item data role to be considered for the sift"""

		return self._data_role
	
	def isValid(self) -> bool:
		"""This sifter is ready to go"""

		return bool(self._sift_string)
	
	def __eq__(self, other) -> bool:

		if type(self) is not type(other):
			return NotImplemented
		
		return all({
			self.siftString() == other.siftString(),
			self.matchType()  == other.matchType(),
			self.dataRole()   == other.dataRole(),
		})
	
	def __repr__(self) -> str:

		return f"<{self.__class__.__name__} at {id(self):#x}: dataRole={self.dataRole().name}; matchType={self.matchType().name}, siftString=\"{self.siftString()}\">"

	@classmethod
	def sift_settings_from_bin(cls, bin_content:avb.bin.Bin, view_setting:binviewitemtypes.BSBinViewInfo) -> list[list[typing.Self]]:
		
		processed_sift_settings:list[BSAbstractSifter] = []

		if not bin_content.sifted:
			return processed_sift_settings
		
		# Sift settings are stored in reverse
		bin_sift_settings:list[avb.bin.SiftItem] = reversed(bin_content.sifted_settings)
		
		for sift_item in bin_sift_settings:

			sift_string = sift_item.string
			column_name = str(sift_item.column)
			match_type  = siftmatchtypes.BSSiftMatchTypes(sift_item.method)

			if column_name == "None":

				from .nocolumnsifter import BSNoColumnSifter

				processed_sift_settings.append(
					BSNoColumnSifter(
						sift_string  = sift_string,
						match_type   = match_type
					)
				)
			
			elif column_name in list(c.display_name for c in view_setting.columns):

				from .singlecolumnsifter import BSSingleColumnSifter

				processed_sift_settings.append(
					BSSingleColumnSifter(
						sift_column_info = view_setting.columns[list(c.display_name for c in view_setting.columns).index(column_name)],
						sift_string = sift_string,
						match_type = match_type,
					)
				)
			
			elif column_name.endswith("Range"): # Ugh I hate it

				from .rangesifter import BSRangeSifter, SIFT_RANGE_COLUMN_DEPENDENCIES

				for _, range_info in SIFT_RANGE_COLUMN_DEPENDENCIES.items():

					if column_name.casefold() == range_info.range_name.casefold():

						processed_sift_settings.append(
							BSRangeSifter(
								sift_string=sift_string,
								data_role=range_info.range_role,
							)
						)

						break

			else:

				from .anycolumnsifter import BSAnyColumnSifter
				
				processed_sift_settings.append(
					BSAnyColumnSifter(
						sift_string  = sift_string,
						match_type   = match_type
					)
				)

		if not len(processed_sift_settings) == 6:
			raise ValueError(f"Expected exactly 6 sift settings, got {len(processed_sift_settings)}")
		

		return [
			processed_sift_settings[:3], 
			processed_sift_settings[3:],
		]