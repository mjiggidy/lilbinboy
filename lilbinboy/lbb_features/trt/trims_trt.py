import pathlib
from PySide6 import QtCore, QtGui, QtWidgets
from timecode import Timecode
from ...lbb_common import LBSpinBoxTC
from . import markers_trt

class TRTControlsTrims(QtWidgets.QGroupBox):

	PATH_MARK_IN = str(pathlib.Path(__file__+"../../../../res/icon_mark_in.svg").resolve())
	PATH_MARK_OUT = str(pathlib.Path(__file__+"../../../../res/icon_mark_out.svg").resolve())

	sig_head_trim_changed = QtCore.Signal(Timecode)
	sig_tail_trim_changed = QtCore.Signal(Timecode)

	sig_head_trim_marker_preset_chosen = QtCore.Signal(str)
	sig_tail_trim_marker_preset_chosen = QtCore.Signal(str)

	sig_use_head_marker_changed = QtCore.Signal(bool)
	sig_use_tail_marker_changed = QtCore.Signal(bool)

	sig_marker_preset_editor_requested = QtCore.Signal()

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

		# Trim from Head / Duration
		self.layout().addWidget(self._icon_mark_in, 0, 0)
		self.layout().addWidget(self._from_head, 0, 1)
		self.layout().addWidget(QtWidgets.QLabel("From Head"), 0, 2)
		self.layout().addItem(QtWidgets.QSpacerItem(0,2, QtWidgets.QSizePolicy.Policy.MinimumExpanding),0,3)
		
		# Trim from Head / Marker
		self.layout().addWidget(self._use_head_marker, 1, 0)
		self.layout().addWidget(self._from_head_marker, 1, 1)
		self._from_head_marker.setEnabled(False)
		self.layout().addWidget(QtWidgets.QLabel("Or FFOA Locator", buddy=self._from_head), 1, 2)

		# Trim from Tail / Duration
		self.layout().addWidget(QtWidgets.QLabel("From Tail", alignment=QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter, buddy=self._from_tail), 0, 4)
		self.layout().addWidget(self._from_tail, 0, 5)
		self.layout().addWidget(self._icon_mark_out, 0, 6)

		# Trim from Tail / Marker
		self.layout().addWidget(QtWidgets.QLabel("Or LFOA Locator", alignment=QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter), 1, 4)
		self.layout().addWidget(self._from_tail_marker, 1, 5)
		self._from_tail_marker.setEnabled(False)
		self.layout().addWidget(self._use_tail_marker, 1, 6)

		self._from_head.sig_timecode_changed.connect(self.sig_head_trim_changed)
		self._from_tail.sig_timecode_changed.connect(self.sig_tail_trim_changed)

		self._use_head_marker.checkStateChanged.connect(lambda: self._from_head_marker.setEnabled(self._use_head_marker.isChecked()))
		self._use_head_marker.checkStateChanged.connect(lambda: self.sig_use_head_marker_changed.emit(self._use_head_marker.isChecked()))
		self._use_tail_marker.checkStateChanged.connect(lambda: self._from_tail_marker.setEnabled(self._use_tail_marker.isChecked()))
		self._use_tail_marker.checkStateChanged.connect(lambda: self.sig_use_tail_marker_changed.emit(self._use_tail_marker.isChecked()))

		self._from_head_marker.sig_marker_preset_editor_requested.connect(self.sig_marker_preset_editor_requested)
		self._from_head_marker.sig_marker_preset_changed.connect(self.sig_head_trim_marker_preset_chosen)
		
		self._from_tail_marker.sig_marker_preset_editor_requested.connect(self.sig_marker_preset_editor_requested)
		self._from_tail_marker.sig_marker_preset_changed.connect(self.sig_tail_trim_marker_preset_chosen)
	
	@QtCore.Slot(Timecode)
	def set_head_trim(self, timecode:Timecode):
		self._from_head.setTimecode(timecode)

	@QtCore.Slot(Timecode)
	def set_tail_trim(self, timecode:Timecode):
		self._from_tail.setTimecode(timecode)
	
	@QtCore.Slot(dict)
	def set_marker_presets(self, marker_presets:dict[str, markers_trt.LBMarkerPreset]):
		"""Update FFOA and LFOA marker combo boxes"""

		if not marker_presets:
			self._use_head_marker.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._use_tail_marker.setCheckState(QtCore.Qt.CheckState.Unchecked)

		self._from_head_marker.setMarkerPresets(marker_presets)
		self._from_tail_marker.setMarkerPresets(marker_presets)
	
	@QtCore.Slot(str)
	def set_head_marker_preset_name(self, marker_preset_name:str|None):

		if not marker_preset_name:
			self._use_head_marker.setCheckState(QtCore.Qt.CheckState.Unchecked)
		else:
			self._use_head_marker.setCheckState(QtCore.Qt.CheckState.Checked)
			self._from_head_marker.setCurrentMarkerPresetName(marker_preset_name)

	@QtCore.Slot(str)
	def set_tail_marker_preset_name(self, marker_preset_name:str|None):

		if not marker_preset_name:
			self._use_tail_marker.setCheckState(QtCore.Qt.CheckState.Unchecked)
		else:
			self._use_tail_marker.setCheckState(QtCore.Qt.CheckState.Checked)
			self._from_tail_marker.setCurrentMarkerPresetName(marker_preset_name)