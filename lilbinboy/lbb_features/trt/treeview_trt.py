import pathlib
from PySide6 import QtCore, QtGui, QtWidgets

class TRTTreeViewHeaderItem(QtCore.QObject):

	def __init__(self, text:str, key:str):

		super().__init__()

		self._text = str(text)
		self._key  = str(key)

	def header_data(self, role:QtCore.Qt.ItemDataRole=QtCore.Qt.ItemDataRole.DisplayRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.name()
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return self.field()
	
	def item_data(self, bin_dict:dict, role:QtCore.Qt.ItemDataRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return str(bin_dict.get(self.field(), ""))
		
		if role == QtCore.Qt.ItemDataRole.InitialSortOrderRole:
			return bin_dict.get(self.field(),"")
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return bin_dict
	
	def name(self) -> str:
		return self._text
	
	def field(self) -> str:
		return self._key
	
class TRTTreeViewHeaderPath(TRTTreeViewHeaderItem):

	def item_data(self, bin_dict:dict, role:QtCore.Qt.ItemDataRole):

		path_data = bin_dict.get(self.field(), pathlib.Path())

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return path_data.name
		
		if role == QtCore.Qt.ItemDataRole.InitialSortOrderRole:
			return path_data.name
		
		elif role == QtCore.Qt.ItemDataRole.ToolTipRole:
			return str(path_data)
		
		elif role == QtCore.Qt.ItemDataRole.DecorationRole:
			return QtWidgets.QFileIconProvider().icon(QtCore.QFileInfo(str(path_data)))

class TRTTreeViewHeaderDuration(TRTTreeViewHeaderItem):

	def item_data(self, bin_dict:dict, role:QtCore.Qt.ItemDataRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return str(bin_dict.get(self.field(), "")).lstrip("0:")
		
		elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
			return QtGui.Qt.AlignmentFlag.AlignRight | QtGui.Qt.AlignmentFlag.AlignVCenter
		
		elif role == QtCore.Qt.ItemDataRole.FontRole:
			return QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont)
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return bin_dict
		
		elif role == QtCore.Qt.ItemDataRole.InitialSortOrderRole:
			return int(bin_dict.get("duration_total",""))
	
	def header_data(self, role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole):
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.name()
		
		elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
			return QtGui.Qt.AlignmentFlag.AlignRight
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return self.field()

		
class TRTTreeViewHeaderColor(TRTTreeViewHeaderItem):

	def item_data(self, bin_dict:dict, role:QtCore.Qt.ItemDataRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return ""
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return bin_dict
		
		elif role == QtCore.Qt.ItemDataRole.InitialSortOrderRole:
			return 0
		
		elif role == QtCore.Qt.ItemDataRole.DecorationRole:
			return self.draw_color(bin_dict.get(self.field(),None))
	
	def header_data(self, role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole):
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.name()
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return self.field()
		
	def draw_color(self, color):

		self.pixmap = QtGui.QPixmap(16,16)
		self.pixmap.fill(QtCore.Qt.GlobalColor.transparent)

		painter = QtGui.QPainter(self.pixmap)

		color_box = QtCore.QRect(0,0, 12, 12)
		color_box.moveCenter(QtCore.QPoint(7,6))
		
		# Set outline and fill
		pen = QtGui.QPen(QtGui.QColorConstants.Black)
		brush = QtGui.QBrush()
		#painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

		# Use clip color if available
		#clip_color_attr = avbutils.composition_clip_color(mob)

		if color is not None:
			clip_color = QtGui.QColor(color)
			brush.setColor(clip_color)
			brush.setStyle(QtGui.Qt.BrushStyle.SolidPattern)
		else:
			brush.setStyle(QtGui.Qt.BrushStyle.NoBrush)
		
		painter.setBrush(brush)
		painter.setPen(pen)
		painter.drawRect(color_box)

		# Box Shadow (TODO: 128 opactiy not working)
		color_box.moveCenter(color_box.center()+QtCore.QPoint(1,1))
		#color_box.setWidth(color_box.width() + 2)

		pen.setColor(QtGui.QColor(0,0,0,64))
		brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
		painter.setPen(pen)
		painter.setBrush(brush)
		painter.drawRect(color_box)

		return self.pixmap
		
class TRTTreeViewHeaderBinLock(TRTTreeViewHeaderItem):

	def item_data(self, bin_dict:dict, role:QtCore.Qt.ItemDataRole):

		lock = bin_dict.get("bin_lock")

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return str(lock).rstrip('\0') if lock is not None else ""
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return bin_dict
		
		elif role == QtCore.Qt.ItemDataRole.InitialSortOrderRole:
			return 0 if lock is not None else 1
		
		elif role == QtCore.Qt.ItemDataRole.DecorationRole:
			return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.SystemLockScreen) if lock is not None else None
	
	def header_data(self, role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole):
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.name()
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return self.field()
		
class TRTTreeViewHeaderDateTime(TRTTreeViewHeaderItem):

	def item_data(self, bin_dict:dict, role:QtCore.Qt.ItemDataRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return str(bin_dict.get(self.field(), ""))
		
		elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
			return QtGui.Qt.AlignmentFlag.AlignRight | QtGui.Qt.AlignmentFlag.AlignVCenter
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return bin_dict
		
		elif role == QtCore.Qt.ItemDataRole.InitialSortOrderRole:
			return int(bin_dict.get(self.field()).timestamp())
	
	def header_data(self, role: QtCore.Qt.ItemDataRole = QtCore.Qt.ItemDataRole.DisplayRole):
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.name()
		
		elif role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
			return QtGui.Qt.AlignmentFlag.AlignRight
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return self.field()
		
class TRTTreeView(QtWidgets.QTreeView):
	"""TRT Readout"""

	sig_remove_rows = QtCore.Signal(list)
	sig_add_bins = QtCore.Signal(list)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		super().setModel(QtCore.QSortFilterProxyModel())
		self.model().setSortRole(QtCore.Qt.ItemDataRole.InitialSortOrderRole)

		self.setColumnWidth(0, 24)
		self.setColumnWidth(1, 128)
		self.setAlternatingRowColors(True)
		self.setIndentation(0)
		self.setSortingEnabled(True)
		self.sortByColumn(1, QtCore.Qt.SortOrder.AscendingOrder)
		self.setSelectionMode(QtWidgets.QTreeView.SelectionMode.ExtendedSelection)
		self.setAcceptDrops(True)
		self.setDropIndicatorShown(True)
#		print(self.dragDropMode())

	def setModel(self, model:QtCore.QAbstractItemModel):
		# Overriding to always set to the proxy model
		self.model().setSourceModel(model)
	
	def fit_headers(self):
		for i in range(self.model().columnCount()):
			self.resizeColumnToContents(i)
	
	def keyPressEvent(self, event:QtCore.QEvent):
		if event.key() == QtCore.Qt.Key_Delete:
			rows = self.selectedRows()
			self.sig_remove_rows.emit(rows)
		else:
			super().keyPressEvent(event)

	def dragEnterEvent(self, event:QtGui.QDragEnterEvent):
		if event.mimeData().hasUrls():
			event.setDropAction(QtGui.Qt.DropAction.LinkAction)
			event.acceptProposedAction()
		else:
			event.ignore()

	def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
		if event.mimeData().hasUrls():
			event.setDropAction(QtGui.Qt.DropAction.LinkAction)
			event.acceptProposedAction()
		else:
			event.ignore()
	
	def dropEvent(self, event:QtGui.QDropEvent):
		if event.mimeData().hasUrls():
			event.setDropAction(QtGui.Qt.DropAction.LinkAction)
			event.acceptProposedAction()
			self.sig_add_bins.emit([f.toLocalFile() for f in event.mimeData().urls()])
		else:
			event.ignore()
	
	@QtCore.Slot()
	def selectedRows(self) -> list[int]:
		return sorted(set([self.model().mapToSource(idx).row() for idx in self.selectedIndexes()]), reverse=True)