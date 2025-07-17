"""
Manage QSettings location & format
"""

import logging
from os import PathLike
from PySide6 import QtCore

class LBSettingsManager:

	def __init__(self, format:QtCore.QSettings.Format=QtCore.QSettings.Format.IniFormat, basepath:str|PathLike|None=None):

		self._format = format
		self._basepath   = basepath or QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.AppDataLocation)
	
	def basePath(self) -> QtCore.QUrl:
		"""The current path"""
		return QtCore.QUrl.fromLocalFile(self._basepath)
	
	def format(self) -> QtCore.QSettings.Format:
		"""The file format used for settings"""
		return self._format
	
	def settings(self, feature_name:str) -> QtCore.QSettings:
		"""Get a settings handler for a given feature"""

		if self.format() == QtCore.QSettings.Format.IniFormat:			
			settings= QtCore.QSettings(self.settingsPath(feature_name).toLocalFile(), QtCore.QSettings.Format.IniFormat)
			logging.getLogger(__name__).debug("Handing off settings for %s at %s", feature_name, settings.fileName())
			return settings
		else:
			return QtCore.QSettings(self.format())
	
	def settingsPath(self, feature_name:str) -> QtCore.QUrl:
		return QtCore.QUrl.fromLocalFile(self.basePath().toLocalFile() + "/" + feature_name + "_config.ini")