from PySide6 import QtWidgets, QtCore

from . import editordelegates, editorproxymodel
from ..binview import binviewitemtypes

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

		self.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
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
		self.itemDelegate().sig_hide_column_index.connect(self.toggleBinColumnVisibility)
		self.itemDelegate().sig_remove_selected_bin_columns.connect(self.removeSelectedColumns)
#		self.itemDelegate().sig_rename_column_for_index.connect(self.model().renameColumnForIndex)
		
		for col in range(model.columnCount(QtCore.QModelIndex())):

			editor_feature = model.headerData(col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

			if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.NameColumn:
				self.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)

			else:
				self.horizontalHeader().setSectionResizeMode(col,QtWidgets.QHeaderView.ResizeMode.ResizeToContents)


	
	def itemDelegate(self) -> editordelegates.BSBinViewColumnDelegate:
		return super().itemDelegate()
	
	@QtCore.Slot(int, QtCore.QModelIndex)
	def toggleBinColumnVisibility(self, row:int, parent:QtCore.QModelIndex):

		if not self.model() or parent.isValid():
			return
		
		row_index = self.model().index(row, 1, QtCore.QModelIndex())
		is_hidden = row_index.data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

		self.model().setData(row_index, not is_hidden, binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

	@QtCore.Slot()
	def removeSelectedColumns(self):
		
		if not self.model():	
			return
		
		del_col = None
		for col in range(self.model().columnCount(QtCore.QModelIndex())):

			if self.model().headerData(col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole) == editorproxymodel.BSBinViewColumnEditorFeature.DeleteColumn:
				del_col = col
				break

		if del_col is None:
			print("Hmm")
			return
		
		selected_row_indexes = sorted(
			(i.row() for i in self.selectionModel().selectedRows(del_col) if i.data(QtCore.Qt.ItemDataRole.UserRole)),
#			key=lambda i: i.row(),
			reverse=True,
		)
		
		if not selected_row_indexes:
			# Hmmmm....
			return True
		
		row_clumps = []
		clump = []
		for row in selected_row_indexes:
			
			if clump:
				if clump[-1] == row+1:
					clump.append(row)
				else:
					row_clumps.append(clump)
					clump = [row]
			else:
				clump = [row]
		
		if clump:
			row_clumps.append(clump)
		else:
			print("No clumps...")
			return

#		print("Clumps: ", row_clumps)

		for clump in row_clumps:

			self.model().removeRows(
				clump[-1],
				len(clump),
				QtCore.QModelIndex()
			)

#			print("Removed clump", clump)
		
		#self.model().removeRow(row, QtCore.QModelIndex())

	def sizeHintForRow(self, row:int):
		
		# Uniform row heights
		return super().sizeHintForRow(0)