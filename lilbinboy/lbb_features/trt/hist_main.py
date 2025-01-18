from lilbinboy.lbb_features.trt.hist_snapshot_panel import TRTHistorySnapshotPanel, TRTHistorySnapshotProxyModel
from lilbinboy.lbb_features.trt.hist_snapshot_list  import TRTHistorySnapshotLabelDelegate
from PySide6 import QtCore, QtGui, QtWidgets, QtSql


class TRTHistoryViewer(QtWidgets.QWidget):
	"""View and admire your favorite TRTs of olde"""

	def __init__(self, database:QtSql.QSqlDatabase,  *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setMinimumSize(QtCore.QSize(600,300))

		self._db = database

		self.setWindowTitle("History Viewer")
		#self.setWindowFlag(QtCore.Qt.WindowType.Tool)
		self.setLayout(QtWidgets.QHBoxLayout())

		self._splt_pane = QtWidgets.QSplitter()
		self._lst_saved = QtWidgets.QListView()
		self._snapshots_scroll = QtWidgets.QScrollArea()

		self._tree_temp_sequences = QtWidgets.QTreeView()

		self._snapshot_query_model = QtSql.QSqlQueryModel()
		self._sequence_query_model = QtSql.QSqlQueryModel()

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
		#self._scroll_panels.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, self.sizePolicy().verticalPolicy())

		self._snapshots_parent = QtWidgets.QWidget()
		self._snapshots_parent.setLayout(QtWidgets.QVBoxLayout())

		self._snapshots_scroll.setWidget(self._snapshots_parent)

		self._splt_pane.addWidget(self._snapshots_scroll)
		#self.layout().addWidget(self._scroll_panels)

		self.layout().addWidget(self._splt_pane)


		## Initial State
		self.updateModelQueries()
		#print(self._snapshot_query_model.query())

	@QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
	def snapshotSelectionChanged(self, selected:QtCore.QItemSelection, deselected:QtCore.QItemSelection):
		
		
		model = self._lst_saved.model()
		selected_indexes = self._lst_saved.selectionModel().selectedIndexes()
		
		selected_snapshots = [model.record(idx.row()) for idx in selected_indexes]

		self.updateSnapshotCard(selected_snapshots)
		
		#selected_snapshot_ids = [model.record(idx.row()).field("id_snapshot").value() for idx in selected_indexes]

		
		#self.updateSnapshotCard(selected_snapshots)

	def updateSnapshotCard(self, snapshots:list[QtSql.QSqlRecord]):

		snapshot_ids = [row.field("id_snapshot").value() for row in snapshots]
		#print(snapshot_ids)

		query = QtSql.QSqlQuery(self._db)

		query_placeholders = ",".join(["?"]*len(snapshot_ids))
		query.prepare(
			f"""
			SELECT
				id_snapshot,
				clip_color,
				name,
				duration_tc,
				duration_ff
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
			history_panel.setModel(self._sequence_query_model)
			history_panel.sig_save_current_requested.connect(self.saveLiveToSnapshot)
			self._snapshots_parent.layout().addWidget(history_panel)
	
	def updateLiveSnapshot(self, reels:list):

		query = QtSql.QSqlQuery(self._db)

		id_snapshots = []

		# Get the ID of the "Current" row
		print(query.exec("SELECT id_snapshot FROM trt_snapshot_labels WHERE is_current=1"))
		while query.next():
			id_snapshots.append(int(query.value("id_snapshot")))
		
		if not id_snapshots:
			print("Nope")
			return
		
		# TODO
		id_snapshot = id_snapshots[0]

		query.prepare("DELETE FROM trt_snapshot_sequences WHERE id_snapshot = ?")
		query.addBindValue(id_snapshot)
		if not query.exec():
			print("I no delet")
			print(query.lastError().text())

		for idx in range(1,7):
			query.prepare(
				"""
				INSERT INTO trt_snapshot_sequences(
					"id_snapshot",
					"clip_color",
					"name",
					"duration_frames",
					"duration_tc",
					"duration_ff"
				) VALUES (
					?,?,?,?,?,?
				)
				""")
			query.addBindValue(id_snapshot)
			query.addBindValue("211,168,103")
			query.addBindValue(f"Reel {idx} v1.{idx}.3")
			query.addBindValue(86400)
			query.addBindValue("00:42:16:00")
			query.addBindValue("800+16")

			if not query.exec():
				print(query.lastError().text())
			print("I insert")

	def saveLiveToSnapshot(self, snapshot_name:str, clip_color:QtGui.QColor):

		query = QtSql.QSqlQuery(self._db)

		if clip_color.isValid():
			clip_color_str = ",".join(str(x) for x in [
				clip_color.red(),
				clip_color.green(),
				clip_color.blue()
			])
		else:
			clip_color_str = None

		# Cet current snapshot ID
		id_snapshots = []

		# Get the ID of the "Current" row
		print(query.exec("SELECT id_snapshot FROM trt_snapshot_labels WHERE is_current=1"))
		while query.next():
			id_snapshots.append(int(query.value("id_snapshot")))
		
		if not id_snapshots:
			print("Nope")
			return
		
		# TODO
		id_snapshot_current = id_snapshots[0]

		print("Gon copy from ", id_snapshot_current)

		# Copy "Current" snapshot label to new label
		query.prepare(
			"""
			INSERT INTO trt_snapshot_labels (
				"name",
				"clip_color",
				"rate",
				"duration_frames",
				"duration_tc",
				"duration_ff",
				"is_current"
			)

			SELECT
				?,
				?,
				rate,
				duration_frames,
				duration_tc,
				duration_ff,
				0
			FROM trt_snapshot_labels
			WHERE id_snapshot = ?
			"""
		)
		query.addBindValue(snapshot_name)
		query.addBindValue(clip_color_str)
		query.addBindValue(id_snapshot_current)
		if not query.exec():
			print(query.lastError().text())
		
		id_snapsphot_new = query.lastInsertId()

		print("Inserted into ", id_snapsphot_new)
		
		# Copy sequences
		query.prepare(
			"""
			INSERT INTO trt_snapshot_sequences (
				id_snapshot,
				clip_color,
				name,
				duration_frames,
				duration_tc,
				duration_ff
			)

			SELECT
				?,
				clip_color,
				name,
				duration_frames,
				duration_tc,
				duration_ff
			FROM trt_snapshot_sequences
			WHERE id_snapshot = ?
			ORDER BY datetime_created ASC
			"""
		)
		query.addBindValue(id_snapsphot_new)
		query.addBindValue(id_snapshot_current)
		if not query.exec():
			print(query.lastError().text())
		print("Copied", id_snapshot_current, "into", id_snapsphot_new)

		#if not self._db.commit():
		#	print(self._db.lastError().text())
		#print(self._db.isOpen())


		self.updateModelQueries()

		for row in range(self._lst_saved.model().rowCount()):
			print("Look at ", self._lst_saved.model().record(row).field("id_snapshot").value())
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
				id_snapshot,
				name,
				clip_color,
				rate,
				duration_frames,
				duration_tc,
				duration_ff,
				is_current,
				datetime(datetime_created, 'localtime') as datetime_created_local
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

