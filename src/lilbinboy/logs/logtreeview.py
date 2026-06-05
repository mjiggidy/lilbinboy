from PySide6 import QtWidgets, QtCore
from . import logmodels

class BSLogTreeView(QtWidgets.QTreeView):
	"""A TreeView for viewin' trees. And logs.  Logs from trees."""

	def __init__(self, log_model:logmodels.BSLogDataModel|None=None, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

		self.setSortingEnabled(True)
		self.setRootIsDecorated(False)
		self.setAlternatingRowColors(True)
		self.setUniformRowHeights(True)
		
		self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
		self.setAutoScroll(False)

		self.header().setFirstSectionMovable(True)
		self.header().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		
		if log_model:
			self.setModel(log_model)