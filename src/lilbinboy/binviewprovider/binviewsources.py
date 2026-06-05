import abc, enum
from os import PathLike

from ..binview import binviewitemtypes

from PySide6 import QtCore

class BSBinViewSourceType(enum.Enum):
	"""Type of bin view source"""

	File = enum.auto()
	"""Bin View originates from a file"""

	Bin  = enum.auto()
	"""Bin View originates from a bin"""

class BSAbstractBinViewSource(abc.ABC):
	"""An available bin view"""

	@abc.abstractmethod
	def binViewInfo(self) -> binviewitemtypes.BSBinViewInfo:
		"""Bin View Info for the given binview.  May load from file."""

	@abc.abstractmethod
	def name(self) -> str:
		"""This bin view's display name"""

	@abc.abstractmethod
	def isModified(self) -> bool:
		"""Is this binview modified from source"""

	@abc.abstractmethod
	def sourceType(self) -> BSBinViewSourceType:
		"""The type of bin view source"""

	def __hash__(self) -> int:
		return hash(self.name())

class BSBinViewSourceFile(BSAbstractBinViewSource):
	"""A file-based bin view"""

	def __init__(self, source_file_path:PathLike[str], name:str|None=None, not_exist_ok:bool=False):

		super().__init__()
		
		file_info = QtCore.QFileInfo(source_file_path)

		if not not_exist_ok and not file_info.isFile():
			raise FileNotFoundError("The requested bin view is not found")

		self._path = QtCore.QDir.toNativeSeparators(file_info.absoluteFilePath())
		
		# NOTE: `completeBaseName` includes all characters up to the last dot
		self._name = name if name is not None else file_info.completeBaseName()

	def name(self) -> str:

		return self._name
	
	def path(self) -> str:

		return self._path
	
	def isModified(self) -> bool:
		return False
	
	def sourceType(self) -> BSBinViewSourceType:

		return BSBinViewSourceType.File
	
	def binViewInfo(self) -> binviewitemtypes.BSBinViewInfo:
		
		from ..binview import jsonadapter

		with open(self._path) as binview_handle:
			return jsonadapter.BSBinViewJsonAdapter().to_binview(binview_handle.read())
		
	def __hash__(self) -> int:
		
		return hash(self._path)
	
	def __eq__(self, other) -> bool:

		if not isinstance(other, self.__class__):
			return False
		
		return hash(self) == hash(other)
			

class BSBinViewSourceBin(BSAbstractBinViewSource):
	"""A bin view from an active bin"""

	def __init__(self, binview_info:binviewitemtypes.BSBinViewInfo, is_modified:bool=False):

		super().__init__()

		self._binview_info = binview_info
		self._is_modified  = is_modified
	
	def name(self) -> str:
		
		return self._binview_info.name
	
	def sourceType(self) -> BSBinViewSourceType:

		return BSBinViewSourceType.Bin
	
	def isModified(self) -> bool:
		
		return self._is_modified
	
	def binViewInfo(self) -> binviewitemtypes.BSBinViewInfo:

		return self._binview_info