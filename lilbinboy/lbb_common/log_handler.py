import logging
from datetime import datetime
from PySide6 import QtCore

class LBLogDataModel(QtCore.QAbstractItemModel):
	"""Qt Data model for Lil' Gui' Loggin Boy"""

	HEADERS:list[str] = ["Module","Timestamp","Message"]

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		self._records:list[logging.LogRecord] = []
	
	def addLogRecord(self, record:logging.LogRecord):
		"""Add a log record"""

		self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
		self._records.insert(0, record)
		self.endInsertRows()

	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		return QtCore.QModelIndex()
	
	def rowCount(self, /, parent:QtCore.QModelIndex=None) -> int:
		
		# Keep er flat
		if parent.isValid():
			return 0
			
		return len(self._records)

		
	def columnCount(self, /, parent:QtCore.QModelIndex=None) -> int:

		return len(self.HEADERS)
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):
		
		#if index.parent().isValid():
		#		return None
		
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.getLogRecordAttribute(log_index=index.row(), log_attribute=index.column())

		
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, /, role:QtCore.Qt.ItemDataRole=None):
		
		if role == QtCore.Qt.ItemDataRole.DisplayRole and orientation == QtCore.Qt.Orientation.Horizontal:
			return self.HEADERS[section]

		#return super().headerData(section, orientation, role)
	
	def getLogRecordAttribute(self, log_index:int, log_attribute:int):
		record = self._records[log_index]

		if log_attribute == 0:
			return record.module
		elif log_attribute == 1:
			return str(datetime.fromtimestamp(record.created))
		elif log_attribute == 2:
			return record.message
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex=QtCore.QModelIndex()):
		return self.createIndex(row, column)

	


class LBLogHandler(logging.Handler):
	"""A python `logging` handler for Lil' GUI Boy"""

	def __init__(self, data_model:LBLogDataModel, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._data_model = data_model

	def data_model(self) -> LBLogDataModel:
		return self._data_model
	

	def emit(self, record:logging.LogRecord):
		print("OH HI")
		self.data_model().addLogRecord(record)
		#return super().emit(record)