from lilbinboy.lbb_features.trt.hist_snapshot_panel import TRTHistorySnapshotPanel
from lilbinboy.lbb_features.trt.hist_snapshot_list  import TRTHistorySnapshotLabelDelegate
from PySide6 import QtCore, QtGui, QtWidgets, QtSql


class TRTHistoryViewer(QtWidgets.QWidget):
	"""View and admire your favorite TRTs of olde"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setWindowTitle("History Viewer")
		#self.setWindowFlag(QtCore.Qt.WindowType.Tool)
		self.setLayout(QtWidgets.QHBoxLayout())

		self._splt_pane = QtWidgets.QSplitter()
		self._lst_saved = QtWidgets.QListView()
		self._snapshots_scroll = QtWidgets.QScrollArea()

		self._tree_temp_sequences = QtWidgets.QTreeView()

		self._sequence_query_model = QtSql.QSqlQueryModel()

		self._setupWidgets()
	
	def _setupWidgets(self):

		self._lst_saved.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, self.sizePolicy().verticalPolicy())
		self._lst_saved.setItemDelegate(TRTHistorySnapshotLabelDelegate())
		self._lst_saved.setAlternatingRowColors(True)
		self._lst_saved.setModel(QtSql.QSqlQueryModel())
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

	@QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
	def snapshotSelectionChanged(self, selected:QtCore.QItemSelection, deselected:QtCore.QItemSelection):
		
		
		model = self._lst_saved.model()
		selected_indexes = self._lst_saved.selectionModel().selectedIndexes()
		
		selected_snapshots = [model.record(idx.row()) for idx in selected_indexes]

		self.updateSnapshotCard(selected_snapshots)
		
		#selected_snapshot_ids = [model.record(idx.row()).field("id_snapshot").value() for idx in selected_indexes]

		
		self.updateSnapshotCard(selected_snapshots)

	def updateSnapshotCard(self, snapshots:list[QtSql.QSqlRecord]):

		snapshot_ids = [row.field("id_snapshot").value() for row in snapshots]
		#print(snapshot_ids)

		query = QtSql.QSqlQuery(QtSql.QSqlDatabase.database("trt"))

		query_placeholders = ",".join(["?"]*len(snapshot_ids))
		query.prepare(f"SELECT id_snapshot,clip_color,name,duration_tc,duration_ff FROM trt_snapshot_sequences s WHERE id_snapshot IN ({query_placeholders})")
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
			self._snapshots_parent.layout().addWidget(history_panel)