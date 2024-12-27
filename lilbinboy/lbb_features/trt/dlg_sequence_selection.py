from PySide6 import QtCore, QtWidgets, QtGui
from ...lbb_common import LBClipColorPicker
from .model_trt import SingleSequenceSelectionProcess
import avbutils

class TRTSequenceSelection(QtWidgets.QDialog):

	sig_process_chosen = QtCore.Signal(SingleSequenceSelectionProcess)
	"""Process has been chosen"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._sort_process = SingleSequenceSelectionProcess()

		self.setWindowTitle("Sequence Selection Settings")

		self.setLayout(QtWidgets.QVBoxLayout())

		lbl_important_instructions = QtWidgets.QLabel("""Set the rules for choosing a sequence from a bin below.\n\nFirst, we'll need to sort the sequences into some sort of order, and then choose the first sequence in the list that matches any of the other paramaters set below."""
		)
		lbl_important_instructions.setWordWrap(True)

		self.layout().addWidget(lbl_important_instructions)

		grp_initial_sort = QtWidgets.QGroupBox()
		grp_initial_sort.setLayout(QtWidgets.QHBoxLayout())

		self.cmb_sort_column_name = QtWidgets.QComboBox()
		self.cmb_sort_column_direction = QtWidgets.QComboBox()
		grp_initial_sort.layout().addWidget(QtWidgets.QLabel("Initially sort sequences based on the"))
		grp_initial_sort.layout().addWidget(self.cmb_sort_column_name)
		grp_initial_sort.layout().addWidget(QtWidgets.QLabel("column, in"))
		grp_initial_sort.layout().addWidget(self.cmb_sort_column_direction)
		grp_initial_sort.layout().addWidget(QtWidgets.QLabel("order."))
		grp_initial_sort.layout().addStretch()
		
		self.layout().addWidget(grp_initial_sort)

		self.layout().addWidget(QtWidgets.QLabel("Then, choose the first sequence in that list that meets the following criteria:"))

		self.chk_name = QtWidgets.QCheckBox(text="Name column should contain the text")
		grp_criteria_name = QtWidgets.QGroupBox()
		grp_criteria_name.setLayout(QtWidgets.QHBoxLayout())
		grp_criteria_name.layout().addWidget(self.chk_name)
		grp_criteria_name.layout().addStretch()
		self.txt_name = QtWidgets.QLineEdit()
		grp_criteria_name.layout().addWidget(self.txt_name)

		self.layout().addWidget(grp_criteria_name)

		self.chk_colors = QtWidgets.QCheckBox(text="The sequence's clip color should be set to")
		grp_criteria_clipcolor = QtWidgets.QGroupBox()
		grp_criteria_clipcolor.setLayout(QtWidgets.QHBoxLayout())
		grp_criteria_clipcolor.layout().addWidget(self.chk_colors)
		grp_criteria_clipcolor.layout().addStretch()
		self.color_picker = LBClipColorPicker()
		self.color_picker.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum,QtWidgets.QSizePolicy.Policy.Maximum)
		self.color_picker.setFixedSize(98,42)
		grp_criteria_clipcolor.layout().addWidget(self.color_picker)

		self.layout().addWidget(grp_criteria_clipcolor)

		btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok|QtWidgets.QDialogButtonBox.StandardButton.Cancel)
		
		btns.accepted.connect(self.accept)
		btns.rejected.connect(self.reject)
		
		self.layout().addWidget(btns)
	
	def setInitialSortProcess(self, sort_process:SingleSequenceSelectionProcess):
		"""Set the available options for initial bin sorting"""

		self.cmb_sort_column_name.addItems(sort_process.SORT_COLUMNS)
		self.cmb_sort_column_name.setCurrentText(sort_process.sortColumn())
		
		self.cmb_sort_column_direction.addItems(sort_process.SORT_DIRECTIONS)
		self.cmb_sort_column_direction.setCurrentText(sort_process.sortDirection())

		for sequence_filter in sort_process.filters():

			if isinstance(sequence_filter, SingleSequenceSelectionProcess.ClipColorFilter):
				self.chk_colors.setChecked(True)
				for color in sequence_filter.colors():
					self.color_picker.setSelectedColor(color)
			
			elif isinstance(sequence_filter, SingleSequenceSelectionProcess.NameContainsFilter):
				self.chk_name.setChecked(True)
				self.txt_name.setText(sequence_filter.name())
	
	def buildSelectionProcess(self) -> SingleSequenceSelectionProcess:
		"""Build a process from the options selected"""

		sort_column_name = self.cmb_sort_column_name.currentText()
		sort_column_direction = self.cmb_sort_column_direction.currentText()
		
		filters = []
		if self.chk_name.isChecked() and self.txt_name.text():
			filters.append(SingleSequenceSelectionProcess.NameContainsFilter(self.txt_name.text()))
		
		if self.chk_colors.isChecked() and self.color_picker.selectedColor():
			color = self.color_picker.selectedColor()
			filters.append(SingleSequenceSelectionProcess.ClipColorFilter([color]))

		process = SingleSequenceSelectionProcess()
		process.setSortColumn(sort_column_name)
		process.setSortDirection(sort_column_direction)
		process.setFilters(filters)

		return process
	
	def accept(self):
		self.sig_process_chosen.emit(self.buildSelectionProcess())
		return super().accept()