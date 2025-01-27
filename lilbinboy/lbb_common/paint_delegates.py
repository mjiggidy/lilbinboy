from PySide6 import QtCore, QtGui

def LBClipColorPainter(rect:QtCore.QRect, painter:QtGui.QPainter, outline_color:QtGui.QColor=None, clip_color:QtGui.QColor=None, pen_width:int=1, padding:QtCore.QSize=None, shadow_offset:QtCore.QPoint=None):
		"""Draw a Clip Color graphic for a given painter"""
		
		outline_color = outline_color or QtGui.QColor("Black")
		clip_color = clip_color or QtGui.QColor()
		padding = padding or QtCore.QSize(3,3)
		shadow_offset = shadow_offset or QtCore.QPoint(1,1)
		
		painter.save()

		# Actual color box area (rect + padding)
		color_box = rect.adjusted(padding.width(), padding.height(), -padding.width(), -padding.height())
		
		# Set outline and fill
		pen = QtGui.QPen()
		pen.setColor(outline_color)
		pen.setWidth(pen_width)
		pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
	
		# Use clip color if available
		brush = QtGui.QBrush()	
		if not clip_color.isValid():
			brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
		else:
			brush.setColor(clip_color)
			brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
		
		painter.setPen(pen)
		painter.setBrush(brush)
		
		# Draw frame + fill
		painter.drawRect(color_box)

		# Box Shadow (TODO: 128 opactiy not working)
		color_box.moveCenter(color_box.center() + shadow_offset)

		color_shadow = pen.color()
		color_shadow.setAlpha(64)
		pen.setColor(color_shadow)

		brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)

		painter.setPen(pen)
		painter.setBrush(brush)

		# Draw shadow
		painter.drawRect(color_box)

		# DEBUG
		painter.drawText(color_box, str(rect.height()), QtCore.Qt.AlignmentFlag.AlignCenter|QtCore.Qt.AlignmentFlag.AlignVCenter)

		painter.restore()