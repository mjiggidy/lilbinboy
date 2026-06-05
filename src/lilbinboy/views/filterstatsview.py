from PySide6 import QtCore, QtWidgets



"""
Model change happens:
- Get proxy rows & columns
- Get source rows & columns
- Set string to formatted text

Later:
- Combo box with options:

	Showing x of x items
	Showing x of x columns
	x items | x columns
"""

class BSFilterModelStatsView(QtWidgets.QLabel):
	"""A little stats viewer thingy to show filtered vs unfiltered counts and such"""

	DEFAULT_TEXT = "Showing {filtered_item_count} of {source_item_count} items"

	def __init__(self, *args, filter_model:QtCore.QSortFilterProxyModel|None=None, source_model:QtCore.QAbstractItemModel|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._filter_model:QtCore.QSortFilterProxyModel = filter_model or QtCore.QSortFilterProxyModel(parent=self)
		self._source_model:QtCore.QAbstractItemModel    = source_model or self._filter_model.sourceModel()

		self._source_model_connections = []

		self._setupModel()

	def _setupModel(self):
		
		self._filter_model.sourceModelChanged .connect(self._setupSourceModel)
		self._filter_model.layoutChanged      .connect(self.modelDataChanged)
		self._filter_model.modelReset         .connect(self.modelDataChanged)

		if self._filter_model.sourceModel() is not None:
			self._setupSourceModel()

	@QtCore.Slot()
	def _setupSourceModel(self):

		for c in self._source_model_connections:
			self.disconnect(c)

		self._source_model_connections = [
			self._filter_model.sourceModel().rowsInserted    .connect(self.modelDataChanged),
			self._filter_model.sourceModel().columnsInserted .connect(self.modelDataChanged),
			self._filter_model.sourceModel().rowsRemoved     .connect(self.modelDataChanged),
			self._filter_model.sourceModel().columnsRemoved  .connect(self.modelDataChanged),
			self._filter_model.sourceModel().modelReset      .connect(self.modelDataChanged),
		]

	@QtCore.Slot()
	def modelDataChanged(self):

		if not self._filter_model.sourceModel():
			self.setText(self.tr("Nothing loaded"))
			return
		
		if self._filter_model.sourceModel().rowCount(QtCore.QModelIndex()) == 0:
			self.setText(self.tr("No items to show"))
			return
		
		filtered_rows = self._filter_model.rowCount(QtCore.QModelIndex())
		source_rows   = self._filter_model.rowCount(QtCore.QModelIndex())

		self.setText(self.tr(self.DEFAULT_TEXT).format(
			filtered_item_count = QtCore.QLocale.system().toString(filtered_rows),
			source_item_count   = QtCore.QLocale.system().toString(source_rows),
		))