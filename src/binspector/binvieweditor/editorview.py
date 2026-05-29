import typing
from PySide6 import QtWidgets, QtGui, QtCore

from . import editordelegates, editorproxymodel
from ..binview import binviewitemtypes
from ..utils import clumper

class BSBinViewColumnListView(QtWidgets.QTableView):
	"""A QTableView for bin view column data"""

	def __init__(self):

		super().__init__()

		self.setItemDelegate(editordelegates.BSBinViewColumnDelegate(parent=self))
		
		# Background 'n' grid
		self.setShowGrid(False)
		self.setAlternatingRowColors(True)
		self.setAutoScroll(True)
#		self.setAutoScrollMargin(128)
		self.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectItems)
		
		# Text
		self.setWordWrap(False)
		self.setTextElideMode(QtCore.Qt.TextElideMode.ElideMiddle)
		
		# Selection Model
		self.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
		self.setSelectionMode(QtWidgets.QTableView.SelectionMode.ExtendedSelection)
		
		# Drag n Drop
		self.setDragEnabled(True)
		self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
		self.setDragDropOverwriteMode(False)

		self.setDropIndicatorShown(True)
		
		self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		
		# Headers
		self.verticalHeader()  .setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		self.verticalHeader()  .hide()
		self.horizontalHeader().hide()

		# Scrolling
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

	@QtCore.Slot()
	def toggleColumnSelection(self):

		# NOTE: Unused?

		self.selectionModel().clearSelection() if self.selectionModel().hasSelection() else self.selectAll()

	@QtCore.Slot()
	def toggleSelectedVisibility(self):

		for row_index in self.selectionModel().selectedRows():
			pass
	
#			self.model().toggleBinColumnVisibiltyForIndex(row_index)
	###

	def setModel(self, model:QtCore.QAbstractItemModel):
		
		if self.model() == model:
			return

		super().setModel(model)

		# NOTE: Need better way to do this for model/delegate reassignments
		self.itemDelegate().sig_user_clicking_remove_buttons   .connect(self.userClickingDeleteColumn)
		self.itemDelegate().sig_user_clicking_hide_buttons     .connect(self.userClickingHideColumn)
		self.itemDelegate().sig_remove_selected_bin_columns    .connect(self.removeSelectedColumns)
		self.itemDelegate().sig_user_toggling_column_visibility.connect(self.toggleSelectedColumnVisibility)
#		self.itemDelegate().sig_rename_column_for_index.connect(self.model().renameColumnForIndex)
		
		for col in range(model.columnCount(QtCore.QModelIndex())):

			editor_feature = self._editorFeatureForColumn(col)

			if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.NameColumn:
				self.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)

			else:
				self.horizontalHeader().setSectionResizeMode(col,QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

	def itemDelegate(self) -> editordelegates.BSBinViewColumnDelegate:
		return super().itemDelegate()
	
	@QtCore.Slot()
	def userClickingDeleteColumn(self):
		"""User is pressing mouse button on one o' them "Delete" buttons prolly"""

		del_col = self._columnForEditorFeature(editorproxymodel.BSBinViewColumnEditorFeature.DeleteColumn)

		if not del_col:

			# No delete column? Probably shouldn't be deleting them then, hoss.  You ever think about that?
			# Lemme just clear this for yas.

			self.selectionModel().clear()
			return

		for selected_button_index in self.selectionModel().selectedRows(del_col):

			if not selected_button_index.data(QtCore.Qt.ItemDataRole.UserRole):

				# Deselect any rows that are not deletable / not showing a delete button probably

				self.selectionModel().select(
					selected_button_index,
					QtCore.QItemSelectionModel.SelectionFlag.Deselect|QtCore.QItemSelectionModel.SelectionFlag.Rows
				)

			else:
				# Repaint any delete buttons to show them goin' down
				self.update(selected_button_index)

	@QtCore.Slot()
	def userClickingHideColumn(self):
		"""User is pressing mouse button on one o' them "Delete" buttons prolly"""

		vis_col = self._columnForEditorFeature(editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn)

		if not vis_col:

			# No delete column? Probably shouldn't be deleting them then, hoss.  You ever think about that?
			# Lemme just clear this for yas.

			self.selectionModel().clear()
			return

		for selected_button_index in self.selectionModel().selectedRows(vis_col):

			if not selected_button_index.data(QtCore.Qt.ItemDataRole.UserRole):

				# Deselect any rows that are not deletable / not showing a delete button probably

				self.selectionModel().select(
					selected_button_index,
					QtCore.QItemSelectionModel.SelectionFlag.Deselect|QtCore.QItemSelectionModel.SelectionFlag.Rows
				)

			else:
				# Repaint any delete buttons to show them goin' down
				self.update(selected_button_index)

	@QtCore.Slot()
	def toggleSelectedColumnVisibility(self):

		if not self.model():
			return
		
		vis_col = self._columnForEditorFeature(editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn)
		
		selected_row_indexes = sorted(
			(i.row() for i in self.selectionModel().selectedRows(vis_col) if i.data(QtCore.Qt.ItemDataRole.UserRole)),
			reverse=True,
		)
		
		if not selected_row_indexes:
			return True
		
		self.model().blockSignals(True)
		
		for row in selected_row_indexes:

			item_index = self.model().index(row, 1, QtCore.QModelIndex())
			self.model().setData(item_index, not item_index.data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole), binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)
		
		self.model().blockSignals(False)

		self.model().layoutChanged.emit()

	def _columnForEditorFeature(self, feature:editorproxymodel.BSBinViewColumnEditorFeature) -> int|None:
		"""Get the model column index for a given bin view editor feature"""

		for col in range(self.model().columnCount(QtCore.QModelIndex())):

			if self.model().headerData(col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole) == feature:
				return col
		
		return None
	
	def _editorFeatureForColumn(self, col_index:int) -> editorproxymodel.BSBinViewColumnEditorFeature|None:
		"""Get the bin view editor feature role for a given column index"""

		if not self.model():
			return None
		
		return self.model().headerData(col_index, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

	@QtCore.Slot()
	def removeSelectedColumns(self):
		
		if not self.model():	
			return
		
		del_col = self._columnForEditorFeature(editorproxymodel.BSBinViewColumnEditorFeature.DeleteColumn)

		if del_col is None:
			return
		
		selected_row_indexes = sorted(
			(i.row() for i in self.selectionModel().selectedRows(del_col) if i.data(QtCore.Qt.ItemDataRole.UserRole)),
			reverse=True,
		)
		
		if not selected_row_indexes:
			return True
		
		row_clumps = clumper.clumpValues(
			(i for i in self.selectionModel().selectedRows(del_col) if i.data(QtCore.Qt.ItemDataRole.UserRole)),
			key=lambda i:i.row(),
			reverse=True
		)

		for clump in row_clumps:

			self.model().removeRows(
				clump[-1].row(),
				len(clump),
				QtCore.QModelIndex()
			)

	def sizeHintForRow(self, row:int):
		
		# Uniform row heights
		return super().sizeHintForRow(0)
	
	def dropEvent(self, event:QtGui.QDropEvent):

		if event.dropAction() != QtCore.Qt.DropAction.MoveAction:

			print("NAH")
			
			event.ignore()
			return super().dropEvent(event)
		
		print(event.dropAction())
		
		# Don't do anything fancy
		event.setDropAction(QtCore.Qt.DropAction.IgnoreAction)
		
		drop_target_index = self.indexAt(event.pos())

		if not drop_target_index.isValid() \
			or not self.selectionModel().hasSelection() \
			or not self.moveSelectedRows(
				source_indexes=self.selectionModel().selectedRows(1),
				destination_index=drop_target_index
		):

			event.ignore()
			return super().dropEvent(event)
		
		event.accept()



	def moveSelectedRows(self, source_indexes:typing.Iterable[QtCore.QModelIndex], destination_index:QtCore.QModelIndex) -> bool:

		if not destination_index.isValid():

			print("Invalid drop target index hmmmmmmm")
			return
		
		drop_target_row   = destination_index.row() if self.dropIndicatorPosition() == QtWidgets.QTableView.DropIndicatorPosition.AboveItem else destination_index.row() + 1
	

		# Clump together contiguous ranges... in reverse!
		
		source_row_index_clumps = list(
			clumper.clumpValues(
				source_indexes,
				key=lambda i: i.row(),
				reverse=True
			)
		)

		if not source_row_index_clumps:
			
			print("No rows to move")
			
			return False



		source_row_offset = 0
		dest_row_offset   = 0
		
		for source_row_index_clump in source_row_index_clumps:

			mapped_clump_length = source_row_index_clump[0].row() - source_row_index_clump[-1].row() + 1

			if self.dropIndicatorPosition() != QtWidgets.QTableView.DropIndicatorPosition.AboveItem:
				if source_row_index_clump[0].row() == drop_target_row:

					print("Nah")
					continue
				print(f"Moving below {destination_index.data(QtCore.Qt.ItemDataRole.DisplayRole)} ({source_row_index_clump[-1].row()=} {drop_target_row=}):")

			else:
				print(self.dropIndicatorPosition())

				print(f"{source_row_index_clump[-1].row()=} { drop_target_row+1=}")
				
				if source_row_index_clump[0].row() == drop_target_row-1:

					print("Nah")
					continue
				
				print(f"Moving above {destination_index.data(QtCore.Qt.ItemDataRole.DisplayRole)} ({source_row_index_clump[-1].row()=} {drop_target_row=}):")

			if source_row_index_clump[-1].row() > drop_target_row:

				# Movin' the under-clumps, as I call them in computery schience
				# Since we're moving it up, make sure the destination index is not the same as the first element


				
				print(f"{source_row_index_clump[0].row()=} {drop_target_row=}")

				
				names = []
				for row in reversed(range(source_row_index_clump[-1].row(), source_row_index_clump[-1].row() + mapped_clump_length)):
					names.append(self.model().index(row+source_row_offset, 0, QtCore.QModelIndex()).data(QtCore.Qt.ItemDataRole.DisplayRole))

				print(f"Move a under-clump: {names}")

				self.model().moveRows(
					QtCore.QModelIndex(),
					source_row_index_clump[-1].row() + source_row_offset,
					mapped_clump_length,
					QtCore.QModelIndex(),
					drop_target_row # + dest_row_offset
				)

				source_row_offset += mapped_clump_length

			elif source_row_index_clump[-1].row() < drop_target_row + dest_row_offset:

				print(f"Move a overboy {source_row_index_clump[-1].row()=} {drop_target_row=}")

				self.model().moveRows(
					QtCore.QModelIndex(),
					source_row_index_clump[-1].row(), # + source_row_offset,
					mapped_clump_length,
					QtCore.QModelIndex(),
					drop_target_row + dest_row_offset
				)


				dest_row_offset -= mapped_clump_length

			else:
				print("BRUH?")
				continue


		# Update selection model to stay selected on those very same indexes! Ooh!

		new_selection = QtCore.QItemSelection(
			self.model().index(drop_target_row +  dest_row_offset, 0, QtCore.QModelIndex()),
			self.model().index(drop_target_row +  dest_row_offset + sum(len(clump) for clump in source_row_index_clumps) - 1, 0, QtCore.QModelIndex())
		)

		self.selectionModel().select(
			new_selection,
			QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect | \
			QtCore.QItemSelectionModel.SelectionFlag.Rows
		)
		
		return True
#		return super().dropEvent(event)