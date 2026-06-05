import logging
from os import PathLike
from PySide6 import QtCore, QtGui, QtSvg
from ..utils import drawing

class BSAbstractPalettedIconEngine(QtGui.QIconEngine):
	"""Abstract icon engine that supports dynamic colors from a `QtGui.QPalette`"""

	def __init__(self, *args, palette:QtGui.QPalette|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._palette = QtGui.QPalette(palette or QtGui.QGuiApplication.palette())
		self._cache:dict[int,QtGui.QPixmap] = dict()

	def setPalette(self, palette:QtGui.QPalette):
		self._palette = palette
	
	def palette(self) -> QtGui.QPalette:
		return self._palette
	
	def addPixmap(self, pixmap:QtGui.QPixmap, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State):

		h = self._makeHash(pixmap.size(), mode, state)
		self._cache[h] = pixmap

	def pixmap(self, size, mode, state):
		"""Get pixmap from cache, or paint it and cache it"""

		# Pull from cache
		h = self._makeHash(size, mode, state)
		if h in self._cache:
			return self._cache[h]
		
		# Or draw new one
		logging.getLogger(__name__).debug("Drawing new icon for size=%s, mode=%s, state=%s (hash=%s)", size, mode, state, h)
		pixmap = QtGui.QPixmap(size)
		pixmap.fill(QtCore.Qt.GlobalColor.transparent)
		
		self.paint(QtGui.QPainter(pixmap), pixmap.rect(), mode, state)
		self.addPixmap(pixmap, mode, state)
		return pixmap
	
	def _makeHash(self, size:QtCore.QSize, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State) -> int:
		""""""

		return hash((
			size,
			mode,
			state,
			self._palette.cacheKey()
		))
	
class BSPalettedClipColorIconEngine(BSAbstractPalettedIconEngine):
	"""A clip color chip icon engine with customizable clip color"""

	def __init__(self, clip_color:QtGui.QColor, *args, border_width:int=1, **kwargs):

		super().__init__(*args, **kwargs)

		self._clip_color   = clip_color
		self._border_width = border_width

	def paint(self, painter:QtGui.QPainter, rect:QtCore.QRect, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State):
		
		drawing.draw_clip_color_chip(
			painter      = painter,
			canvas       = rect,
			clip_color   = self._clip_color,
			border_width = self._border_width,
			border_color = self._palette.brightText().color() if mode == QtGui.QIcon.Mode.Selected else self._palette.buttonText().color(),
			shadow_color = self._palette.shadow().color(),
		)

	def clone(self) -> "BSPalettedClipColorIconEngine":
		
		logging.getLogger(__name__).debug("I do be clonin haha look")
		return self.__class__(self._clip_color, border_width=self._border_width)
	
class BSPalettedMarkerIconEngine(BSAbstractPalettedIconEngine):
	"""A marker icon engine with customizable marker color"""

	def __init__(self, marker_color:QtGui.QColor, *args, border_width:int=1, **kwargs):

		super().__init__(*args, **kwargs)

		self._marker_color   = marker_color
		self._border_width = border_width

	def paint(self, painter:QtGui.QPainter, rect:QtCore.QRect, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State):

		active_rect = rect.adjusted(10,3,-10,-3)

		
		drawing.draw_marker_tick(
			painter      = painter,
			canvas       = active_rect,
			marker_color = self._marker_color,
			border_color = self._palette.brightText().color() if mode == QtGui.QIcon.Mode.Selected else self._palette.buttonText().color(),
			border_width = self._border_width,
			#border_color = self._palette.windowText().color(),
			#shadow_color = self._palette.shadow().color(),
		)
	
	def pixmap(self, size, mode, state):
		return super().pixmap(size, mode, state)

	def clone(self) -> "BSPalettedClipColorIconEngine":
		
		logging.getLogger(__name__).debug("I do be clonin haha look")
		return self.__class__(self._marker_color, border_width=self._border_width)

class BSPalettedSvgIconEngine(BSAbstractPalettedIconEngine):
	"""An SVG icon engine with support for `QPalette` color replacements"""
	
	def __init__(self, svg_path:PathLike, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._svg_path     = svg_path
		self._svg_template = self._svgStringFromPath(svg_path)

		self._renderer     = QtSvg.QSvgRenderer()
		self._palette_dict = self._paletteToDict(self._palette)

		self._renderer.setAspectRatioMode(QtCore.Qt.AspectRatioMode.KeepAspectRatioByExpanding)
		#self._svg_template = bytes(QtCore.QResource(svg_path).uncompressedData().data()).decode("utf-8")
	
	def clone(self) -> "BSPalettedSvgIconEngine":
		logging.getLogger(__name__).debug("I do be clonin haha look")
		return self.__class__(self._svg_path)
	
	def paint(self, painter:QtGui.QPainter, rect:QtCore.QRect, mode:QtGui.QIcon.Mode, state:QtGui.QIcon.State):
		
		# NOTE: Loads during setPalette now.  Assume it's better performance.
		#  BUT: Probably need this back here to deal with current mode/state?
		#self._palette.setCurrentColorGroup(QtGui.QPalette.ColorGroup.Inactive if mode == QtGui.QPalette.ColorGroup.Inactive else QtGui.QPalette.ColorGroup.Active)
		
		if mode == QtGui.QIcon.Mode.Selected:
			self._palette_dict["ButtonText"] = self._palette.brightText().color().name()
		elif state == QtGui.QIcon.State.On:
			self._palette_dict["ButtonText"] = self._palette.accent().color().name()
		else:
			self._palette_dict["ButtonText"] = self._palette.buttonText().color().name()
		
		self._renderer.load(self._svg_template.format_map(self._palette_dict).encode("utf-8"))
		self._renderer.render(painter, rect)
	
	def setPalette(self, palette:QtGui.QPalette):

		super().setPalette(palette)
		self._palette_dict = self._paletteToDict(self._palette)
		#self._palette_dict = self._paletteToDict(palette)

		# Moved here from paint()
		#self._renderer.load(self._svg_template.format_map(self._palette_dict).encode("utf-8"))

	@staticmethod
	def _paletteToDict(palette:QtGui.QPalette) -> dict[str,str]:

		# NOTE: NColorRoles causes a periodic segfault that was JUST RUINING MY LIFE for a long time there
		# Paraphrasing QPalette docs: "color role int should be less than NColorRoles" so I guess it's more of a sentinel
		return {role.name: palette.color(role).name() for role in QtGui.QPalette.ColorRole if role.name != "NColorRoles"}
	
	@staticmethod
	def _svgStringFromPath(svg_path:PathLike) -> str:

		f = QtCore.QFile(svg_path)
		
		if not f.open(QtCore.QFile.OpenModeFlag.ReadOnly):
			raise IOError(f"Cannot open {svg_path}: {f.errorString()}")
		
		try:
			svg_string = f.readAll().toStdString()
		finally:
			f.close()
		
		return svg_string
