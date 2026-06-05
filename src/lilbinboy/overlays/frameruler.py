from __future__ import annotations
import typing
from PySide6 import QtCore, QtGui

from . import abstractoverlay

from ..core import grid

DEFAULT_RULER_WIDTH         = 24   # px
DEFAULT_RULER_OUTLINE_WIDTH = 1    # px
DEFAULT_FANCY_ALPHA         = 0.75 # %
DEFAULT_FONT_SCALE          = 0.7  # %
DEFAULT_RULER_POSITION      = QtCore.QPointF(0,0)
USE_ANTIALIASING            = False
DEFAULT_TICK_SIZE           = 3    # px

DEFAULT_TICK_TYPES          = set((grid.BSGridTickType.MAJOR,))

class BSFrameRulerOverlay(abstractoverlay.BSAbstractOverlay):
	"""Ruler displayed over widget"""

	sig_ruler_width_changed          = QtCore.Signal(int)
	sig_ruler_ticks_changed          = QtCore.Signal(object)
	sig_ruler_orientations_changed   = QtCore.Signal(object)
	sig_ruler_position_changed       = QtCore.Signal(object)
	sig_mouse_coords_changed         = QtCore.Signal(object)
	sig_show_mouse_coords_changed    = QtCore.Signal(bool)

	def __init__(self, *args, ruler_width:int=DEFAULT_RULER_WIDTH, **kwargs):
		
		super().__init__(*args, **kwargs)

		self._ruler_position         = DEFAULT_RULER_POSITION
		self._ruler_stoke_width      = DEFAULT_RULER_OUTLINE_WIDTH
		self._ruler_width            = ruler_width
		self._ruler_tick_size        = DEFAULT_TICK_SIZE
		self._font_ruler_ticks_scale = DEFAULT_FONT_SCALE
		self._tick_types             = DEFAULT_TICK_TYPES
		
		self._ruler_ticks:dict[QtCore.Qt.Orientation, list[grid.BSGridTickInfo]] = {
			QtCore.Qt.Orientation.Horizontal: set(),
			QtCore.Qt.Orientation.Vertical:   set(),
		}

		self._ruler_orientations = set([
			QtCore.Qt.Orientation.Horizontal,
			QtCore.Qt.Orientation.Vertical
		])

		self._last_mouse_coords      = QtCore.QPointF(500,500)
		self._mouse_coords_enabled   = True
		self._mouse_drag_start       = QtCore.QPointF()

		# Pens
		self._pen_ruler_base    = QtGui.QPen()

		self._pen_ruler_base.setStyle(QtCore.Qt.PenStyle.SolidLine)
		self._pen_ruler_base.setCapStyle(QtCore.Qt.PenCapStyle.SquareCap)
		self._pen_ruler_base.setJoinStyle(QtCore.Qt.PenJoinStyle.BevelJoin)

		self._pen_ruler_ticks        = QtGui.QPen(self._pen_ruler_base)
		self._pen_mouse_coords       = QtGui.QPen(self._pen_ruler_base)

		# Brushes
		self._brush_ruler_base       = QtGui.QLinearGradient()

		# Fonts
		self._font_mouse_coords      = self.font()
		self._font_ruler_ticks       = self.font()

		self.setupDrawingTools()

	@QtCore.Slot(bool)
	def _setEnabled(self, is_enabled:bool):
		"""Refresh drawing tools in re-enabled (probably missed PaletteChange events)"""

		if is_enabled == True:
			self.setupDrawingTools()
		
		super()._setEnabled(is_enabled)

	@QtCore.Slot(object)
	def setMouseCoordinates(self, mouse_coordinates:QtCore.QPoint|QtCore.QPointF):
		"""Set the local mouse coordinates relative to the topLeft of the widget rect"""

		if self._last_mouse_coords != mouse_coordinates:

			self._last_mouse_coords = mouse_coordinates
			self.sig_mouse_coords_changed.emit(mouse_coordinates)

			# NOTE: Can do this more efficently, and should
			for new_rect in self.activeRects(self.rect()):
				self.update(new_rect)
	
	def mouseCoordinates(self) -> QtCore.QPoint|QtCore.QPointF:
		"""Last known mouse coordinates relative to the topLeft of the widget rect"""

		return self._last_mouse_coords

	@QtCore.Slot(bool)
	def setMouseCoordsEnabled(self, coords_enabled:bool):
		"""Enable live mouse coordinates to be drawn"""

		if self._mouse_coords_enabled != coords_enabled:

			self._mouse_coords_enabled = coords_enabled
			self.sig_show_mouse_coords_changed.emit(coords_enabled)

	def mouseCoordsEnabled(self) -> bool:
		"""Mouse coordinates are enabled to be drawn"""

		return self._mouse_coords_enabled

	
	@QtCore.Slot(object)
	def setRulerPosition(self, ruler_position:QtCore.QPoint|QtCore.QPointF):
		"""Set the offset of the ruler relative to the topLeft of the widget rect"""

		for old_rect in self.activeRects(self.rect()):
			self.update(old_rect)

		if self._ruler_position != ruler_position:
			
			self._ruler_position = ruler_position
			self.sig_ruler_position_changed.emit(ruler_position)
			
			for new_rect in self.activeRects(self.rect()):
				self.update(new_rect)

	def rulerPosition(self) -> QtCore.QPoint|QtCore.QPointF:
		"""The offset of the ruler relative to the topLeft of the widget rect"""

		return self._ruler_position


	@QtCore.Slot(object)
	def setRulerOrientations(self, orientations:typing.Iterable[QtCore.Qt.Orientation]):
		"""Set ruler display orientations"""

		orientations = set(orientations)

		for old_rect in self.activeRects(self.rect()):
			self.update(old_rect)

		if self._ruler_orientations != orientations:
			
			self._ruler_orientations = orientations
			self.sig_ruler_orientations_changed.emit(orientations)
			
			for new_rect in self.activeRects(self.rect()):
				self.update(new_rect)
	
	def rulerOrientations(self) -> set[QtCore.Qt.Orientation]:
		"""Ruler orientations displayed"""

		return set(self._ruler_orientations)
	
	@QtCore.Slot(object)
	def setTicks(self, ruler_ticks:typing.Iterable[grid.BSGridTickInfo], orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal):

		self._ruler_ticks[orientation] = set(ruler_ticks)
		self.sig_ruler_ticks_changed.emit(ruler_ticks)
		
		self.update(self.rulerRect(self.rect(), orientation))
	
	def ticks(self, orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal) -> list[grid.BSGridTickInfo]:

		return list(self._ruler_orientations[orientation])

	@QtCore.Slot()
	def setupDrawingTools(self):
		"""Setup pens, brushes and fonts"""

		self._pen_ruler_base  .setColor(self.palette().dark().color())
		self._pen_ruler_base  .setWidth(self._ruler_stoke_width)

		# Light mode?
		if self.palette().window().color().value() > self.palette().windowText().color().value():
			kewl_color = self.palette().button().color().lighter(105)
		else:
			kewl_color = self.palette().button().color().darker(105)
		kewl_color.setAlphaF(DEFAULT_FANCY_ALPHA)

		self._brush_ruler_base.setColorAt(0.0, self.palette().light() .color())
		self._brush_ruler_base.setColorAt(0.1, self.palette().button().color().darker(110))
		self._brush_ruler_base.setColorAt(0.5, self.palette().button().color())
		self._brush_ruler_base.setColorAt(0.9, kewl_color)
		self._brush_ruler_base.setColorAt(1.0, self.palette().dark()  .color())

		self._pen_ruler_ticks .setColor(self.palette().buttonText().color())
		self._pen_ruler_ticks .setWidth(self._ruler_stoke_width)

		tick_font = self.font()
		tick_font.setPointSizeF(tick_font.pointSizeF() * self._font_ruler_ticks_scale)
		self._font_ruler_ticks = tick_font

	def rulerWidth(self) -> int:
		"""Size of the ruler"""

		return self._ruler_width
	
	@QtCore.Slot(int)
	def setRulerWidth(self, ruler_width:int):

		if ruler_width != self._ruler_width:

			for old_rect in self.activeRects(self.rect()):
				self.update(old_rect)

			self._ruler_width = ruler_width
			self.sig_ruler_width_changed.emit(ruler_width)
			
			for new_rect in self.activeRects(self.rect()):
				self.update(new_rect)

	def _dragIsActive(self) -> bool:
		"""User is currently dragging"""

		return not self._mouse_drag_start.isNull()

	def paintOverlay(self, painter, rect_canvas):
		"""Do the paint"""

		painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, USE_ANTIALIASING)

		for orientation in self._ruler_orientations:

			painter.save()

			self._draw_ruler_base(painter, rect_canvas, orientation)
			self._draw_ruler_ticks(painter, rect_canvas, orientation)
			
			if self._mouse_coords_enabled:
				self._draw_mouse_coords(painter, rect_canvas)

			self._draw_ruler_handle(painter, rect_canvas)

			painter.restore()
	
	def _draw_mouse_coords(self, painter:QtGui.QPainter, rect_canvas:QtGui.QRectF):

		painter.save()

		painter.setPen(self._pen_mouse_coords)

		mouse_coords_local = self._last_mouse_coords

		if QtCore.Qt.Orientation.Horizontal in self._ruler_orientations:

			rect_rule = self.rulerRect(rect_canvas, QtCore.Qt.Orientation.Horizontal)
			painter.setClipRect(rect_rule)

			painter.drawLine(QtCore.QLineF(
				QtCore.QPointF(mouse_coords_local.x(), rect_rule.topLeft().y()),
				QtCore.QPointF(mouse_coords_local.x(), rect_rule.bottomLeft().y()),
			))
		

		if QtCore.Qt.Orientation.Vertical in self._ruler_orientations:

			rect_rule = self.rulerRect(rect_canvas, QtCore.Qt.Orientation.Vertical)
			painter.setClipRect(rect_rule)

			painter.drawLine(QtCore.QLineF(
				QtCore.QPointF(rect_rule.topLeft().x(), mouse_coords_local.y()),
				QtCore.QPointF(rect_rule.topRight().x(), mouse_coords_local.y()),
			))	

		painter.restore()

	def _draw_ruler_handle(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRectF):

		painter.save()

		painter.setPen(self._pen_ruler_base)

		rect_handle = self.handleRect(rect_canvas)

		# Draw background

		grad = QtGui.QLinearGradient(self._brush_ruler_base)
		grad.setStart(rect_handle.topLeft())
		grad.setFinalStop(rect_handle.bottomLeft())
		painter.setBrush(grad)

		#rect_handle.translate(self._ruler_position)
#		rect_handle.adjust(
#			-self._ruler_stoke_width/2,
#			-self._ruler_stoke_width/2,
#			-self._ruler_stoke_width/2,
#			-self._ruler_stoke_width/2,
#		)

		painter.drawRect(rect_handle)

		# Draw button (inverted gradient)

		pen = painter.pen()

		pen.setWidthF(pen.widthF() * 2)
		pen.setCapStyle(QtCore.Qt.PenCapStyle.RoundCap)
		pen.setJoinStyle(QtCore.Qt.PenJoinStyle.RoundJoin)
		
		col = pen.color()
		col.setAlphaF(0.5)
		pen.setColor(col)
		
		painter.setPen(pen)
		
		if not self._dragIsActive():
			grad.setStart(rect_handle.bottomLeft())
			grad.setFinalStop(rect_handle.topLeft())
			painter.setBrush(grad)

		rect_handle.adjust(
			 self._ruler_stoke_width * 2,
			 self._ruler_stoke_width * 2,
			-self._ruler_stoke_width * 2,
			-self._ruler_stoke_width * 2,
		)

		painter.drawRect(rect_handle)


		painter.restore()
	
	def _draw_ruler_base(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRectF, orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal):

		painter.save()

		ruler_rect = self.rulerRect(rect_canvas, orientation)
		
		if orientation == QtCore.Qt.Orientation.Horizontal:
			
			grad = QtGui.QLinearGradient(self._brush_ruler_base)
			grad.setStart(ruler_rect.topLeft())
			grad.setFinalStop(ruler_rect.bottomLeft())

		elif orientation == QtCore.Qt.Orientation.Vertical:
			
			grad = QtGui.QLinearGradient(self._brush_ruler_base)
			grad.setStart(ruler_rect.topLeft())
			grad.setFinalStop(ruler_rect.topRight())
			

		painter.setBrush(grad)
		painter.setPen(self._pen_ruler_base)
		painter.drawRect(ruler_rect)

		painter.restore()

	def _draw_ruler_ticks(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRectF, orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal):

		painter.save()
		
		ruler_rect  = self.rulerRect(rect_canvas, orientation)
		painter.setClipRect(ruler_rect)
		
		painter.setPen(self._pen_ruler_ticks)
		painter.setFont(self._font_ruler_ticks)

		for tick_info in filter(lambda t: t.tick_type in self._tick_types, self._ruler_ticks[orientation]):
			
			tick_lines = []

			if orientation == QtCore.Qt.Orientation.Horizontal:
				
				# Bottom Ticks
				if ruler_rect.bottom() < self.rect().bottom():

					tick_lines.append(QtCore.QLineF(
						QtCore.QPointF(tick_info.local_offset, ruler_rect.bottom() - self._ruler_tick_size),
						QtCore.QPointF(tick_info.local_offset, ruler_rect.bottom())
					))

				# Top Ticks
				if ruler_rect.top() > self.rect().top():
					
					tick_lines.append(QtCore.QLineF(
						QtCore.QPointF(tick_info.local_offset, ruler_rect.top() + self._ruler_tick_size),
						QtCore.QPointF(tick_info.local_offset, ruler_rect.top())
					))

				tick_text = QtCore.QRectF(
					ruler_rect.topLeft(),
					ruler_rect.size()
				)

				tick_text.moveCenter(QtCore.QPoint(tick_info.local_offset, ruler_rect.center().y()))

			elif orientation == QtCore.Qt.Orientation.Vertical:

				# Right ticks
				if ruler_rect.right() < self.rect().right():

					tick_lines.append(QtCore.QLineF(
						QtCore.QPointF(ruler_rect.right() - self._ruler_tick_size, tick_info.local_offset),
						QtCore.QPointF(ruler_rect.right(), tick_info.local_offset)
					))

				# Left ticks
				if ruler_rect.left() > self.rect().left():
					#print(ruler_rect.left(), self.rect().left())
					tick_lines.append(QtCore.QLineF(
						QtCore.QPointF(ruler_rect.left() + self._ruler_tick_size, tick_info.local_offset),
						QtCore.QPointF(ruler_rect.left(), tick_info.local_offset)
					))

				tick_text = QtCore.QRectF(
					ruler_rect.topLeft(),
					ruler_rect.size()
				)
				tick_text.moveCenter(QtCore.QPoint(ruler_rect.center().x(), tick_info.local_offset))

			for line_tick in tick_lines:
				painter.drawLine(line_tick)

			painter.drawText( 
				tick_text,
				QtCore.Qt.AlignmentFlag.AlignCenter,
				tick_info.tick_label
			)

		painter.restore()

	def activeRects(self, rect_canvas:QtCore.QRect|QtCore.QRectF) -> list[QtCore.QRect|QtCore.QRectF]:
		
		rects = []

		for orientation in self._ruler_orientations:
			rects.append(self.rulerRect(rect_canvas, orientation))
		rects.append(self.handleRect(rect_canvas))

		return rects
	
	def safePosition(self, test_point:QtCore.QRect|QtCore.QRectF, rect_canvas:QtCore.QRect|QtCore.QRectF):
		"""Determine the nearest "safe" position for the ruler, ensuring the handle rect is visible"""

		handle_rect = self.handleRect(rect_canvas)

		return QtCore.QPointF(
			max(rect_canvas.topLeft().x(), min(test_point.x(), rect_canvas.width() - handle_rect.width())),
			max(rect_canvas.topLeft().y(), min(test_point.y(), rect_canvas.height() - handle_rect.height())),
		)

	def handleRect(self, rect_canvas:QtCore.QRect|QtCore.QRectF) -> QtCore.QRectF:
		"""Rect represending the handle"""

		return QtCore.QRectF(
			self._ruler_position,
			QtCore.QSizeF(self._ruler_width, self._ruler_width)
		)
	
	def rulerRect(self, rect_canvas:QtCore.QRectF, orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal) -> QtCore.QRectF:
		"""Given a viewport rect, get a rect of the current ruler area"""

		ruler_rect = QtCore.QRectF(rect_canvas)

		if orientation == QtCore.Qt.Orientation.Vertical:

			ruler_rect.setWidth(self._ruler_width)
#			ruler_rect.adjust(
#				-self._ruler_stoke_width/2,
#				-self._ruler_stoke_width/2,
#				-self._ruler_stoke_width/2,
#				-self._ruler_stoke_width/2,
#			)

			ruler_rect.translate(self._ruler_position.x(), 0)
		
		elif orientation == QtCore.Qt.Orientation.Horizontal:	

			ruler_rect.setHeight(self._ruler_width)
#			ruler_rect.adjust(
#				self._ruler_stoke_width/2,
#				self._ruler_stoke_width/2,
#				-self._ruler_stoke_width/2,
#				-self._ruler_stoke_width/2,
#			)
			ruler_rect.translate(0, self._ruler_position.y())

		return ruler_rect
	
	def beginUserDragHandle(self, drag_start_position:QtCore.QPointF) -> bool:
		
		self._mouse_drag_start = drag_start_position - self.handleRect(self.rect()).topLeft()
		self.update(self.handleRect(self.rect()))

		return True
	
	def updateUserDragHandle(self, drag_update_position:QtCore.QPointF) -> bool:

		if not self._dragIsActive():
			return False
		
		# Mouse position relative to drag start, for proper offset from handle
		mouse_rel = drag_update_position - self._mouse_drag_start

		pos = self.safePosition(
			mouse_rel, self.rect()
		)

		# setRulerPosition calls update()
		self.setRulerPosition(pos)

		return True
	
	def endUserDragHandle(self) -> bool:

		self._mouse_drag_start = QtCore.QPointF()
		self.update(self.handleRect(self.rect()))
		return True

	def keepHandleVisible(self, rect_scene:QtCore.QRect|QtCore.QRectF):
		
		handle_rect = self.handleRect(rect_scene)

		if not rect_scene.contains(handle_rect.bottomRight().toPoint()):
			self.setRulerPosition(
				self.safePosition(handle_rect.topLeft(), rect_scene)
			)


	def event(self, event):
		if event.type() == QtCore.QEvent.Type.MouseButtonPress and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
			
			if self.handleRect(self.rect()).contains(event.position()):
				return self.beginUserDragHandle(event.position())
		
		elif event.type() == QtCore.QEvent.Type.MouseButtonRelease and self._dragIsActive():
			return self.endUserDragHandle()
		
		elif event.type() == QtCore.QEvent.Type.MouseMove:

			self.setMouseCoordinates(event.position())
			if self._dragIsActive():
				return self.updateUserDragHandle(event.position())

		elif event.type() == QtCore.QEvent.Type.Resize:
			self.keepHandleVisible(self.rect())

		elif event.type() == QtCore.QEvent.Type.PaletteChange:

			self.setupDrawingTools()
			
			for new_rect in self.activeRects(self.rect()):
				self.update(new_rect)
			
			return True

		return super().event(event)