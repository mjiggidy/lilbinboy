from __future__ import annotations
import typing, logging
from PySide6 import QtCore, QtGui, QtWidgets

from ..core import grid

from ..core.config import BSFrameViewModeConfig
from ..utils import gestures
from ..overlays import framemap, frameruler, manager

from . import gridsnapper, painters
from .framescene import BSBinFrameScene
from .actions import BSFrameViewActions

DEFAULT_FRAME_VIEW_MARGINS = QtCore.QMarginsF(
	BSFrameViewModeConfig.GRID_UNIT_SIZE.width(),
	BSFrameViewModeConfig.GRID_UNIT_SIZE.height(),
	BSFrameViewModeConfig.GRID_UNIT_SIZE.width(),
	BSFrameViewModeConfig.GRID_UNIT_SIZE.height(),
)


class BSBinFrameView(QtWidgets.QGraphicsView):
	"""Frame view for an Avid bin"""

	sig_zoom_level_changed        = QtCore.Signal(int)
	sig_zoom_range_changed        = QtCore.Signal(object)
	sig_overlay_manager_changed   = QtCore.Signal(object)
	sig_view_rect_changed         = QtCore.Signal(object)
	sig_scene_rect_changed        = QtCore.Signal(object)
	sig_scene_margins_changed     = QtCore.Signal(object)
	sig_scene_changed             = QtCore.Signal(object)
	sig_visible_tick_info_updated = QtCore.Signal(object) # dict

	def __init__(self, *args, frame_scene:BSBinFrameScene|None=None, margins:QtCore.QMarginsF|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		# QGraphics init
		self.setInteractive(True)
		self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)
		self.setAcceptDrops(False)
		self.setViewportUpdateMode(QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
		self.setOptimizationFlags(
			QtWidgets.QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing |
			QtWidgets.QGraphicsView.OptimizationFlag.DontSavePainterState
		)

		# Scrollbar init
		self.setVerticalScrollBarPolicy  (QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self.setCornerWidget(QtWidgets.QSizeGrip(self))

		self._current_zoom       = 1.0
		self._zoom_range         = range(100)
		self._grid_info          = grid.BSGridSystemInfo(unit_size=BSFrameViewModeConfig.GRID_UNIT_SIZE, unit_divisions=BSFrameViewModeConfig.GRID_DIVISIONS)
		self._scene_rect_margins = margins or DEFAULT_FRAME_VIEW_MARGINS
		
		self._visible_tick_info:dict[QtCore.Qt.AlignmentFlag, list[grid.BSGridTickInfo]]  = {
			QtCore.Qt.Orientation.Horizontal: [],
			QtCore.Qt.Orientation.Vertical:   [],
			
		}

		self._anim_zoom_adjust   = QtCore.QPropertyAnimation(parent=self)
		self._timer_cursor_reset = QtCore.QTimer()

		# Zoomer
		self._anim_zoom_adjust.setTargetObject(self)
		self._anim_zoom_adjust.setPropertyName(QtCore.QByteArray.fromStdString("raw_zoom"))
		self._anim_zoom_adjust.setDuration(300) #ms
		self._anim_zoom_adjust.setEasingCurve(QtCore.QEasingCurve.Type.OutExpo)

		# Cursor Resetter
		self._timer_cursor_reset.setInterval(1_000)  # ms
		self._timer_cursor_reset.setSingleShot(True)

		# Actions
		self._actions = BSFrameViewActions(self)

		# Background Painter
		# NOTE: Watches the QGraphicsView for palette changes (`parent=self`), NOT the viewport().
		# Viewport doesn't fire paletteChange events here.  Dunno. Maybe a TODO in disguise lol
		self._background_painter = painters.BSBinFrameBackgroundPainter(parent=self, tick_info=self._visible_tick_info)
		self._item_brushes       = painters.BSFrameItemBrushManager(parent=self)
		self._grid_snapper       = gridsnapper.BSFrameGridSnapper(frame_view=self)

		# Doers of things
		# NOTE: Most of these fellers install themselves as eventFilters, enable mouse tracking on the widget, etc
		self._overlay_manager    = manager.BSGraphicsOverlayManager(parent=self.viewport())
		self._overlay_ruler      = frameruler.BSFrameRulerOverlay()
		self._overlay_map        = framemap.BSThumbnailMapOverlay()

		self._pinchy_boy         = gestures.BSPinchEventFilter(parent=self.viewport())
		self._pan_man            = gestures.BSPanEventFilter(parent=self.viewport())
		self._wheelzoom          = gestures.BSWheelZoomEventFilter(parent=self.viewport(), modifier_keys=QtCore.Qt.KeyboardModifier.AltModifier)

		self._overlay_map.setThumbnailOffset(self.viewport().rect().topRight())

		self._overlay_map._setEnabled(False)
		self._overlay_ruler._setEnabled(False)
		self._background_painter.setEnabled(False)

		self._overlay_manager.installOverlay(self._overlay_ruler)
		self._overlay_manager.installOverlay(self._overlay_map)

		# Actions

		self.addActions(self._actions.navigationActions().actions())
		self.addActions(self._actions.overlayActions().actions())
		
		self._actions.act_zoom_in.triggered         .connect(lambda: self.zoomIncrement())
		self._actions.act_zoom_out.triggered        .connect(lambda: self.zoomDecrement())
		
		# Action to Overlay
		self._actions.act_toggle_ruler.toggled      .connect(self._overlay_ruler._setEnabled)
		self._actions.act_toggle_map.toggled        .connect(self._overlay_map._setEnabled)
		self._actions.act_toggle_grid.toggled       .connect(self._background_painter.setEnabled)

		# Overlay to Action
		self._overlay_map.sig_enabled_changed       .connect(self._actions.act_toggle_map.setChecked)
		self._overlay_ruler.sig_enabled_changed     .connect(self._actions.act_toggle_ruler.setChecked)
		self._background_painter.sig_enabled_changed.connect(self._actions.act_toggle_grid.setChecked)
		self._background_painter.sig_enabled_changed.connect(self._grid_snapper.setEnabled)

		self._grid_snapper.sig_active_grid_unit_changed.connect(self.setActiveGridUnit)
		self._grid_snapper.sig_active_grid_unit_chosen .connect(self.snapSelectedToGridUnit)

		# Manager signals
		
		self._overlay_map.sig_view_reticle_panned   .connect(self.centerOn)
		self._background_painter.sig_enabled_changed.connect(self.viewport().update)

		self._pan_man.sig_user_pan_started          .connect(self.beginPan)
		self._pan_man.sig_user_pan_moved            .connect(self.panViewByDelta)
		self._pan_man.sig_user_pan_finished         .connect(self.finishPan)

		self._pinchy_boy.sig_user_pinch_started     .connect(self._anim_zoom_adjust.stop)
		self._pinchy_boy.sig_user_pinch_moved       .connect(self.zoomViewByDelta)
		self._pinchy_boy.sig_user_pinch_finished    .connect(self.userFinishedPinch)

		self._wheelzoom.sig_user_zoomed             .connect(self.zoomByWheel)
		self._timer_cursor_reset.timeout            .connect(self.unsetCursor)

		# Misc signals

		self.horizontalScrollBar().valueChanged     .connect(self.processViewRectChanges)
		self.verticalScrollBar().valueChanged       .connect(self.processViewRectChanges)

		

	@QtCore.Slot(QtCore.QPointF)
	def snapSelectedToGridUnit(self, unit_coordinates:QtCore.QPointF):
		"""Snap the current selection to a given coordinate"""

		if not self.scene().mouseGrabberItem():
			return
		
		delta_coords = unit_coordinates - self.scene().mouseGrabberItem().scenePos()
		
		for item in self.scene().selectedItems():

			item.moveBy(delta_coords.x(), delta_coords.y())

	@QtCore.Slot()
	@QtCore.Slot(QtCore.QPointF)
	def setActiveGridUnit(self, unit_coordinates:QtCore.QPointF|None=None):
		"""Set the currently-active grid unit for snappings to gridsings"""

		if not self.scene().mouseGrabberItem():
			return

		self._background_painter.setActiveGridUnit(QtCore.QRectF(unit_coordinates, self._grid_info.unit_size) if unit_coordinates is not None else None)
		self.viewport().update()

	def actions(self) -> BSFrameViewActions:
		"""Get the actions manager for the frame view"""

		return self._actions

	def setScene(self, scene:BSBinFrameScene):
		"""Override of `super().setScene()` with signals and cool stuff"""

		if self.scene() == scene:
			return

		if self.scene():
			self.scene().disconnect(self)

		scene.changed.connect(self.processActiveSceneRectChanges)
		#self.sceneRect.connect(lambda: self._overlay_map.setSceneRect)
		#scene.sig_bin_item_added.connect(self.updateThumbnails)

		super().setScene(scene)
#		self.setSceneRect(
#			scene.itemsBoundingRect().marginsAdded(DEFAULT_FRAME_VIEW_MARGINS)
#		)
		self.sig_scene_changed.emit(scene)

	@QtCore.Slot()
	def processActiveSceneRectChanges(self):
		"""
		Update stuff with the latest active scene rect.
		"Active" as in "the part of the scene we can scroll around in" rather 
		than "visible rect" being the part currently drawn in the viewport
		"""
		
		# Base the active scene rect on the item bounding box, plus margins
		padded_scene_rect = self.scene().itemsBoundingRect().marginsAdded(DEFAULT_FRAME_VIEW_MARGINS)

		if self.sceneRect() == padded_scene_rect:
			return
		
		self.setSceneRect(padded_scene_rect)

		self.updateBinMap()

		self.sig_scene_rect_changed.emit(padded_scene_rect)

	@QtCore.Slot()
	def processViewRectChanges(self):
		"""Do necessary updates when user pans/zooms"""

		self.updateVisibleGridTicks()

		self.updateBinMap()

		self.sig_view_rect_changed.emit(self.visibleSceneRect())

	def setTransform(self, matrix:QtGui.QTransform, *args, combine:bool=False, **kwargs) -> None:

		super().setTransform(matrix, combine)
		self.processViewRectChanges()

	def activeSceneRectMargins(self) -> QtCore.QMarginsF:

		return self._scene_rect_margins
	
	@QtCore.Slot(QtCore.QMarginsF)
	def setActiveSceneRectMargins(self, margins:QtCore.QRectF):

		if self._scene_rect_margins == margins:
			return
		
		self._scene_rect_margins = margins
		self.sig_scene_margins_changed.emit(margins)
		self.scene().update(self.visibleSceneRect())


	def overlayManager(self) -> manager.BSGraphicsOverlayManager:

		return self._overlay_manager

	@QtCore.Slot(object)
	def setOverlayManager(self, overlay_manager:manager.BSGraphicsOverlayManager):

		if self._overlay_manager != overlay_manager:

			self._overlay_manager = overlay_manager
			self.sig_overlay_manager_changed.emit(overlay_manager)


	def scene(self) -> BSBinFrameScene:
		# Just for type hints
		return super().scene()

	@QtCore.Slot(int, QtCore.Qt.Orientation)
	def zoomByWheel(self, zoom_delta:int, orientation:QtCore.Qt.Orientation):

		if zoom_delta > 0:
			self.zoomIncrement(1)
		elif zoom_delta < 0:
			self.zoomIncrement(-1)
		else:
			logging.getLogger(__name__).debug("Ignored weird 0-delta zoom")

	@QtCore.Slot()
	@QtCore.Slot(int)
	def zoomIncrement(self, zoom_step:int=1):

		zoom_step += self._current_zoom

		self.setZoom(
			max(
				self._zoom_range.start,
				min(
					zoom_step,
					self._zoom_range.stop
				)
			)
		)

	@QtCore.Slot()
	@QtCore.Slot(int)
	def zoomDecrement(self, zoom_step:int=1):

		return self.zoomIncrement(-zoom_step)

	@QtCore.Slot()
	def beginPan(self):

		self._timer_cursor_reset.stop()
		self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)

	@QtCore.Slot(QtCore.QPoint)
	def panViewByDelta(self, pan_delta:QtCore.QPoint):

		self._timer_cursor_reset.stop()
		self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - pan_delta.x())
		self.verticalScrollBar()  .setValue(self.verticalScrollBar()  .value() - pan_delta.y())

	@QtCore.Slot()
	def finishPan(self):

		self._timer_cursor_reset.start()
		self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)

	@QtCore.Slot(float)
	def zoomViewByDelta(self, zoom_delta:float):

		zoom_delta += 1
		new_zoom = self._current_zoom * (zoom_delta)

		# Allow overshoot
		ZOOM_RANGE_OVERSHOOT = range(self._zoom_range.start-1, self._zoom_range.stop +1)
		padded_zoom = max(
			ZOOM_RANGE_OVERSHOOT.start,
			min(
				new_zoom,
				ZOOM_RANGE_OVERSHOOT.stop
			)
		)

		self.setZoom(padded_zoom)

	@QtCore.Slot()
	def userFinishedPinch(self):

		start_val = self._current_zoom
		end_val = max(self._zoom_range.start, min(round(self._current_zoom), self._zoom_range.stop))

		if start_val == end_val:
			#print("EXACT")
			return

		self._anim_zoom_adjust.stop()
		self._anim_zoom_adjust.setStartValue(start_val)
		self._anim_zoom_adjust.setEndValue(end_val)
		self._anim_zoom_adjust.start()

	@QtCore.Slot(object)
	def setZoomRange(self, zoom_range:range):

		if self._zoom_range != zoom_range:
			self._zoom_range = zoom_range
			self.sig_zoom_range_changed.emit(zoom_range)

	def zoomRange(self) -> range:
		return self._zoom_range

	@QtCore.Property(float)
	def raw_zoom(self) -> float:

		return self._current_zoom

	@raw_zoom.setter
	def raw_zoom(self, raw_zoom:float):

		#print(raw_zoom)

		if raw_zoom != self._current_zoom:
			self._current_zoom = raw_zoom

			t = QtGui.QTransform()
			t.scale(raw_zoom, raw_zoom)
			self.setTransform(t)

			self.sig_zoom_level_changed.emit(raw_zoom)

	@QtCore.Slot(int)
	@QtCore.Slot(float)
	def setZoom(self, zoom_level:int|float):

		if zoom_level != self._current_zoom:

			zoom_level = float(zoom_level) #/ float(4)
			self._current_zoom = zoom_level

			t = QtGui.QTransform()
			t.scale(zoom_level, zoom_level)
			self.setTransform(t)

			self.sig_zoom_level_changed.emit(zoom_level)

			self.processViewRectChanges()

	def visibleGridTicks(self, orientation:QtCore.Qt.Orientation) -> list[grid.BSGridTickInfo]:
		"""Grid ticks visible in the current view"""

		return self._visible_tick_info.get(orientation, [])

	def updateVisibleGridTicks(self, rect_scene:QtCore.QRect|None=None, tick_orientations:typing.Iterable[QtCore.Qt.Orientation]|None=None):
		"""Update grid ticks visible in the viewport"""

		rect_scene        = rect_scene or self.visibleSceneRect()
		tick_orientations = tick_orientations or [QtCore.Qt.Orientation.Horizontal, QtCore.Qt.Orientation.Vertical]

		# NOTE:  See Background drawing code for better coordinate alignment, gonna wanna roll that all in 

		if QtCore.Qt.Orientation.Horizontal in tick_orientations:

			# Align to grid divisions
			range_scene_start = self._grid_info.snapToGrid(rect_scene.topLeft()).x() - self._grid_info.unit_size.width()
			range_scene_end   = self._grid_info.snapToGrid(rect_scene.topRight()).x() + self._grid_info.unit_size.width()

			range_scene_steps = round((range_scene_end - range_scene_start) / self._grid_info.unit_step.x())

			ticks = []

			for step in range(range_scene_steps):

				scene_x    = range_scene_start + (step * self._grid_info.unit_step.x())
				viewport_x = self.mapFromScene(scene_x, 0).x()

				ticks.append(
					grid.BSGridTickInfo(
						local_offset = viewport_x,
						scene_offset = scene_x,
						tick_label   = str(round(scene_x)),
						tick_type    = grid.BSGridTickType.MAJOR \
						  if not step % self._grid_info.unit_divisions.x()
						  else grid.BSGridTickType.MINOR
					)
				)

			self._visible_tick_info[QtCore.Qt.Orientation.Horizontal] = ticks
			self._background_painter.setVisibleTickInfo(self._visible_tick_info)
			self._overlay_ruler.setTicks(ticks, QtCore.Qt.Orientation.Horizontal)

		if QtCore.Qt.Orientation.Vertical in tick_orientations:

			# Align to grid divisions
			range_scene_start = self._grid_info.snapToGrid(rect_scene.topLeft()).y() - self._grid_info.unit_size.height()
			range_scene_end   = self._grid_info.snapToGrid(rect_scene.bottomLeft()).y() + self._grid_info.unit_size.height()
			
			range_scene_steps = round((range_scene_end - range_scene_start) / self._grid_info.unit_step.y())

			ticks = []

			for step in range(round(range_scene_steps)):

				scene_y    = range_scene_start + (step * self._grid_info.unit_step.y())
				viewport_y = self.mapFromScene(0, scene_y).y()

				ticks.append(
					grid.BSGridTickInfo(
						local_offset  = viewport_y,
						scene_offset  = scene_y,
						tick_label    = str(round(scene_y)),
						tick_type     = grid.BSGridTickType.MAJOR \
						  if not step % self._grid_info.unit_divisions.y()
						  else grid.BSGridTickType.MINOR
					)
				)

			self._visible_tick_info[QtCore.Qt.Orientation.Vertical] = ticks
			self._overlay_ruler.setTicks(ticks, QtCore.Qt.Orientation.Vertical)

			self.sig_visible_tick_info_updated.emit(self._visible_tick_info)
	
	def updateBinMap(self):
		"""Update scene rect, reticle and """

		visible_scene_rect = self.visibleSceneRect()
		padded_scene_rect  = self.sceneRect()

		bin_map_rect = QtCore.QRectF(
			QtCore.QPointF(
				min(visible_scene_rect.left(), padded_scene_rect.left()),
				min(visible_scene_rect.top(), padded_scene_rect.top()),
			),
			QtCore.QPointF(
				max(visible_scene_rect.right(), padded_scene_rect.right()),
				max(visible_scene_rect.bottom(), padded_scene_rect.bottom()),
			)
		)


		# NOTE: Started getting errors at exit here, setting rect when scene is None.
		# Investigate root cause.  For now, ignore lol
		if not self.scene():
			return

		if self._overlay_map.sceneRect() != bin_map_rect:
			self._overlay_map.setSceneRect(bin_map_rect)
			self._overlay_map.setThumbnailRects([item.sceneBoundingRect() for item in self.scene().items()])
		
		if self._overlay_map.viewReticle() != visible_scene_rect:
			self._overlay_map.setViewReticle(visible_scene_rect)
			

	def visibleSceneRect(self) -> QtCore.QRectF:
		"""The portion of the scene rect viewable in the viewport"""

		return QtCore.QRectF(
			self.mapToScene(self.viewport().rect().topLeft()),
			self.mapToScene(self.viewport().rect().bottomRight()),
		)

	def drawBackground(self, painter:QtGui.QPainter, rect:QtCore.QRectF):

		super().drawBackground(painter, rect)

		self._background_painter.drawBackground(painter, rect)

#	def drawForeground(self, painter, rect):
		#  NOTE Just because I keep forgetting and trying it: drawForeground is not suitable for
		#  drawing overlays because the painter is scaled to scene coords and it's a whole thing.

	def drawOverlays(self, painter:QtGui.QPainter, rect:QtCore.QRectF):

		self._overlay_manager.paintOverlays(painter, self.viewport().rect())

	def paintEvent(self, event):
		"""Paint widget, then overlays"""

		super().paintEvent(event)

		painter = QtGui.QPainter(self.viewport())
		try:
			self.drawOverlays(painter, self.viewport().rect())
		except Exception as e:
			logging.getLogger(__name__).error("Error drawing overlays: %s", e)
		finally:
			painter.end()

	def resizeEvent(self, event):

		self.processViewRectChanges()
		return super().resizeEvent(event)
	
	def mousePressEvent(self, event:QtGui.QMouseEvent):

		if event.buttons() & QtCore.Qt.MouseButton.LeftButton:
			
			# Handle super() first so items are selected
			ret = super().mousePressEvent(event)
			self.scene().raiseItemsToTop(self.scene().selectedItems())
			return ret
		
		return super().mousePressEvent(event)