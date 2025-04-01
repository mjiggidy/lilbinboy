import enum
from PySide6 import QtWidgets, QtCore, QtGui
from lilbinboy.lbb_features.trt import markers_trt
from lilbinboy.lbb_common import make_unique_name

class TRTMarkerMaker(QtWidgets.QDialog):

	class EditingMode(enum.Enum):
		"""Preset editing modes"""

		CREATE_NEW = enum.auto()
		"""Creating a new thing"""
		EDIT_EXISTING = enum.auto()
		"""Editing an existing thing"""

	sig_save_preset = QtCore.Signal(str, markers_trt.LBMarkerPreset)

	sig_set_as_ffoa = QtCore.Signal(str)
	sig_set_as_lfoa = QtCore.Signal(str)

	sig_delete_preset = QtCore.Signal(str)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		self.setWindowTitle("Match Marker By Criteria Presets[*]")
		self.setLayout(QtWidgets.QVBoxLayout())

		self._default_marker_preset = markers_trt.LBMarkerPreset(
			color   = None,
			comment = None,
			author  = None
		)
		self._default_preset_name = "New Preset"

		self._marker_presets = dict()
		self._editing_mode = self.EditingMode.EDIT_EXISTING	# Default to creating new with empty markers list at first
		self._is_dirty = False
		self._current_marker_preset = self._default_marker_preset

		# Stack for toggling between "new preset" name editor & controls, vs "update existing" controls
		self.stack_name_editor = QtWidgets.QStackedWidget()
		self.stack_page_addnew = QtWidgets.QWidget()
		self.stack_page_update = QtWidgets.QWidget()

		# Stack for saving or setting (the ones near the bottom left)
		self.stack_save_set = QtWidgets.QStackedWidget()
		self.stack_page_set_as   = QtWidgets.QWidget()
		
		self.cmb_marker_presets = markers_trt.LBMarkerPresetComboBox()
		self.txt_preset_name = QtWidgets.QLineEdit()
		self.vld_preset_name = markers_trt.LBMarkerPresetNameValidator() # NOTE: Used for save button

		self.btn_save_preset = QtWidgets.QPushButton()	# Update existing preset
		self.btn_duplicate_preset = QtWidgets.QPushButton()
		self.btn_delete_preset = QtWidgets.QPushButton()

		self.btn_set_as_ffoa = QtWidgets.QPushButton()
		self.btn_set_as_lfoa = QtWidgets.QPushButton()

		self.cmb_marker_color = QtWidgets.QComboBox()
		self.txt_marker_comment = QtWidgets.QLineEdit()
		self.txt_marker_author  = QtWidgets.QLineEdit()
		self.btn_box = QtWidgets.QDialogButtonBox()

		self._setupWidgets()
		self._setupSignals()
	
		self.setMinimumWidth(500)
		self.setFixedHeight(self.sizeHint().height())

		self.setEditingMode(self.EditingMode.EDIT_EXISTING)
 
		#self.btn_box.button(QtWidgets.QDialogButtonBox.StandardButton.Close).setDefault(True)

	def _setupWidgets(self):

		lay_presets = QtWidgets.QHBoxLayout()
		lay_presets.addWidget(self.cmb_marker_presets)

		# New Preset Name Editor & Controls
		self.stack_page_addnew.setLayout(QtWidgets.QHBoxLayout())
		self.stack_page_addnew.layout().setContentsMargins(0,0,0,0)
		
		self.txt_preset_name.setMaxLength(16)
		self.txt_preset_name.setValidator(self.vld_preset_name)
		self.txt_preset_name.setPlaceholderText("Marker Preset Name")

		self.stack_page_addnew.layout().addWidget(self.txt_preset_name)

		self.stack_name_editor.addWidget(self.stack_page_addnew)

		# Update Existing Preset Controls
		self.stack_page_update.setLayout(QtWidgets.QHBoxLayout())
		self.stack_page_update.layout().setContentsMargins(0,0,0,0)

		self.btn_save_preset.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentSave))
		self.btn_save_preset.setText("Save")
		self.btn_save_preset.setToolTip("Save Preset")
		self.btn_save_preset.setShortcut(QtGui.QKeySequence.StandardKey.Save)

		self.btn_duplicate_preset.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditCopy))
		self.btn_duplicate_preset.setText("Duplicate")
		self.btn_duplicate_preset.setToolTip("Duplicate Preset")
		self.btn_duplicate_preset.setShortcut(QtGui.QKeySequence(QtGui.Qt.KeyboardModifier.ControlModifier| QtGui.Qt.Key.Key_D))

		self.btn_delete_preset.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove))
		self.btn_delete_preset.setText("Delete")
		self.btn_delete_preset.setToolTip("Delete Preset")

		self.stack_page_update.layout().addStretch()
		self.stack_page_update.layout().addWidget(self.btn_duplicate_preset)
		self.stack_page_update.layout().addWidget(self.btn_delete_preset)

		self.stack_name_editor.addWidget(self.stack_page_update)

		# Foof!  Add stacked widget and the rest to the master layout
		lay_presets.addWidget(self.stack_name_editor)
		self.layout().addLayout(lay_presets)


		# Match criteria editor

		self.grp_edit = QtWidgets.QGroupBox()
		self.grp_edit.setLayout(QtWidgets.QGridLayout())

		self.grp_edit.layout().addWidget(QtWidgets.QLabel("Match Color"), 0, 0)
		self.grp_edit.layout().addWidget(self.cmb_marker_color, 1, 0)

		self.grp_edit.layout().addWidget(QtWidgets.QLabel("Comment Contains"), 0, 1)
		self.txt_marker_comment.setPlaceholderText("(Any)")
		self.grp_edit.layout().addWidget(self.txt_marker_comment, 1,1)

		self.grp_edit.layout().addWidget(QtWidgets.QLabel("Author Contains"), 0, 2)
		self.txt_marker_author.setPlaceholderText("(Any)")
		self.grp_edit.layout().addWidget(self.txt_marker_author, 1, 2)

		self.layout().addWidget(self.grp_edit)

		
		# Lower left Save 'n' Set
		lay_btns = QtWidgets.QHBoxLayout()

		self.stack_page_set_as.setLayout(QtWidgets.QHBoxLayout())
		self.stack_page_set_as.layout().setContentsMargins(0,0,0,0)

		self.btn_set_as_ffoa.setText("Use For FFOA")
		self.btn_set_as_ffoa.setToolTip("Use this preset to match FFOA markers")
		self.btn_set_as_ffoa.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.CallStart))

		self.btn_set_as_lfoa.setText("Use For LFOA")
		self.btn_set_as_lfoa.setToolTip("Use this preset to match LFOA markers")
		self.btn_set_as_lfoa.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.CallStop))

		self.stack_page_set_as.layout().addWidget(self.btn_set_as_ffoa)
		self.stack_page_set_as.layout().addWidget(self.btn_set_as_lfoa)

		self.stack_save_set.addWidget(self.btn_save_preset)
		self.stack_save_set.addWidget(self.stack_page_set_as)
		
		lay_btns.addWidget(self.stack_save_set)
		
		self.btn_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Close)
		lay_btns.addWidget(self.btn_box)

		self.layout().addLayout(lay_btns)
		self.btn_box.button(QtWidgets.QDialogButtonBox.StandardButton.Close).setDefault(True)

	def _setupSignals(self):

		# Combo box things
		self.cmb_marker_presets.sig_marker_preset_changed.connect(self.editPresetRequested)
		self.cmb_marker_presets.sig_marker_preset_editor_requested.connect(self.createPresetRequested)

		# Preset buttons
		self.btn_save_preset.clicked.connect(self.savePresetRequested)
		self.btn_delete_preset.clicked.connect(lambda: self.sig_delete_preset.emit(self.cmb_marker_presets.currentText()))
		self.btn_duplicate_preset.clicked.connect(self.duplicatePresetRequested)

		# Set selected preset as...
		self.btn_set_as_ffoa.clicked.connect(lambda: self.sig_set_as_ffoa.emit(self.cmb_marker_presets.currentText()))
		self.btn_set_as_lfoa.clicked.connect(lambda: self.sig_set_as_lfoa.emit(self.cmb_marker_presets.currentText()))
		
		self.txt_preset_name.textChanged.connect(self.presetNameInputChanged)
		self.cmb_marker_color.currentIndexChanged.connect(self.criteriaInputChanged)
		self.txt_marker_comment.textChanged.connect(self.criteriaInputChanged)
		self.txt_marker_author.textChanged.connect(self.criteriaInputChanged)

		# Dialog close button signals `reject``, I guess
		self.btn_box.rejected.connect(self.reject)

#	---
#	Window stuff
#	---
	@QtCore.Slot()
	def reject(self):
		"""Window has been asked to close"""
		
		#if not self.switchPresetsAllowed():
		#	return
		
		return super().reject()
	

#	---
#	Basic getters/setters
#	---
	def defaultMarkerPresetName(self) -> str:
		return self._default_preset_name

	def defaultMarkerPreset(self) -> markers_trt.LBMarkerPreset:
		"""Default criteria for a new/blank marker match criteria preset"""

		return self._default_marker_preset
	
	def setCurrentMarkerPreset(self, preset:markers_trt.LBMarkerPreset):
		self._current_marker_preset = preset

	def currentMarkerPreset(self) -> markers_trt.LBMarkerPreset:
		return self._current_marker_preset
	
	@QtCore.Slot()
	def buildMarkerPresetFromCurrent(self) -> markers_trt.LBMarkerPreset:
		"""Create a marker preset from the current settings"""

		return markers_trt.LBMarkerPreset(
			color   = self.cmb_marker_color.currentData(),	# None indicates "Any" marker
			comment = self.txt_marker_comment.text() or None,
			author  = self.txt_marker_author.text() or None
		)
	
#	---
#	Actual quote-unquote "data model" stuff
#	---
	def addMarkerColor(self, marker:markers_trt.LBMarkerIcon):
		"""Add marker color to marker color combo box"""
		self.cmb_marker_color.addItem(marker, marker.name() or "(Any)", marker.name() or None)
		self.cmb_marker_color.update()

	@QtCore.Slot(dict)
	def setMarkerPresets(self, marker_presets:dict[str, markers_trt.LBMarkerPreset]):
		"""Set the marker presets model"""

		self._marker_presets = marker_presets
		self.cmb_marker_presets.setMarkerPresets(self._marker_presets)
		self.update_completers()

		if self.txt_preset_name.text() in self._marker_presets:
			self.editPresetRequested(self.txt_preset_name.text())
		elif self._marker_presets:
			self.editPresetRequested(self.cmb_marker_presets.itemText(0))
		else:
			self.createPresetRequested()


#	---
#	UI Handlers
#	---
	@QtCore.Slot()
	def createPresetRequested(self):
		"""User requested new preset"""

		#if not self.switchPresetsAllowed():
		#	return
		
		
		self.setEditingMode(self.EditingMode.CREATE_NEW)
		self.setCriteriaEditorData(preset_name=self.getUniquePresetName(self.defaultMarkerPresetName()), preset_info=self.defaultMarkerPreset())

	@QtCore.Slot()
	def duplicatePresetRequested(self):
		"""Duplicate the current marker match preset"""

		#if not self.switchPresetsAllowed():
		#	return

		preset_name = self.txt_preset_name.text() or None
		preset_info = self.buildMarkerPresetFromCurrent()
		

		self.setEditingMode(self.EditingMode.CREATE_NEW)
		self.setCriteriaEditorData(preset_name=self.getUniquePresetName(preset_name), preset_info=preset_info)

	@QtCore.Slot(str)
	def editPresetRequested(self, marker_preset_name:str):
		"""Allow user to edit the criteria for a particular marker preset name"""

		#if not self.switchPresetsAllowed():
		#	return
		
		self.setEditingMode(self.EditingMode.EDIT_EXISTING)

		try:
			marker_preset = self._marker_presets[marker_preset_name]
		except Exception as e:
			raise ValueError("Marker preset doesn't exist: ", str(marker_preset_name)) from e

		self.setCriteriaEditorData(preset_name=marker_preset_name, preset_info=marker_preset)

	def savePresetRequested(self):
		"""Save the current preset"""

		self.setIsDirty(False)
		self.sig_save_preset.emit(self.txt_preset_name.text(), self.buildMarkerPresetFromCurrent())


#	---
#	Criteria editing stuff
#	---
	@QtCore.Slot()
	def setCriteriaEditorData(self, preset_name:str|None=None, preset_info:markers_trt.LBMarkerPreset|None=None):
		"""Load new or existing criteria data into the widgets"""

		self.setCurrentMarkerPreset(preset_info)
		self.cmb_marker_presets.setCurrentMarkerPresetName(preset_name)

		self.txt_preset_name.setText(preset_name)
		#self.txt_preset_name.setVisible(True)
		
		self.cmb_marker_color.setCurrentText(preset_info.color or "(Any)")
		self.txt_marker_comment.setText(preset_info.comment)
		self.txt_marker_author.setText(preset_info.author)


	
#	---
#	Input validators & processors
#	---
	@QtCore.Slot(str)
	def presetNameInputChanged(self, preset_name:str):
		"""User is typing the preset name"""

		if preset_name in self._marker_presets:
			self.setSaveButtonDescription(self.EditingMode.EDIT_EXISTING)
		else:
			self.setSaveButtonDescription(self.EditingMode.CREATE_NEW)
		
		# Note: Could also just call `.validate` here and have `QValidator.changed` connected to the button enabled..ness...
		# But this seems find lol I dunno
		self.btn_save_preset.setEnabled(all([
			self.vld_preset_name.validate(preset_name, len(preset_name)) is self.vld_preset_name.State.Acceptable,
			#preset_name != self._default_preset_name,
			#preset_name not in self._marker_presets
		]))

	def update_completers(self):
		"""Build autocomplete data for text inputs based on existing marker match criteria presets"""

		completer_comments = QtWidgets.QCompleter(sorted(set([m.comment for m in self._marker_presets.values() if m.comment is not None])))
		completer_comments.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
		completer_comments.setCompletionMode(QtWidgets.QCompleter.CompletionMode.UnfilteredPopupCompletion)

		completer_authors = QtWidgets.QCompleter(sorted(set([m.author for m in self._marker_presets.values() if m.author is not None])))
		completer_authors.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
		completer_authors.setCompletionMode(QtWidgets.QCompleter.CompletionMode.UnfilteredPopupCompletion)

		self.txt_marker_comment.setCompleter(completer_comments)
		self.txt_marker_author.setCompleter(completer_authors)

	def getUniquePresetName(self, name:str|None=None) -> str:
		"""If a marker match preset already exists, make it unique"""

		return make_unique_name(name if name is not None else self._default_preset_name, list(self._marker_presets.keys()))

	
#	---
#	State tracking
#	---

	def setEditingMode(self, mode:EditingMode):
		"""Set the mode of the criteria editor (create new, or existing...)"""

		#if mode is self._editing_mode:
		#	return
		
		self._editing_mode = mode
		
		self.setSaveButtonDescription(mode)

		if mode is self.EditingMode.EDIT_EXISTING:
			# Set button to "Update" verbage
			
			# Show "Update" tool stack
			self.stack_name_editor.setCurrentWidget(self.stack_page_update)
			#self.txt_preset_name.setVisible(False)
			
			# Start off with no modifications
			self.setIsDirty(False)
		
		elif mode is self.EditingMode.CREATE_NEW:
			# Set button to "Save New" verbage

			# Show Preset Name Textbox
			self.stack_name_editor.setCurrentWidget(self.stack_page_addnew)
		
			# Select preset name box
			self.txt_preset_name.selectAll()
			self.txt_preset_name.setFocus()
			
			# Start off as "dirty" ;)
			self.setIsDirty(True)

	
	def editingMode(self) -> EditingMode:
		"""The current editing mode"""
		return self._editing_mode
	

	def setSaveButtonDescription(self, mode:EditingMode):
		"""Set the Save Button verbiage depending on mode"""

		if mode is self.EditingMode.CREATE_NEW:
			self.btn_save_preset.setText("Create New Preset")
			self.btn_save_preset.setToolTip("Save Criteria As New Preset")
			self.btn_save_preset.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentNew))
		
		elif mode is self.EditingMode.EDIT_EXISTING:
			self.btn_save_preset.setText("Update Preset Criteria")
			self.btn_save_preset.setToolTip("Update Existing Preset Criteria")
			self.btn_save_preset.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentSave))	
		
		else:
			# Yeah I dunno
			pass
	
	@QtCore.Slot()
	def criteriaInputChanged(self):
		"""Somebody typed somethin"""
		
		# CREATE_NEW should always be dirty
		criteria_is_modified = self.editingMode() is self.EditingMode.CREATE_NEW or self.isPresetCriteriaModified()
		self.setIsDirty(criteria_is_modified)
	
	def isPresetCriteriaModified(self) -> bool:
		"""Compare the user input data against what was initially set"""

		marker_preset = self.currentMarkerPreset()

		if not marker_preset:
			return True#?

		return any([
			self.cmb_marker_color.currentData() != marker_preset.color,
			(self.txt_marker_comment.text() or None) != marker_preset.comment,
			(self.txt_marker_author.text() or None) != marker_preset.author
		])
	
	@QtCore.Slot(bool)
	def setIsDirty(self, is_dirty:bool):
		"""Set as a dirty form"""

		#if self._is_dirty == is_dirty:
		#	return
		
		self._is_dirty = bool(is_dirty)
		self.setWindowModified(is_dirty)
		
		
		if is_dirty:
			self.stack_save_set.setCurrentWidget(self.btn_save_preset)
		else:
			self.stack_save_set.setCurrentWidget(self.stack_page_set_as)

		self.btn_save_preset.setDefault(is_dirty)
		self.btn_box.button(QtWidgets.QDialogButtonBox.StandardButton.Close).setDefault(not is_dirty)
	
	def isDirty(self) -> bool:
		"""Is the form dirty"""
		return self._is_dirty
	
	def switchPresetsAllowed(self) -> bool:
		"""If it's cool to switch to editing another marker preset criteria"""
		if not self.isDirty():
		#	print("Ain't dirty")
			return True
		
		#print("Deemed dirty (dd)")
		
		btn_chosen = QtWidgets.QMessageBox.warning(self, "Current Preset Not Saved", "You have unsaved changes to the current preset.", buttons=QtWidgets.QMessageBox.StandardButton.Discard|QtWidgets.QMessageBox.StandardButton.Cancel)

		if btn_chosen  == QtWidgets.QMessageBox.StandardButton.Cancel:
			return False
		
		elif btn_chosen  == QtWidgets.QMessageBox.StandardButton.Save:
			self.savePresetRequested()
		
		return True
