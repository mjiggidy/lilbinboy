"""
Watch a folder for changes
"""

from __future__ import annotations

import logging
from PySide6 import QtCore, QtWidgets

class BSFileSystemModel(QtWidgets.QFileSystemModel):
	"""A File System Model that does nice things nicely thank you"""

	def rootPathIndex(self) -> QtCore.QModelIndex:
		"""The root index to the current root path"""

		if not self.rootPath():
			return QtCore.QModelIndex()

		return self.index(self.rootPath())

	def moveToTrash(self, index:QtCore.QModelIndex) -> bool:
		"""Move file to trash"""

		file_info:QtCore.QFileInfo = self.fileInfo(index)

		if not file_info.isFile():
			logging.getLogger(__name__).error(
				"Could not delete file because it is not a file: %s",
				QtCore.QDir.toNativeSeparators(file_info.absoluteFilePath())
			)
			return False
		
		success = QtCore.QFile.moveToTrash(file_info.absoluteFilePath())

		if not success:
			
			logging.getLogger(__name__).error("Unable to move to trash")
			return False
		
		logging.getLogger(__name__).info("Moved file to trash")
		
		# Force a lil refresharooni
		self.setRootPath(self.rootPath())

		return True
	
	def writeToFile(self, file_name:str, contents:bytes|bytearray|str) -> QtCore.QFileInfo:
		"""Write file safely with a tempfile"""

		output_path     = QtCore.QFileInfo(self.rootDirectory().filePath(file_name))
		tempfile_handle = QtCore.QTemporaryFile(self.rootDirectory().filePath(".XXXXXX.tmp"))

		if not tempfile_handle.open():
			raise OSError(f"Cannot create binview tempfile: {tempfile_handle.errorString()}")

		if not tempfile_handle.write(contents):
			raise OSError(f"Cannot write to binview tempfile: {tempfile_handle.errorString()}")
		
		output_handle = QtCore.QFile(output_path.absoluteFilePath())

		if output_handle.exists() and not output_handle.remove():
			raise OSError(f"Cannot replace existing binview at {QtCore.QDir.toNativeSeparators(output_path.absoluteFilePath())}: {output_handle.errorString()}")
		
		tempfile_handle.setAutoRemove(False)
		tempfile_handle.flush()

		if not tempfile_handle.rename(output_path.absoluteFilePath()):
			raise OSError(f"Cannot update stored binview: {tempfile_handle.error()}")
		
		tempfile_handle.close()

		# Force a lil refresharooni
		self.setRootPath(self.rootPath())
		
		return QtCore.QFileInfo(tempfile_handle)