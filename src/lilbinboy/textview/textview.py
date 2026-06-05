from __future__ import annotations
import logging
from PySide6 import QtCore, QtGui, QtWidgets

from . import textviewheader

from ..core.config import BSTextViewModeConfig
from ..utils import columnselect
from ..res import icons_binitems
from . import proxydelegates
from ..binwidget import itemdelegates
from ..core import icon_providers, icon_registry

from ..binview import binviewitemtypes
from ..binfilters import binviewproxymodel

import avbutils

class BSBinTextView(QtWidgets.QTreeView):
	"""QTreeView but nicer"""

#	sig_default_sort_columns_changed = QtCore.Signal(object)
#	"""TODO: HMMMMMM"""

	sig_selection_model_changed      = QtCore.Signal(object)
	"""Selection model was changed"""

	sig_item_padding_changed         = QtCore.Signal(object)

	sig_hide_column_requested        = QtCore.Signal(object)
	"""Hide a given bin view column info"""


	def __init__(self, *args, bin_item_icon_registry:icon_registry.IconRegistryType|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self.ICON_ASPECT_RATIO = QtCore.QSizeF(4,3)

		self.setSortingEnabled(True)
		self.setRootIsDecorated(False)
		self.setUniformRowHeights(True)
		self.setAlternatingRowColors(True)

		self.setHeader(textviewheader.BSTextViewColumnHeaderView(QtCore.Qt.Orientation.Horizontal))

		self.header().setFirstSectionMovable(True)
		self.header().setSectionsMovable(True)
		self.header().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.header().setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
		self.header().setStretchLastSection(True)

#		self.setModel(QtCore.QIdentityProxyModel())
		self.setSelectionBehavior(BSTextViewModeConfig.DEFAULT_SELECTION_BEHAVIOR)
		self.setSelectionMode(BSTextViewModeConfig.DEFAULT_SELECTION_MODE)

		#self.setAllColumnsShowFocus(True)

		self.setDragEnabled(True)
		self.setAcceptDrops(True)
		self.setDropIndicatorShown(True)
		self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)

		self._bin_item_icon_registry = bin_item_icon_registry or dict()
		self._delegate_provider      = proxydelegates.BSBinColumnDelegateProvider(view=self)
		self._proxy_delegate         = proxydelegates.BSBinColumnProxyDelegate(delegate_provider=self._delegate_provider)

		self.registerCustomDelegates()
		self.setItemDelegate(self._proxy_delegate)

		self._column_select_watcher = columnselect.BSColumnSelectWatcher(parent=self)
		self._column_select_watcher.sig_column_selected.connect(self.selectSectionFromCoordinates)
		self.header().viewport().installEventFilter(self._column_select_watcher)
		
		self._item_padding          = QtCore.QMarginsF(BSTextViewModeConfig.DEFAULT_ITEM_PADDING)
		self.setItemPadding(self._item_padding)

		self._act_show_column_editor = None


		self.header().sectionMoved.connect(self.binColumnDragged)
		self.header().customContextMenuRequested.connect(self.showColumnContextMenu)
		#self.header().sectionResized.connect(self.setBinColumnWidth)

		# Setup Actions
		# NOTE: Moved this out of binwidget, never sure what to do with actions
		self._act_autofit_columns = QtGui.QAction(self)
		self._act_autofit_columns.setText(self.tr("Auto-fit bin columns to contents"))
		self._act_autofit_columns.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ControlModifier|QtCore.Qt.Key.Key_T))
		self._act_autofit_columns.triggered.connect(self.resizeAllColumnsToContents)
		self.addAction(self._act_autofit_columns)

	def setShowColumnEditorAction(self, action:QtGui.QAction):

		self._act_show_column_editor = action	

	@QtCore.Slot(QtCore.QPoint)
	def showColumnContextMenu(self, point:QtCore.QPoint):

		import functools

		menu = QtWidgets.QMenu("Column Actions", parent=self.header())

		#print("Yo")

		idx_logical = self.header().logicalIndexAt(point)
		field_id    = self.model().headerData(idx_logical, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)

		if field_id == avbutils.bins.BinColumnFieldIDs.BinItemIcon:
			column_name = "Item Icon"
		else:
			column_name = self.model().headerData(idx_logical, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole)
		
		act_hide_col = QtGui.QAction(self.tr("Hide {column_name}".format(column_name=column_name)), parent=self.header())
		act_hide_col.triggered.connect(functools.partial(self.sig_hide_column_requested.emit, idx_logical))

		is_permanent = self.model().headerData(idx_logical, QtCore.Qt.Orientation.Horizontal, binviewproxymodel.BSBinViewFilterRole.IsPermanentlyVisibleRole)
		if is_permanent:
			act_hide_col.setEnabled(False)
			act_hide_col.setToolTip(self.tr("This is a permanent column that cannot be hidden."))
		
		menu.addAction(act_hide_col)

		if self._act_show_column_editor:

			menu.addSeparator()
			menu.addAction(self._act_show_column_editor)

		menu.popup(self.header().mapToGlobal(point))

	###

	@QtCore.Slot(int, int, int)
	def binColumnDragged(self, col_logical_old:int, col_vis_old:int, col_vis_new:int):
		"""User dragged column to reorder"""

		# NOTE: This method I think is alright
		
		col_logical_new = (self.header().logicalIndex(col_vis_new - 1) + 1) if col_vis_new > 0 else 0


		if col_logical_old == col_logical_new:
			logging.getLogger(__name__).debug("Not moving columns: Source and destination logical indeces are the same (%s)", col_logical_old)
			return

#		moving_column_name = self.model().headerData(col_logical_old, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole)
#		left_column_name   = self.model().headerData(col_logical_new-1, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole) if col_logical_new > 0 else "<<FRONT>>"
#		print(f"Treeview asks the proxy model to move {moving_column_name} to after {left_column_name} ({col_logical_old} -> {col_logical_new})")
		
		was_moved = self.model().moveColumn(QtCore.QModelIndex(), col_logical_old, QtCore.QModelIndex(), col_logical_new)

		if was_moved:

			# AAAAAAAAAH HA HA HAAAAA I FUCKIN GOT IT BITCCHCHCHCHCHCHHHHHHHH YEAAAAAH BOIIIIIII
			# Undo the visual move here.  Yes this triggers another move request but it gets stopped there because of identical indexes yesssss

#			width_vis_new = self.header().sectionSize(self.header().logicalIndex(col_vis_new))
#			width_vis_old = self.header().sectionSize(self.header().logicalIndex(col_vis_old))

			self.header().moveSection(col_vis_new, col_vis_old)

			# Restore column widths after move
			# NOTE: May want to hook this into a generic sections moved thing,
			# so far this doesn't work when columns are moved by other means like the bin view editor

#			self.header().resizeSection(self.header().logicalIndex(col_vis_new), width_vis_new)
#			self.header().resizeSection(self.header().logicalIndex(col_vis_old), width_vis_old)
		
		return False

	def setBinItemIconRegistry(self, registry:icon_registry.IconRegistryType):
		"""Register bin item icon paths"""

		if self._bin_item_icon_registry == registry:
			return
		
		self._bin_item_icon_registry = registry
		
		self.registerCustomDelegates()

	def setSelectionModel(self, selectionModel):

		if selectionModel == self.selectionModel():
			return

		logging.getLogger(__name__).debug("BinTreeView changed selection model to %s", str(selectionModel))
		self.sig_selection_model_changed.emit(selectionModel)

		return super().setSelectionModel(selectionModel)

	@QtCore.Slot(object)
	def setModel(self, model:QtCore.QAbstractItemModel):

		if self.model() == model:
			return
		
		# TODO: Disconnect old model...?
		if self.model():
			self.model().disconnect(self)

		model.columnsInserted .connect(self.binColumnsInserted, QtCore.Qt.ConnectionType.QueuedConnection) # NOTE: Queued because QHeader needs to update first
		model.rowsInserted    .connect(self.binItemsInserted)
		model.modelReset      .connect(lambda: self.sortByColumn(-1, QtCore.Qt.SortOrder.AscendingOrder))
#		model.modelReset.connect(lambda: self.binColumnsInserted(QtCore.QModelIndex(), 0, self.model().columnCount(QtCore.QModelIndex())), QtCore.Qt.ConnectionType.QueuedConnection)
#		model.headerDataChanged.connect(self.updateBinColumns)

		super().setModel(model)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binColumnsInserted(self, parent:QtCore.QModelIndex, idx_log_first:int, idx_log_last:int):
		"""Handle new columns (NOTE: Needs a `QueuedConnection` for updated logical indexes)"""

		# TODO: Seems to be firing twice...?
		#print("OK")

		
		for idx_log_current in range(idx_log_first, idx_log_last+1):
			self.resizeColumnToContents(idx_log_current)


	@QtCore.Slot(object)
	def selectSectionFromCoordinates(self, viewport_coords:QtCore.QPoint):

		section_logical = self.header().logicalIndexAt(viewport_coords.x())
		self.selectSection(section_logical)

	@QtCore.Slot(int)
	def selectSection(self, column_logical:int):

		self.toggleSelectionBehavior(
			QtWidgets.QTreeView.SelectionBehavior.SelectColumns,
			keep_current_selection = QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier
		)

		if QtWidgets.QApplication.keyboardModifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
			selection_behavior_flags = QtCore.QItemSelectionModel.SelectionFlag.Toggle

		else:
			selection_behavior_flags = QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect

		self.selectionModel().select(
			QtCore.QItemSelection(self.model().index(0, column_logical), self.model().index(self.model().rowCount()-1, column_logical)),
			QtCore.QItemSelectionModel.SelectionFlag.Columns|
			selection_behavior_flags
		)

	def copySelection(self):
		"""Copy selection to clipboard"""
     
		# TODO: Messssssy
		# TODO: This'll be good to refactor for ALE/CSV/JSON exports, yay!

		if not self.selectionModel().hasSelection():

			logging.getLogger(__name__).debug("Nothing selected to copy")
			return

		# Figure out which columns are selected, total
		selected_columns_visual = sorted(
			set(self.header().visualIndex(i.column()) for i in self.selectedIndexes())
		)


		# Collect header strings from selected columns
		headers_text:dict[int,str] = dict()

		for col_vis in selected_columns_visual:

			col_logical = self.header().logicalIndex(col_vis)

			header_text = self.model().headerData(
				col_logical,
				QtCore.Qt.Orientation.Horizontal,
				QtCore.Qt.ItemDataRole.DisplayRole,
			)

			# NOTE: Needed?
			headers_text[col_vis] = header_text if isinstance(header_text,str) else ""

		# Collect item strings from selected bin items
		rows_text:list[dict[int, str]] = []

		last_row = None

		for item_index in sorted(self.selectedIndexes(), key=lambda i: i.row()):

			if item_index.row() != last_row:
				last_row = item_index.row()
				rows_text.append(dict())

			item_text   = item_index.data(
				QtCore.Qt.ItemDataRole.DisplayRole,
			)

			rows_text[-1][self.header().visualIndex(item_index.column())] = item_text if isinstance(item_text, str) else ""



		# Join all together

		final_headers = "\t".join(headers_text[c] for c in selected_columns_visual)
		final_items   = "\n".join(
			"\t".join(i.get(c,"") for c in selected_columns_visual) for i in rows_text
		)

		QtWidgets.QApplication.clipboard().setText("\n".join([final_headers, final_items]))

	def toggleSelectionBehavior(self, behavior:QtWidgets.QTreeView.SelectionBehavior|None=None, keep_current_selection:bool=False):

		behavior = behavior or BSTextViewModeConfig.DEFAULT_SELECTION_BEHAVIOR

		if self.selectionBehavior() == behavior:

			#logging.getLogger(__name__).debug("Selection behavior already %s. Not changed.", behavior)
			return

		# NOTE: BIG NOTE: TODO: ETC:
		# Disabling keep_current_selection for all instances for now
		keep_current_selection = keep_current_selection and BSTextViewModeConfig.ALLOW_KEEP_CURRENT_SELECTION_BETWEEN_MODES

		if not keep_current_selection:
			self.clearSelection()

		self.setSelectionBehavior(behavior)

		if behavior == QtWidgets.QTreeView.SelectionBehavior.SelectItems:
			self.setSelectionMode(QtWidgets.QTreeView.SelectionMode.MultiSelection)

		else:
			self.setSelectionMode(BSTextViewModeConfig.DEFAULT_SELECTION_MODE)

		logging.getLogger(__name__).debug("Treeview selection changed to behavior=%s, mode=%s", self.selectionBehavior(), self.selectionMode())


	def keyPressEvent(self, event):

		if event.matches(QtGui.QKeySequence.StandardKey.Copy) and not event.isAutoRepeat():

			self.copySelection()
			event.accept()

		else:
			return super().keyPressEvent(event)


	def mousePressEvent(self, event:QtGui.QMouseEvent):

		if event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier:
			self.toggleSelectionBehavior(QtWidgets.QTreeView.SelectionBehavior.SelectItems, keep_current_selection=(event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier))
			#event.accept()
		else:
			self.toggleSelectionBehavior()
			#event.accept()

		return super().mousePressEvent(event)

	@QtCore.Slot()
	def resizeAllColumnsToContents(self):
		"""Generic resize-to-fit"""

		for idx in range(self.header().count()):
			self.resizeColumnToContents(idx)

	@QtCore.Slot(QtCore.QMarginsF)
	def setItemPadding(self, padding:QtCore.QMarginsF):
		"""Set item padding and add frame size padding"""

		if self._item_padding == padding:
			return
		
		self._item_padding = QtCore.QMarginsF(padding)

		for delegate in self._delegate_provider.delegates():
			delegate.setItemPadding(padding)

		logging.getLogger(__name__).debug("Setting padding to %s", str(self._item_padding))
		
		self.updateMinimumSectionWidths()
		#self.scheduleDelayedItemsLayout()

		#self.update()
		self.sig_item_padding_changed.emit(padding)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def binItemsInserted(self, parent:QtCore.QModelIndex, row_first:int, row_last:int):

		# NOTE: Basically we need to set minimum column widths
		# But the column width for icons depends on the row height, so we need at least one 
		# row to query the height, then calculate the minimum width from that.  It's probably 
		# a dumb design that I should rethink.

		# So only if we insert at the first row, recalculate.
		# I dunno.  Maybe I just do this at the end of the loading?

		if row_first == 0:
#			print(f"I UPDATE {row_first=} {row_last=}")
			self.updateMinimumSectionWidths()


	
	def updateMinimumSectionWidths(self):

		# If no rows
		if not self.model() or not self.model().hasIndex(0, 0, QtCore.QModelIndex()):
			return
		
		# Gon set minimum column width based on row height, but adjusted for icon aspect ratio
		row_height = self.rowHeight(self.model().index(0, 0, QtCore.QModelIndex())) - self._item_padding.top() - self._item_padding.bottom()
		col_width  = row_height * self.ICON_ASPECT_RATIO.width() / self.ICON_ASPECT_RATIO.height() + self._item_padding.left() + self._item_padding.right()

		self.header().setMinimumSectionSize(col_width)
		
#		for col_logical in range(self.header().count()):
#
#			title = self.model().headerData(col_logical, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole)
#			og_size = self.sizeHintForIndex(self.model().index(0, 0, QtCore.QModelIndex()))
#			logging.getLogger(__name__).debug("Set minimum section width for %s to %s for size hint %s", str(title), int(og_size.width()), repr(og_size))

#	@QtCore.Slot(object)
#	def setDefaultSortColumns(self, sort_columns:list[list[int,str]]):
#
#		self._default_sort = sort_columns
#		self.sig_default_sort_columns_changed.emit(self._default_sort)

	def registerCustomDelegates(self):
		"""Register custom delegates, but probably not here"""

		# Clip Color
		self._delegate_provider.setUniqueDelegateForField(
			avbutils.bins.BinColumnFieldIDs.Color,
			itemdelegates.BSIconLookupItemDelegate(
				parent=self,
				aspect_ratio=self.ICON_ASPECT_RATIO,
				icon_provider=icon_providers.BSStyledClipColorIconProvider(),
			)
		)


		# Markers
		self._delegate_provider.setUniqueDelegateForField(
			avbutils.bins.BinColumnFieldIDs.Marker,
			itemdelegates.BSIconLookupItemDelegate(
				parent=self,
				aspect_ratio=self.ICON_ASPECT_RATIO,
				icon_provider=icon_providers.BSStyledMarkerIconProvider(),
			)
		)

		# Bin Display Item Icon
		self._delegate_provider.setUniqueDelegateForField(
			avbutils.bins.BinColumnFieldIDs.BinItemIcon,
			itemdelegates.BSIconLookupItemDelegate(
				parent=self,
				aspect_ratio=self.ICON_ASPECT_RATIO,
				icon_provider=icon_providers.BSStyledBinItemTypeIconProvider(path_registry=self._bin_item_icon_registry),
			)

		)

#		self._delegate_provider.setUniqueDelegateForField(
#			avbutils.bins.BinColumnFieldIDs.Frame,
#			itemdelegates.BSFrameThumbnailDelegate(
#				parent=self
#			)
#		)