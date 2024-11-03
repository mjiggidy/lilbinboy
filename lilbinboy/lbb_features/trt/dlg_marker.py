import enum
from PySide6 import QtWidgets, QtCore, QtGui
from . import markers_trt

class TRTMarkerMaker(QtWidgets.QDialog):

	class EditingMode(enum.Enum):
		"""Preset editing modes"""

		CREATE_NEW = enum.auto()
		"""Creating a new thing"""
		EDIT_EXISTING = enum.auto()
		"""Editing an existing thing"""

	sig_save_preset = QtCore.Signal(str, markers_trt.LBMarkerPreset)
	sig_delete_preset = QtCore.Signal(str)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		self.setWindowTitle("Match Marker Criteria")
		self.setLayout(QtWidgets.QVBoxLayout())

		self._marker_presets = dict()
		self._editing_mode = self.EditingMode.CREATE_NEW	# Default to creating new with empty markers list at first

		self.cmb_marker_presets = markers_trt.LBMarkerPresetComboBox()
		self.txt_preset_name = QtWidgets.QLineEdit()
		self.val_preset_name = markers_trt.LBMarkerPresetNameValidator() # NOTE: Used for save button

		self.btn_save_preset = QtWidgets.QPushButton()
		self.btn_duplicate_preset = QtWidgets.QPushButton()
		self.btn_delete_preset = QtWidgets.QPushButton()

		self.cmb_marker_color = QtWidgets.QComboBox()
		self.txt_marker_comment = QtWidgets.QLineEdit()
		self.txt_marker_author  = QtWidgets.QLineEdit()
		self.btn_box = QtWidgets.QDialogButtonBox()

		self._setupWidgets()
		self._setupSignals()
	

	def _setupWidgets(self):

		lay_presets = QtWidgets.QHBoxLayout()
		lay_presets.addWidget(self.cmb_marker_presets)
		
		p = self.txt_preset_name.sizePolicy()
		p.setRetainSizeWhenHidden(True)
		self.txt_preset_name.setSizePolicy(p)
		self.txt_preset_name.setMaxLength(16)
		self.txt_preset_name.setValidator(self.val_preset_name)
		lay_presets.addWidget(self.txt_preset_name)
		
		self.btn_save_preset.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentSave))
		self.btn_save_preset.setToolTip("Save Preset")
		lay_presets.addWidget(self.btn_save_preset)
		
		self.btn_duplicate_preset.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditCopy))
		self.btn_duplicate_preset.setToolTip("Duplicate Preset")
		lay_presets.addWidget(self.btn_duplicate_preset)
		
		self.btn_delete_preset.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove))
		self.btn_delete_preset.setToolTip("Delete Preset")
		lay_presets.addWidget(self.btn_delete_preset)

		self.layout().addLayout(lay_presets)


		self.grp_edit = QtWidgets.QGroupBox()
		self.grp_edit.setLayout(QtWidgets.QGridLayout())

		self.grp_edit.layout().addWidget(QtWidgets.QLabel("Match Color"), 0, 0)
		self.grp_edit.layout().addWidget(self.cmb_marker_color, 1, 0)

		self.grp_edit.layout().addWidget(QtWidgets.QLabel("Match Comment"), 0, 1)
		self.txt_marker_comment.setPlaceholderText("(Any)")
		self.grp_edit.layout().addWidget(self.txt_marker_comment, 1,1)

		self.grp_edit.layout().addWidget(QtWidgets.QLabel("Match Author"), 0, 2)
		self.txt_marker_author.setPlaceholderText("(Any)")
		self.grp_edit.layout().addWidget(self.txt_marker_author, 1, 2)

		self.layout().addWidget(self.grp_edit)

		self.btn_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Close)
		self.layout().addWidget(self.btn_box)

	def _setupSignals(self):

		self.cmb_marker_presets.sig_marker_preset_changed.connect(self.setCurrentMarkerPresetName)
		self.cmb_marker_presets.sig_marker_preset_editor_requested.connect(self.createNewPreset)

		# Preset buttons
		self.btn_save_preset.clicked.connect(self.makeMarkerPreset)
		self.btn_delete_preset.clicked.connect(lambda: self.sig_delete_preset.emit(self.cmb_marker_presets.currentText()))
		
		#self.btn_box.accepted.connect(self.makeMarkerPreset)
		#self.btn_box.accepted.connect(self.accept)
		self.btn_box.rejected.connect(self.reject)

		self.txt_preset_name.textChanged.connect(self.presetNameChanged)
	
	def addMarker(self, marker:markers_trt.LBMarkerIcon):
		self.cmb_marker_color.addItem(marker, marker.name())
		self.cmb_marker_color.update()
	
	@QtCore.Slot()
	def makeMarkerPreset(self) -> markers_trt.LBMarkerPreset:
		"""Create a marker preset from the current settings"""

		self.sig_save_preset.emit(self.txt_preset_name.text(), markers_trt.LBMarkerPreset(
			color   = self.cmb_marker_color.currentText(),	# TODO: Use data in preparation for (Any) and such
			comment = self.txt_marker_comment.text() or None,
			author  = self.txt_marker_author.text() or None
		))
	
	@QtCore.Slot(dict)
	def setMarkerPresets(self, marker_presets:dict[str, markers_trt.LBMarkerPreset]):
		self._marker_presets = marker_presets
		self.cmb_marker_presets.setMarkerPresets(self._marker_presets)
		self.update_completers()

		if self.txt_preset_name.text() in self._marker_presets:
			self.cmb_marker_presets.setCurrentText(self.txt_preset_name.text())
		else:
			self.cmb_marker_presets.setCurrentIndex(0)
	
	@QtCore.Slot(str)
	def setCurrentMarkerPresetName(self, marker_preset_name:str|None):

		self.setEditingMode(self.EditingMode.EDIT_EXISTING)
		
		if marker_preset_name not in self._marker_presets:
			print("Not in there", marker_preset_name)
			return
		
		marker_preset:markers_trt.LBMarkerPreset = self._marker_presets[marker_preset_name]
		self.txt_preset_name.setText(marker_preset_name)
		self.txt_preset_name.setVisible(False)

		self.cmb_marker_color.setCurrentIndex(self.cmb_marker_color.findText(marker_preset.color))
		self.txt_marker_comment.setText(marker_preset.comment)
		self.txt_marker_author.setText(marker_preset.author)
	
	@QtCore.Slot()
	def createNewPreset(self):
		"""We makin a newy"""

		self.setEditingMode(self.EditingMode.CREATE_NEW)

		self.txt_preset_name.setText("New Preset")
		self.txt_preset_name.setVisible(True)
		self.cmb_marker_color.setCurrentIndex(0)
		self.txt_marker_comment.clear()
		self.txt_marker_author.clear()

		self.txt_preset_name.selectAll()
		self.txt_preset_name.setFocus()
	
	def setEditingMode(self, mode:EditingMode):
		self._editing_mode = mode
	
	def editingMode(self) -> EditingMode:
		return self._editing_mode
	
	@QtCore.Slot(str)
	def presetNameChanged(self, preset_name:str):
		"""Update the little groupbox title to include the preset name"""

		self.grp_edit.setTitle(f"Marker Match Criteria for \"{preset_name or '(Untited)'}\"")
		
		self.btn_save_preset.setEnabled(self.val_preset_name.validate(preset_name, len(preset_name)) is self.val_preset_name.State.Acceptable)
	
	def update_completers(self):

		completer_comments = QtWidgets.QCompleter(sorted(set([m.comment for m in self._marker_presets.values() if m.comment is not None])))
		completer_comments.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
		completer_comments.setCompletionMode(QtWidgets.QCompleter.CompletionMode.UnfilteredPopupCompletion)

		completer_authors = QtWidgets.QCompleter(sorted(set([m.author for m in self._marker_presets.values() if m.author is not None])))
		completer_authors.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
		completer_authors.setCompletionMode(QtWidgets.QCompleter.CompletionMode.UnfilteredPopupCompletion)

		self.txt_marker_comment.setCompleter(completer_comments)
		self.txt_marker_author.setCompleter(completer_authors)