import abc
import timecode
from lilbinboy.lbb_common import LBClipColorPicker
from lilbinboy.lbb_common.paint_delegates import LBClipColorPainter
from lilbinboy.lbb_features.trt import wdg_summary
from PySide6 import QtSql, QtCore, QtGui, QtWidgets

class SnapshotClipColorDelegate(QtWidgets.QStyledItemDelegate):

	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOption, index:QtCore.QModelIndex):

		option.widget.style().drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter, option.widget)
		
		rect_device = option.rect
		
		min_size = min(rect_device.width(), rect_device.height())
		rect_clip_color = QtCore.QRectF(0, 0, min_size, min_size)
		rect_clip_color.moveCenter(rect_device.center())

		if index.data(QtCore.Qt.ItemDataRole.UserRole):
			clip_color =  QtGui.QColor(index.data(QtCore.Qt.ItemDataRole.UserRole))
		elif index.data(QtCore.Qt.ItemDataRole.DisplayRole):
			display_role = str(index.data(QtCore.Qt.ItemDataRole.DisplayRole))
			clip_color = QtGui.QColor(*[int(x) for x in display_role.split(",")])
		else:
			clip_color = QtGui.QColor()
		
		LBClipColorPainter(rect_clip_color, painter, clip_color=clip_color)
	
	def sizeHint(self, option:QtWidgets.QStyleOption, index:QtCore.QModelIndex) -> QtCore.QSize:
		min_size = min_size = min(option.rect.width(), option.rect.height())
		return QtCore.QSize(min_size,min_size)


class TRTHistorySnapshotAbstractProxyModel(QtCore.QSortFilterProxyModel):
	"""Abstract proxy model to filter for an individual snapshot ID"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		#self._filter_snapshot_ids = []
		self._field_column_names = {
			"sequence_color": "",
			"sequence_name": "Sequence Name",
			"duration_trimmed_tc": "Duration (TC)",
			"duration_trimmed_ff": "Duration (F+F)",
			"duration_trimmed_frames": "Duration (Frames)",
		}

	@abc.abstractmethod
	def resolveFieldName(self, source_column:int) -> str:
		"""Determine the field name (key) of a given column"""
	
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
		#self._field_column_names = {
		#	"sequence_color": "",
		#	"sequence_name": "Sequence Name",
		#	"duration_trimmed_tc": "Duration (TC)",
		#	"duration_trimmed_ff": "Duration (F+F)",
		#}

	
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

	sig_save_current_requested = QtCore.Signal(str, QtGui.QColor, int, int, int, list)
	"""Save "Current" Snapshot"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setSizePolicy(self.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.Maximum)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._color_clip = None

		self._final_adjust_frames = 0
		self._trt_frames = 0
		self._rate = 24

		# Stacked Header (Editor for "Current", Viewer for rest)
		self._stack_header = QtWidgets.QStackedWidget()
		self._stack_header.setSizePolicy(self._stack_header.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.Maximum)

		self._pixmap_clip_color = QtGui.QPixmap(QtCore.QSize(16, 16))
		self._pixmap_clip_color.fill(QtCore.Qt.GlobalColor.transparent)

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

		# Summary
		self._summary = wdg_summary.TRTSummary()
		self._summary.add_summary_item(wdg_summary.TRTSummaryItem(
			label = "Rate",
			value = "--"
		))
		self._summary.add_summary_item(wdg_summary.TRTSummaryItem(
			label ="Final Adjustment",
			value = "--"
		))
		self._summary.add_summary_item(wdg_summary.TRTSummaryItem(
			label ="Total Running Time",
			value = "--"
		))
		self.layout().addWidget(self._stack_header)
		self.layout().addWidget(self._tree_sequences)
		self.layout().addWidget(self._summary)

		self.setFrameShape(QtWidgets.QFrame.Shape.Panel)
		self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

		self._btn_save.clicked.connect(self.saveCurrentRequested)

	def setModel(self, model:QtCore.QAbstractItemModel):

		self._tree_sequences.model().setSourceModel(model)
		
		self.updateTreeSizes()
		
		# Listen for updates if this is a live view
		if isinstance(self._tree_sequences.model(), TRTHistorySnapshotLiveProxyModel):
			self._tree_sequences.model().rowsInserted.connect(self.updateTreeSizes)
	
	@QtCore.Slot()
	def updateTreeSizes(self):
		for col in range(self._tree_sequences.header().count()):
			self._tree_sequences.resizeColumnToContents(col)
		
		# Resize treeview to show all seqences (up to 10)
		if self._tree_sequences.model().rowCount():
			self._tree_sequences.setFixedHeight(
				self._tree_sequences.sizeHintForRow(0) * min(self._tree_sequences.model().rowCount(), 10) + self._tree_sequences.header().size().height() + self._tree_sequences.horizontalScrollBar().size().height()
			)

	def model(self) -> QtCore.QAbstractItemModel:
		return self._tree_sequences.model().sourceModel()
	
	def setClipColor(self, color:QtGui.QColor):
		self._color_clip = color

		icon_color = QtGui.QIcon()

		# Draw for std/hi dpi
		for s in [16, 32]:
			pix_color = QtGui.QPixmap(QtCore.QSize(s,s))
			pix_color.fill(QtCore.Qt.GlobalColor.transparent)
			scale_factor = s/16
			LBClipColorPainter(pix_color.rect(), QtGui.QPainter(pix_color), clip_color=self._color_clip, padding=QtCore.QSize(scale_factor * 3, scale_factor * 3), pen_width=scale_factor*1, shadow_offset=QtCore.QPoint(1*scale_factor, 1*scale_factor))
			icon_color.addPixmap(pix_color)

		self._btn_clip_color.setIcon(icon_color)
		self._lbl_clip_color.setPixmap(icon_color.pixmap(16,16))
	
	def setTrtFrames(self, trt:timecode.Timecode):
		self._trt_frames = trt.frame_number
		
		if self._rate != trt.rate:
			self.setRate(trt.rate)
		
		self._summary.add_summary_item(wdg_summary.TRTSummaryItem(
			label = "Total Running Time",
			value = timecode.Timecode(self._trt_frames, rate=self._rate)
		))

		#print("TRT set to ", timecode.Timecode(self._trt_frames, rate=self._rate))
	
	def setFinalAdjustmentFrames(self, adjustment:timecode.Timecode):
		self._final_adjust_frames = adjustment.frame_number

		if self._rate != adjustment.rate:
			self.setRate(adjustment.rate)

		self._summary.add_summary_item(wdg_summary.TRTSummaryItem(
			label = "Final Adjustment",
			value = timecode.Timecode(self._final_adjust_frames, rate=self._rate)
		))
		
		#print("Final adjust set to ", timecode.Timecode(self._rate, rate=self._rate))

	def setRate(self, rate:int):
		#print("Ayy I'm setting the thing to ", str(rate))
		self._rate = rate
	
	def setSnapshotRecord(self, snapshot_record:QtSql.QSqlRecord):
		

		# NOTE TO SELF: I'm setting the proxy models here, but the source models are set with setModel()
		# I... I forgot about that.

		if snapshot_record.field("is_current").value() == 1:
			self._stack_header.setCurrentIndex(1)
			self._txt_snapshot_name.setPlaceholderText("Current")
			self._tree_sequences.setModel(TRTHistorySnapshotLiveProxyModel())
		
		else:

			self._lbl_snapshot_name.setText(
				snapshot_record.field("label_name").value()
			)
			self._txt_snapshot_name.setPlaceholderText(
				snapshot_record.field("label_name").value()
			)
			self._lbl_datetime.setText(str(
				QtCore.QDateTime.fromString(
					snapshot_record.field("datetime_created_local").value(),
					format=QtCore.Qt.DateFormat.ISODate
				).toLocalTime().toString("dd MMM yyyy · hh:mm aP")
			))
			self._tree_sequences.model().setSnapshotIds([snapshot_record.field("id_snapshot").value()])
			
			self.setTrtFrames(timecode.Timecode(
				snapshot_record.field("duration_trimmed_frames").value(),
				rate = snapshot_record.field("rate").value()
			))

			self.setFinalAdjustmentFrames(timecode.Timecode(
				snapshot_record.field("duration_offset_frames").value(),
				rate = snapshot_record.field("rate").value()
			))

			self.setRate(timecode.Timecode(
				snapshot_record.field("rate").value()
			))

		self._tree_sequences.setItemDelegateForColumn(0, SnapshotClipColorDelegate())
		self._tree_sequences.model().rowsInserted.connect(lambda: print("Ayyy"))

		if snapshot_record.field("label_color").isNull():
			clip_color = QtGui.QColor(None)
		else:
			clip_color = QtGui.QColor(*[int(x) for x in str(snapshot_record.field("label_color").value()).split(",")])

		self.setClipColor(clip_color)

	@QtCore.Slot()
	def saveCurrentRequested(self):
		from lilbinboy.lbb_features.trt import exporters_trt

		label_text = self._txt_snapshot_name.text()
		label_color = self._color_clip
		sequences = exporters_trt.exportToSnapshot(self._tree_sequences.model())
		
		self.sig_save_current_requested.emit(label_text, label_color, self._rate, self._final_adjust_frames, self._trt_frames, sequences)