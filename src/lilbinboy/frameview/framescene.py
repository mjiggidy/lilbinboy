import logging
from PySide6 import QtCore, QtWidgets

from ..textview import textviewproxymodel

from ..core import config
from . import sceneitems, painters

from ..binitems import binitemtypes

class BSBinFrameScene(QtWidgets.QGraphicsScene):
	"""Graphics scene based on a bin model"""

	sig_bin_filter_model_changed   = QtCore.Signal(object)
	sig_bin_item_added             = QtCore.Signal(object)

	def __init__(self,
		*args,
		bin_filter_model:QtCore.QAbstractItemModel|None=None,
		brushes_manager:painters.BSFrameItemBrushManager|None=None,
		**kwargs
	):

		super().__init__(*args, **kwargs)

		self._bin_filter_model = bin_filter_model or QtCore.QIdentityProxyModel()
		self._brushes_manager  = brushes_manager  or painters.BSFrameItemBrushManager(parent=self.parent())

		self._bin_items:list[sceneitems.BSFrameModeItem] = list()

		self._z_top = 0

		self._setupModel()

	def _setupModel(self):

		self._bin_filter_model.rowsInserted         .connect(self.addBinItems)
		self._bin_filter_model.rowsMoved            .connect(self.reloadBinFilterModel)
		self._bin_filter_model.rowsAboutToBeRemoved .connect(self.removeBinItems)
		self._bin_filter_model.modelReset           .connect(self.clear)

		self._bin_filter_model.layoutChanged .connect(self.reloadBinFilterModel)

	@QtCore.Slot(object)
	def setSelectedItems(self, item_indexes:list[int]):
		"""Set selected items"""

		for idx, item in enumerate(self._bin_items):
			item.setSelected(idx in item_indexes)

	def binFilterModel(self) -> QtCore.QAbstractItemModel:
		return self._bin_filter_model

	@QtCore.Slot(object)
	def setBinFilterModel(self, bin_model:QtCore.QAbstractItemModel):

		if self._bin_filter_model == bin_model:
			return

		self._bin_filter_model.disconnect(self)

		self._bin_filter_model = bin_model
		self._setupModel()

		logging.getLogger(__name__).debug("Set bin filter model=%s (source model=%s)", self._bin_filter_model, self._bin_filter_model.sourceModel())
		self.sig_bin_filter_model_changed.emit(bin_model)

	@QtCore.Slot()
	def reloadBinFilterModel(self):
		"""Reset and reload items from bin filter model to stay in sync with order changes"""

		logging.getLogger(__name__).debug("About to clear bin frame view for layout change")
		self.clear()

		self.addBinItems(QtCore.QModelIndex(), 0, self._bin_filter_model.rowCount()-1)
		#self.setSelectedItemsFromSelectionModel(self._selection_model.selection(), QtCore.QItemSelection())

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def addBinItems(self, parent_row_index:QtCore.QModelIndex, row_start:int, row_end:int):

		for row in range(row_start, row_end+1):

			# Resolve source model to ensure we always have relevent columns available
			proxy_row_index  = self._bin_filter_model.index(row, 0, parent_row_index)

			bin_item_name   = proxy_row_index.data(binitemtypes.BSBinItemDataRoles.ItemNameRole)
			bin_item_coords = proxy_row_index.data(binitemtypes.BSBinItemDataRoles.FrameCoordinatesRole) or [-3000,-3000]
			bin_item_color  = proxy_row_index.data(binitemtypes.BSBinItemDataRoles.ClipColorRole)
			bin_item_type   = proxy_row_index.data(binitemtypes.BSBinItemDataRoles.ItemTypesRole)

			bin_item = sceneitems.BSFrameModeItem(brush_manager=self._brushes_manager)

			bin_item.setName(str(bin_item_name))
			bin_item.setClipColor(bin_item_color)
			bin_item.setClipType(bin_item_type)
			bin_item.setFlags(config.BSFrameViewModeConfig.DEFAULT_ITEM_FLAGS)

			x, y, z = *bin_item_coords, self._z_top
			self._z_top += 1

			bin_item.setPos(QtCore.QPoint(x, y))
			bin_item.setZValue(z)

			self._bin_items.insert(row, bin_item)

			self.addItem(bin_item)

			self.sig_bin_item_added.emit(bin_item)

	@QtCore.Slot(QtCore.QModelIndex, int, int)
	def removeBinItems(self, parent_row_index:QtCore.QModelIndex, row_start:int, row_end:int):

		for row in range(row_end, row_start-1, -1):

			bin_item = self._bin_items.pop(row)
			self.removeItem(bin_item)

	@QtCore.Slot(object)
	def raiseItemToTop(self, item:QtWidgets.QGraphicsItem):

		self._z_top += 1
		item.setZValue(self._z_top)

	@QtCore.Slot(object)
	def raiseItemsToTop(self, items:list[QtWidgets.QGraphicsItem]):

		for item in sorted(items, key=lambda i: i.zValue()):
			self.raiseItemToTop(item)

	@QtCore.Slot()
	def clear(self):

		self._bin_items.clear()
		logging.getLogger(__name__).debug("Bin frame view cleared")
		return super().clear()