import logging
from datetime import datetime
from PySide6 import QtCore

class LBLogDataModel(QtCore.QAbstractItemModel):
	"""Qt Data model for Lil' Gui' Loggin Boy"""

	HEADERS:list[str] = ["Module","Timestamp","Message"]
	"""Headers available for display"""

	DEFAULT_MAX_RECORDS:int = 128
	"""Default number of maxmimum records unless explicitly set per instance"""

	sig_record_count_changed = QtCore.Signal(int)
	"""Number of records has changed"""

	sig_max_records_changed = QtCore.Signal(int)
	"""Maxmimum number of allowed records has changed"""

	def __init__(self, max_records:int=DEFAULT_MAX_RECORDS, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		self._records:list[logging.LogRecord] = []
		self._max_records = max(int(max_records), 0)
	
	def addLogRecord(self, record:logging.LogRecord):
		"""Add a log record"""

		self.beginInsertRows(QtCore.QModelIndex(), 0, 0)
		self._records.insert(0, record)
		self.endInsertRows()

		self.cullRecords()
	
	def cullRecords(self) -> int:
		"""Keep record count below max length"""

		extra_records = max(len(self._records) - self._max_records, 0)

		if extra_records:
			self.beginRemoveRows(QtCore.QModelIndex(), self._max_records, self._max_records + extra_records)
			self._records = self._records[:self._max_records]
			self.endRemoveRows()

		# Return how many records have been yeeted gracefully	
		return extra_records
	
	def setMaxRecords(self, max_records:int, delay_cull:bool=False):
		"""Set a new max record length and cull extras"""

		if self._max_records < 0:
			raise ValueError("Max records cannot be negative")

		self._max_records = int(max_records)
		
		# Trim off them extras real good. No room for you fellas!
		if not delay_cull:
			self.cullRecords()
		
		self.sig_max_records_changed.emit(self._max_records)
	
	def maxRecords(self) -> int:
		"""Maximum number of log records maintained"""
		
		return self._max_records

	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Return the parent index (will be invalid; keepin' it flat)"""
		# Keepin' it flat for now
		return QtCore.QModelIndex()
	
	def rowCount(self, /, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Return the number of records"""

		# Keep 'er flat
		if parent.isValid():
			return 0
			
		return len(self._records)
		
	def columnCount(self, /, parent:QtCore.QModelIndex=None) -> int:
		"""Return the number of column headers"""

		return len(self.HEADERS)
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole):
		"""Return the requested data for an index"""

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.getLogRecordAttribute(log_index=index.row(), log_attribute=index.column())
		
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, /, role:QtCore.Qt.ItemDataRole=None):
		
		if role == QtCore.Qt.ItemDataRole.DisplayRole and orientation == QtCore.Qt.Orientation.Horizontal:
			return self.HEADERS[section]

		#return super().headerData(section, orientation, role)
	
	def getLogRecordAttribute(self, log_index:int, log_attribute:int):
		"""Get a record"""
		# TODO: Needs work

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
	"""
	A python `logging` handler for Lil' GUI Boy.
	Hands off `logging.LogRecord`s to `LBLogDataModel` for PySide6 model/view stuff
	"""

	def __init__(self, data_model:LBLogDataModel, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._data_model = data_model

	def data_model(self) -> LBLogDataModel:
		"""Return the associated `LBLogDataModel` instance"""
		return self._data_model
	
	def emit(self, record:logging.LogRecord):
		"""Do a log real nice"""
		self.data_model().addLogRecord(record)