import dataclasses, re
import avbutils
from PySide6 import QtCore, QtGui, QtWidgets

class LBMarkerIcons:

	ICONS:dict[str, "LBMarkerIcon"] = {}

	def __init__(self):

		for color in avbutils.MarkerColors:
			self.ICONS.update({color.value: LBMarkerIcon(color.value)})
	
	def __iter__(self):
		return iter(self.ICONS.values())

@dataclasses.dataclass()
class LBMarkerPreset:
	"""Marker criteria presets"""

	color: "LBMarkerIcon | None"
	comment: str | None
	author:  str | None

class LBMarkerPresetNameValidator(QtGui.QValidator):
	"""Validate marker preset names"""

	pat_valid_preset_name = re.compile("^[a-z0-9\-_](?:[a-z0-9\-_ ]*[a-z0-9\-_])?$", re.I)

	@QtCore.Slot(str, int)
	def validate(self, preset_name:str, pos:int) -> QtGui.QValidator.State:

		if self.pat_valid_preset_name.match(preset_name):
			return QtGui.QValidator.State.Acceptable
		
		elif self.pat_valid_preset_name.match(preset_name.strip()) or not preset_name:
			return QtGui.QValidator.State.Intermediate
		
		else:
			return QtGui.QValidator.State.Invalid

class LBMarkerIcon(QtGui.QIcon):
	
	def __init__(self, color:str|None):

		super().__init__()

		self._name = color
		self._color = QtGui.QColor().fromString(color)

		self.addPixmap(self._create_pixmap())
	
	def color(self) -> QtGui.QColor:
		return self._color
	
	def name(self) -> str:
		return self._name
	
	def _create_pixmap(self):
		pixmap = QtGui.QPixmap(32, 32)
		pixmap.fill(QtGui.QColor(0,0,0,0))

		painter = QtGui.QPainter(pixmap)
		painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

		pen = QtGui.QPen()
		pen.setWidth(3)
		pen.setColor(self.color().darker(300))
		painter.setPen(pen)
		
		brush = QtGui.QBrush(self.color())
		painter.setBrush(brush)

		painter.drawRoundedRect(QtCore.QRect(5, 2, pixmap.rect().height()/2, pixmap.rect().height()-4), 75, 50, QtGui.Qt.SizeMode.RelativeSize)
		painter.end()

		return pixmap
	
class LBMarkerPresetComboBox(QtWidgets.QComboBox):

	sig_marker_preset_editor_requested = QtCore.Signal()
	"""Request the editor"""

	sig_marker_preset_changed = QtCore.Signal(str)
	
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._last_selected_preset_name = None
		self._allow_edit_option = True

		self.currentIndexChanged.connect(self.processSelection)

	def setAllowEditOption(self, allow_editing:bool):
		self._allow_edit_option = bool(allow_editing)
	
	def allowEditOption(self) -> bool:
		return self._allow_edit_option
	
	@QtCore.Slot(dict)
	def setMarkerPresets(self, marker_presets:dict[str, LBMarkerPreset]):
		"""Set marker presets list from marker model (external signals blocked)"""

		self.blockSignals(True)
		
		self.clear()

		# Add presets; storing actual preset as userdata basically only for tooltip creation I guess
		for preset_name, preset_data in marker_presets.items():
			self.addItem(LBMarkerIcon(preset_data.color), preset_name, preset_data)

		# Add edit option if it's there
		if self.allowEditOption():
			if marker_presets:
				self.insertSeparator(len(marker_presets))
			self.addItem(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd), "Add/Edit...", None)

		# Once presets are updated, we need to figure out what to select.
		# If nothing was selected previously (marker presets were empty initially), select the top of the list if now there are markers
		# If there still are no markers, select... nothing? TODO
		if not self._last_selected_preset_name:
			if marker_presets:
				self._last_selected_preset_name = self.itemText(0)
			else:
				self._last_selected_preset_name = None

		self.setCurrentIndex(self.findText(self._last_selected_preset_name) if self._last_selected_preset_name else 0)

		self.blockSignals(False)

	
	@QtCore.Slot(int)
	def processSelection(self, index:int):
		"""Validate and process the pickins"""

		# If new selection contains a marker preset, store its preset name and notify the peoples
		if self.currentData() is not None:
			self._last_selected_preset_name = self.currentText()
			self.updateToolTip()
			self.sig_marker_preset_changed.emit(self._last_selected_preset_name)

		# If new selection does not contain a preset (Add/Edit Option), and it wasn't previously selected, request the editor
		elif self.allowEditOption():
# TEMP		self.setCurrentIndex(self.findText(self._last_selected_preset_name))
			self.sig_marker_preset_editor_requested.emit()
			
			# TODO: Then return to last?? I think?
			#self.setCurrentText(self._last_selected_preset_name)
		
	@QtCore.Slot(str)
	def setCurrentMarkerPresetName(self, marker_preset:str|None):
		
		idx = self.findText(marker_preset)
		if marker_preset is None or self.findText(marker_preset) < 0: # findText() returns -1 if not found
			self.setCurrentIndex(self.count()-1)
		else:
			self.setCurrentText(marker_preset)

	def currentMarkerPresetName(self) -> str:

		return self.currentText() if self.currentData() else None

	@QtCore.Slot()
	def updateToolTip(self):

		marker_preset = self.currentData()
		
		if marker_preset is None:
			return "No Marker Preset Chosen"
		
		else:
			return "Color: {color}; Comment: {comment}; Author: {author}".format(
				color = marker_preset.color or "(Any)",
				comment = ("\"" + marker_preset.comment + "\"") if marker_preset.comment else "(Any)",
				author = ("\"" + marker_preset.author + "\"") if marker_preset.author else "(Any)",
			)