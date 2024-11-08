import pathlib
from PySide6 import QtCore, QtGui, QtWidgets
from timecode import Timecode
from ...lbb_common import LBSpinBoxTC
from . import markers_trt

class TRTControlsTrims(QtWidgets.QGroupBox):

	# TODO: Better
	PATH_MARK_IN = str(pathlib.Path(__file__+"../../../../res/icon_mark_in.svg").resolve())
	PATH_MARK_OUT = str(pathlib.Path(__file__+"../../../../res/icon_mark_out.svg").resolve())

	sig_head_trim_changed = QtCore.Signal(Timecode)
	"""Timcode trim from head changed"""
	sig_tail_trim_changed = QtCore.Signal(Timecode)
	"""Timecode trim from tail changed"""

	sig_head_trim_marker_preset_chosen = QtCore.Signal(str)
	"""Marker preset trim from head changed"""
	sig_tail_trim_marker_preset_chosen = QtCore.Signal(str)
	"""Marker preset trim from tail changed"""

	sig_marker_preset_editor_requested = QtCore.Signal()
	"""Marker editor requested"""

	def __init__(self):

		super().__init__()

		self.setTitle("Sequence Trimming")

		self.setLayout(QtWidgets.QGridLayout())

		self._from_head = LBSpinBoxTC()
		self._from_tail = LBSpinBoxTC()

		self._use_head_marker = QtWidgets.QCheckBox()
		self._use_tail_marker = QtWidgets.QCheckBox()

		self._from_head_marker = markers_trt.LBMarkerPresetComboBox()
		self._from_tail_marker = markers_trt.LBMarkerPresetComboBox()

		self._icon_mark_in  = QtWidgets.QLabel(pixmap=QtGui.QPixmap(self.PATH_MARK_IN).scaledToHeight(16, QtCore.Qt.TransformationMode.SmoothTransformation))
		self._icon_mark_out = QtWidgets.QLabel(pixmap=QtGui.QPixmap(self.PATH_MARK_OUT).scaledToHeight(16, QtCore.Qt.TransformationMode.SmoothTransformation))

		self._setupWidgets()
		self._setupSignals()

	
	def _setupWidgets(self):

		# Trim from Head / Duration
		self.layout().addWidget(self._icon_mark_in, 0, 0)
		self.layout().addWidget(self._from_head, 0, 1)
		self.layout().addWidget(QtWidgets.QLabel("From Head"), 0, 2)
		self.layout().addItem(QtWidgets.QSpacerItem(0,2, QtWidgets.QSizePolicy.Policy.MinimumExpanding),0,3)
		
		# Trim from Head / Marker
		self._use_head_marker.setCheckState(QtCore.Qt.CheckState.Checked) # Start checked to sync state with combo box
		self.layout().addWidget(self._use_head_marker, 1, 0)
		self.layout().addWidget(self._from_head_marker, 1, 1)
		self.layout().addWidget(QtWidgets.QLabel("Or FFOA Locator", buddy=self._from_head), 1, 2)

		# Trim from Tail / Duration
		self._use_tail_marker.setCheckState(QtCore.Qt.CheckState.Checked)  # Start checked to sync state with combo box
		self.layout().addWidget(QtWidgets.QLabel("From Tail", alignment=QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter, buddy=self._from_tail), 0, 4)
		self.layout().addWidget(self._from_tail, 0, 5)
		self.layout().addWidget(self._icon_mark_out, 0, 6)

		# Trim from Tail / Marker
		self.layout().addWidget(QtWidgets.QLabel("Or LFOA Locator", alignment=QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter), 1, 4)
		self.layout().addWidget(self._from_tail_marker, 1, 5)
		self.layout().addWidget(self._use_tail_marker, 1, 6)

		
	def _setupSignals(self):
		# Timecode trim from head/tail changed
		self._from_head.sig_timecode_changed.connect(self.sig_head_trim_changed)
		self._from_tail.sig_timecode_changed.connect(self.sig_tail_trim_changed)

		# Marker presets checkboxes toggled on/off
		self._use_head_marker.checkStateChanged.connect(self._use_head_marker_toggled)
		self._use_tail_marker.checkStateChanged.connect(self._use_tail_marker_toggled)

		# Marker presets chosen from combo box (or editor called)
		self._from_head_marker.sig_marker_preset_editor_requested.connect(self.sig_marker_preset_editor_requested)
		self._from_head_marker.sig_marker_preset_changed.connect(self.sig_head_trim_marker_preset_chosen)
		
		self._from_tail_marker.sig_marker_preset_editor_requested.connect(self.sig_marker_preset_editor_requested)
		self._from_tail_marker.sig_marker_preset_changed.connect(self.sig_tail_trim_marker_preset_chosen)
	
	# Setters
	@QtCore.Slot(Timecode)
	def set_head_trim(self, timecode:Timecode):
		"""Set head trim TC"""
		self._from_head.blockSignals(True)
		self._from_head.setTimecode(timecode)
		self._from_head.blockSignals(False)

	@QtCore.Slot(Timecode)
	def set_tail_trim(self, timecode:Timecode):
		"""Set tail trim TC"""
		self._from_tail.blockSignals(True)
		self._from_tail.setTimecode(timecode)
		self._from_tail.blockSignals(False)
	
	@QtCore.Slot(dict)
	def set_marker_presets(self, marker_presets:dict[str, markers_trt.LBMarkerPreset]):
		"""Set marker preset selection for combo boxes"""

		# Disable marker presets if there are none
		if not marker_presets:
			self._use_head_marker.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._use_tail_marker.setCheckState(QtCore.Qt.CheckState.Unchecked)

		# Set marker presets lists for each combo box
		self._from_head_marker.setMarkerPresets(marker_presets)
		self._from_tail_marker.setMarkerPresets(marker_presets)
	
	@QtCore.Slot(str)
	def set_head_marker_preset_name(self, marker_preset_name:str|None):
		"""Set the active marker preset based on preset name (or None to deactivate)"""

		if not marker_preset_name:
			self._use_head_marker.setCheckState(QtCore.Qt.CheckState.Unchecked)
		else:
			self._use_head_marker.setCheckState(QtCore.Qt.CheckState.Checked)
			self._from_head_marker.setCurrentMarkerPresetName(marker_preset_name)

	@QtCore.Slot(str)
	def set_tail_marker_preset_name(self, marker_preset_name:str|None):
		"""Set the active marker preset based on preset name (or None to deactivate)"""

		if not marker_preset_name:
			self._use_tail_marker.setCheckState(QtCore.Qt.CheckState.Unchecked)
		else:
			self._use_tail_marker.setCheckState(QtCore.Qt.CheckState.Checked)
			self._from_tail_marker.setCurrentMarkerPresetName(marker_preset_name)
	
	# User actions
	@QtCore.Slot(QtCore.Qt.CheckState)
	def _use_head_marker_toggled(self, state:QtCore.Qt.CheckState):
		"""Use Head Marker checkbox was toggled"""

		# Enable/Disable combo box
		self._from_head_marker.setEnabled(state is QtCore.Qt.CheckState.Checked)

		# Request editor if checked but no selection available from combo box
		if state is QtCore.Qt.CheckState.Checked and not self._from_head_marker.currentMarkerPresetName():
			self.sig_marker_preset_editor_requested.emit()
		
		else:		
			# Emit change in preset choice
			self.sig_head_trim_marker_preset_chosen.emit(
				self._from_head_marker.currentMarkerPresetName() if state is QtCore.Qt.CheckState.Checked else None
			)

	@QtCore.Slot(QtCore.Qt.CheckState)
	def _use_tail_marker_toggled(self, state:QtCore.Qt.CheckState):
		"""Use Tail Marker checkbox was toggled"""

		# Enable/Disable combo box
		self._from_tail_marker.setEnabled(state is QtCore.Qt.CheckState.Checked)

		# Request editor if checked but no selection available from combo box
		if state is QtCore.Qt.CheckState.Checked and not self._from_tail_marker.currentMarkerPresetName():
			self.sig_marker_preset_editor_requested.emit()

		else:
			# Emit change in preset choice
			self.sig_tail_trim_marker_preset_chosen.emit(
				self._from_tail_marker.currentMarkerPresetName() if state is QtCore.Qt.CheckState.Checked else None
		)