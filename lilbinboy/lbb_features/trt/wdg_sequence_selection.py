from PySide6 import QtCore, QtGui, QtWidgets
from .model_trt import SequenceSelectionMode

class TRTModeSelection(QtWidgets.QFrame):
	"""Select how sequences are chosen from bins"""

	sig_sequence_selection_mode_changed = QtCore.Signal(SequenceSelectionMode)
	sig_sequence_selection_settings_requested = QtCore.Signal()

	def __init__(self):

		super().__init__()

		self.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
		self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
		self.updateStylesheet()

		#self.setSizePolicy(self.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.Maximum)

		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setContentsMargins(0,0,0,0)

		self._rdo_one_sequence = QtWidgets.QRadioButton()
		self._btn_one_sequence_config = QtWidgets.QPushButton()
		
		self._rdo_all_sequence = QtWidgets.QRadioButton()

		self._btn_group = QtWidgets.QButtonGroup()
		self._btn_group.addButton(self._rdo_one_sequence)
		self._btn_group.addButton(self._rdo_all_sequence)
		
		self.layout().addStretch()

		self._rdo_one_sequence.setText("One Sequence Per Bin")
		self.layout().addWidget(self._rdo_one_sequence)

		self._btn_one_sequence_config.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentProperties))
		self._btn_one_sequence_config.setIconSize(QtCore.QSize(8,8))
		self.layout().addWidget(self._btn_one_sequence_config)

		self.layout().addStretch()

		self._rdo_all_sequence.setText("All Sequences In Bin")
		self.layout().addWidget(self._rdo_all_sequence)

		self.layout().addStretch()

		self._btn_group.buttonClicked.connect(self.selectionChanged)
		self._btn_one_sequence_config.clicked.connect(self.sig_sequence_selection_settings_requested)
	
	def updateStylesheet(self):
		# I hate using CSS for this
		border_color = QtWidgets.QApplication.palette().color(QtGui.QPalette.ColorRole.Dark).name()
		#background_color = QtWidgets.QApplication.palette().color(QtGui.QPalette.ColorRole.Midlight).name()
		self.setStyleSheet(f"QFrame {{ border-radius: 2px; border: 1px solid {border_color}; }}") # Ugh
	
	@QtCore.Slot(QtWidgets.QAbstractButton)
	def selectionChanged(self, button:QtWidgets.QAbstractButton):

		if button == self._rdo_one_sequence:
			self.sig_sequence_selection_mode_changed.emit(SequenceSelectionMode.ONE_SEQUENCE_PER_BIN)
		elif button == self._rdo_all_sequence:
			self.sig_sequence_selection_mode_changed.emit(SequenceSelectionMode.ALL_SEQUENCES_PER_BIN)
		else:
			import logging
			logging.getLogger(__name__).error("Invalid selection mode selected: %s", button)
	
	@QtCore.Slot(SequenceSelectionMode)
	def setSequenceSelectionMode(self, mode:SequenceSelectionMode):
		
		if mode is SequenceSelectionMode.ONE_SEQUENCE_PER_BIN:
			self._rdo_one_sequence.setChecked(True)
		elif mode is SequenceSelectionMode.ALL_SEQUENCES_PER_BIN:
			self._rdo_all_sequence.setChecked(True)