import timecode
from .db_hist_sqlite import SnapshotDatabaseManager
from lilbinboy.lbb_features.trt.model_trt import TRTViewModel
from lilbinboy.lbb_features.trt.hist_snapshot_panel import TRTHistorySnapshotPanel, TRTHistorySnapshotDatabaseProxyModel
from lilbinboy.lbb_features.trt.hist_snapshot_list  import TRTHistorySnapshotLabelDelegate
from PySide6 import QtCore, QtGui, QtWidgets, QtSql

class SnapshotListProxyModel(QtCore.QIdentityProxyModel):
	"""Snapshot list with "Current" live option up top"""

	CUSTOM_ITEM_COUNT:int = 1
	"""Number of custom records at the top of the view"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._live_record = QtSql.QSqlRecord()
		self._live_name = "Current Sequences"

	# ---
	# Source model as QSqlQueryModel
	# ---
	def setSourceModel(self, sourceModel:QtSql.QSqlQueryModel):
		"""Set the source `QtSql.QSqlQueryModel` model"""
		
		if not isinstance(sourceModel, QtSql.QSqlQueryModel):
			raise TypeError("Source model must be of type `QtSql.QSqlQueryModel`")
		
		super().setSourceModel(sourceModel)

		# Get an empty record with rows defined for the table so we can fill it in
		# NOTE: sourceModel() needs to have already run the Query to provide a valid record here.
		# Handled in the controller via updateModelQueries()
		self._live_record = self.sourceModel().query().record()
		self._setLiveRecordDefaults()
	
	def sourceModel(self) -> QtSql.QSqlQueryModel:
		"""Returns, specifically, a QSqlQueryModel"""

		return super().sourceModel()

	# ---
	# QSqlQueryModel compliance
	# ---
	def record(self, row:int) -> QtSql.QSqlRecord:
		"""Return an SQL record for a given row"""

		if row < self.CUSTOM_ITEM_COUNT:
			return self._live_record

		return self.sourceModel().record(row-self.CUSTOM_ITEM_COUNT)
	
	# ---
	# Adding that live record up top there
	# ---
	def rowCount(self, /, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Row Count which includes the live row"""

		return super().rowCount(parent) + self.CUSTOM_ITEM_COUNT
	
	def mapToSource(self, proxyIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Map back to source model, accounting for offsets from live records"""

		# Live row doesn't exist in source
		if not proxyIndex.isValid() or proxyIndex.row() < self.CUSTOM_ITEM_COUNT:
			return QtCore.QModelIndex()
		
		# Otherwise offset the row by the live record count
		return self.sourceModel().index(proxyIndex.row() - self.CUSTOM_ITEM_COUNT, proxyIndex.column())
	
	def mapFromSource(self, sourceIndex:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Adjust source indexes to offset for live records"""

		if not sourceIndex.isValid():
			return QtCore.QModelIndex()
		
		return self.createIndex(sourceIndex.row() + self.CUSTOM_ITEM_COUNT, sourceIndex.column())
	
	def data(self, proxyIndex:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole=QtCore.Qt.ItemDataRole.DisplayRole):
		"""Return data, including the live row"""

		if not proxyIndex.isValid():
			return None
		
		if proxyIndex.row() < self.CUSTOM_ITEM_COUNT:
			if role == QtCore.Qt.ItemDataRole.DisplayRole:
				return self._live_record.value(self.sourceModel().headerData(proxyIndex.column(), QtCore.Qt.Orientation.Horizontal, role=QtCore.Qt.ItemDataRole.DisplayRole))
		
		else:
			return super().data(proxyIndex, role)
	
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> QtCore.QModelIndex:
		"""Create a valid index for the live row; pass through the rest"""
		
		if parent.isValid() or not self.hasIndex(row, column, parent):
			return QtCore.QModelIndex()
		
		if not parent.isValid() and row < self.CUSTOM_ITEM_COUNT:
			return self.createIndex(row, column, parent)
		
		return super().index(row-self.CUSTOM_ITEM_COUNT, column, parent)
	
	def flags(self, index:QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:
		"""Set standard flags for the live record; passthrough the rest"""

		if index.row() < self.CUSTOM_ITEM_COUNT:
			return QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled

		return super().flags(index)

	# ---
	# Live record updates
	# ---
	@QtCore.Slot(int)
	def setRate(self, rate:int):
		"""Set the current rate of the live record"""

		self._live_record.setValue("rate", rate)

		self.liveRecordUpdated()

	@QtCore.Slot(timecode.Timecode)
	def setDuration(self, duration:timecode.Timecode):
		"""Set the current duration of the live record"""

		self._live_record.setValue("duration_trimmed_tc", str(duration))
		self._live_record.setValue("duration_trimmed_frames", duration.frame_number)

		self.liveRecordUpdated()

	@QtCore.Slot()
	def _setLiveRecordDefaults(self):
		"""Set the default fields on the live record"""

		self._live_record.setValue("is_current", True)
		self._live_record.setValue("label_name", "Current")
		self._live_record.setValue("rate", 24)
		self._live_record.setValue("duration_trimmed_tc", "00:00:00:00")
		self._live_record.setValue("duration_trimmed_frames", 0)
		self._live_record.setValue("datetime_created_local", QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.DateFormat.ISODate))
		self._live_record.setNull("label_color")

		self.liveRecordUpdated()
	
	@QtCore.Slot()
	def liveRecordUpdated(self):
		"""Live record was updated"""

		self._live_record.setValue("datetime_created_local", QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.DateFormat.ISODate))
		
		self.dataChanged.emit(self.index(0, 0, QtCore.QModelIndex()), self.index(0, self.columnCount()-1, QtCore.QModelIndex()))

class TRTHistoryViewer(QtWidgets.QWidget):
	"""View and admire your favorite TRTs of olde"""

	sig_is_closing = QtCore.Signal()
	"""Window is about to close"""

	sig_live_trt_changed = QtCore.Signal(timecode.Timecode)
	sig_live_total_adjust_changed = QtCore.Signal(timecode.Timecode)
	sig_live_rate_changed = QtCore.Signal(int)


	def __init__(self, database:QtSql.QSqlDatabase,  *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setWindowTitle("History Viewer")
		self.setWindowFlag(QtCore.Qt.WindowType.Tool)
		self.setMinimumSize(QtCore.QSize(600,300))

		self._db = SnapshotDatabaseManager(database)

		self._db.initializeDatabase()
		

		#self.setWindowFlag(QtCore.Qt.WindowType.Tool)
		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(2,2,2,2)

		self._splt_pane = QtWidgets.QSplitter()
		self._lst_saved = QtWidgets.QListView()
		self._snapshots_scroll = QtWidgets.QScrollArea()

		self._snapshot_query_model = QtSql.QSqlQueryModel()
		self._snapshot_query_model.setQuery(self._db.getModelQuery())
		self._snapshot_query_proxy_model = SnapshotListProxyModel()
		self._snapshot_query_proxy_model.setSourceModel(self._snapshot_query_model)

		self.sig_live_rate_changed.connect(self._snapshot_query_proxy_model.setRate)
		self.sig_live_trt_changed.connect(self._snapshot_query_proxy_model.setDuration)

		self._sequence_query_model = QtSql.QSqlQueryModel()
		self._live_model = TRTViewModel()
		"""The "Current View" model from the main program"""

		self._status_bar = QtWidgets.QStatusBar()
		self._status_bar.setSizeGripEnabled(True)
		self._status_bar.setSizePolicy(self._status_bar.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.Maximum)

		self._key_delete = QtGui.QShortcut(QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Delete), self._lst_saved)
		self._key_delete.activated.connect(self.deleteSnapshotLabelsRequested)
		self._key_delete.setContext(QtGui.Qt.ShortcutContext.WidgetWithChildrenShortcut)

		self._setupWidgets()
	
	def _setupWidgets(self):

		self._lst_saved.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, self.sizePolicy().verticalPolicy())
		self._lst_saved.setItemDelegate(TRTHistorySnapshotLabelDelegate())
		self._lst_saved.setAlternatingRowColors(True)
		self._lst_saved.setModel(self._snapshot_query_proxy_model)
		self._lst_saved.selectionModel().selectionChanged.connect(self.snapshotSelectionChanged)
		self._lst_saved.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._lst_saved.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
		self._lst_saved.model().dataChanged.connect(lambda: self.updateStatusBarDelta(self.getSelectedSnapshotRecords()))

		self._splt_pane.addWidget(self._lst_saved)

		#self.layout().addWidget(self._lst_saved)

		self._snapshots_scroll.setLayout(QtWidgets.QVBoxLayout())
		self._snapshots_scroll.setVerticalScrollBarPolicy(QtGui.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._snapshots_scroll.setWidgetResizable(True)
		self._snapshots_scroll.layout().setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		self._snapshots_scroll.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		#self._scroll_panels.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, self.sizePolicy().verticalPolicy())

		self._snapshots_parent = QtWidgets.QWidget()
		self._snapshots_parent.setLayout(QtWidgets.QVBoxLayout())

		self._snapshots_scroll.setWidget(self._snapshots_parent)

		self._splt_pane.addWidget(self._snapshots_scroll)
		self._splt_pane.setSizes([185, 200])
		self._splt_pane.setStretchFactor(0, 0)
		self._splt_pane.setStretchFactor(1, 1)
		#self.layout().addWidget(self._scroll_panels)

		self.layout().addWidget(self._splt_pane)

		self.layout().addWidget(self._status_bar)

		lbl_deltaicon = QtWidgets.QLabel()
		lbl_deltaicon.setPixmap(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.AppointmentSoon).pixmap(QtCore.QSize(16,16) ))
		self._status_bar.addPermanentWidget(lbl_deltaicon)

		## Initial State
		self.updateModelQueries()
		#print(self._snapshot_query_model.query())

	def closeEvent(self, event):
		self.sig_is_closing.emit()
		event.accept()

	def getSelectedSnapshotRecords(self) -> QtSql.QSqlRecord:
		"""Resolve the selected records from the list"""

		# NOTE: selectionBehavor needs to be SelectRows for this to work (...and it is... but... I'm just sayin. y'know.)
		selected_rows = [idx.row() for idx in self._lst_saved.selectionModel().selectedRows()]	
		return [self._lst_saved.model().record(row) for row in selected_rows]

	@QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
	def snapshotSelectionChanged(self, selected:QtCore.QItemSelection, deselected:QtCore.QItemSelection):
		
		selected_snapshots = self.getSelectedSnapshotRecords()
		
		self.updateSnapshotCard(selected_snapshots)
		self.updateStatusBarDelta(selected_snapshots)
	
	@QtCore.Slot(list)
	def updateStatusBarDelta(self, snapshots:list[QtSql.QSqlRecord]):
		"""Calculate duration delta"""

		if len(snapshots) < 2:
			self._status_bar.clearMessage()
			return
		
		snapshots = sorted(snapshots, key=lambda r: QtCore.QDateTime.fromString(r.field("datetime_created_local").value(), format=QtCore.Qt.DateFormat.ISODate))
		snap_first = snapshots[0]
		snap_last = snapshots[-1]

		if snap_first.field("rate").value() != snap_last.field("rate").value():
			self._status_bar.showMessage("Cannot compare time deltas between mixed frame rates")
			return
		
		timecode_first = timecode.Timecode(snap_first.field("duration_trimmed_frames").value(), rate=snap_first.field("rate").value())
		timecode_last = timecode.Timecode(snap_last.field("duration_trimmed_frames").value(), rate=snap_last.field("rate").value())
		timecode_delta = timecode_last - timecode_first

		pos = "+" if timecode_delta > 0 else ""

		self._status_bar.showMessage(f"Duration from {snap_first.field("label_name").value()} to {snap_last.field("label_name").value()} changed by {pos}{timecode_delta}")

	@QtCore.Slot(list)
	def updateSnapshotCard(self, records:list[QtSql.QSqlRecord]):

		query = self._db.getSnapshotRecords(records)

		self._sequence_query_model.setQuery(query)

		# Clear old panels
		while self._snapshots_parent.layout().count():
			self._snapshots_parent.layout().itemAt(0).widget().deleteLater()
			self._snapshots_parent.layout().itemAt(0).widget().setParent(None)

		# Load in new panels
		for snapshot in records:
			history_panel = TRTHistorySnapshotPanel()
			history_panel.setSnapshotRecord(snapshot)

			if snapshot.field("is_current").value() == 1:
				history_panel.setModel(self._live_model)
				
				history_panel.setTrtFrames(self._live_trt)
				history_panel.setFinalAdjustmentFrames(self._live_adjust)
				history_panel.setRate(self._live_rate)
				
				history_panel.sig_save_current_requested.connect(self.saveLiveToSnapshot)
				
				self.sig_live_trt_changed.connect(history_panel.setTrtFrames)
				self.sig_live_total_adjust_changed.connect(history_panel.setFinalAdjustmentFrames)
				self.sig_live_rate_changed.connect(history_panel.setRate)
			else:
				history_panel.setModel(self._sequence_query_model)
				
			self._snapshots_parent.layout().addWidget(history_panel)
	
	def setLiveModel(self, datamodel:TRTViewModel):
		"""Set the "Current sequences" model from the main program"""
		self._live_model = datamodel
	
	def setLiveRate(self, rate:int):
		self._live_rate = rate
		self.sig_live_rate_changed.emit(self._live_rate)

	def setLiveTotalAdjustment(self, adjustment:timecode.Timecode):
		self._live_adjust = adjustment
		self.sig_live_total_adjust_changed.emit(self._live_adjust)
	
	def setLiveRuntime(self, trt:timecode.Timecode):
		self._live_trt = trt
		self.sig_live_trt_changed.emit(self._live_trt)

	def saveLiveToSnapshot(self, snapshot_name:str, clip_color:QtGui.QColor, rate:int, adjust_frames:int, duration_frames:int, timeline_info_list:list):

		id_snapsphot_new = self._db.saveLiveToSnapshot(snapshot_name,
			clip_color,
			rate,
			adjust_frames,
			duration_frames,
			timeline_info_list
		)

		self.updateModelQueries()

		for row in range(self._lst_saved.model().rowCount()):
			if self._lst_saved.model().record(row).field("id_snapshot").value() == id_snapsphot_new:
				self._lst_saved.setCurrentIndex(self._lst_saved.model().index(row,0))
				break

	def updateModelQueries(self):
		"""Refresh the data model"""
		
		self._snapshot_query_model.refresh()
		
		# NOTE: Keep an eye on the above -- re: Live Snapshot card.  Old code below, but resets Live Record to defaults
		#self._snapshot_query_model.setQuery(self._db.getModelQuery())
		#self._snapshot_query_proxy_model.setSourceModel(self._snapshot_query_model)
	
	def deleteSnapshotLabelsRequested(self):
		"""User requested to delete snapshots"""

		selected_snapshots = self.getSelectedSnapshotRecords()

		records_selected = [snap for snap in selected_snapshots if not snap.field("is_current").value()]

		if not records_selected:
			QtWidgets.QApplication.beep()
			return
		
		if len(records_selected) > 1:
			msg_warning = QtWidgets.QMessageBox.warning(self, "Delete Snapshots?", f"Are you sure you want to permanently delete these {len(records_selected)} snapshots?", QtWidgets.QMessageBox.StandardButton.YesToAll|QtWidgets.QMessageBox.StandardButton.Cancel)
		else:
			msg_warning = QtWidgets.QMessageBox.warning(self, "Delete Snapshot?", f"Are you sure you want to permanently delete this snapshot?", QtWidgets.QMessageBox.StandardButton.Yes|QtWidgets.QMessageBox.StandardButton.Cancel)
		
		if msg_warning == QtWidgets.QMessageBox.StandardButton.Cancel:
			return
		
		self.deleteSnapshotLabels(records_selected)
	
	def deleteSnapshotLabels(self, records:list[QtSql.QSqlRecord]):
		"""Delete a snapshot"""

		self._db.deleteSnapshotRecords(records)

		self.updateModelQueries()
		self.updateSnapshotCard([])
