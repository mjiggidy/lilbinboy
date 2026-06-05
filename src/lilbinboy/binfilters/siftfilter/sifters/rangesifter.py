import dataclasses

from PySide6 import QtCore
from . import BSAbstractSifter
from ..siftmatchtypes import BSSiftMatchTypes
from ....binitems import binitemtypes

import timecode, avbutils

@dataclasses.dataclass(frozen=True)
class BSSiftRangeInfo:
	"""Define which bin column must be visible to enable which range"""

	range_name:str
	range_role:binitemtypes.BSBinItemDataRoles

SIFT_RANGE_COLUMN_DEPENDENCIES:dict[avbutils.bins.BinColumnFieldIDs, BSSiftRangeInfo] = {

	avbutils.bins.BinColumnFieldIDs.Start: BSSiftRangeInfo(
		range_name = "Start to End Range",
		range_role= binitemtypes.BSBinItemDataRoles.TimecodeRangeRole,
	),

	avbutils.bins.BinColumnFieldIDs.AuxiliaryTC1: BSSiftRangeInfo(
		range_name = "Auxiliary TC 1 Range",
		range_role= binitemtypes.BSBinItemDataRoles.AuxTC1RangeRole,
	),

	avbutils.bins.BinColumnFieldIDs.AuxiliaryTC2: BSSiftRangeInfo(
		range_name = "Auxiliary TC 2 Range",
		range_role= binitemtypes.BSBinItemDataRoles.AuxTC2RangeRole,
	),

	avbutils.bins.BinColumnFieldIDs.AuxiliaryTC3: BSSiftRangeInfo(
		range_name = "Auxiliary TC 3 Range",
		range_role= binitemtypes.BSBinItemDataRoles.AuxTC3RangeRole,
	),

	avbutils.bins.BinColumnFieldIDs.AuxiliaryTC4: BSSiftRangeInfo(
		range_name = "Auxiliary TC 4 Range",
		range_role= binitemtypes.BSBinItemDataRoles.AuxTC4RangeRole,
	),

	avbutils.bins.BinColumnFieldIDs.AuxiliaryTC5: BSSiftRangeInfo(
		range_name = "Auxiliary TC 5 Range",
		range_role= binitemtypes.BSBinItemDataRoles.AuxTC5RangeRole,
	),

	avbutils.bins.BinColumnFieldIDs.InkNumber: BSSiftRangeInfo(
		range_name = "Ink Number Range",
		range_role= binitemtypes.BSBinItemDataRoles.InkNumberRangeRole,
	),

	avbutils.bins.BinColumnFieldIDs.MarkIn: BSSiftRangeInfo(
		range_name = "Mark In to Out Range",
		range_role= binitemtypes.BSBinItemDataRoles.TCMarkInOutRangeRole,
	),

	avbutils.bins.BinColumnFieldIDs.AuxiliaryInk: BSSiftRangeInfo(
		range_name = "Auxiliary Ink Range",
		range_role= binitemtypes.BSBinItemDataRoles.AuxInkNumberRangeRole,
	),

	avbutils.bins.BinColumnFieldIDs.KNMarkIn: BSSiftRangeInfo(
		range_name = "KN Mark In to Out Range",
		range_role= binitemtypes.BSBinItemDataRoles.KNMarkInOutRangeRole,
	),

	avbutils.bins.BinColumnFieldIDs.FilmTC: BSSiftRangeInfo(
		range_name = "Film TC Range",
		range_role= binitemtypes.BSBinItemDataRoles.FilmTCRangeRole,
	),

	avbutils.bins.BinColumnFieldIDs.KNStart: BSSiftRangeInfo(
		range_name = "KN Start to End Range",
		range_role= binitemtypes.BSBinItemDataRoles.KNRangeRole,
	),

	avbutils.bins.BinColumnFieldIDs.SoundTC: BSSiftRangeInfo(
		range_name = "Sound TC Range",
		range_role= binitemtypes.BSBinItemDataRoles.SoundTCRole,
	),

}
"""Define which bin column must be visible to enable sift on a particular range"""


class BSRangeSifter(BSAbstractSifter):
	"""Sift items for which a specified range contains a specified value"""

	def __init__(
		self,
		sift_string:str                    = "",
		data_role  :QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole,
	):
	

		super().__init__(
			sift_string = sift_string,
			match_type  = BSSiftMatchTypes.Contains,
			data_role   = data_role
		)

	def sifterAcceptsIndex(self, index:QtCore.QModelIndex) -> bool:

		if not index.isValid() or not self._sift_string:
			return False
		
		item_range = index.data(self._data_role)

		if item_range is None:
			return False
		
		if isinstance(item_range, timecode.TimecodeRange):

			try:
				# NOTE: Not doing this conversion in __init__ because I'm not sure what item values we'll uncover for now...

				sift_string_santized = self._sift_string.strip(":; ")
				sift_value = timecode.Timecode(sift_string_santized, rate=item_range.rate, mode=item_range.mode)

			except Exception as e:
				return False
			
			return sift_value in item_range
		
		else:
			raise NotImplementedError(f"** Sift range not yet supported for {repr(item_range)}")