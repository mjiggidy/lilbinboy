import dataclasses
import avbutils
from PySide6 import QtCore, QtGui

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