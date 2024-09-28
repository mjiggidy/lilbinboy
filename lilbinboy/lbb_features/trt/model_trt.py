import pathlib
from PySide6 import QtCore, QtGui, QtWidgets
from timecode import Timecode
from . import logic_trt



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

class TRTModel(QtCore.QObject):

	sig_data_changed = QtCore.Signal()

	LFOA_PERFS_PER_FOOT = 16

	# TODO: Not a great place for these probably
	MAX_8b = (1 << 8) - 1
	"""Maximum 8-bit value"""
	MAX_16b = (1 << 16) - 1
	"""Maximum 16-bit value"""

	def __init__(self, bin_info_list:list[logic_trt.BinInfo]=None):
		super().__init__()

		self._data = bin_info_list or []

		# TODO: Deal with
		self._fps = 24
		self._trim_head = Timecode("8:00", rate=self._fps)
		self._trim_tail = Timecode("4:00", rate=self._fps)
		self._trim_total = Timecode(0, rate=self._fps)
		self._adjust_total = Timecode(0, rate=self._fps)
	
	def sequence_count(self) -> int:
		"""Number of sequences being considered"""
		return len(self._data)
	
	def bin_count(self) -> int:
		"""Number of individual bins involved in this"""
		return len(set(b.path for b in self._data))
	
	def total_runtime(self) -> Timecode:
		
		trt = Timecode(0, rate=self._fps)

		for bin_info in self._data:
			reel_info = bin_info.reel
			trt += reel_info.duration_total - self._trim_head_amount(reel_info) - self._trim_tail_amount(reel_info)
		
		return max(Timecode(0, rate=self.rate()), trt + self.trimTotal())
	
	def rate(self) -> int:
		return self._fps
	
	def setRate(self, rate:int) -> int:
		self._fps = rate
		self.sig_data_changed.emit()
	
	def trimFromHead(self) -> Timecode:
		return self._trim_head
	
	def setTrimFromHead(self, timecode:Timecode):
		self._trim_head = timecode
		self.sig_data_changed.emit()
	
	def trimFromTail(self) -> Timecode:
		return self._trim_tail
	
	def setTrimFromTail(self, timecode:Timecode):
		self._trim_tail = timecode
		self.sig_data_changed.emit()

	def trimTotal(self) -> Timecode:
		return self._trim_total

	def setTrimTotal(self, timecode:Timecode):
		self._trim_total = timecode
		self.sig_data_changed.emit()
	
	def total_lfoa(self) -> str:
		trt = self.total_runtime()
		return self.tc_to_lfoa(trt)
	
	def locked_bin_count(self) -> int:
		return len([x for x in self.data() if x.lock is not None])
	
	def tc_to_lfoa(self, tc:Timecode) -> str:
		zpadding = len(str(self.LFOA_PERFS_PER_FOOT))
		#tc = max(tc, Timecode(0, rate=self.rate()))
		return str(tc.frame_number // 16) + "+" + str(tc.frame_number % self.LFOA_PERFS_PER_FOOT).zfill(zpadding)
		
	def _trim_head_amount(self, reel_info:logic_trt.ReelInfo) -> Timecode:
		# TODO: Implement markers; indiciate if it was Marker or head trim
		return self._trim_head
	
	def _trim_tail_amount(self, reel_info:logic_trt.ReelInfo) -> Timecode:
		# TODO: Implement markers; indiciate if it was Marker or tail trim
		return self._trim_tail

	
	def set_data(self, bin_info_list:list[logic_trt.BinInfo]):
		self._data = bin_info_list
		self.sig_data_changed.emit()
	
	def add_sequence(self, bin_info:logic_trt.BinInfo):
		self._data.append(bin_info)
		self.sig_data_changed.emit()
	
	def remove_sequence(self, index:int):
		try:
			del self._data[index]
		except Exception as e:
			print(f"Didn't remove because {e}")
		
		self.sig_data_changed.emit()

	def clear(self):
		self.set_data([])
	
	def data(self):
		return iter(self._data)
	
	def item_to_dict(self, index:int):
		
		bin_info = self._data[index]
		reel_info = bin_info.reel

		return {
			"sequence_name": reel_info.sequence_name,
			"sequence_color": QtGui.QColor(*(c/self.MAX_16b * self.MAX_8b for c in reel_info.sequence_color)) if reel_info.sequence_color else None,
			"duration_total": reel_info.duration_total,
			"duration_trimmed": max(Timecode(0, rate=self.rate()), reel_info.duration_total - self._trim_head - self._trim_tail),
			"head_trimmed": self._trim_head,
			"tail_trimmed": self._trim_tail,
			"lfoa": self.tc_to_lfoa(max(Timecode(0, rate=self.rate()), reel_info.duration_total - self._trim_tail - 1)), # TODO: Think through the -1 but I think it makes sense being zero-based instead of 1-based for durations? Like, LFOA may be on 0+00 but that means it's 0+01 frame long
			"date_modified": reel_info.date_modified,
			"bin_path": bin_info.path,
			"bin_lock": bin_info.lock
		}
	

class TRTViewModel(QtCore.QAbstractItemModel):
	
	def __init__(self, trt_model:TRTModel, headers_list:list[TRTTreeViewHeaderItem]=None):
		"""Create and setup a new model"""
		super().__init__()

		self.set_model(trt_model)
		self._headers = headers_list or []

		self.model().sig_data_changed.connect(self.modelReset)
		
		# Typically a list of data here
		# Typically a dict of header keys and values here
	
	def set_model(self, trt_model:TRTModel):
		self._model = trt_model
		self.modelReset.emit()
	
	def model(self) -> TRTModel:
		return self._model
	
	def set_headers(self, headers:list[TRTTreeViewHeaderItem]):
		self._headers = headers
		self.headerDataChanged.emit(QtCore.Qt.Orientation.Horizontal, 0, len(self._headers)-1)
	
	def index(self, row:int, column:int, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> QtCore.QModelIndex:
		"""Returns the index of the item in the model specified by the given row, column and parent index."""
		return self.createIndex(row, column, self.model().item_to_dict(row))
	
	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:
		"""Returns the parent of the model item with the given index. If the item has no parent, an invalid QModelIndex is returned."""
		return QtCore.QModelIndex()

	def rowCount(self, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Returns the number of rows under the given parent. When the parent is valid it means that is returning the number of children of parent."""
		if parent.isValid():
			return 0
		else:
			return self.model().sequence_count()
	
	def columnCount(self, parent:QtCore.QModelIndex=QtCore.QModelIndex()) -> int:
		"""Returns the number of columns for the children of the given parent."""
		return len(self._headers)

	def data(self, index:QtCore.QModelIndex, role:int=QtCore.Qt.ItemDataRole.DisplayRole) -> QtCore.QObject:
		"""Returns the data stored under the given role for the item referred to by the index."""
		header = self._headers[index.column()]
		return header.item_data(self.model().item_to_dict(index.row()), role)

	def headerData(self, section:int, orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal, role:int=QtCore.Qt.ItemDataRole.DisplayRole) -> QtCore.QObject:
		"""Returns the data for the given role and section in the header with the specified orientation."""
		return self._headers[section].header_data(role)
	
class TRTViewSortModel(QtCore.QSortFilterProxyModel):
	pass

class TRTTreeView(QtWidgets.QTreeView):
	"""TRT Readout"""

	sig_remove_rows = QtCore.Signal(list)
	sig_add_bins = QtCore.Signal(list)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

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