import typing, dataclasses, logging
from PySide6 import QtCore, QtGui, QtWidgets

from ..storage import storagemodel

from . import binviewsources
from ..binview import binviewitemtypes, jsonadapter

#DEFAULT_MODIFIED_SYMBOL = "*"
#"""Symbol appended to the name of a bin view"""

DEFAULT_FILE_EXTENSION = ".json"
DEFAULT_FILE_ENCODING  = "utf-8"
	

class BSBinViewProviderModel(QtCore.QAbstractItemModel):

	sig_session_sources_changed = QtCore.Signal()
	sig_stored_sources_changed  = QtCore.Signal()
	sig_storage_model_changed   = QtCore.Signal(object)

	def __init__(self, *args, storage_model:storagemodel.BSFileSystemModel|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._session_view_sources :list[binviewsources.BSAbstractBinViewSource] = []
		self._stored_view_sources  :list[binviewsources.BSAbstractBinViewSource] = []

		self._storage_model = None
		self.setStorageModel(storage_model or storagemodel.BSFileSystemModel(parent=self))
	
	def setStorageModel(self, storage_model:storagemodel.BSFileSystemModel):

		self.beginResetModel()

		if self._storage_model == storage_model:
			return
		
		if self._storage_model is not None:
			self._storage_model.disconnect(self)

		storage_model.rowsInserted .connect(self.storageFoundNewFiles)
		storage_model.rowsRemoved  .connect(self.storageRemovedFiles)
		storage_model.modelReset   .connect(self.storageModelReset)
		storage_model.layoutChanged.connect(self.storageLayoutChanged)
#		storage_model.rowsMoved    .connect(self.storageRowsMoved)
#		storage_model.dataChanged  .connect(print)
		
		self._storage_model = storage_model

		self.endResetModel()

		self.sig_storage_model_changed.emit(storage_model)

	def storageModel(self) -> storagemodel.BSFileSystemModel:

		return self._storage_model
	
	@QtCore.Slot()
	def storageModelReset(self):

		self.beginResetModel()
		self._stored_view_sources = []
		self.endResetModel()
	
#	@QtCore.Slot(QtCore.QModelIndex, int, int, QtCore.QModelIndex, int)
#	def storageRowsMoved(self, parent:QtCore.QModelIndex, sourceStart:int, sourceEnd:int, destParent:QtCore.QModelIndex, destStart:int):
#		
#		NOTE: Doesn't make sense to do here; should be handled by the storage model

#		print("Ok moving")

	@QtCore.Slot()
	def storageLayoutChanged(self, *args, **kwargs):
		"""Storage model moved things around, usually for sorting"""

		self.layoutAboutToBeChanged.emit()

		for row in range(
			self._storage_model.rowCount(self._storage_model.rootPathIndex())):
			
			file_index = self._storage_model.index(row, 0, self._storage_model.rootPathIndex())

			bin_info = binviewsources.BSBinViewSourceFile(
				self._storage_model.fileInfo(file_index).absoluteFilePath(),
				self._storage_model.fileInfo(file_index).completeBaseName()
				
			)

			self._stored_view_sources[row] = bin_info
		
		self.layoutChanged.emit()
			
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def storageFoundNewFiles(self, parent:QtCore.QModelIndex, first:int, last:int):

		if parent != self._storage_model.rootPathIndex():
			return
		
		self.beginInsertRows(QtCore.QModelIndex(), first + self._stored_views_row_offset(), last + self._stored_views_row_offset())

		binview_infos = []
		
		for new_binview_row in range(first, last+1):

			file_index                  = self._storage_model.index(new_binview_row, 0, parent)
			file_info:QtCore.QFileInfo  = file_index.data(QtWidgets.QFileSystemModel.Roles.FileInfoRole)

			logging.getLogger(__name__).debug("Found new stored binview: %s", QtCore.QDir.toNativeSeparators(file_info.absoluteFilePath()))

			bin_info = binviewsources.BSBinViewSourceFile(
				file_info.absoluteFilePath(),
				file_info.completeBaseName()
				
			)

			binview_infos.append(bin_info)

		self._stored_view_sources[first:first] = binview_infos
		
		self.endInsertRows()

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def storageRemovedFiles(self, parent:QtCore.QModelIndex, first:int, last:int):

		if parent != self._storage_model.rootPathIndex():
			return
		
		self.beginRemoveRows(QtCore.QModelIndex(), first + self._stored_views_row_offset(), last + self._stored_views_row_offset()+1)

		del self._stored_view_sources[first:last+1]

		self.endRemoveRows()

	######
	# Session Bin View Read/Write
	######
	
	def addSessionBinViewSource(self, binview_source:binviewsources.BSAbstractBinViewSource) -> bool:
		"""Add a new bin view to session memory."""

		separator_offset = 0 if self._session_view_sources else 1

		self.beginInsertRows(QtCore.QModelIndex(), 0, 0 + separator_offset)
		self._session_view_sources.insert(0, binview_source)
		self.endInsertRows()

		self.sig_session_sources_changed.emit()

	def clearSessionViewSources(self):
		"""Delete any ephemeral binviews"""

		if not len(self._session_view_sources):
			return
		
		self.beginRemoveRows(QtCore.QModelIndex(), 0, len(self._session_view_sources)) # NOTE: Not subtracting 1 because also removing separator
		self._session_view_sources = []
		self.endRemoveRows()

		self.sig_session_sources_changed.emit()

	
	#####
	# Stored Bin View Read/Write
	#####

	
	def deleteStoredBinViewSource(self, stored_binview:binviewsources.BSAbstractBinViewSource):
		"""Delete bin viewfrom storage"""

		for row, binview_source in enumerate(self._stored_view_sources):

			if stored_binview.name() == binview_source.name():
			
				self._storage_model.moveToTrash(
					self._storage_model.index(row, 0, self._storage_model.rootPathIndex())
				)

				self.sig_stored_sources_changed.emit()

				return
		
		else:
			raise ValueError("Bin view source unknown")
	
	def saveAsStoredBinView(self, binview_info:binviewitemtypes.BSBinViewInfo, with_name:str|None=None):

		with_name = with_name or binview_info.name
		
		data = jsonadapter.BSBinViewJsonAdapter().from_binview(
			dataclasses.replace(binview_info, name=with_name)
		).encode(DEFAULT_FILE_ENCODING)

		file_info = self._storage_model.writeToFile(
			file_name = with_name + DEFAULT_FILE_EXTENSION, 
			contents = data
		)

		if file_info is None:

			logging.getLogger(__name__).error(
				"Failed to write bin view %s to %s for some reason",
				with_name,
				with_name + DEFAULT_FILE_EXTENSION
			)

			return
	
		logging.getLogger(__name__).info(
			"Wrote bin view %s to %s",
			with_name,
			QtCore.QDir.toNativeSeparators(file_info.absoluteFilePath())
		)

		self.sig_stored_sources_changed.emit()
		
		return file_info

	#####
	# Convenience Methods
	#####

	def binViewSourceForRow(self, row:int) -> binviewsources.BSAbstractBinViewSource:
		"""Get a bin view source given a model row"""

		if row < len(self._session_view_sources):
			return self._session_view_sources[row]

		else:
			return self._stored_view_sources[row - self._stored_views_row_offset()]
		
	def binViewSources(self) -> list[binviewsources.BSAbstractBinViewSource]:
		"""All binviews in the collection.  Session and stored alike!  Wow!  Haha cool!"""

		return self._session_view_sources + self._stored_view_sources
	
	def binViewNames(self) -> list[str]:
		"""A list of all binview names.  From me, to me.  There ya go me.  Ya weirdo."""

		return [bvs.name() for bvs in self.binViewSources()]
	
	def sessionBinViewSources(self) -> list[binviewsources.BSAbstractBinViewSource]:
		
		return self._session_view_sources
	
	def storedBinViewSources(self) -> list[binviewsources.BSAbstractBinViewSource]:

		return self._stored_view_sources
		
	def _stored_views_row_offset(self) -> int:
		"""Return the row offset between stored views indexes and view row indexes"""

		session_count = len(self._session_view_sources)

		return session_count + (1 if session_count > 0 else 0)
	
	def _index_is_separator(self, index:QtCore.QModelIndex) -> bool:

		return self._session_view_sources and index.row() == self._stored_views_row_offset()-1

	###
	# QAbstractItemModel Stuff
	###

	def hasChildren(self, /, parent:QtCore.QModelIndex) -> bool:
		return False
	
	def columnCount(self, /, parent:QtCore.QModelIndex) -> int:
		return 1
	
	def rowCount(self, /, parent:QtCore.QModelIndex) -> int:
		return len(self._session_view_sources) + len(self._stored_view_sources) + (1 if self._session_view_sources else 0)
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		if parent.isValid():
			return QtCore.QModelIndex()
		
		return self.createIndex(row, column, None)
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		
		return QtCore.QModelIndex()
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):
		
		if not index.isValid():
			return
		
		if self._index_is_separator(index):
			
			if role == QtCore.Qt.ItemDataRole.AccessibleDescriptionRole:
				return "separator"

#			if role == QtCore.Qt.ItemDataRole.DisplayRole:
#				return self.tr("Stored Bin Views")
			
			return None

		
		item = self.binViewSourceForRow(index.row())
		
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			
			return item.name()
		
		elif role == QtCore.Qt.ItemDataRole.DecorationRole:

			return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.FolderVisiting if item.sourceType() == binviewsources.BSBinViewSourceType.File else QtGui.QIcon.ThemeIcon.DriveHarddisk) 
		
		elif role == QtCore.Qt.ItemDataRole.FontRole:

			if item.isModified():
#				print("*******MODIFIED")
				font = QtGui.QFont()
				font.setItalic(True)
				return font
		
		elif role == QtCore.Qt.ItemDataRole.ToolTipRole:
			return item.path() if item.sourceType() == binviewsources.BSBinViewSourceType.File else "Loaded From Active Bin"
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return item
		
	def flags(self, index:QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:

		if self._index_is_separator(index):
			return QtCore.Qt.ItemFlag.NoItemFlags
		
		return super().flags(index)
	
	def clear(self):
		"""Clear and reset the entire model"""

		self.beginResetModel()

		self._session_view_sources = []
		self._stored_view_sources  = []

		self.endResetModel()