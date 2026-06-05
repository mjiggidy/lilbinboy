from __future__ import annotations
import logging, dataclasses
from typing import TYPE_CHECKING
from PySide6 import QtCore, QtGui, QtWidgets
from . import abstractoverlay

@dataclasses.dataclass(frozen=True)
class BSOverlayParentWidgetInfo:
	"""Widget info for overlays"""

	font   :QtGui.QFont
	palette:QtGui.QPalette
	rect   :QtCore.QRectF

		
class BSGraphicsOverlayManager(QtCore.QObject):
	"""Overlay manager for a widget"""

	sig_overlay_installed   = QtCore.Signal(object)
	sig_overlay_removed     = QtCore.Signal(object)
	sig_overlay_toggled     = QtCore.Signal(bool)

	sig_widget_info_changed = QtCore.Signal(object)

	def __init__(self, *args, parent:QtWidgets.QWidget, **kwargs):

		if not isinstance(parent, QtWidgets.QWidget):
			raise ValueError(f"Parent must be a `QWidget` (got {type(parent)})")

		super().__init__(*args, parent=parent, **kwargs)

		self._overlays:set[abstractoverlay.BSAbstractOverlay] = set()

		self._widget_info = BSOverlayParentWidgetInfo(
			font    = self.parent().font(),
			palette = self.parent().palette(),
			rect    = self.parent().rect()
		)

		self._installOnParent()

	def _installOnParent(self):
		"""Hook manager into the parent widget event loop"""
		
		self.parent().setMouseTracking(True)
		self.parent().installEventFilter(self)

	def _updateWidgetInfo(self, *args, **kwargs):

		self._widget_info = dataclasses.replace(self._widget_info, **kwargs)
		self.sig_widget_info_changed.emit(self._widget_info)

	def widgetInfo(self) -> BSOverlayParentWidgetInfo:
		"""Cached widget info"""

		return self._widget_info
	
	@QtCore.Slot(object)
	def installOverlay(self, overlay:abstractoverlay.BSAbstractOverlay):
		"""Install a new overlay"""

		if overlay in self._overlays:

			logging.getLogger(__name__).debug(
				"Skipping install %s: Already installed (%s)",
				overlay, self._overlays
			)
			return

		overlay.setParent(self)

		self._overlays.add(overlay)
		self.installEventFilter(overlay)

		self.sig_widget_info_changed.connect(overlay.updateWidgetInfo)

		overlay.sig_update_requested     .connect(self.parent().update)
		overlay.sig_update_rect_requested.connect(self.parent().update)
		
		logging.getLogger(__name__).debug("Installed parent %s on %s", overlay.parent(), overlay)
		self.sig_overlay_installed.emit(overlay)
		
	def overlays(self) -> list[abstractoverlay.BSAbstractOverlay]:
		"""Get all installed overlays"""

		return list(self._overlays)

	@QtCore.Slot()
	def clear(self):
		"""Remove all overlays"""

		for overlay in reversed(list(self._overlays)):
			self.removeOverlay(overlay)

	def removeOverlay(self, overlay:abstractoverlay.BSAbstractOverlay):
		"""Remove an installed overlay"""

		try:
			self._overlays.remove(overlay)
		except KeyError as e:
			raise ValueError(f"Overlay {overlay} not installed in this manager") from e
		
		logging.getLogger(__name__).debug("Removed overlay %s", overlay)
		
		overlay.disconnect(self)

		self.disconnect(overlay)
		self.sig_overlay_removed.emit(overlay)

		overlay.deleteLater()

	def setOverlayEnabled(self, overlay:abstractoverlay.BSAbstractOverlay, is_enabled:bool):

		if not overlay in self._overlays:
			raise ValueError(f"Overlay {overlay} does not belong to this manager")
		
		if overlay.isEnabled() == is_enabled:
			return
		
		overlay._setEnabled(is_enabled)
		overlay.blockSignals(not is_enabled)

		logging.getLogger(__name__).debug("Overlay %s enabled=%s", str(overlay), str(overlay.isEnabled()))
		self.sig_overlay_toggled.emit(is_enabled)

	def overlayEnabled(self, overlay:abstractoverlay.BSAbstractOverlay) -> bool:
		"""Is the overlay enabled"""

		if not overlay in self._overlays:
			raise ValueError(f"Overlay {overlay} does not belong to this manager")
		
		return overlay.isEnabled()

	def paintOverlays(self, painter:QtGui.QPainter, rect:QtCore.QRect):
		"""Paint installed overlays"""

		for overlay in filter(lambda o: o.isEnabled(), self._overlays):

			painter.save()
			try:
				overlay.paintOverlay(painter, rect)
			except Exception as e:
				logging.getLogger(__name__).error("Error painting %s: %s", overlay, e)
			finally:
				painter.restore()
	
	def eventFilter(self, watched:QtWidgets.QWidget, event:QtCore.QEvent):
		"""Foreward events to active overlays"""

		###
		# Ignore paint events -- must be handled via parent widget's paintEvent
		###
		if event.type() == QtCore.QEvent.Type.Paint:
			return False
		
		###
		# Update widget info
		###
		if event.type() in (QtCore.QEvent.Type.Resize, QtCore.QEvent.Type.Move):
			self._updateWidgetInfo(rect=QtCore.QRectF(watched.rect()))
		
		if event.type() == QtCore.QEvent.Type.FontChange:
			self._updateWidgetInfo(font = watched.font())
		
		if event.type() == QtCore.QEvent.Type.PaletteChange:
			self._updateWidgetInfo(palette = watched.palette())

		###
		# Pass event through to overlays
		###
		for overlay in filter(lambda o: o.isEnabled(), self._overlays):

			if QtWidgets.QApplication.sendEvent(overlay, event):
				return True
		
		return False