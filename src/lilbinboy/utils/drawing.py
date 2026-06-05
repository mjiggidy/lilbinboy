from PySide6 import QtCore, QtGui

def draw_marker_tick(
	painter      :QtGui.QPainter,
	canvas       :QtCore.QRect,
	marker_color :QtGui.QColor,
#	/,
	border_color :QtGui.QColor|None=None,
	border_width :int=2,
	border_radius:int=2,
	shadow_color :QtGui.QColor|None=None,
	shadow_alpha :float=0.25
):
	border_color = border_color or QtGui.QGuiApplication.palette().buttonText().color()
	shadow_color = shadow_color or QtGui.QGuiApplication.palette().shadow().color()
	
	painter.save()
	painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
	
	active_rect = canvas

	pen = QtGui.QPen()
	pen.setColor(border_color)
	pen.setWidth(border_width)
	pen.setStyle(QtCore.Qt.PenStyle.SolidLine)

	brush = QtGui.QBrush()
	brush.setColor(marker_color)
	brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern if marker_color.isValid() else QtCore.Qt.BrushStyle.LinearGradientPattern)
	
	# No Marker color?
	if not marker_color:
		raise ValueError("Nothing to draw")
	
	# Draw shadow first I guess
	if shadow_color.isValid() and border_width > 0:

		shadow_offset = QtCore.QPointF(border_width/2,border_width/2)
		active_rect.translate(shadow_offset.toPoint())
		
		shadow_color.setAlphaF(shadow_alpha)
		pen.setColor(shadow_color)
		brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
		
		painter.setPen(pen)
		painter.setBrush(brush)

		painter.drawRoundedRect(active_rect, border_radius, border_radius)

		active_rect.translate(-shadow_offset.toPoint())

	brush.setColor(marker_color)
	brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern if marker_color.isValid() else QtCore.Qt.BrushStyle.LinearGradientPattern)

	pen.setColor(border_color)
	pen.setWidth(border_width)
	pen.setStyle(QtCore.Qt.PenStyle.SolidLine)	

	painter.setPen(pen)
	painter.setBrush(brush)
	
	painter.drawRoundedRect(
		active_rect, border_radius, border_radius
	)
	
	painter.restore()

def draw_frame_thumbnail(
	painter      :QtGui.QPainter,
	canvas       :QtCore.QRectF,
	frame_offset :int = 0,

	base_color   :QtGui.QColor|None = None,
	clip_color   :QtGui.QColor|None = None,
	border_width :float=2,

	shadow_color :QtGui.QColor|None=None,
	shadow_offset:QtCore.QPointF|None=None,
):
	
		clip_color    = clip_color    or QtGui.QColor()
		shadow_color  = shadow_color  or QtGui.QColor()
		shadow_offset = shadow_offset or QtCore.QPointF(border_width, border_width)

		active_rect = QtCore.QRectF(canvas).marginsRemoved(
			QtCore.QMarginsF(*[border_width * 2] * 4)
		)
		
		painter.save()

		# Draw shadow first
		if shadow_color.isValid() and shadow_color.alpha() and not shadow_offset.isNull():

			pen_shadow = QtGui.QPen()
			pen_shadow.setStyle(QtCore.Qt.PenStyle.NoPen)

			brush_shadow = QtGui.QBrush(shadow_color)
			brush_shadow.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

			painter.setPen(pen_shadow)
			painter.setBrush(brush_shadow)
			painter.drawRect(active_rect.translated(shadow_offset))

		# Draw base rect

		brush_bg = QtGui.QBrush(base_color)
		brush_bg.setStyle(QtCore.Qt.BrushStyle.SolidPattern)

		pen_fg  = QtGui.QPen()

		if clip_color.isValid():
			pen_fg.setColor(clip_color)
			pen_fg.setStyle(QtCore.Qt.PenStyle.SolidLine)
			pen_fg.setWidthF(border_width)
			pen_fg.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
		
		else:
			pen_fg.setColor(QtGui.QColor(235,235,235))
			pen_fg.setStyle(QtCore.Qt.PenStyle.NoPen)

		painter.setBrush(brush_bg)
		painter.setPen(pen_fg)

		painter.drawRect(active_rect)


		# Draw text

		size_hint = canvas.size()
		pen_fg.setStyle(QtCore.Qt.PenStyle.SolidLine)
		painter.setPen(pen_fg)
		painter.drawText(active_rect, f"{size_hint.width()} x {size_hint.height()}", QtCore.Qt.AlignmentFlag.AlignTop)
		painter.drawText(active_rect, str(frame_offset), QtCore.Qt.AlignmentFlag.AlignBottom)

		painter.restore()

def draw_clip_color_chip(
	painter      :QtGui.QPainter,
	canvas       :QtCore.QRectF,
	clip_color   :QtGui.QColor,
#	*,
	border_color :QtGui.QColor|None=None,
	border_width :float=2,
	shadow_color :QtGui.QColor|None=None,
	shadow_alpha :float=0.25,
	shadow_offset:QtCore.QPointF|None=None,
	margins      :QtCore.QMarginsF|None=None,
):
	
	border_color  = border_color or QtGui.QGuiApplication.palette().buttonText().color()
	shadow_color  = shadow_color or QtGui.QGuiApplication.palette().shadow().color()
	shadow_offset = shadow_offset or QtCore.QPointF(border_width,border_width)
	
	# No border and no clip color?
	if not clip_color.isValid() and (border_width==0 or not border_color.isValid()):
		raise ValueError("Nothing to draw")
	
	# Calculate margins for stroke and shadow
	margins = margins or QtCore.QMarginsF(*([border_width * 2] * 4))
	active_rect = QtCore.QRectF(canvas).marginsRemoved(margins)

	# Pen and brush initial values
	pen = painter.pen()
	pen.setWidth(border_width)
	pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
	pen.setStyle(QtCore.Qt.PenStyle.SolidLine)
	
	brush = painter.brush()

	painter.save()
	#painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

	# Draw shadow first I guess
	if shadow_color.isValid() and border_width > 0:

		
		active_rect.translate(shadow_offset)
		
		shadow_color.setAlphaF(shadow_alpha)
		pen.setColor(shadow_color)
		brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
		
		painter.setPen(pen)
		painter.setBrush(brush)

		painter.drawRect(active_rect)

		active_rect.translate(-shadow_offset)

	# Draw main clip color chip
	pen.setColor(border_color)
	brush.setColor(clip_color)
	brush.setStyle(
		QtCore.Qt.BrushStyle.SolidPattern if clip_color.isValid()
		else QtCore.Qt.BrushStyle.NoBrush
	)

	painter.setPen(pen)
	painter.setBrush(brush)

	painter.drawRect(active_rect)

	painter.restore()