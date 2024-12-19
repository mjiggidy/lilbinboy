from PySide6 import QtCore, QtWidgets
from ...lbb_common import LBClipColorPicker

class TRTSequenceSelection(QtWidgets.QDialog):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setWindowTitle("Sequence Selection Settings")

		self.setLayout(QtWidgets.QVBoxLayout())

		lbl_important_instructions = QtWidgets.QLabel("""Set the rules for choosing a sequence from a bin below.

First, we'll need to sort the sequences into some sort of order, and then choose the first sequence in the list that matches any of the other paramaters set below."""
		)
		lbl_important_instructions.setWordWrap(True)

		self.layout().addWidget(lbl_important_instructions)

		grp_initial_sort = QtWidgets.QGroupBox()
		grp_initial_sort.setLayout(QtWidgets.QHBoxLayout())

		grp_initial_sort.layout().addWidget(QtWidgets.QLabel("Initially sort sequences based on the"))
		grp_initial_sort.layout().addWidget(QtWidgets.QComboBox())
		grp_initial_sort.layout().addWidget(QtWidgets.QLabel("column, in"))
		grp_initial_sort.layout().addWidget(QtWidgets.QComboBox())
		grp_initial_sort.layout().addWidget(QtWidgets.QLabel("order."))
		grp_initial_sort.layout().addStretch()
		
		self.layout().addWidget(grp_initial_sort)

		self.layout().addWidget(QtWidgets.QLabel("Then, choose the first sequence in that list that meets the following criteria:"))

		grp_criteria_name = QtWidgets.QGroupBox()
		grp_criteria_name.setLayout(QtWidgets.QHBoxLayout())
		grp_criteria_name.layout().addWidget(QtWidgets.QCheckBox(text="Name column should contain the text"))
		grp_criteria_name.layout().addStretch()
		grp_criteria_name.layout().addWidget(QtWidgets.QLineEdit())

		self.layout().addWidget(grp_criteria_name)

		grp_criteria_clipcolor = QtWidgets.QGroupBox()
		grp_criteria_clipcolor.setLayout(QtWidgets.QHBoxLayout())
		grp_criteria_clipcolor.layout().addWidget(QtWidgets.QCheckBox(text="The sequence's clip color should be set to"))
		grp_criteria_clipcolor.layout().addStretch()
		picker = LBClipColorPicker()
		picker.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum,QtWidgets.QSizePolicy.Policy.Maximum)
		picker.setFixedSize(80,32)
		grp_criteria_clipcolor.layout().addWidget(picker)

		self.layout().addWidget(grp_criteria_clipcolor)

		btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok|QtWidgets.QDialogButtonBox.StandardButton.Cancel)
		
		btns.accepted.connect(self.accept)
		btns.rejected.connect(self.reject)
		
		self.layout().addWidget(btns)