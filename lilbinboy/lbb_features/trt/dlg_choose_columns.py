from PySide6 import QtWidgets, QtGui, QtCore

class TRTChooseColumnsList(QtWidgets.QListWidget):

	def __init__(self):
		super().__init__()
		self.setAlternatingRowColors(True)
		self.setUniformItemSizes(True)
		self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)


class TRTChooseColumnsDialog(QtWidgets.QDialog):
	"""Choose columns"""

	sig_columns_chosen = QtCore.Signal(list)
	"""Column indices chosen"""

	def __init__(self, *args):
		super().__init__(*args)

		self.setWindowTitle("Choose Visible Columns")

		self.setLayout(QtWidgets.QVBoxLayout())

		self.list_headers = TRTChooseColumnsList()
		self.list_headers.itemSelectionChanged.connect(self.selectionChanged)
		
		self.btn_toggle_selection = QtWidgets.QPushButton()
		self.txt_summary  = QtWidgets.QLabel()

		self.btn_box = QtWidgets.QDialogButtonBox()
		self.btn_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Save|QtWidgets.QDialogButtonBox.StandardButton.Cancel)
		self.btn_box.rejected.connect(self.reject)
		self.btn_box.accepted.connect(self.saveChanges)

		grp_available = QtWidgets.QGroupBox("Available Columns")
		grp_available.setLayout(QtWidgets.QVBoxLayout())
		grp_available.layout().addWidget(self.list_headers)
		grp_available.layout().setContentsMargins(2,2,2,2)
		
		lay_summary = QtWidgets.QHBoxLayout()
		self.btn_toggle_selection.setText("Select All / None")
		self.btn_toggle_selection.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditSelectAll))
		self.btn_toggle_selection.clicked.connect(self.toggleSelection)
		lay_summary.addWidget(self.btn_toggle_selection)
		lay_summary.addStretch()
		lay_summary.addWidget(self.txt_summary)
		
		grp_available.layout().addLayout(lay_summary)

		self.layout().addWidget(grp_available)

		self.layout().addWidget(self.btn_box)

		self.selectionChanged()
	
	def addColumn(self, header, is_hidden:bool):
		item = QtWidgets.QListWidgetItem(header.name() or header.field().title(), )
		self.list_headers.addItem(item)
		item.setSelected(not is_hidden)

	@QtCore.Slot()
	def selectionChanged(self):
		count_selected = len(self.list_headers.selectedItems())
		self.txt_summary.setText(f"{count_selected} Visible   {self.list_headers.count() - count_selected} Hidden")
		self.btn_box.button(QtWidgets.QDialogButtonBox.StandardButton.Save).setEnabled(bool(count_selected))
	
	@QtCore.Slot()
	def toggleSelection(self):
		if self.list_headers.selectedItems():
			self.list_headers.clearSelection()
		else:
			self.list_headers.selectAll()
		self.list_headers.setFocus()

	@QtCore.Slot()
	def saveChanges(self):
		"""Inform the people"""
		self.sig_columns_chosen.emit([idx.row() for idx in self.list_headers.selectedIndexes()])
		self.accept()