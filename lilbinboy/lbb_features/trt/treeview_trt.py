import typing, enum
import avbutils
from PySide6 import QtCore, QtGui, QtWidgets
from timecode import Timecode
from lilbinboy.lbb_features.trt import model_trt
from lilbinboy.lbb_common.paint_delegates import LBClipColorPainter

#
# Cell items
# I figured I'd precompute the ItemDataRoles for performance purposes
#

class TRTAbstractItem(QtCore.QObject):
	"""An abstract item for TRT views"""

	def __init__(self, raw_data:typing.Any, icon:QtGui.QIcon|None=None, tooltip:QtWidgets.QToolTip|str|None=None):
		super().__init__()

		self._data = raw_data
		self._icon = icon
		self._tooltip = tooltip

		self._data_roles = {}
		self._prepare_data()
	
	def _prepare_data(self):
		"""Precalculate data for all them roles"""
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:				str(self._data),
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: 	avbutils.human_sort(str(self._data)),
			QtCore.Qt.ItemDataRole.UserRole:				self._data,
			QtCore.Qt.ItemDataRole.DecorationRole:			self._icon,
			QtCore.Qt.ItemDataRole.ToolTipRole:				self._tooltip
		})

	def data(self, role:QtCore.Qt.ItemDataRole) -> typing.Any:
		"""Get item data for a given role.  By default, returns the raw data as a string."""
		return self._data_roles.get(role, None)
	
class TRTStringItem(TRTAbstractItem):
	"""A standard string"""

	def __init__(self, raw_data:str, *args, **kwargs):
		super().__init__(str(raw_data), *args, **kwargs)

class TRTPathItem(TRTAbstractItem):
	"""A file path"""

	def __init__(self, raw_data:str|QtCore.QFileInfo):
		super().__init__(QtCore.QFileInfo(raw_data))
	
	def _prepare_data(self):
		super()._prepare_data()

		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:				self._data.fileName(),
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: 	avbutils.human_sort(self._data.fileName()),
			QtCore.Qt.ItemDataRole.DecorationRole:			QtWidgets.QFileIconProvider().icon(self._data),
			QtCore.Qt.ItemDataRole.ToolTipRole:				QtCore.QDir.toNativeSeparators(self._data.absoluteFilePath()),
		})

class TRTDateTimeItem(TRTAbstractItem):
	"""A datetime entry"""

	def __init__(self, raw_data:QtCore.QDateTime):
		super().__init__(raw_data)

	def _prepare_data(self):
		super()._prepare_data()
	
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:		self._data.toLocalTime().toString("dd MMM yyyy hh:mm:ss AP")
		})

class TRTTimecodeItem(TRTAbstractItem):
	"""A timecode"""

	def __init__(self, raw_data:Timecode, *args, **kwargs):
		if not isinstance(raw_data, Timecode):
			raise TypeError("Data must be an instance of `Timecode`")
		super().__init__(raw_data, *args, **kwargs)
	
	def _prepare_data(self):
		super()._prepare_data()
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:				str(self._data).rjust(12),
			QtCore.Qt.ItemDataRole.InitialSortOrderRole:	self._data.frame_number,
			QtCore.Qt.ItemDataRole.FontRole:				QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont)
		})
	
class TRTDurationItem(TRTTimecodeItem):
	"""A duration (hh:mm:ss:ff), a subset of timecode"""

	def _prepare_data(self):
		super()._prepare_data()
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:	str("-" if str(self._data).startswith("-") else "" + str(self._data).lstrip("-00:")).rjust(12),
		})

class TRTFeetFramesItem(TRTAbstractItem):

	def __init__(self, raw_data:int, *args, **kwargs):

		if not isinstance(raw_data, int):
			raise TypeError(f"Data must be an integer (not {type(raw_data)})")
		super().__init__(raw_data, *args, **kwargs)

	def _prepare_data(self):
		super()._prepare_data()
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:	str(str(self._data // 16) + "+" + str(self._data % 16).zfill(2)).rjust(9),
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: self._data,
			QtCore.Qt.ItemDataRole.FontRole: 	QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont),
		})

class TRTClipColorItem(TRTAbstractItem):
	"""A clip color"""

	def __init__(self, raw_data:avbutils.ClipColor|QtGui.QRgba64, *args, **kwargs):

		if isinstance(raw_data, avbutils.ClipColor):
			raw_data = QtGui.QColor.fromRgba64(*raw_data, raw_data.max_16b())
		elif isinstance(raw_data, QtGui.QRgba64):
			raw_data = QtGui.QColor.fromRgba64(raw_data)
		elif not isinstance(raw_data, QtGui.QColor):
			raise TypeError(f"Data must be a QColor object (got {type(raw_data)})")
		
		super().__init__(raw_data, *args, **kwargs)
	
	def _prepare_data(self):
		# Not calling super, would be weird

		color_8b = QtGui.QColor(self._data)

		self._data_roles.update({
			QtCore.Qt.ItemDataRole.UserRole: self._data,
			QtCore.Qt.ItemDataRole.ToolTipRole: f"R: {color_8b.red()} G: {color_8b.green()} B: {color_8b.blue()}" if color_8b.isValid() else None,
			QtCore.Qt.ItemDataRole.InitialSortOrderRole: self._data.getRgb() if self._data is not None else QtGui.QColor.rgb()
		})

class TRTBinLockItem(TRTAbstractItem):
	"""Bin lock info"""

	# Note: For now I think we'll do a string, but want to expand this later probably
	def __init__(self, raw_data:avbutils.LockInfo, *args, **kwargs):
		super().__init__(raw_data, *args, **kwargs)

	def _prepare_data(self):
		super()._prepare_data()
		self._data_roles.update({
			QtCore.Qt.ItemDataRole.DisplayRole:    self._data.name if self._data else "",
			QtCore.Qt.ItemDataRole.DecorationRole: QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.SystemLockScreen if self._data else None)
		})


#
# Header items
#

class TRTTreeViewHeaderItem(QtCore.QObject):

	def __init__(self, text:str, key:str, include_total:bool=False, display_delegate:QtWidgets.QStyledItemDelegate|None=None):

		super().__init__()

		self._text = str(text)
		self._key  = str(key)
		self._display_delegate = display_delegate
		self._include_total = bool(include_total)

	def header_data(self, role:QtCore.Qt.ItemDataRole=QtCore.Qt.ItemDataRole.DisplayRole):

		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return self.name()
		
		elif role == QtCore.Qt.ItemDataRole.UserRole:
			return self.field()
	
	def name(self) -> str:
		"""Get the title of this header"""
		return self._text
	
	def field(self) -> str:
		"""Get the field of item data this header will display"""
		return self._key
	
	def displayDelegate(self) -> QtWidgets.QStyledItemDelegate|None:
		"""Get the display delegate assigned to this header"""
		return self._display_delegate
	
	def includeTotal(self) -> bool:
		"""Does UserData contain data that can be summed"""
		return self._include_total
	


#
# Delegates
#
	

class TRTClipColorDisplayDelegate(QtWidgets.QStyledItemDelegate):
	"""Draw a clip color"""

	PADDING = 5 #px
	SHADOW_OFFSET = QtCore.QPoint(1,1)

	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex|QtCore.QPersistentModelIndex):
		"""Painter"""

		super().paint(painter, option, index)
		
		# Get clip color from UserRole (Qrgba64 struct)
		clip_color = QtGui.QColor(index.data(role=QtCore.Qt.ItemDataRole.UserRole))

		# Based on the device rect, determine a centered, square QRect
		rect_device:QtCore.QRect = option.rect
		min_size = min(rect_device.width(), rect_device.height())
		rect_colorbox = QtCore.QRect(0, 0, min_size, min_size)
		rect_colorbox.moveCenter(rect_device.center())
		
		# Draw that sucker
		LBClipColorPainter(rect_colorbox, painter, clip_color=clip_color)
	


		
class TRTTreeView(QtWidgets.QTreeView):
	"""TRT Readout"""

	class TRTTreeViewDisplayStatus(enum.Enum):
		"""The status of the data currently being displayed in the TreeView"""

		EMPTY           = enum.auto()
		"""TreeView is currently empty and inactive"""
		INITIAL_LOADING = enum.auto()
		"""TreeView is currently empty, but loading"""
		NO_ITEMS_FOUND  = enum.auto()
		"""TreeView is currently empty, after no sequences were found in the bins"""
		POPULATED       = enum.auto()
		"""TreeView is displaying data"""

		def message(self) -> str:
			"""Get the display message for a given status"""
			
			if self is self.EMPTY:
				return  "Add Bins To Begin\nTo load in sequences from your Avid bins, click the \"Add From Bins...\" button above, or drag-and-drop Avid bin (.avb) files here."
			
			if self is self.INITIAL_LOADING:
				return "Now Loading...\nSequences will begin to appear here shortly."
			
			if self is self.NO_ITEMS_FOUND:
				return "No Sequences Found\nNo sequences were found that matched the criteria."
			
			return ""
			
				


	sig_remove_rows_requested = QtCore.Signal(list)
	sig_bins_dragged_dropped  = QtCore.Signal(list)
	sig_field_order_changed   = QtCore.Signal(list)
	sig_sorting_changed       = QtCore.Signal(str,QtCore.Qt.SortOrder)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		super().setModel(model_trt.TRTViewSortModel())

		self._status = self.TRTTreeViewDisplayStatus.EMPTY

		self.model().setSortRole(QtCore.Qt.ItemDataRole.InitialSortOrderRole)

		#self.setColumnWidth(0, 24)
		#self.setColumnWidth(1, 128)
		self.setUniformRowHeights(True)
		self.setAllColumnsShowFocus(True)
		self.setAlternatingRowColors(True)
		self.setIndentation(0)
		self.setSortingEnabled(True)
		self.sortByColumn(1, QtCore.Qt.SortOrder.AscendingOrder)
		self.setSelectionMode(QtWidgets.QTreeView.SelectionMode.ExtendedSelection)
		self.setAcceptDrops(True)
		self.setDropIndicatorShown(True)
		self.setTextElideMode(QtCore.Qt.TextElideMode.ElideMiddle)
		self.model().headerDataChanged.connect(self.headerDataChanged)
		self.header().sectionMoved.connect(self.sectionMoved)
		self.header().sortIndicatorChanged.connect(self.sortingChanged)

#		print(self.dragDropMode())

	def status(self) -> TRTTreeViewDisplayStatus:
		"""The state of the data being displayed in the TreeView"""
		return self._status
	
	def setStatus(self, status:TRTTreeViewDisplayStatus):
		"""Set the display status of the treeview"""
		self._status = self.TRTTreeViewDisplayStatus(status)
		self.viewport().update()

	def setModel(self, model:QtCore.QAbstractItemModel):
		# Overriding to always set to the proxy model
		self.model().setSourceModel(model)

	@QtCore.Slot(int, QtCore.Qt.SortOrder)
	def sortingChanged(self, idx_logical:int, order:QtCore.Qt.SortOrder):
		"""Sorting column or direction has changed"""

		field = self.model().headerData(idx_logical, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)
		self.sig_sorting_changed.emit(field, order)

	@QtCore.Slot(str, QtCore.Qt.SortOrder)
	def setSorting(self, sort_field:str, sort_order:QtCore.Qt.SortOrder):
		
		fields_logical = [self.model().headerData(col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole) for col in range(self.model().columnCount())]

		if sort_field not in fields_logical:
			return
		
		self.header().setSortIndicator(fields_logical.index(sort_field), sort_order)
		print("Set to ", sort_field, sort_order)
	
	@QtCore.Slot(int, int, int)
	def sectionMoved(self, idx_logical:int, idx_visual_old:int, idx_visual_new:int):
		"""A header column was moved"""
		self.sig_field_order_changed.emit(self.displayedFields())
	
	def displayedFields(self) -> list[str]:
		"""Returns a list of visible fields in the order they are displayed"""

		field_order = []

		# Iterate over visual indexes to look up the field name at the corresponding logical index
		for idx_visual in range(self.header().count()):
			idx_logical = self.header().logicalIndex(idx_visual)
			field_name = self.model().headerData(idx_logical, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)
			field_order.append(field_name)

		return field_order
	
	@QtCore.Slot(list)
	def setFieldOrder(self, field_order:list[str]):
		"""Arrange columns based on an ordered list of fields"""

		for idx_visual_new, field_name in enumerate(field_order):
			if field_name not in self.displayedFields():
				continue

			idx_visual_old = self.displayedFields().index(field_name)
			self.header().moveSection(idx_visual_old, idx_visual_new)
	
	def fit_headers(self):
		for i in range(self.model().columnCount()):
			self.resizeColumnToContents(i)
	
	def keyPressEvent(self, event:QtCore.QEvent):
		if event.key() == QtCore.Qt.Key_Delete:
			rows = self.selectedRows()
			self.sig_remove_rows_requested.emit(rows)
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
			self.sig_bins_dragged_dropped.emit([f.toLocalFile() for f in event.mimeData().urls()])
		else:
			event.ignore()
	
	@QtCore.Slot()
	def selectedRows(self) -> list[int]:
		return sorted(set([self.model().mapToSource(idx).row() for idx in self.selectedIndexes()]), reverse=True)
	
	@QtCore.Slot(QtCore.Qt.Orientation, int, int)
	def headerDataChanged(self, orientation: QtCore.Qt.Orientation, idx_first:int, idx_last:int):
		"""Headers were inserted or something"""

		for idx_header in range(idx_first, idx_last+1):
			header = self.model().sourceModel().headers()[idx_header]
			if header.displayDelegate():
				self.setItemDelegateForColumn(idx_header, header.displayDelegate())

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def rowsInserted(self, parent:QtCore.QModelIndex, start:int, end:int):
		self.setStatus(self.TRTTreeViewDisplayStatus.POPULATED)
		return super().rowsInserted(parent, start, end)
	
	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def rowsRemoved(self, parent, first, last):
		
		# TODO: This doesn't seem to be called/connected from the model...?
		if not self.model().rowCount():
			self.setStatus(self.TRTTreeViewDisplayStatus.EMPTY)

		return super().rowsRemoved(parent, first, last)
	
	@QtCore.Slot()
	def beginLoadingSequences(self):
		"""Program is starting to load in new sequences"""
		if not self.model().rowCount():
			self.setStatus(self.TRTTreeViewDisplayStatus.INITIAL_LOADING)
	
	@QtCore.Slot()
	def doneLoadingSequences(self):
		"""Program finished loading for now"""
		if not self.model().rowCount():
			self.setStatus(self.TRTTreeViewDisplayStatus.NO_ITEMS_FOUND)
	
	# Status Messages
	def paintEvent(self, event:QtGui.QPaintEvent):
		"""Draw any relevant status messages up in there"""

		super().paintEvent(event)

		if self.status().message():

			painter = QtGui.QPainter(self.viewport())
			painter.save()
			
			rect_viewport = QtCore.QRectF(0, 0, painter.device().width(), painter.device().height())

			status_message = self.status().message()
			text_options = QtGui.QTextOption()
			text_options.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

			painter.drawText(rect_viewport.adjusted(50, 0, -50, 0), status_message, text_options)

			painter.restore()

		return event
	
