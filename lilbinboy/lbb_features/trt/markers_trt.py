import dataclasses
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
	
	def setMarkerPresets(self, marker_presets:dict[str, LBMarkerPreset]):

		self.clear()

		for preset_name, preset_data in marker_presets.items():
			self.addItem(LBMarkerIcon(preset_data.color), preset_name, preset_data)

		# Add edit option if it's there
		if self.allowEditOption():
			self.insertSeparator(len(marker_presets))
			self.addItem("Add/Edit...")

		self.setCurrentIndex(self.findData(self._last_selected_preset_name))
	
	@QtCore.Slot(int)
	def processSelection(self, index:int):
		"""Validate and process the pickins"""

		if self.currentData() is not None:
			self._last_selected_preset_name = self.currentData()
			self.updateToolTip()
			self.sig_marker_preset_changed.emit(self._last_selected_preset_name)

		# If None (Edit selected), and it wasn't before, put the selection back to the previously-selected marker and request the editor
		# I think this'll solve some recursive dialog boxes that do be happenin
		elif self._last_selected_preset_name is not None and self.allowEditOption():
			self.setCurrentIndex(self.findData(self._last_selected_preset_name))
			self.sig_marker_preset_editor_requested.emit()

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