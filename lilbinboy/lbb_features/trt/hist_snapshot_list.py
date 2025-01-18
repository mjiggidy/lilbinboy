from PySide6 import QtSql, QtCore, QtGui, QtWidgets

class TRTHistorySnapshotLabelDelegate(QtWidgets.QStyledItemDelegate):

	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		#super().paint(painter, custom_option, index)

		style = option.widget.style()  # Get the current style
		style.drawControl(QtWidgets.QStyle.CE_ItemViewItem, option, painter, option.widget)

		painter.save()
		
		label_info = index.model().record(index.row())

		is_current = bool(label_info.field("is_current").value())
		if label_info.field("clip_color").isNull():
			clip_color = QtGui.QColor(None)
		else:
			clip_color = QtGui.QColor(*[int(x) for x in str(label_info.field("clip_color").value()).split(",")])


		if option.state & QtWidgets.QStyle.StateFlag.State_Selected:
			text_color = option.palette.highlightedText().color()
		else:
			text_color = option.palette.text().color()
		
		margin = QtCore.QPoint(26, 5)
		


		rect:QtCore.QRect = option.rect

		rect_clip_color = QtCore.QRectF(0,0, 10, 10)
		rect_clip_color.moveCenter(QtCore.QPointF(12, rect.center().y()))
		self.drawClipColor(rect=rect_clip_color, painter=painter, clip_color=clip_color)
		#self.drawClipColor()

		font = painter.font()
		#font.setPointSizeF(font.pointSizeF() * 1.2)
		if is_current:
			font.setItalic(True)
		font.setBold(True)

		painter.setPen(text_color)
		painter.setFont(font)
		painter.drawText(rect.adjusted(margin.x(), margin.y(), -margin.y(), -margin.y()), label_info.field("name").value())

		font = QtGui.QFont()
		# font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont)
		#font.setPointSizeF(font.pointSizeF() * 1.2)
		sub_rect = rect.adjusted(margin.x(), margin.y() + 16, -margin.y(), -margin.y())

		font.setPointSizeF(font.pointSizeF() * 0.8)
		painter.setFont(font)
		painter.drawText(sub_rect, "01:47:23:12", QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignBottom)

		datetime_str = QtCore.QDateTime.fromString(label_info.field("datetime_created_local").value(), QtCore.Qt.DateFormat.ISODate)
		#print(datetime_str.toString(QtCore.Qt.DateFormat.TextDate))
		painter.drawText(sub_rect, datetime_str.toString("dd MMM yyyy"), QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignBottom)

		if is_current:

			pen = QtGui.QPen()
			pen.setWidth(1)
			#pen.setColor(QtGui.QPalette().text())
			pen.setStyle(QtCore.Qt.PenStyle.SolidLine)

			line = QtCore.QLine(rect.bottomLeft(), rect.bottomRight())
			painter.setPen(pen)
			painter.drawLine(line)

		painter.restore()

	def drawClipColor(self, rect:QtCore.QRect, painter:QtGui.QPainter, clip_color:QtGui.QColor):
	#def drawClipColor():

		painter.save()

		

		#painter = QtGui.QPainter(self)
		#rect = QtCore.QRect(10, 5, 32, 32)
		#clip_color = QtGui.QColor(0,0,244)
		# Set box location
		color_box = rect
		#color_box.moveCenter(rect.center())
		
		# Set outline and fill
		pen = QtGui.QPen(QtGui.QColor(QtGui.QPalette().text().color()))
		pen.setJoinStyle(QtCore.Qt.PenJoinStyle.MiterJoin)
		brush = QtGui.QBrush()	

		# Use clip color if available
		if not clip_color.isValid():
			brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
		else:
			brush.setColor(clip_color)
			brush.setStyle(QtCore.Qt.BrushStyle.SolidPattern)
		
		painter.setBrush(brush)
		painter.setPen(pen)
		painter.drawRect(color_box)

		# Box Shadow (TODO: 128 opactiy not working)
		color_box.moveCenter(color_box.center() + QtCore.QPointF(1,1))
		#color_box.setWidth(color_box.width() + 2)

		color_shadow = pen.color()
		color_shadow.setAlpha(64)
		pen.setColor(color_shadow)
		brush.setStyle(QtCore.Qt.BrushStyle.NoBrush)
		painter.setPen(pen)
		painter.setBrush(brush)
		painter.drawRect(color_box)

		painter.restore()
	
	def sizeHint(self, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex) -> QtCore.QSizeF:
		return QtCore.QSize(165, 38)