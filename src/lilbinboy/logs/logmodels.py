import logging, datetime
from PySide6 import QtCore, QtGui, QtWidgets

class BSLogDataModel(QtCore.QAbstractItemModel):
	"""Qt Data model for Lil' Gui' Loggin Boy"""

	HEADERS:list[str] = [
		QtCore.QObject.tr("Timestamp"),
		QtCore.QObject.tr("Module"),
		QtCore.QObject.tr("Level"),
		QtCore.QObject.tr("Message"),
	]
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
		#self._max_records.
		self.endInsertRows()

		self.cullRecords()
	
	def cullRecords(self) -> int:
		"""Keep record count below max length"""

		extra_records = max(len(self._records) - self._max_records, 0)

		if extra_records:
			self.beginRemoveRows(QtCore.QModelIndex(), self._max_records, self._max_records + extra_records - 1)
			self._records = self._records[:self._max_records]
			self.endRemoveRows()

		# Return how many records have been yeeted gracefully	
		return extra_records
	
	def setMaxRecords(self, max_records:int, delay_cull:bool=False):
		"""Set a new max record length and cull extras"""

		if max_records < 0:
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

		record = self._records[index.row()]
		header = self.HEADERS[index.column()]

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			if header == self.tr("Module"):
				return record.module
			elif header == self.tr("Timestamp"):
				return str(datetime.datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S"))
			elif header == self.tr("Message"):
				return record.getMessage()
			elif header == self.tr("Level"):
				return record.levelname.title()
			else:
				return ""
		
		elif role == QtCore.Qt.ItemDataRole.ForegroundRole:
			if record.levelno >= logging.ERROR:
				return QtGui.QBrush(QtGui.QColor("Red"))
			elif record.levelno <= logging.DEBUG:
				return QtGui.QBrush(
					QtWidgets.QApplication.palette().color(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Text)
				)
		
		elif role == QtCore.Qt.ItemDataRole.FontRole:
			if record.levelno >= logging.CRITICAL:
				font = QtWidgets.QApplication.font()
				font.setBold(True)
				return font
				

			#return self.getLogRecordAttribute(log_index=index.row(), log_attribute=index.column())
		
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
			return str(datetime.fromtimestamp(record.created).strftime("%Y-%m-%d %H:%M:%S"))
		elif log_attribute == 2:
			return record.getMessage()
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex=QtCore.QModelIndex()):
		return self.createIndex(row, column)