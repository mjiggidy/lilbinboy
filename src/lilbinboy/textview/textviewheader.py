from PySide6 import QtCore, QtGui, QtWidgets

class BSTextViewColumnHeaderView(QtWidgets.QHeaderView):
	"""Bin View Column Header"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

	def moveSection(self, idx_vis_start:int, idx_vis_dest:int):
		
		width_start = self.sectionSize(self.logicalIndex(idx_vis_dest))
		width_dest  = self.sectionSize(self.logicalIndex(idx_vis_start))
		
		
#		print("MOVING")
		super().moveSection(idx_vis_start, idx_vis_dest)

		self.resizeSection(self.logicalIndex(idx_vis_start), width_dest)
		self.resizeSection(self.logicalIndex(idx_vis_dest), width_start)


# NOTE: This works for column selection but ruins column dragging

#	def mousePressEvent(self, e:QtGui.QMouseEvent):
#
#		treeview:QtWidgets.QTreeView = self.parent()
#		idx_logical = self.logicalIndexAt(e.pos())
#
#		if idx_logical == -1:
#			return
#		
#		treeview.selectionModel().select(
#			treeview.model().index(0, idx_logical, QtCore.QModelIndex()),
#			QtCore.QItemSelectionModel.SelectionFlag.Columns|QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect
#		)
#
#		#return super().mousePressEvent(e)
#	
#	def mouseDoubleClickEvent(self, e):
#
#		idx_logical = self.logicalIndexAt(e.pos())
#
#		if idx_logical == -1:
#			return
#		
#		if self.sortIndicatorSection() == idx_logical:
#			self.setSortIndicator(idx_logical, QtCore.Qt.SortOrder.AscendingOrder if self.sortIndicatorOrder() == QtCore.Qt.SortOrder.DescendingOrder else QtCore.Qt.SortOrder.DescendingOrder)
#		
#		self.setSortIndicator(idx_logical, self.sortIndicatorOrder())
#		
#
#		return super().mouseDoubleClickEvent(e)
#
#	# TODO: Maybe needed.  May as well.