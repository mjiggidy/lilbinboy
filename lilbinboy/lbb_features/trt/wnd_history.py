import random
from lilbinboy.lbb_features.trt import wdg_summary
from PySide6 import QtCore, QtGui, QtWidgets, QtSql

class TRTHistorySnapshotProxyModel(QtCore.QSortFilterProxyModel):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._filter_snapshot_ids = []
		self._filter_field_names  = ["name", "duration_tc", "duration_ff"]
		self._field_column_names = {
			"clip_color": "",
			"name": "Sequence Name",
			"duration_tc": "Duration (TC)",
			"duration_ff": "Duration (F+F)",
		}

	
	def setSnapshotIds(self, ids:list[int]):
		self._filter_snapshot_ids = [int(id) for id in ids]
		self.invalidateRowsFilter()

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex):
		
		id_snapshot = self.sourceModel().record(source_row).field("id_snapshot").value()
		if id_snapshot not in self._filter_snapshot_ids:
			return False
		
		return super().filterAcceptsRow(source_row, source_parent)
	
	def filterAcceptsColumn(self, source_column:int, source_parent:QtCore.QModelIndex):
		record = self.sourceModel().record()
		field_name = record.field(source_column).name()

		if field_name not in self._filter_field_names:
			return False
		
		return super().filterAcceptsColumn(source_column, source_parent)
	
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, role:QtCore.Qt.ItemDataRole):
		
		if orientation == QtCore.Qt.Orientation.Horizontal and role == QtCore.Qt.ItemDataRole.DisplayRole:

			field_name = super().headerData(section, orientation, role)
			if field_name in self._field_column_names:
				return self._field_column_names[field_name]
		
		return super().headerData(section, orientation, role)

class TRTHistoryPanel(QtWidgets.QFrame):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._lbl_clip_color    = QtWidgets.QLabel()
		self._pixmap_clip_color = self.drawClipColor(QtCore.QSize(16, 16), QtGui.QColor())
		self._txt_snapshot_name = QtWidgets.QLabel()
		self._txt_datetime      = QtWidgets.QLabel("24 Jun 2024")
		self._summary           = wdg_summary.TRTSummary()

		font = self._txt_snapshot_name.font()
		font.setBold(True)
		self._txt_snapshot_name.setFont(font)

		self._tree_sequences    = QtWidgets.QTreeView()
		self._tree_sequences.setModel(TRTHistorySnapshotProxyModel())
		self._tree_sequences.setUniformRowHeights(True)
		self._tree_sequences.setAlternatingRowColors(True)
		self._tree_sequences.setIndentation(0)
	#	self.lbl.setFixedHeight(50)

		frm_title = QtWidgets.QFrame()
		frm_title.setLayout(QtWidgets.QHBoxLayout())
		frm_title.layout().setContentsMargins(0,0,0,0)
		
		self._lbl_clip_color.setPixmap(self._pixmap_clip_color)
		frm_title.layout().addWidget(self._lbl_clip_color)
		
		frm_title.layout().addWidget(self._txt_snapshot_name)
		frm_title.layout().addStretch()
		frm_title.layout().addWidget(self._txt_datetime)

		self.layout().addWidget(frm_title)
		self.layout().addWidget(self._tree_sequences)
		self.layout().addWidget(QtWidgets.QGroupBox())

		self.setFrameShape(QtWidgets.QFrame.Shape.Panel)
		self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

	def setModel(self, model:QtCore.QAbstractItemModel):

		self._tree_sequences.model().setSourceModel(model)

	def model(self) -> QtCore.QAbstractItemModel:
		return self._tree_sequences.model().sourceModel()
	
	def setSnapshotRecord(self, snapshot_record:QtSql.QSqlRecord):

		self._txt_snapshot_name.setText(snapshot_record.field("name").value())
		self._tree_sequences.model().setSnapshotIds([snapshot_record.field("id_snapshot").value()])

		clip_color = [int(x) for x in str(snapshot_record.field("clip_color").value()).split(",")] if not snapshot_record.field("clip_color").isNull() else None
		#print("Using", clip_color)

		self._pixmap_clip_color = self.drawClipColor(size=QtCore.QSize(14,14), clip_color=QtGui.QColor(*clip_color))
		self._lbl_clip_color.setPixmap(self._pixmap_clip_color)

	def drawClipColor(self, size:QtCore.QSize, clip_color:QtGui.QColor) -> QtGui.QPixmap:

		"""For now"""

		pixmap = QtGui.QPixmap(size)

		painter = QtGui.QPainter(pixmap)
		
		color_box = QtCore.QRectF(0, 0, size.width(), size.height()).adjusted(2,2,-2,-2)

		pixmap.fill(QtGui.QColor(255,255,255,255))

		
		# Set outline and fill
		pen = QtGui.QPen(QtGui.QColor(QtGui.QPalette().text().color()))
		pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
		brush = QtGui.QBrush()	

		# Use clip color if available
		if not clip_color.isValid():
			brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
		else:
			brush.setColor(clip_color)
			brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
		
		painter.setBrush(brush)
		painter.setPen(pen)
		painter.drawRect(color_box)

		# Box Shadow (TODO: 128 opactiy not working)
		color_box.moveCenter(color_box.center() + QtCore.QPointF(1,1))
		#color_box.setWidth(color_box.width() + 2)

		color_shadow = pen.color()
		color_shadow.setAlpha(64)
		pen.setColor(color_shadow)
		brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
		painter.setPen(pen)
		painter.setBrush(brush)
		painter.drawRect(color_box)

		painter.end()

		return pixmap
	
	#def sizeHint(self) -> QtCore.QSize:
	#	return QtCore.QSize(super().sizeHint().width(), 100)

class TRTHistorySnapshotLabelDelegate(QtWidgets.QStyledItemDelegate):

	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		super().paint(painter, option, index)
		painter.save()
		
		label_info = index.model().record(index.row())
		clip_color:QtSql.QSqlField = label_info.field("clip_color")

		r,g,b = (int(x) for x in clip_color.value().split(","))
		
		margin = QtCore.QPoint(30, 5)
		


		rect:QtCore.QRect = option.rect

		rect_clip_color = QtCore.QRectF(0,0, 10, 10)
		rect_clip_color.moveCenter(QtCore.QPointF(9, rect.center().y()))
		self.drawClipColor(rect=rect_clip_color, painter=painter, clip_color=QtGui.QColor(r,g,b))
		#self.drawClipColor()

		font = painter.font()
		#font.setPointSizeF(font.pointSizeF() * 1.2)
		font.setBold(True)

		painter.setFont(font)
		painter.drawText(rect.adjusted(margin.x(), margin.y(), -margin.y(), -margin.y()), label_info.field("name").value())

		font = QtGui.QFont()
		# font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont)
		#font.setPointSizeF(font.pointSizeF() * 1.2)
		sub_rect = rect.adjusted(margin.x(), margin.y() + 16, -margin.y(), -margin.y())

		font.setPointSizeF(font.pointSizeF() * 0.8)
		painter.setFont(font)
		painter.drawText(sub_rect, "01:47:23:12", QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignBottom)

		datetime_str = QtCore.QDateTime.fromString(label_info.field("datetime_created").value(), QtCore.Qt.DateFormat.ISODate)
		#print(datetime_str.toString(QtCore.Qt.DateFormat.TextDate))
		painter.drawText(sub_rect, datetime_str.toString("dd MMM yyyy"), QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignBottom)

		painter.restore()

	def drawClipColor(self, rect:QtCore.QRect, painter:QtGui.QPainter, clip_color:QtGui.QColor):
	#def drawClipColor():

		painter.save()

		

		#painter = QtGui.QPainter(self)
		#rect = QtCore.QRect(10, 5, 32, 32)
		#clip_color = QtGui.QColor(0,0,244)
		# Set box location
		color_box = rect
		#color_box.moveCenter(rect.center())
		
		# Set outline and fill
		pen = QtGui.QPen(QtGui.QColor(QtGui.QPalette().text().color()))
		pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
		brush = QtGui.QBrush()	

		# Use clip color if available
		if not clip_color.isValid():
			brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
		else:
			brush.setColor(clip_color)
			brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
		
		painter.setBrush(brush)
		painter.setPen(pen)
		painter.drawRect(color_box)

		# Box Shadow (TODO: 128 opactiy not working)
		color_box.moveCenter(color_box.center() + QtCore.QPointF(1,1))
		#color_box.setWidth(color_box.width() + 2)

		color_shadow = pen.color()
		color_shadow.setAlpha(64)
		pen.setColor(color_shadow)
		brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
		painter.setPen(pen)
		painter.setBrush(brush)
		painter.drawRect(color_box)

		painter.restore()
	
	def sizeHint(self, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex) -> QtCore.QSizeF:
		return QtCore.QSize(165, 38)




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

		while self._snapshots_parent.layout().count():
			self._snapshots_parent.layout().itemAt(0).widget().setParent(None)


		for idx, snapshot in enumerate(snapshots):
			history_panel = TRTHistoryPanel()
			history_panel.setSnapshotRecord(snapshot)
			history_panel.setModel(self._sequence_query_model)
			self._snapshots_parent.layout().addWidget(history_panel)

		#self._temp_history_panel.setSnapshotRecord(snapshots[0])