from PySide6 import QtCore, QtGui
from . import abstractoverlay

DEFAULT_DISPLAY_SIZE      = QtCore.QSizeF(150, 150)
DEFAULT_DISPLAY_MARGINS   = QtCore.QMarginsF(32, 32, 32, 32)
DEFAULT_DISPLAY_ALIGNMENT = QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignTop
DEFAULT_DISPLAY_OFFSET    = QtCore.QPointF(0,0)

DEFAULT_KEY_DRAG_THUMBNAIL= QtCore.Qt.KeyboardModifier.AltModifier

class BSThumbnailMapOverlay(abstractoverlay.BSAbstractOverlay):
	"""A thumbnail map overlay thing"""

	sig_thumbnail_alignment_changed = QtCore.Signal(QtCore.Qt.AlignmentFlag)
	sig_thumbnail_position_changed  = QtCore.Signal(QtCore.QPointF)
	sig_thumbnail_size_changed      = QtCore.Signal(QtCore.QSizeF)
	sig_scene_rect_changed          = QtCore.Signal(QtCore.QRectF)
	sig_view_reticle_changed        = QtCore.Signal(QtCore.QRectF)

	sig_view_reticle_panned         = QtCore.Signal(QtCore.QPointF)
	"""New view rect in scene coordinates"""


	def __init__(self,
		*args,
		thumbnail_max_size:   QtCore.QSize|QtCore.QSizeF|None = None,
		thumbnail_align:  QtCore.Qt.AlignmentFlag|None    = None,
		thumbnail_offset: QtCore.QPointF|None             = None,
		display_margins:  QtCore.QMarginsF|None           = None,
		scene_rect:       QtCore.QRectF|None              = None,
		view_rect:        QtCore.QRectF|None              = None,
		keep_in_view:     bool                            = True,
		**kwargs):

		super().__init__(*args, **kwargs)

		# Metrics
		self._thumb_display_max_size = thumbnail_max_size or DEFAULT_DISPLAY_SIZE
		self._thumb_display_offset   = thumbnail_offset   or DEFAULT_DISPLAY_OFFSET
		self._thumb_display_margins  = display_margins    or DEFAULT_DISPLAY_MARGINS
		self._thumb_display_align    = thumbnail_align    or DEFAULT_DISPLAY_ALIGNMENT
		self._keep_thumb_in_view     = keep_in_view

		self._thumbnails_path        = QtGui.QPainterPath()
		self._thumbnails_rects       = []

		# Source rects
		self._rect_scene   = scene_rect or QtCore.QRectF(-500,-500,1000,1000)
		self._rect_reticle = view_rect  or QtCore.QRectF(self._rect_scene)
		
		# Transforms
		self._scene_to_display_transform = QtGui.QTransform()
		"""Transform scene coordinate rects to viewport coordinate rects"""
		self._display_to_scene_transform = QtGui.QTransform()
		"""Transform display coordinates to scene coordinates (inverted from scene-to-display)"""

		# Mouse tracking
		self._mouse_thumbnail_offset   = QtCore.QPointF()
		"""The intitial offset of the mouse from the topLeft corner of the thumbnail rect, when it was clicked"""
		self._mouse_reticle_offset     = QtCore.QPointF()
		"""The initial offset of the mouse from the topLeft corner of the user reticle, when it was clicked"""
	
		self.setThumbnailOffset(self._thumb_display_offset, self._thumb_display_align)

	def enabledChanged(self, is_enabled):
		
		# Update relative offset based on the latest window size
		if is_enabled:
			self.setThumbnailOffset()

		return super().enabledChanged(is_enabled)

	def paintOverlay(self, painter, rect_canvas):
		
		super().paintOverlay(painter, rect_canvas)
		
		self._draw_thumbnail_base(painter)
		#painter.drawText(self._thumb_display_offset, str(self._thumb_display_offset))
		#painter.drawRect(self.safeCanvas())
		painter.drawPath(self._thumbnails_path.translated(self._thumb_display_offset))
		self._draw_user_reticle(painter)

	@QtCore.Slot(QtGui.QRegion)
	def setThumbnailRects(self, thumb_rects:list[QtCore.QRectF]):

		#print("Got", thumb_region)

		self.update(self.finalThumbnailRect())

		self._thumbnails_rects = thumb_rects

		self.buildThumbnailsPath()
		
		self.update(self.finalThumbnailRect())

	def buildThumbnailsPath(self):

		self.update(self.finalThumbnailRect())

		self._thumbnails_path = QtGui.QPainterPath()
		for thumb in self._thumbnails_rects:
			self._thumbnails_path.addRect(thumb)
		self._thumbnails_path = self._scene_to_display_transform.map(self._thumbnails_path)

		self.update(self.finalThumbnailRect())

	# Drawing

	def _draw_thumbnail_base(self, painter:QtGui.QPainter):

		pen_thumbnail = QtGui.QPen()
		pen_thumbnail.setColor(self.palette().windowText().color())
		pen_thumbnail.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
		pen_thumbnail.setWidthF(1)

		brush_thumbnail = QtGui.QBrush()
		brush_thumbnail.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
		col_thumbnail = self.palette().window().color()
		col_thumbnail.setAlphaF(0.75)
		brush_thumbnail.setColor(col_thumbnail)
		
		painter.setPen(pen_thumbnail)
		painter.setBrush(brush_thumbnail)
		painter.drawRect(self.finalThumbnailRect())


	def _draw_user_reticle(self, painter:QtGui.QPainter):

		if self._dragReticleActive():
			painter.setPen(self.palette().accent().color().lighter())
#		elif self.finalReticleRect().contains(self.widget().mapFromGlobal(QtGui.QCursor.pos())):
#			painter.setPen(self.palette().accent().color())
		painter.drawRect(self.finalReticleRect())

	# Calculations	

	def normalizedThumbnailRect(self) -> QtCore.QRectF:
		"""Thumbnail rect normalized to `topLeft=(0,0)`, `size=displaySize`"""

		return self._scene_to_display_transform.mapRect(self._rect_scene)
	
	def normalizedReticleRect(self) -> QtCore.QRectF:
		return self._scene_to_display_transform.mapRect(self._rect_reticle)
	
	def finalThumbnailRect(self) -> QtCore.QRectF:

		return self.normalizedThumbnailRect().translated(self._thumb_display_offset)
	
	def finalReticleRect(self) -> QtCore.QRectF:

		return self.normalizedReticleRect().translated(self._thumb_display_offset)
	
	# Properties

	@QtCore.Slot(QtCore.QRectF)
	def setSceneRect(self, scene_rect:QtCore.QRectF):

		if self._rect_scene == scene_rect:
			return
		
		if not scene_rect.isValid():
			return
		
		old_rect = self.normalizedThumbnailRect()
		self.update(old_rect)

		self._rect_scene = scene_rect

		# Update transform:
		# Get scene rect to display coords: 0,0 - scaled width,height using transform
		transform = QtGui.QTransform()
		transform.scale(self._thumb_display_max_size.width()/scene_rect.width(), self._thumb_display_max_size.width()/scene_rect.width())
		transform.translate(-scene_rect.left(), -scene_rect.top())
		
		self._scene_to_display_transform   = transform
		self._display_to_scene_transform, was_it_tho = transform.inverted()

		if not was_it_tho:
			raise ValueError("Unable to invert display-to-scene transform")

		self.sig_scene_rect_changed.emit(scene_rect)

		# Also probably recalc offset
		new_rect = self.normalizedThumbnailRect()

		new_offset = QtCore.QPointF(self._thumb_display_offset)
		if self._thumb_display_align & QtCore.Qt.AlignmentFlag.AlignRight:
			new_offset += QtCore.QPointF(old_rect.width() - new_rect.width(), 0)
		if self._thumb_display_align & QtCore.Qt.AlignmentFlag.AlignBottom:
			new_offset += QtCore.QPointF(0, old_rect.height() - new_rect.height())

		self.setThumbnailOffset(new_offset)

	def sceneRect(self) -> QtCore.QRectF:
		return self._rect_scene
	
	@QtCore.Slot(QtCore.QSizeF)
	def setThumbnailSize(self, thumbnail_size:QtCore.QSizeF):
		
		if self._thumb_display_max_size == thumbnail_size:
			return
		
		old_rect = self.normalizedThumbnailRect()
		self.update(old_rect)

		self._thumb_display_max_size = thumbnail_size
		self.sig_thumbnail_size_changed.emit(thumbnail_size)

		new_rect = self.normalizedThumbnailRect()
		self.update(new_rect)
	
	def thumbnailSize(self) -> QtCore.QSizeF:
		return self._thumb_display_max_size
	
	def _normalizeCoordinates(self, coordinates:QtCore.QPointF, from_anchor:QtCore.Qt.AlignmentFlag) -> QtCore.QPointF:
		"""Normalize coordinates to TopLeft widget origin"""

		coordinates = QtCore.QPointF(coordinates)

		if from_anchor == QtCore.Qt.AlignmentFlag.AlignTop|QtCore.Qt.AlignmentFlag.AlignLeft:
			return coordinates
		
		safe_rect = self.safeCanvas()
		thumb_rect = self.normalizedReticleRect()
		
		if from_anchor & QtCore.Qt.AlignmentFlag.AlignRight:
			coordinates.setX(safe_rect.right() - thumb_rect.width() + coordinates.x())
			
		if from_anchor & QtCore.Qt.AlignmentFlag.AlignBottom:
			coordinates.setY(safe_rect.bottom() - thumb_rect.height() + coordinates.y())

		return coordinates
	
	@QtCore.Slot()
	@QtCore.Slot(QtCore.QPointF)
	def setThumbnailOffset(self,
		proposed_offset:QtCore.QPointF|None=None,
		coordinate_space:QtCore.Qt.AlignmentFlag|None=None
	):
		"""Set (or recalculate) a safe thumbnail offset"""
				
		old_thumb_rect = self.finalThumbnailRect()
		self.update(old_thumb_rect)
		
		proposed_offset = proposed_offset or self._thumb_display_offset
		coordinate_space = coordinate_space or self._thumb_display_align
		proposed_offset = self._normalizeCoordinates(proposed_offset, coordinate_space)


		# Check bounds
		final_offset = self._getSafeOffset(proposed_offset) if self._keep_thumb_in_view else proposed_offset
		if self._thumb_display_offset == final_offset:
			#print("Ignored because same")
			return


		#print(f"Initially propose: {self._thumb_display_offset=} {proposed_offset=} {final_offset=} {self.safeCanvas()=}")
		self._thumb_display_offset = final_offset

		#print("Final offset ", final_offset)

		new_rect = self.finalThumbnailRect()
		self.update(new_rect)

	def _getSafeOffset(self, proposed_offset:QtCore.QPointF) -> QtCore.QPointF:
		"""Calculate a safe offset (visible, within margins) from a given one"""


		# Get the previous final rect with proposed new coordinates
		proposed_thumb_rect = self.finalThumbnailRect().translated(proposed_offset - self._thumb_display_offset)
		safe_canvas         = self.safeCanvas()

		if safe_canvas.contains(proposed_thumb_rect):
			return proposed_offset
		
		# Constrain within horiontal margins
		if self._thumb_display_align & QtCore.Qt.AlignmentFlag.AlignLeft:                           # IF ANCHORED LEFT:
			proposed_thumb_rect.moveRight(min(safe_canvas.right(), proposed_thumb_rect.right()))    # Protect right margin
			proposed_thumb_rect.moveLeft(max(safe_canvas.left(), proposed_thumb_rect.left()))       # but prioritize left margin

		else:                                                                                       # IF ANCHORED RIGHT:
			proposed_thumb_rect.moveLeft(max(safe_canvas.left(), proposed_thumb_rect.left()))       # Protect left margin
			proposed_thumb_rect.moveRight(min(safe_canvas.right(), proposed_thumb_rect.right()))    # but prioritize right margin
		
		# Constrain within vertical margins
		if self._thumb_display_align & QtCore.Qt.AlignmentFlag.AlignTop:                            # IF ANCHORED TOP:
			proposed_thumb_rect.moveBottom(min(safe_canvas.bottom(), proposed_thumb_rect.bottom())) # Protect bottom margin
			proposed_thumb_rect.moveTop(max(safe_canvas.top(), proposed_thumb_rect.top()))          # but prioritize top margin

		else:                                                                                       # IF ANCHORED BOTTOM:
			proposed_thumb_rect.moveTop(max(safe_canvas.top(), proposed_thumb_rect.top()))          # Protect top margin
			proposed_thumb_rect.moveBottom(min(safe_canvas.bottom(), proposed_thumb_rect.bottom())) # but prioritize bottom margin

		return proposed_thumb_rect.topLeft()

	def safeCanvas(self) -> QtCore.QRectF:
		"""Safe canvas with margins removed"""

		return QtCore.QRectF(self.rect()).marginsRemoved(self._thumb_display_margins)
	
	@QtCore.Slot(QtCore.QRectF)
	def setViewReticle(self, view_rect:QtCore.QRectF):

		if self._rect_reticle == view_rect:
			return
		
		old_rect = self.viewReticle()
		self.update(old_rect)

		self._rect_reticle = view_rect
		self.sig_view_reticle_changed.emit(view_rect)

		new_rect = self.viewReticle()
		self.update(new_rect)

	def viewReticle(self) -> QtCore.QRectF:
		return self._rect_reticle
	
	###
	# Events
	###

	def event(self, event):
		
		if event.type() == QtCore.QEvent.Type.MouseButtonPress:
			return self._handleMouseButtonPress(event)
		
		if event.type() == QtCore.QEvent.Type.MouseButtonDblClick:
			return self._handleMouseDoubleClick(event)
		
		elif event.type() == QtCore.QEvent.Type.MouseButtonRelease:
			return self._handleMouseButtonRelease(event)
		
		elif event.type() == QtCore.QEvent.Type.MouseMove:
			return self._handleMouseMove(event)
		
		elif event.type() == QtCore.QEvent.Type.Resize:
			return self._handleWidgetResize(event)
		
		return super().event(event)
	
	def _handleWidgetResize(self, resize_event:QtGui.QResizeEvent) -> bool:
		"""Update positioning stuff"""

		new_offset = QtCore.QPointF(self._thumb_display_offset)

		resize_diff = resize_event.size() - resize_event.oldSize()

		# Offset for alternative anchors
		if self._thumb_display_align & QtCore.Qt.AlignmentFlag.AlignRight:
			new_offset.setX(new_offset.x() + resize_diff.width())

		if self._thumb_display_align & QtCore.Qt.AlignmentFlag.AlignBottom:
			new_offset.setY(new_offset.y() + resize_diff.height())

		self.setThumbnailOffset(new_offset)

		return False
	
	def _dragThumbnailActive(self) -> bool:
		"""Is user dragging thumbnail?"""
		
		return not self._mouse_thumbnail_offset.isNull()
	
	def _dragReticleActive(self) -> bool:
		"""Is user dragging reticle?"""

		return not self._mouse_reticle_offset.isNull()
	
	def _handleMouseDoubleClick(self, event:QtGui.QMouseEvent) -> bool:
		"""Ignore double-clicks"""

		return self.finalReticleRect().contains(event.position())
	
	def _handleMouseDragReticle(self, event:QtGui.QMouseEvent) -> bool:
		"""Mouse reticle was clicked/dragged"""

		scene_pos = self._display_to_scene_transform.map(self._mouse_reticle_offset)
		self.sig_view_reticle_panned.emit(scene_pos)

		return True
	
	def _handleMouseButtonPress(self, event:QtGui.QMouseEvent) -> bool:

		if any((
			self._dragThumbnailActive(),
			self._dragReticleActive(),
			not self.finalThumbnailRect().contains(event.position())
		)):
			# Ignore weird mouse presses during active drags or outside of bounds
			return False
		
		if event.modifiers() & DEFAULT_KEY_DRAG_THUMBNAIL:
			# Begin alternative drag (move thumbnail)
			
			#self.widget().setCursor(QtCore.Qt.CursorShape.DragMoveCursor)
			self._mouse_thumbnail_offset = event.position() - self.finalThumbnailRect().topLeft()
			
			return True

		else:
			# Begin normal click-to-center/drag of the reticle
			
			self._mouse_reticle_offset = event.position() - self.finalThumbnailRect().topLeft()
			self.update(self.finalReticleRect())
			return self._handleMouseDragReticle(event)

	def _handleMouseButtonRelease(self, event:QtGui.QMouseEvent):

		if self._dragThumbnailActive():
			# End alternative drag
			
			#self.widget().unsetCursor()
			self._mouse_thumbnail_offset = QtCore.QPointF()
			
			return True
		
		if self._dragReticleActive():
			# End reticle drag

			self._mouse_reticle_offset = QtCore.QPointF()
			self.update(self.finalReticleRect())
			return True
	
		return False
		
	def _handleMouseMove(self, event:QtGui.QMouseEvent):
		
		if self._dragThumbnailActive():
			# Handle thumbnail drag
			
			self.setThumbnailOffset(event.position() - self._mouse_thumbnail_offset, QtCore.Qt.AlignmentFlag.AlignTop|QtCore.Qt.AlignmentFlag.AlignTop)
			return True
		
		elif self._dragReticleActive():
			# Handle click/drag reticle
			
			self._mouse_reticle_offset = event.position() - self.finalThumbnailRect().topLeft()
			self._handleMouseDragReticle(event)
			return True
		
		elif self.finalReticleRect().contains(event.position()):
			# Just repaint on hover for effects
			
			self.update(self.finalThumbnailRect())
			return False

		return False