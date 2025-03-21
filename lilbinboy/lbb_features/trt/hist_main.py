import timecode
from lilbinboy.lbb_features.trt.model_trt import TRTViewModel
from lilbinboy.lbb_features.trt.hist_snapshot_panel import TRTHistorySnapshotPanel, TRTHistorySnapshotDatabaseProxyModel
from lilbinboy.lbb_features.trt.hist_snapshot_list  import TRTHistorySnapshotLabelDelegate
from PySide6 import QtCore, QtGui, QtWidgets, QtSql


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

		self._db = database
		if not QtSql.QSqlQuery(self._db).exec("PRAGMA foreign_keys = ON;"):
			print("Error enabling foregin keys: ", self._db.lastError().text())

		if not QtSql.QSqlQuery(self._db).exec(
			"""
			CREATE TABLE IF NOT EXISTS "trt_snapshot_labels" (
				"id_snapshot"	INTEGER NOT NULL UNIQUE,
				"label_name"	TEXT NOT NULL,
				"datetime_created"	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
				"label_color"	TEXT,
				"rate"	INTEGER NOT NULL DEFAULT 24,
				"duration_trimmed_frames"	INTEGER NOT NULL DEFAULT 0,
				"duration_trimmed_tc"	TEXT NOT NULL DEFAULT '00:00:00:00',
				"duration_trimmed_ff"	TEXT NOT NULL DEFAULT '0+00',
				"duration_offset_frames"	INTEGER NOT NULL DEFAULT 0,
				"is_current"	INTEGER NOT NULL DEFAULT 0,
				PRIMARY KEY("id_snapshot" AUTOINCREMENT)
			)
			"""
		):
			print("Error setting up snapshot labels: ", self._db.lastError().text())

		if not QtSql.QSqlQuery(self._db).exec(
			"""
			CREATE TABLE IF NOT EXISTS "trt_snapshot_sequences" (
				"id_snapshot"	INTEGER NOT NULL,
				"id_sequence"	INTEGER NOT NULL UNIQUE,
				"sequence_color"	TEXT,
				"sequence_name"	TEXT NOT NULL,
				"duration_trimmed_frames"	INTEGER NOT NULL,
				"duration_trimmed_tc"	TEXT NOT NULL,
				"duration_trimmed_ff"	TEXT NOT NULL,
				"datetime_created"	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
				PRIMARY KEY("id_sequence" AUTOINCREMENT),
				FOREIGN KEY("id_snapshot") REFERENCES "trt_snapshot_labels"("id_snapshot") ON DELETE CASCADE
			)
			"""
		):
			print("Error setting up snapshot sequences: ", self._db.lastError().text())

		if not QtSql.QSqlQuery(self._db).exec(
			"""
			INSERT INTO trt_snapshot_labels (
				"label_name",
				"rate",
				"duration_trimmed_frames",
				"duration_trimmed_tc",
				"duration_trimmed_ff",
				"is_current"
			) SELECT
				"Current",
				24,
				0,
				"00:00:00:00",
				"0+00",
				1
			WHERE NOT EXISTS (
				SELECT 1 FROM trt_snapshot_labels
				WHERE is_current = 1
			)
			"""
		):
			print("Error adding Current label:", self._db.lastError().text())

		

		#self.setWindowFlag(QtCore.Qt.WindowType.Tool)
		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(2,2,2,2)

		self._splt_pane = QtWidgets.QSplitter()
		self._lst_saved = QtWidgets.QListView()
		self._snapshots_scroll = QtWidgets.QScrollArea()

		self._snapshot_query_model = QtSql.QSqlQueryModel()
		self._sequence_query_model = QtSql.QSqlQueryModel()
		self._current_model = TRTViewModel()
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
		self._lst_saved.setModel(self._snapshot_query_model)
		self._lst_saved.selectionModel().selectionChanged.connect(self.snapshotSelectionChanged)
		self._lst_saved.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

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

		## Initial State
		self.updateModelQueries()
		#print(self._snapshot_query_model.query())

	def closeEvent(self, event):
		self.sig_is_closing.emit()
		event.accept()

	@QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
	def snapshotSelectionChanged(self, selected:QtCore.QItemSelection, deselected:QtCore.QItemSelection):
		
		
		model = self._lst_saved.model()
		selected_indexes = self._lst_saved.selectionModel().selectedIndexes()
		
		selected_snapshots = [model.record(idx.row()) for idx in selected_indexes]

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
	def updateSnapshotCard(self, snapshots:list[QtSql.QSqlRecord]):

		snapshot_ids = [row.field("id_snapshot").value() for row in snapshots]
		#print(snapshot_ids)

		query = QtSql.QSqlQuery(self._db)

		query_placeholders = ",".join(["?"]*len(snapshot_ids))
		query.prepare(
			f"""
			SELECT
				"id_snapshot",
				"sequence_color",
				"sequence_name",
				"duration_trimmed_tc",
				"duration_trimmed_ff",
				"duration_trimmed_frames"
			FROM trt_snapshot_sequences
			WHERE id_snapshot IN ({query_placeholders})
			"""
		)
		for place, snapshot_id in enumerate(snapshot_ids):
			query.bindValue(place, snapshot_id)
		query.exec()

		self._sequence_query_model.setQuery(query)

		# Clear old panels
		while self._snapshots_parent.layout().count():
			self._snapshots_parent.layout().itemAt(0).widget().setParent(None)

		# Load in new panels
		for snapshot in snapshots:
			history_panel = TRTHistorySnapshotPanel()
			history_panel.setSnapshotRecord(snapshot)

			if snapshot.field("is_current").value() == 1:
				history_panel.setModel(self._current_model)
				self.sig_live_trt_changed.connect(history_panel.setTrtFrames)
				self.sig_live_total_adjust_changed.connect(history_panel.setFinalAdjustmentFrames)
				self.sig_live_rate_changed.connect(history_panel.setRate)
			else:
				history_panel.setModel(self._sequence_query_model)
				
			history_panel.sig_save_current_requested.connect(self.saveLiveToSnapshot)
			self._snapshots_parent.layout().addWidget(history_panel)
	
	def setCurrentModel(self, datamodel:TRTViewModel):
		"""Set the "Current sequences" model from the main program"""
		self._current_model = datamodel

	def saveLiveToSnapshot(self, snapshot_name:str, clip_color:QtGui.QColor, rate:int, adjust_frames:int, duration_frames:int, timeline_info_list:list):

		query = QtSql.QSqlQuery(self._db)

		if clip_color.isValid():
			clip_color_str = ",".join(str(x) for x in [
				clip_color.red(),
				clip_color.green(),
				clip_color.blue()
			])
		else:
			clip_color_str = None

		# Copy "Current" snapshot label to new label
		query.prepare(
			"""
			INSERT INTO trt_snapshot_labels (
				"label_name",
				"label_color",
				"rate",
				"duration_trimmed_frames",
				"duration_trimmed_tc",
				"duration_trimmed_ff",
				"duration_offset_frames",
				"is_current"
			)

			VALUES (
				?,
				?,
				?,
				?,
				?,
				?,
				?,
				0
			)
			"""
		)
		query.addBindValue(snapshot_name)
		query.addBindValue(clip_color_str)
		query.addBindValue(rate)
		query.addBindValue(duration_frames)
		query.addBindValue(str(timecode.Timecode(duration_frames, rate=rate)))
		query.addBindValue(str(duration_frames)) # TODO: F+F
		query.addBindValue(adjust_frames)
		if not query.exec():
			print(query.lastError().text())
		
		id_snapsphot_new = query.lastInsertId()

		print("Inserted into ", id_snapsphot_new)
		
		# Copy sequences
		for timeline_info in timeline_info_list:
			query.prepare(
				"""
				INSERT INTO trt_snapshot_sequences(
					"id_snapshot",
					"sequence_color",
					"sequence_name",
					"duration_trimmed_frames",
					"duration_trimmed_tc",
					"duration_trimmed_ff"
				) VALUES (
					?,?,?,?,?,?
				)
				""")
			query.addBindValue(id_snapsphot_new)
			query.addBindValue(timeline_info.clip_color)
			query.addBindValue(timeline_info.name)
			query.addBindValue(timeline_info.duration_frames)
			query.addBindValue(timeline_info.duration_tc)
			query.addBindValue(timeline_info.duration_ff)

			if not query.exec():
				print(query.lastError().text())
			print("I insert")

		#if not self._db.commit():
		#	print(self._db.lastError().text())
		#print(self._db.isOpen())


		self.updateModelQueries()

		for row in range(self._lst_saved.model().rowCount()):
			if self._lst_saved.model().record(row).field("id_snapshot").value() == id_snapsphot_new:
				self._lst_saved.setCurrentIndex(self._lst_saved.model().index(row,0))
				print("Yee")
				break
		#self._snapshot_query_model.setQuery("SELECT * FROM trt_snapshot_labels", QtSql.QSqlDatabase.database("trt"))
		#self._sequence_query_model.setQuery(self._sequence_query_model.query(), QtSql.QSqlDatabase.database("trt"))

	def updateModelQueries(self):
		self._snapshot_query_model.setQuery(QtSql.QSqlQuery(
			"""
			SELECT
				"id_snapshot",
				"label_name",
				"label_color",
				"rate",
				"duration_trimmed_frames",
				"duration_trimmed_tc",
				"duration_trimmed_ff",
				"duration_offset_frames",
				"is_current",
				datetime(datetime_created, "localtime") as "datetime_created_local"
			FROM trt_snapshot_labels
			ORDER BY is_current DESC, datetime_created DESC
			""",
			self._db))
	
	def deleteSnapshotLabelsRequested(self):
		"""User requested to delete snapshots"""

		model = self._snapshot_query_model
		records_selected = [model.record(r.row()) for r in self._lst_saved.selectedIndexes() if not bool(model.record(r.row()).field("is_current").value())]

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

		if not records:
			return

		id_snapshots = [record.field("id_snapshot").value() for record in records]

		query = QtSql.QSqlQuery(self._db)

		# Build placeholders
		placeholders = ",".join(["?"] * len(id_snapshots))

		query.prepare(
			f"""
			DELETE FROM trt_snapshot_labels
			WHERE id_snapshot IN ({placeholders})
			"""
		)
		for id_snapshot in id_snapshots:
			query.addBindValue(id_snapshot)
		
		if not query.exec():
			print(query.lastError().text())

		self.updateModelQueries()
		self.updateSnapshotCard([])
