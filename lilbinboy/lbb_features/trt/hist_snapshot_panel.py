from PySide6 import QtSql, QtCore, QtGui, QtWidgets

class TRTHistorySnapshotProxyModel(QtCore.QSortFilterProxyModel):
	"""Proxy model to filter for an individual snapshot ID"""

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

class TRTHistorySnapshotPanel(QtWidgets.QFrame):
	"""A card/panel displaying details for a given snapshot"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._lbl_clip_color    = QtWidgets.QLabel()
		self._pixmap_clip_color = self.drawClipColor(QtCore.QSize(16, 16), QtGui.QColor())
		self._lbl_snapshot_name = QtWidgets.QLabel()
		self._lbl_datetime      = QtWidgets.QLabel("24 Jun 2024")

		# Editor
		self._txt_snapshot_name = QtWidgets.QLineEdit()
		self._btn_clip_color    = QtWidgets.QPushButton()
		self._btn_save          = QtWidgets.QPushButton()

		self._stack_header = QtWidgets.QStackedWidget()

		wdg_header_viewer = QtWidgets.QWidget()
		wdg_header_viewer.setLayout(QtWidgets.QHBoxLayout())
		wdg_header_viewer.layout().setContentsMargins(0,0,0,0)
		wdg_header_viewer.layout().addWidget(self._lbl_clip_color)
		wdg_header_viewer.layout().addWidget(self._lbl_snapshot_name)
		wdg_header_viewer.layout().addStretch()
		wdg_header_viewer.layout().addWidget(self._lbl_datetime)

		wdg_header_editor = QtWidgets.QWidget()
		wdg_header_editor.setLayout(QtWidgets.QHBoxLayout())
		wdg_header_editor.layout().setContentsMargins(0,0,0,0)
		wdg_header_editor.layout().addWidget(self._btn_clip_color)
		wdg_header_editor.layout().addWidget(self._txt_snapshot_name)
		wdg_header_editor.layout().addStretch()
		wdg_header_editor.layout().addWidget(self._btn_save)


		self._stack_header.addWidget(wdg_header_viewer)
		self._stack_header.addWidget(wdg_header_editor)
		self._stack_header.setSizePolicy(self._stack_header.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.Maximum)

		font = self._lbl_snapshot_name.font()
		font.setBold(True)
		self._lbl_snapshot_name.setFont(font)

		self._tree_sequences    = QtWidgets.QTreeView()
		self._tree_sequences.setModel(TRTHistorySnapshotProxyModel())
		self._tree_sequences.setUniformRowHeights(True)
		self._tree_sequences.setAlternatingRowColors(True)
		self._tree_sequences.setIndentation(0)

		self._lbl_clip_color.setPixmap(self._pixmap_clip_color)
		self._btn_clip_color.setIcon(QtGui.QIcon(self._pixmap_clip_color))

		self.layout().addWidget(self._stack_header)
		self.layout().addWidget(self._tree_sequences)
		self.layout().addWidget(QtWidgets.QGroupBox())

		self.setFrameShape(QtWidgets.QFrame.Shape.Panel)
		self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

	def setModel(self, model:QtCore.QAbstractItemModel):

		self._tree_sequences.model().setSourceModel(model)

	def model(self) -> QtCore.QAbstractItemModel:
		return self._tree_sequences.model().sourceModel()
	
	def setSnapshotRecord(self, snapshot_record:QtSql.QSqlRecord):
		

		if snapshot_record.field("is_current").value() == 1:
			self._stack_header.setCurrentIndex(1)

		self._lbl_snapshot_name.setText(snapshot_record.field("name").value())
		self._lbl_datetime.setText(snapshot_record.field("datetime_created").value())
		self._tree_sequences.model().setSnapshotIds([snapshot_record.field("id_snapshot").value()])

		if snapshot_record.field("clip_color").isNull():
			clip_color = QtGui.QColor(None)
		else:
			clip_color = QtGui.QColor(*[int(x) for x in str(snapshot_record.field("clip_color").value()).split(",")])
		#print("Using", clip_color)

		self._pixmap_clip_color = self.drawClipColor(size=QtCore.QSize(14,14), clip_color=clip_color)
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