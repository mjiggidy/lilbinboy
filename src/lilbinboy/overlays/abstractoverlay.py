from __future__ import annotations
from typing import TYPE_CHECKING
from PySide6 import QtCore, QtGui, QtWidgets

if TYPE_CHECKING:
	from . import manager

class BSAbstractOverlay(QtCore.QObject):
	"""Abstract overlay for display over a widget"""
	
	sig_enabled_changed       = QtCore.Signal(bool)
	sig_update_rect_requested = QtCore.Signal(object)
	sig_update_requested      = QtCore.Signal()

	def __init__(self, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

		self._is_enabled:bool = True
	
	def paintOverlay(self, painter:QtGui.QPainter, rect_canvas:QtCore.QRect):
		"""Paint the overlay, with the given paintEvent"""
		# Virtual method

	@QtCore.Slot(object)
	def updateWidgetInfo(self, widget_info:manager.BSOverlayParentWidgetInfo):
		"""Parent info was updated.  Do stuff."""
		# Virtual method

	def _widgetInfo(self) -> manager.BSOverlayParentWidgetInfo|None:
		"""Overlay's parent widget info"""
		
		# NOTE TO SELF: Preferring not to acces this directly from overlays
		# as this returns references to the Qt data objects instead of copies.
		# Use palette(), font(), rect() etc instead
		return self.parent().widgetInfo() if self.parent() else None

	def palette(self) -> QtGui.QPalette:
		"""Overlay's parent widget palette"""

		return QtGui.QPalette(self.parent().widgetInfo().palette) if self.parent() \
			else QtWidgets.QApplication.palette()
	
	def font(self) -> QtGui.QFont:
		"""Overlay's parent widget font"""

		return QtGui.QFont(self.parent().widgetInfo().font) if self.parent() \
			else QtWidgets.QApplication.font()
	
	def rect(self) -> QtCore.QRect:
		"""Overlay's parent widget rect"""

		return QtCore.QRectF(self.parent().widgetInfo().rect) if self.parent() \
			else QtCore.QRectF(QtCore.QPointF(0,0), QtCore.QSizeF(100,100))
	
	def isEnabled(self) -> bool:
		"""Overlay is enabled"""

		return self._is_enabled
	
	def manager(self) -> manager.BSGraphicsOverlayManager:
		"""
		Return a reference to the manager

		Note that, for now, the manager is also just the `parent()`.  But maybe not always!
		Who knows!  I just don't want to lock that in with a bunch of calls to `parent()`.
		"""

		return self.parent()
	
	def enabledChanged(self, is_enabled:bool):
		"""Virtual Method: Enable state was changed"""
		
		return
	
	@QtCore.Slot(bool)
	def _setEnabled(self, is_enabled:bool):
		"""This should be set via the manager"""

		if self._is_enabled == is_enabled:
			return

		self._is_enabled = is_enabled
		
		# Virtual function
		self.enabledChanged(is_enabled)
		
		self.sig_enabled_changed.emit(is_enabled)
		self.update()

	def update(self, update_rect:QtCore.QRectF|None=None):
		"""Request update, optionally for a particular `QRectF`"""
		
		if update_rect:
			self.sig_update_rect_requested.emit(update_rect)
		else:
			self.sig_update_requested.emit()