import abc
from lilbinboy.lbb_common import LBClipColorPicker
from PySide6 import QtSql, QtCore, QtGui, QtWidgets

class SnapshotClipColorDelegate(QtWidgets.QStyledItemDelegate):

	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOption, index:QtCore.QModelIndex):

		option.widget.style().drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter, option.widget)
		
		rect_device = option.rect
		
		min_size = min(rect_device.width(), rect_device.height())
		rect_clip_color = QtCore.QRectF(0, 0, min_size, min_size).adjusted(2, 2, -2, -2)
		rect_clip_color.moveCenter(rect_device.center())

		if index.data(QtCore.Qt.ItemDataRole.UserRole):
			clip_color =  QtGui.QColor(index.data(QtCore.Qt.ItemDataRole.UserRole))
		elif index.data(QtCore.Qt.ItemDataRole.DisplayRole):
			display_role = str(index.data(QtCore.Qt.ItemDataRole.DisplayRole))
			clip_color = QtGui.QColor(*[int(x) for x in display_role.split(",")])
		else:
			clip_color = QtGui.QColor()
		
		self.drawClipColor(rect_clip_color, painter, clip_color)

		

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

class TRTHistorySnapshotAbstractProxyModel(QtCore.QSortFilterProxyModel):
	"""Proxy model to filter for an individual snapshot ID"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._filter_snapshot_ids = []
		self._field_column_names = {
			"sequence_color": "",
			"sequence_name": "Sequence Name",
			"duration_trimmed_tc": "Duration (TC)",
			"duration_trimmed_ff": "Duration (F+F)",
		}

	@abc.abstractmethod
	def resolveFieldName(self, source_column:int) -> str:
		"""Determine the field name (key) of a given column"""
		pass
	

	
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, role:QtCore.Qt.ItemDataRole):
		
		if orientation == QtCore.Qt.Orientation.Horizontal and role == QtCore.Qt.ItemDataRole.DisplayRole:

			field_name = super().headerData(section, orientation, role)
			if field_name in self._field_column_names:
				return self._field_column_names[field_name]
		
		return super().headerData(section, orientation, role)



class TRTHistorySnapshotLiveProxyModel(TRTHistorySnapshotAbstractProxyModel):
	"""Proxy Model for the Current View"""

	def resolveFieldName(self, source_column:int) -> str:
		
		field_name = self.sourceModel().headerData(source_column, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)
		return field_name
	
	def filterAcceptsColumn(self, source_column:int, source_parent:QtCore.QModelIndex) -> bool:
		field_name = self.resolveFieldName(source_column)
		return field_name in self._field_column_names
	
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, role:QtCore.Qt.ItemDataRole):
		
		if orientation == QtCore.Qt.Orientation.Horizontal and role == QtCore.Qt.ItemDataRole.DisplayRole:

			# I don't remember/understand why I can't use resolveFieldName here buuuut....
			field_name = super().headerData(section, orientation, QtCore.Qt.ItemDataRole.UserRole)
			if field_name in self._field_column_names:
				return self._field_column_names[field_name]
		
	#	return super().headerData(section, orientation, role)


class TRTHistorySnapshotDatabaseProxyModel(TRTHistorySnapshotAbstractProxyModel):
	"""Proxy model to filter for an individual snapshot ID"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self._filter_snapshot_ids = []
		self._field_column_names = {
			"sequence_color": "",
			"sequence_name": "Sequence Name",
			"duration_trimmed_tc": "Duration (TC)",
			"duration_trimmed_ff": "Duration (F+F)",
		}

	
	def setSnapshotIds(self, ids:list[int]):
		self._filter_snapshot_ids = [int(id) for id in ids]
		self.invalidateRowsFilter()

	def filterAcceptsRow(self, source_row:int, source_parent:QtCore.QModelIndex):
		
		id_snapshot = self.sourceModel().record(source_row).field("id_snapshot").value()
		if id_snapshot not in self._filter_snapshot_ids:
			return False
		
		return super().filterAcceptsRow(source_row, source_parent)
	
	def resolveFieldName(self, source_column:int) -> str:
		record = self.sourceModel().record()
		field_name = record.field(source_column).name()
		return field_name
	
	def filterAcceptsColumn(self, source_column:int, source_parent:QtCore.QModelIndex):

		field_name = self.resolveFieldName(source_column)

		if field_name not in self._field_column_names:
			return False
		
		return super().filterAcceptsColumn(source_column, source_parent)
		
	

class TRTHistorySnapshotPanel(QtWidgets.QFrame):
	"""A card/panel displaying details for a given snapshot"""

	sig_save_current_requested = QtCore.Signal(str, QtGui.QColor, list)
	"""Save "Current" Snapshot"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._color_clip = None

		# Stacked Header (Editor for "Current", Viewer for rest)
		self._stack_header = QtWidgets.QStackedWidget()
		self._stack_header.setSizePolicy(self._stack_header.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.Maximum)

		self._pixmap_clip_color = self.drawClipColor(QtCore.QSize(16, 16), QtGui.QColor())

		# Viewer widgets
		self._lbl_clip_color    = QtWidgets.QLabel()
		self._lbl_snapshot_name = QtWidgets.QLabel()
		self._lbl_datetime      = QtWidgets.QLabel()

		font = self._lbl_snapshot_name.font()
		font.setBold(True)
		self._lbl_snapshot_name.setFont(font)
		
		# Viewer stack
		wdg_header_viewer = QtWidgets.QWidget()
		wdg_header_viewer.setLayout(QtWidgets.QHBoxLayout())
		wdg_header_viewer.layout().setContentsMargins(0,0,0,0)
		wdg_header_viewer.layout().addWidget(self._lbl_clip_color)
		wdg_header_viewer.layout().addWidget(self._lbl_snapshot_name)
		wdg_header_viewer.layout().addStretch()
		wdg_header_viewer.layout().addWidget(self._lbl_datetime)

		# Editor widgets
		self._txt_snapshot_name = QtWidgets.QLineEdit()
		self._btn_clip_color    = QtWidgets.QToolButton()
		self._btn_save          = QtWidgets.QPushButton()

		self._txt_snapshot_name.setMaxLength(32)
		font = self._txt_snapshot_name.font()
		font.setBold(True)
		self._txt_snapshot_name.setFont(font)

		self._btn_save.setText("Save Snapshot")
		self._btn_save.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentSave))

		# Editor stack
		wdg_header_editor = QtWidgets.QWidget()
		wdg_header_editor.setLayout(QtWidgets.QHBoxLayout())
		wdg_header_editor.layout().setContentsMargins(0,0,0,0)
		wdg_header_editor.layout().addWidget(self._btn_clip_color)
		wdg_header_editor.layout().addWidget(self._txt_snapshot_name)
		wdg_header_editor.layout().addWidget(self._btn_save)


		self._stack_header.addWidget(wdg_header_viewer)
		self._stack_header.addWidget(wdg_header_editor)


		self._tree_sequences    = QtWidgets.QTreeView()
		self._tree_sequences.setModel(TRTHistorySnapshotDatabaseProxyModel())
		self._tree_sequences.setUniformRowHeights(True)
		self._tree_sequences.setAlternatingRowColors(True)
		self._tree_sequences.setIndentation(0)

		
		self._clip_color_picker = LBClipColorPicker()
		self._clip_color_picker.setFixedSize(8*11, 4*10)

		self._mnu_clip_color = QtWidgets.QMenu()
		self._act_clip_color = QtWidgets.QWidgetAction(self._mnu_clip_color)
		self._act_clip_color.setDefaultWidget(self._clip_color_picker)
		self._clip_color_picker.sig_selected_color_changed.connect(self.setClipColor)
		self._clip_color_picker.sig_hovered_color_changed.connect(self.setClipColor)
		self._mnu_clip_color.addAction(self._act_clip_color)
		
		self._btn_clip_color.setMenu(self._mnu_clip_color)
		self._btn_clip_color.setPopupMode(QtWidgets.QToolButton.ToolButtonPopupMode.InstantPopup)



		self.layout().addWidget(self._stack_header)
		self.layout().addWidget(self._tree_sequences)
		self.layout().addWidget(QtWidgets.QGroupBox())

		self.setFrameShape(QtWidgets.QFrame.Shape.Panel)
		self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

		self._btn_save.clicked.connect(self.saveCurrentRequested)

	def setModel(self, model:QtCore.QAbstractItemModel):

		self._tree_sequences.model().setSourceModel(model)

	def model(self) -> QtCore.QAbstractItemModel:
		return self._tree_sequences.model().sourceModel()
	
	def setClipColor(self, color:QtGui.QColor):
		self._color_clip = color

		pix_color = self.drawClipColor(QtCore.QSize(16, 16), color)
		self._btn_clip_color.setIcon(pix_color)
		self._lbl_clip_color.setPixmap(pix_color)
	
	def setSnapshotRecord(self, snapshot_record:QtSql.QSqlRecord):
		

		# NOTE: Wasn't if/else here before... trying to sus out the Current View thing
		if snapshot_record.field("is_current").value() == 1:
			self._stack_header.setCurrentIndex(1)
			self._txt_snapshot_name.setPlaceholderText("Current")
			self._tree_sequences.setModel(TRTHistorySnapshotLiveProxyModel())
		
		else:

			self._lbl_snapshot_name.setText(snapshot_record.field("label_name").value())
			self._txt_snapshot_name.setPlaceholderText(snapshot_record.field("label_name").value())
			self._lbl_datetime.setText(str(QtCore.QDateTime.fromString(snapshot_record.field("datetime_created_local").value(), format=QtCore.Qt.DateFormat.ISODate).toLocalTime().toString("dd MMM yyyy · hh:mm aP")))
			self._tree_sequences.model().setSnapshotIds([snapshot_record.field("id_snapshot").value()])

		self._tree_sequences.setItemDelegateForColumn(0, SnapshotClipColorDelegate())

		if snapshot_record.field("label_color").isNull():
			clip_color = QtGui.QColor(None)
		else:
			clip_color = QtGui.QColor(*[int(x) for x in str(snapshot_record.field("label_color").value()).split(",")])
		#print("Using", clip_color)

		self.setClipColor(clip_color)

	def drawClipColor(self, size:QtCore.QSize, clip_color:QtGui.QColor) -> QtGui.QPixmap:

		"""For now"""

		pixmap = QtGui.QPixmap(size)
		pixmap.fill(QtCore.Qt.GlobalColor.transparent)

		painter = QtGui.QPainter(pixmap)
		
		rect_device = QtCore.QRectF(0, 0, size.width(), size.height())
		rect_color_box = rect_device.adjusted(2,2,-2,-2)

		#painter.setBackgroundMode(QtCore.Qt.BGMode.TransparentMode)

		
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
		painter.drawRect(rect_color_box)

		# Box Shadow (TODO: 128 opactiy not working)
		rect_color_box.moveCenter(rect_color_box.center() + QtCore.QPointF(1,1))
		#color_box.setWidth(color_box.width() + 2)

		color_shadow = pen.color()
		color_shadow.setAlpha(64)
		pen.setColor(color_shadow)
		brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
		painter.setPen(pen)
		painter.setBrush(brush)
		painter.drawRect(rect_color_box)

		painter.end()

		return pixmap
	
	@QtCore.Slot()
	def saveCurrentRequested(self):
		from lilbinboy.lbb_features.trt import exporters_trt

		label_text = self._txt_snapshot_name.text()
		label_color = self._color_clip
		sequences = exporters_trt.exportToSnapshot(self._tree_sequences.model())
		self.sig_save_current_requested.emit(label_text, label_color, sequences)