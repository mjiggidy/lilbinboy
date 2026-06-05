from __future__ import annotations
from PySide6 import QtCore, QtGui, QtWidgets

from ..core import grid
from ..utils import stylewatcher


class BSFrameItemBrushManager(QtCore.QObject):
	"""Pens, brushes and fonts for frame items"""

	def __init__(self, parent:QtCore.QObject, *args, **kwargs):

		super().__init__(parent=parent, *args, **kwargs)

		self._watcher_style = stylewatcher.BSWidgetStyleEventFilter(parent=self)

		self._palette = parent.palette() \
		  if isinstance(parent, QtWidgets.QWidget) \
		  else QtWidgets.QApplication.palette()

		self.font_label     = parent.font() \
		  if isinstance(parent, QtWidgets.QWidget) \
		  else QtGui.QFont()
		
		self.font_metrics   = QtGui.QFontMetricsF(self.font_label)
		self.options_label  = QtGui.QTextOption()
		
		self.pen_none       = QtGui.QPen()
		self.pen_label      = QtGui.QPen()
		self.pen_base       = QtGui.QPen()
		self.pen_selected   = QtGui.QPen()
		self.pen_clip_color = QtGui.QPen()

		self.brush_none     = QtGui.QBrush()
		self.brush_base     = QtGui.QBrush()
		self.brush_thumb    = QtGui.QBrush()
		self.brush_selected = QtGui.QBrush()

		# Initial setup

		# TODO: Testing for linux
		self.font_label     .setHintingPreference(QtGui.QFont.HintingPreference.PreferFullHinting)
		self.font_label     .setKerning(True)

		self.options_label  .setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignTop)
		self.options_label  .setUseDesignMetrics(True)
		self.options_label  .setWrapMode(QtGui.QTextOption.WrapMode.NoWrap)

		self.brush_base     .setStyle(QtCore.Qt.BrushStyle.SolidPattern)
		self.brush_thumb    .setStyle(QtCore.Qt.BrushStyle.SolidPattern)
		self.brush_selected .setStyle(QtCore.Qt.BrushStyle.SolidPattern)
		
		self.pen_none       .setStyle(QtCore.Qt.PenStyle.NoPen)
		
		self.pen_label      .setCosmetic(True)
		
		self.pen_base       .setStyle(QtCore.Qt.PenStyle.SolidLine)
		self.pen_base       .setCosmetic(True)
		self.pen_base       .setWidthF(1)
		
		self.pen_selected   .setStyle(QtCore.Qt.PenStyle.SolidLine)
		self.pen_selected   .setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
		self.pen_selected   .setCosmetic(True)
		self.pen_selected   .setWidthF(1)

		self.pen_clip_color .setStyle(QtCore.Qt.PenStyle.SolidLine)
		self.pen_clip_color .setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
		self.pen_clip_color .setCosmetic(True)
		self.pen_clip_color .setWidthF(4)

		parent.installEventFilter(self._watcher_style)
		self._watcher_style.sig_font_changed.connect(self.setFont)
		self._watcher_style.sig_palette_changed.connect(self.setPalette)

		# Complete setup
		self.setFont(self.font_label)
		self.setPalette(self._palette)

	@QtCore.Slot(QtGui.QPalette)
	def setPalette(self, palette:QtGui.QPalette):

		color_base = palette.shadow().color()
		color_base.setAlphaF(0.5)
		self.brush_base.setColor(color_base)

		color_thumb = palette.dark().color()
		self.brush_thumb.setColor(color_thumb)

		color_label = palette.windowText().color()
		self.pen_label.setColor(color_label)

		color_selected = palette.highlight().color()
		color_selected.setAlphaF(0.5)
		self.brush_selected.setColor(color_selected)

		color_selected = palette.highlightedText().color()
		self.pen_selected.setColor(color_selected)

		color_default = palette.windowText().color()
		self.pen_base.setColor(color_default)

	@QtCore.Slot(QtGui.QFont)
	def setFont(self, font:QtGui.QFont):

		self.font_label = font
		self.font_label.setPointSizeF(1.25)
		self.font_label.setKerning(True)
		#self.font_label.setHintingPreference(QtGui.QFont.HintingPreference.PreferFullHinting)
		
		# A value of 100 will keep the spacing unchanged; a value of 200 will 
		# enlarge the spacing after a character by the width of the character itself.
		# https://doc.qt.io/qtforpython-6/PySide6/QtGui/QFont.html#PySide6.QtGui.QFont.SpacingType
		#self.font_label.setLetterSpacing(QtGui.QFont.SpacingType.PercentageSpacing, 90)

		temp_font = QtGui.QFont(self.font_label)
		temp_font.setBold(True)
		self.font_metrics = QtGui.QFontMetricsF(temp_font)

class BSBinFrameBackgroundPainter(QtCore.QObject):
	"""Draw the background grid on a frame view"""
	
	sig_enabled_changed          = QtCore.Signal(bool)
	sig_active_grid_unit_changed = QtCore.Signal(object)
	sig_visible_tick_info_changed= QtCore.Signal(object)

	def __init__(self,
		parent:QtWidgets.QWidget,
		*args,
		tick_info:dict[QtCore.Qt.Orientation, list[grid.BSGridTickInfo]]|None=None,
		tick_width_major:float=3,
		tick_width_minor:float=1.5,
		**kwargs
	):

		super().__init__(parent, *args, **kwargs)

		self._is_enabled = True

		self._visible_tick_info = tick_info or dict()

		self._active_grid_unit = QtCore.QRectF()
		"""Rect for highlighting a particular cell"""
		
		self._watcher_style   = stylewatcher.BSWidgetStyleEventFilter(parent=self)
		parent.installEventFilter(self._watcher_style)

		self._pen_nopen         = QtGui.QPen()
		self._pen_tick_major    = QtGui.QPen()
		self._pen_tick_minor    = QtGui.QPen()

		self._brush_active_grid = QtGui.QBrush()

		self._pen_nopen.setStyle(QtCore.Qt.PenStyle.NoPen)

		self._pen_tick_major.setStyle(QtCore.Qt.PenStyle.SolidLine)
		self._pen_tick_major.setCosmetic(True)
		self.setMajorTickWidth(tick_width_major)

		self._pen_tick_minor.setStyle(QtCore.Qt.PenStyle.DashLine)
		self._pen_tick_minor.setCosmetic(True)
		self.setMinorTickWidth(tick_width_minor)

		self._brush_active_grid.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		self.setPalette(parent.palette())
		self._watcher_style.sig_palette_changed.connect(self.setPalette)

	@QtCore.Slot(bool)
	def setEnabled(self, is_enabled):

		if self._is_enabled == is_enabled:
			return
		
		self._is_enabled = is_enabled
		self.sig_enabled_changed.emit(is_enabled)
	
	def isEnabled(self) -> bool:
		return self._is_enabled

	@QtCore.Slot(QtGui.QPalette)
	def setPalette(self, palette:QtGui.QPalette):

#		logging.getLogger(__name__).debug("Setting palette...")

		self._pen_tick_major.setColor(palette.alternateBase().color())
		self._pen_tick_minor.setColor(palette.alternateBase().color())
		
		active_grid_unit_color = palette.accent().color()
		active_grid_unit_color.setAlphaF(0.1)
		self._brush_active_grid.setColor(active_grid_unit_color)

	@QtCore.Slot(object)
	def setVisibleTickInfo(self, visible_tick_info:dict[QtCore.Qt.Orientation, list[grid.BSGridTickInfo]]):

		if self._visible_tick_info == visible_tick_info:
			return
		
		self._visible_tick_info = visible_tick_info
		self.sig_visible_tick_info_changed.emit(visible_tick_info)

	@QtCore.Slot()
	@QtCore.Slot(QtCore.QPointF)
	def setActiveGridUnit(self, grid_unit:QtCore.QRectF|None=None):

		if self._active_grid_unit == grid_unit:
			return

		self._active_grid_unit = grid_unit
			
		self.sig_active_grid_unit_changed.emit(grid_unit)

	@QtCore.Slot(int)
	@QtCore.Slot(float)
	def setMajorTickWidth(self, tick_width_major:float):

		self._pen_tick_major.setWidthF(float(tick_width_major))

	@QtCore.Slot(int)
	@QtCore.Slot(float)
	def setMinorTickWidth(self, tick_width_minor:float):

		self._pen_tick_minor.setWidthF(float(tick_width_minor))

	def drawBackground(self, painter:QtGui.QPainter, rect_scene:QtCore.QRectF):

		painter.save()

		if self._is_enabled:
			
			self._draw_horizontal_grid(painter, rect_scene)
			self._draw_vertical_grid(painter, rect_scene)

		if self._active_grid_unit:
			self._draw_active_grid_unit(painter, rect_scene)

		painter.restore()

	def _draw_horizontal_grid(self, painter:QtGui.QPainter, rect_scene:QtCore.QRectF):
		
		for tick in self._visible_tick_info.get(QtCore.Qt.Orientation.Horizontal, []):

			x_pos = tick.scene_offset

			painter.setPen(self._pen_tick_major if tick.tick_type == grid.BSGridTickType.MAJOR else self._pen_tick_minor)

			painter.drawLine(QtCore.QLineF(
				QtCore.QPointF(x_pos, rect_scene.top()),
				QtCore.QPointF(x_pos, rect_scene.bottom())
			))

	def _draw_vertical_grid(self, painter:QtGui.QPainter, rect_scene:QtCore.QRectF):

		# Vertical
		# Align to grid divisions
		for tick in self._visible_tick_info.get(QtCore.Qt.Orientation.Vertical, []):

			y_pos = tick.scene_offset

			painter.setPen(self._pen_tick_major if tick.tick_type == grid.BSGridTickType.MAJOR else self._pen_tick_minor)

			painter.drawLine(QtCore.QLineF(
				QtCore.QPointF(rect_scene.left(), y_pos),
				QtCore.QPointF(rect_scene.right(), y_pos)
			))
	
	def _draw_active_grid_unit(self, painter:QtGui.QPainter, rect_scene:QtCore.QRectF):

		painter.setPen(self._pen_nopen)
		painter.setBrush(self._brush_active_grid)

		painter.drawRect(self._active_grid_unit)