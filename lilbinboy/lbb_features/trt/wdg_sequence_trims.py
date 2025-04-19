import pathlib
from PySide6 import QtCore, QtGui, QtWidgets
from timecode import Timecode
from lilbinboy.lbb_common import LBSpinBoxTC, resources
from lilbinboy.lbb_features.trt import markers_trt

class TRTControlsTrims(QtWidgets.QWidget):

	PATH_MARK_IN  = ":/trt/icons/icon_mark_in.svg"
	PATH_MARK_OUT = ":/trt/icons/icon_mark_out.svg"

	sig_head_trim_changed = QtCore.Signal(Timecode)
	"""Timcode trim from head changed"""
	sig_tail_trim_changed = QtCore.Signal(Timecode)
	"""Timecode trim from tail changed"""

	sig_head_trim_marker_preset_chosen = QtCore.Signal(str)
	"""Marker preset trim from head changed"""
	sig_tail_trim_marker_preset_chosen = QtCore.Signal(str)
	"""Marker preset trim from tail changed"""

	sig_total_trim_changed = QtCore.Signal(Timecode)
	"""Total running adjustment changed"""

	sig_marker_preset_editor_requested = QtCore.Signal()
	"""Marker editor requested"""

	def __init__(self):

		super().__init__()

		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setContentsMargins(0,0,0,0)

		self._from_head  = LBSpinBoxTC()
		self._from_tail  = LBSpinBoxTC()
		self._from_total = LBSpinBoxTC()

		self._use_head_marker = QtWidgets.QCheckBox()
		self._use_tail_marker = QtWidgets.QCheckBox()

		self._from_head_marker = markers_trt.LBMarkerPresetComboBox()
		self._from_tail_marker = markers_trt.LBMarkerPresetComboBox()

		self._icon_mark_in  = QtWidgets.QLabel(pixmap=QtGui.QIcon(self.PATH_MARK_IN).pixmap(QtCore.QSize(16,16)))
		self._icon_mark_out = QtWidgets.QLabel(pixmap=QtGui.QIcon(self.PATH_MARK_OUT).pixmap(QtCore.QSize(16,16)))

		self._lbl_total_note = QtWidgets.QLabel()

		self._setupWidgets()
		self._setupSignals()

	
	def _setupWidgets(self):

		# Trim from Head / Duration
		grp_head_trims = QtWidgets.QGroupBox("Per-Sequence FFOA")
		grp_head_trims.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
		grp_head_trims.setLayout(QtWidgets.QGridLayout())

		grp_head_trims.layout().addWidget(self._icon_mark_in, 0, 0)
		grp_head_trims.layout().addWidget(self._from_head, 0, 1)
		grp_head_trims.layout().addWidget(QtWidgets.QLabel("From Head"), 0, 2)

		# Trim from Head / Marker
		self._use_head_marker.setCheckState(QtCore.Qt.CheckState.Checked) # Start checked to sync state with combo box
		grp_head_trims.layout().addWidget(self._use_head_marker, 1, 0)
		grp_head_trims.layout().addWidget(self._from_head_marker, 1, 1)
		grp_head_trims.layout().addWidget(QtWidgets.QLabel("Or FFOA Marker", buddy=self._from_head), 1, 2)
		
		self.layout().addWidget(grp_head_trims)

		self.layout().addStretch()

		# Total Running Adjustments
		
		grp_total_trims = QtWidgets.QGroupBox("Total Running Adjustment")
		grp_total_trims.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
		grp_total_trims.setLayout(QtWidgets.QGridLayout())

		self._from_total.setAllowNegative(True)
		grp_total_trims.layout().addWidget(self._from_total)
		self._lbl_total_note.setText("(This does not affect individual sequence durations)")
		self._lbl_total_note.setWordWrap(True)
		self._lbl_total_note.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter|QtCore.Qt.AlignmentFlag.AlignVCenter)
		#self._lbl_total_note.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, self._lbl_total_note.sizePolicy().verticalPolicy())
		
		fnt_lbl = self._lbl_total_note.font()
		fnt_lbl.setPointSize(fnt_lbl.pointSize() - 2)
		self._lbl_total_note.setFont(fnt_lbl)
		grp_total_trims.layout().addWidget(self._lbl_total_note)

		self.layout().addWidget(grp_total_trims)

		self.layout().addStretch()

		# Trim from Tail / Duration

		grp_tail_trims = QtWidgets.QGroupBox("Per-Sequence LFOA")
		grp_tail_trims.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		grp_tail_trims.setLayout(QtWidgets.QGridLayout())

		self._use_tail_marker.setCheckState(QtCore.Qt.CheckState.Checked)  # Start checked to sync state with combo box
		grp_tail_trims.layout().addWidget(QtWidgets.QLabel("From Tail", alignment=QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter, buddy=self._from_tail), 0, 4)
		grp_tail_trims.layout().addWidget(self._from_tail, 0, 5)
		grp_tail_trims.layout().addWidget(self._icon_mark_out, 0, 6)

		# Trim from Tail / Marker
		grp_tail_trims.layout().addWidget(QtWidgets.QLabel("Or LFOA Marker", alignment=QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter), 1, 4)
		grp_tail_trims.layout().addWidget(self._from_tail_marker, 1, 5)
		grp_tail_trims.layout().addWidget(self._use_tail_marker, 1, 6)

		self.layout().addWidget(grp_tail_trims)

		
	def _setupSignals(self):
		# Timecode trim from head/tail changed
		self._from_head.sig_timecode_changed.connect(self.sig_head_trim_changed)
		self._from_tail.sig_timecode_changed.connect(self.sig_tail_trim_changed)
		self._from_total.sig_timecode_changed.connect(self.sig_total_trim_changed)

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
	
	@QtCore.Slot(Timecode)
	def set_total_trim(self, timecode:Timecode):
		"""Set total running adjustment"""
		self._from_total.blockSignals(True)
		self._from_total.setTimecode(timecode)
		self._from_total.blockSignals(False)
	
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

		print("Setting head marker to", marker_preset_name)

		if not marker_preset_name:
			self._use_head_marker.setCheckState(QtCore.Qt.CheckState.Unchecked)
			
			self._from_head_marker.blockSignals(True)
			self._from_head_marker.setCurrentIndex(0)
			self._from_head_marker.blockSignals(False)

		else:
			self._use_head_marker.setCheckState(QtCore.Qt.CheckState.Checked)
			self._from_head_marker.setCurrentMarkerPresetName(marker_preset_name)

	@QtCore.Slot(str)
	def set_tail_marker_preset_name(self, marker_preset_name:str|None):
		"""Set the active marker preset based on preset name (or None to deactivate)"""

		print("Setting tail marker to ", marker_preset_name)
		
		if not marker_preset_name:
			self._use_tail_marker.setCheckState(QtCore.Qt.CheckState.Unchecked)
			
			self._from_tail_marker.blockSignals(True)
			self._from_tail_marker.setCurrentIndex(0)
			self._from_tail_marker.blockSignals(False)
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