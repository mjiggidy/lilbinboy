"""
Snappy little guy gonna keep ya aligned
"""

from __future__ import annotations
import typing

from PySide6 import QtCore, QtWidgets



if typing.TYPE_CHECKING:
	from . import frameview

class BSFrameGridSnapper(QtCore.QObject):
	"""Return the coordinates of the nearest grid unit"""

	# NOTE: I think I can pull this out further to just use grid info

	sig_active_grid_unit_changed = QtCore.Signal(object)
	sig_active_grid_unit_chosen  = QtCore.Signal(object)
	sig_enabled_changed          = QtCore.Signal(bool)

	def __init__(self, frame_view:frameview.BSBinFrameView, *args, is_enabled:bool=True, **kwargs):

		super().__init__(parent=frame_view.viewport())

		self._frameview  = frame_view
		self._is_enabled = is_enabled

		self._moved = False

		frame_view.viewport().setMouseTracking(True)
		frame_view.viewport().installEventFilter(self)

	@QtCore.Slot(bool)
	def setEnabled(self, is_enabled:bool):
		"""Enable reporting of nearest grid unit"""

		if self._is_enabled == is_enabled:
			return

		if not is_enabled:
			self.sig_active_grid_unit_changed.emit(None)

		self._is_enabled = is_enabled
		self.sig_enabled_changed.emit(is_enabled)

	def isEnabled(self) -> bool:
		"""Is grid unit detection enabled"""

		return self._is_enabled

	def nearestGridUnitFromView(self, viewport_coords:QtCore.QPointF) -> QtCore.QPointF:
		"""Given local view coordinates, find scene coordinates of the nearest grid unit"""

		if isinstance(viewport_coords, QtCore.QPointF):
			viewport_coords = viewport_coords.toPoint()

		return self.nearestGridUnitFromScene(
			self._frameview.mapToScene(viewport_coords)
		)

	def nearestGridUnitFromScene(self, scene_coords:QtCore.QPointF) -> QtCore.QPointF:
		"""Given scene coordinates, find the scene coordinates of the nearest grid"""

		#grid_unit = self._frameview._grid_info.unit_size

		return self._frameview._grid_info.snapToGrid(scene_coords, use_divisions=False)

	def eventFilter(self, watched:QtWidgets.QWidget, event:QtCore.QEvent):
		"""Intercept mouse events for this"""

		if not self._is_enabled:
			return super().eventFilter(watched, event)

		if event.type() == QtCore.QEvent.Type.MouseMove and event.buttons() & QtCore.Qt.MouseButton.LeftButton:

			# Handle mouse drag
			self._moved = True

			self.sig_active_grid_unit_changed.emit(
				self.nearestGridUnitFromView(event.position())
			)

		elif event.type() == QtCore.QEvent.Type.MouseButtonPress and event.button() & QtCore.Qt.MouseButton.LeftButton:

			# Handle mouse press
			self._moved = False
			self.sig_active_grid_unit_changed.emit(
				self.nearestGridUnitFromView(event.position())
			)

		elif event.type() == QtCore.QEvent.Type.MouseButtonRelease and event.button() & QtCore.Qt.MouseButton.LeftButton:

			# Handle mouse release
			if self._moved:

				self.sig_active_grid_unit_chosen.emit(
					self.nearestGridUnitFromView(event.position())
				)

			self.sig_active_grid_unit_changed.emit(None)

		return super().eventFilter(watched, event)




