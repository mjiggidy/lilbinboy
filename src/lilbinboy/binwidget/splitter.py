from PySide6 import QtWidgets, QtCore, QtGui
from ..textview import textview

# NOTE: This does not work at all lol.  Redo entirely.

class BSTreeViewSplitter(QtCore.QObject):

	def __init__(self, treeview_master:textview.BSBinTextView, treeview_frozen:textview.BSBinTextView):

		super().__init__(treeview_master)

		self._tree_master = treeview_master
		self._tree_frozen = treeview_frozen

		self._split_size  = 200 #px

		self._tree_master.viewport().installEventFilter(self)

		self._tree_master.header().sectionResized.connect(lambda idx_logical, _, size_new: self._tree_frozen.header().resizeSection(idx_logical, size_new))
		self._tree_master.header().sectionMoved.connect(lambda idx_logical, idx_vis_old, idx_vis_new: self._tree_frozen.header().moveSection(idx_vis_old, idx_vis_new))

	def updateFrozenSize(self):
		"""Resize frozen treeview"""

		self._tree_frozen.resize(
			self._split_size,
			self._tree_master.size().height() - self._tree_master.horizontalScrollBar().style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent)
		)


	def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent):

		
		if event.type() == QtCore.QEvent.Type.Resize:
			
			self.updateFrozenSize()
		
		return super().eventFilter(watched, event)