from PySide6 import QtCore
from . import BSAbstractSifter

from ..siftmatchtypes import BSSiftMatchTypes

class BSNoColumnSifter(BSAbstractSifter):
	"""Sift no column -- basically an inactive sifter I guess"""

	def __init__(self,
		sift_string:str                    = "",
		match_type :BSSiftMatchTypes       = BSSiftMatchTypes.Contains,
		data_role  :QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole
	):
		
		super().__init__(
			sift_string = sift_string,
			match_type  = match_type,
			data_role   = data_role
		)

	def sifterAcceptsIndex(self, index:QtCore.QModelIndex):

		return True
	
	def isValid(self) -> bool:
		"""No Column sift is essentially perma-inactive"""

		return False