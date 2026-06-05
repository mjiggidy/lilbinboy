"""
Widgets for adding as scrollBarWidgets to `QScrollArea`

Mostly standard widgets sublcassed for style
"""

import typing
from PySide6 import QtCore, QtWidgets

class BSBinStatsLabel(QtWidgets.QComboBox):
	"""Display label intended for use in a `QScrollArea` widget"""

	DEFAULT_TEXT = [
		QtCore.QCoreApplication.tr("Showing {filtered_item_count} of {source_item_count} items"),
		QtCore.QCoreApplication.tr("Showing {filtered_column_count} of {source_column_count} columns"),
		QtCore.QCoreApplication.tr("Showing {filtered_item_count} items; {filtered_column_count} columns"),
	]

	def __init__(
		self,
		*args,
		filter_model:QtCore.QAbstractItemModel,
		source_items_model:QtCore.QAbstractItemModel,
		source_cols_model:QtCore.QAbstractItemModel,
		font_scale:float=0.8,
		char_width:int=32,  # len("Showing 999,999 of 999,999 items")
		stat_strings:typing.Iterable[str]|None=None,
		**kwargs
	):

		super().__init__(*args, **kwargs)

		self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, self.sizePolicy().verticalPolicy())
#		self.setAlignment (QtCore.Qt.AlignmentFlag.AlignCenter)
#		self.setFrameStyle(QtWidgets.QFrame.Shape.StyledPanel|QtWidgets.QFrame.Shadow.Sunken)

		f = self.font()
		f.setPointSizeF(f.pointSizeF() * font_scale)
		self.setFont(f)
		
		self.setMinimumWidth(self.fontMetrics().averageCharWidth() * char_width)

		self._filter_model = filter_model

		self._source_items_model   = source_items_model
		self._source_cols_model    = source_cols_model

		self._source_model_connections = []

		self._stat_strings = stat_strings or self.DEFAULT_TEXT

		self._last_index = 0

		self.activated.connect(self.selectedIndexChanged)

		self._setupFilterModels()
		self._setupSourceModel()

	def setStatStrings(self, stat_strings:typing.Iterable[str]):
		"""Supported tokens: `{filtered_item_count}`,`{filtered_column_count}`,`{source_item_count}`,`{source_column_count}`"""

		self._stat_strings = stat_strings
		self.updateStats()

	@QtCore.Slot(int)
	def selectedIndexChanged(self, selected_index:int):

		self._last_index = selected_index

	def _setupFilterModels(self):

#		self._filtered_items_model.layoutChanged   .connect(self.updateStats)
		self._filter_model.rowsInserted    .connect(self.updateStats)
		self._filter_model.columnsInserted .connect(self.updateStats)
		self._filter_model.rowsRemoved     .connect(self.updateStats)
		self._filter_model.columnsRemoved  .connect(self.updateStats)
		self._filter_model.modelReset      .connect(self.updateStats)

	@QtCore.Slot()
	def _setupSourceModel(self):


		self._source_items_model.rowsInserted    .connect(self.updateStats)
#		self._source_items_model.columnsInserted .connect(self.updateStats)
		self._source_items_model.rowsRemoved     .connect(self.updateStats)
#		self._source_items_model.columnsRemoved  .connect(self.updateStats)
		self._source_items_model.modelReset      .connect(self.updateStats)

		self._source_cols_model.rowsInserted    .connect(self.updateStats)
#		self._source_cols_model.columnsInserted .connect(self.updateStats)
		self._source_cols_model.rowsRemoved     .connect(self.updateStats)
#		self._source_cols_model.columnsRemoved  .connect(self.updateStats)
		self._source_cols_model.modelReset      .connect(self.updateStats)

	@QtCore.Slot()
	def updateStats(self):

		self.clear()

		if not self._source_items_model or not self._source_cols_model:
			self.addItem(self.tr("Nothing loaded"))
			return
		
		source_rows      = self._source_items_model.rowCount(QtCore.QModelIndex())
		source_columns   = self._source_cols_model .rowCount(QtCore.QModelIndex())

		if source_rows == 0 or source_columns == 0:
			self.addItem(self.tr("No items to show"))
			return
		
		filtered_rows    = self._filter_model.rowCount(QtCore.QModelIndex())
		filtered_columns = self._filter_model.columnCount(QtCore.QModelIndex())


		for label_text in self._stat_strings:
			self.addItem(label_text.format(
				filtered_item_count   = QtCore.QLocale.system().toString(filtered_rows),
				source_item_count     = QtCore.QLocale.system().toString(source_rows),
				filtered_column_count = QtCore.QLocale.system().toString(filtered_columns),
				source_column_count   = QtCore.QLocale.system().toString(source_columns),
			))

		self.setCurrentIndex(self._last_index)