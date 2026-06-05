import logging, typing
from PySide6 import QtCore, QtGui, QtWidgets

from ..core  import icon_providers, config


class BSGenericItemDelegate(QtWidgets.QStyledItemDelegate):

	def __init__(self, padding:QtCore.QMarginsF|None=None, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._padding = padding or QtCore.QMarginsF()

	def sizeHint(self, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex) -> QtCore.QSize:
		"""Return size hint with padding factored in"""
		
		hint_og = super().sizeHint(option, index)
		
		return QtCore.QSize(
			hint_og.width()  + self._padding.left() + self._padding.right(),
			hint_og.height() + self._padding.top()  + self._padding.bottom()
		)
	
	@QtCore.Slot(object)
	def setItemPadding(self, padding:QtCore.QMargins):
		"""Set padding around individual items"""

		if self._padding == padding:
			return

		self._padding = QtCore.QMarginsF(padding)

		# NOTE: Binding to sizeHintChanged here to trigger redraw
		# Passing invalid model index seems to work ok
		self.sizeHintChanged.emit(QtCore.QModelIndex())
	
	def itemPadding(self) -> QtCore.QMargins:

		return self._padding

	def activeRectFromRect(self, rect:QtCore.QRectF) -> QtCore.QRectF:
		"""The active area without padding and such"""

		return QtCore.QRectF(rect).marginsRemoved(self._padding)
	
	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		# NOTE: Since items can be offset asymetrically (such as pushed up top in Script View), need to 
		# separate drawing the base elements (row background, selection, etc) from the item elements 
		# (text, decoration, etc)

		self.initStyleOption(option, index)
		
		# BACKGROUND STUFF
		# Setup style option to draw the background stuff, then draw it using the app's style (hey look! I learned!)
		# NOTE: Original style option will have padding baked in

		bg_options = QtWidgets.QStyleOptionViewItem(option)
		bg_options.text = ""
		bg_options.state = option.state &~ QtWidgets.QStyle.StateFlag.State_HasFocus	# Don't paint focus indicator

		style = bg_options.widget.style() if bg_options.widget else QtWidgets.QApplication.style()
		style.drawControl(QtWidgets.QStyle.ControlElement.CE_ItemViewItem, bg_options, painter)

		# FOREGROUND STUFF
		# Pull in rect with padding removed so we've got just our active area
		# and re-elide text to the smaller, active rect area

		option.rect = self.activeRectFromRect(option.rect).toRect()
		option.text = QtGui.QFontMetrics(option.font).elidedText(option.text, option.textElideMode, option.rect.width())
		
		painter.setFont(option.font)
		
		style.drawItemText(
			painter,
			option.rect,
			int(option.displayAlignment),
			option.palette,
			bool(option.state & QtWidgets.QStyle.StateFlag.State_Enabled),
			option.text,
			QtGui.QPalette.ColorRole.HighlightedText if bool(option.state & QtWidgets.QStyle.StateFlag.State_Selected) else QtGui.QPalette.ColorRole.Text
		)

		# DEBUG:
		#painter.drawRect(kewl_options.rect)

	def clone(self, *args, **kwargs) -> typing.Self:

		return self.__class__(QtCore.QMarginsF(self._padding), *args, **kwargs)
	
class BSFrameThumbnailDelegate(BSGenericItemDelegate):
	"""Display a thumbnailed frame"""

	DEFAULT_ASPECT_RATIO = QtCore.QSizeF(16, 9)

	sig_aspect_ratio_changed = QtCore.Signal(QtCore.QSize)
	sig_frame_scale_changed  = QtCore.Signal(int)

	def __init__(self, *args, aspect_ratio:QtCore.QSize|QtCore.QSizeF|None=None, frame_scale:int=config.BSScriptViewModeConfig.DEFAULT_SCRIPT_ZOOM_START, **kwargs):

		super().__init__(*args, **kwargs)

		self._aspect_ratio = aspect_ratio or self.DEFAULT_ASPECT_RATIO
#		self._unit_height  = 32 # Height in pixels at scale=1.0
		self._frame_scale  = frame_scale  # TODO

	def sizeHint(self, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex) -> QtCore.QSize:

		self.initStyleOption(option, index)

		# ROUGHLY maintains one line visible in the script comment box
		min_height = self._padding.top() + option.fontMetrics.height() + self._padding.top() + option.fontMetrics.height() + self._padding.bottom()

		size = QtCore.QSizeF(
			self._aspect_ratio.width()  * self._frame_scale + self._padding.left() + self._padding.right(),
			max(min_height, self._aspect_ratio.height() * self._frame_scale + self._padding.top()  + self._padding.bottom())
		).toSize()
		
		return size

	def setAspectRatio(self, aspect_ratio:QtCore.QSize|QtCore.QSizeF):

		if self._aspect_ratio == aspect_ratio:
			return
		
		self._aspect_ratio = aspect_ratio

		self.sig_aspect_ratio_changed.emit(aspect_ratio)

	def aspectRatio(self) -> QtCore.QSize|QtCore.QSizeF:

		return self._aspect_ratio
	
	def setFrameScale(self, frame_scale:int):

		if self._frame_scale == frame_scale:
			return
		
		self._frame_scale = frame_scale

#		self.sizeHintChanged.emit(QtCore.QModelIndex())

		self.sig_frame_scale_changed.emit(frame_scale)

	def frameScale(self) -> int:
		return self._frame_scale
	
#	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):
#
#		super().paint(painter, option, index)
#
#		self.initStyleOption(option, index)
#
#		active_rect = QtCore.QRect(
#			QtCore.QPoint(option.rect.left(), option.rect.top()),
#			QtCore.QSize(self._aspect_ratio.width() * self._frame_scale, self._aspect_ratio.height() * self._frame_scale)
#		)
#
#		clip_color = index.data(binitemtypes.BSBinItemDataRoles.ClipColorRole)
#
#		frame_offset = index.data(binitemtypes.BSBinItemDataRoles.FrameThumbnailRole)
#		shadow_color:QtGui.QColor = option.palette.color(QtGui.QPalette.ColorRole.Shadow)
#		shadow_color.setAlphaF(0.25)
#
#		drawing.draw_frame_thumbnail(
#			painter=painter,
#			canvas=active_rect,
#			frame_offset=frame_offset,
#			base_color = QtGui.QColor(32,32,32),
#			clip_color = clip_color,
#			shadow_color=shadow_color
#		)



class BSIconLookupItemDelegate(BSGenericItemDelegate):
	"""Displays an icon centered in its item rect, with padding and aspect ratio preservation or something"""

	def __init__(self, *args, aspect_ratio:QtCore.QSizeF|None=None, icon_provider:icon_providers.BSStyledIconProvider|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._aspect_ratio  = aspect_ratio  or QtCore.QSizeF(1,1)
		self._icon_provider = icon_provider or icon_providers.BSStyledIconProvider()

	def iconProvider(self) -> icon_providers.BSStyledIconProvider:
		return self._icon_provider

	def sizeWithAspectRatio(self, rect:QtCore.QSize) -> QtCore.QSize:
		"""Over-engineering?  Probably.  Return a size corrected for aspect ratio with priority given to height."""

		# NOTE: Holy moly this had me cranky.  Two things to remember here:
		# 1: All these BS lookups apply padding to their sizeHint
		# 2: The aspect ratio is based on the fixed height of the row so we can vary the width of the column
		# 3: HOWEVER Because Script View has "unbalaced" vertical padding, so...
		# 4: We need to remove it first so the height doesn't throw off aspect ratio calculations.

		rect_height_no_padding = rect.height() - self._padding.top() - self._padding.bottom()

		rect_width_aspect_corrected = rect_height_no_padding * self._aspect_ratio.width()/self._aspect_ratio.height()

		return QtCore.QSize(
			rect_width_aspect_corrected + self._padding.left() + self._padding.right(),
			rect_height_no_padding + self._padding.top() + self._padding.bottom()
		)

	def sizeHint(self, option:QtWidgets.QStyleOption, index:QtCore.QModelIndex) -> QtCore.QSize:
		"""Return aspect ratio-corrected width x original height"""

		orig_size = super().sizeHint(option, index)

		return self.sizeWithAspectRatio(orig_size)
	
	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		self.initStyleOption(option, index)
		style = option.widget.style() if option.widget else QtWidgets.QApplication.style()
		
		decoration_role = index.data(QtCore.Qt.ItemDataRole.DecorationRole)
		#user_role = index.data(QtCore.Qt.ItemDataRole.UserRole)
		
		
		# TODO: Get Icon WITH PALETTE
		icon      = self._icon_provider.getIcon(decoration_role, option.palette)

		# Center, size and shape the canvas QRect
		text_rect = QtCore.QRect(option.rect.topLeft(), QtCore.QSize(option.rect.width(), self._padding.top() + option.fontMetrics.height() + self._padding.bottom()))
		
		canvas_active = self.activeRectFromRect(text_rect)#.marginsRemoved(self._padding)




		
		
		# NOTE: Based on the active canvas area, bind the width to
		# Min: Same as height (square)
		# Max: Aspect ratio (w * w/h)
		w_min = canvas_active.height()
		w_max = canvas_active.height() * (self._aspect_ratio.width() / self._aspect_ratio.height())
		if canvas_active.width() < canvas_active.height():
			w_active = w_min
		elif canvas_active.width() > w_max:
			w_active = w_max
		else:
			w_active = canvas_active.width()
		
		canvas_active.setWidth(w_active)


		#if option.displayAlignment & QtCore.Qt.AlignmentFlag.AlignVCenter or option.displayAlignment & QtCore.Qt.AlignmentFlag.AlignHCenter:
		canvas_active.moveCenter(QtCore.QRectF(option.rect).marginsRemoved(self._padding).center())

		if option.displayAlignment & QtCore.Qt.AlignmentFlag.AlignBottom:
			canvas_active.moveBottom(QtCore.QRectF(option.rect).marginsRemoved(self._padding).bottom())

		if option.displayAlignment & QtCore.Qt.AlignmentFlag.AlignTop:
			canvas_active.moveTop(QtCore.QRectF(option.rect).marginsRemoved(self._padding).top())
		
		
		painter.save()
		painter.setClipRect(option.rect)
		
		# DEBUG
		#painter.drawRect(QtCore.QRect(option.rect.topLeft(), self.sizeHint(option, index)))
		#painter.drawRect()
		
		try:
			style.drawPrimitive(QtWidgets.QStyle.PrimitiveElement.PE_PanelItemViewItem, option, painter, option.widget)

			icon:QtGui.QIcon
			icon.paint(
				painter,
				canvas_active.toRect(),
				mode=QtGui.QIcon.Mode.Selected if option.state & QtWidgets.QStyle.StateFlag.State_Selected else QtGui.QIcon.Mode.Active,
				state=QtGui.QIcon.State.On     if option.state & QtWidgets.QStyle.StateFlag.State_On       else QtGui.QIcon.State.Off,
			)
		
		except Exception as e:
			logging.getLogger(__name__).error("Error drawing icon: %s", e)
		
		painter.restore()

	def clone(self) -> typing.Self:

		return self.__class__(
			aspect_ratio  = QtCore.QSizeF(self._aspect_ratio),
			icon_provider = self._icon_provider,
			padding       = QtCore.QMarginsF(self._padding),
		)