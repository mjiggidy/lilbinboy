from PySide6 import QtWidgets
from . import logtreeview

class BSLogViewerWidget(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._tree_log = logtreeview.BSLogTreeView()
		
		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(0,0,0,0)
		
		self.layout().addWidget(self._tree_log)

		#lay_buttons = QtWidgets.QHBoxLayout()
		#
		#self._btn_show_storage = buttons.LBPushButtonAction()
		#
		#lay_buttons.addStretch()
		#lay_buttons.addWidget(self._btn_show_storage)
#
		#self.layout().addLayout(lay_buttons)

	
	def treeView(self) -> logtreeview.BSLogTreeView:
		"""Get the treeview displaying the logs"""

		return self._tree_log