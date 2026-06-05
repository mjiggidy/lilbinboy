"""
I guess I need to describe pieces of grids now lol what is my life
"""

import dataclasses, enum

from PySide6 import QtCore

class BSGridTickType(enum.IntEnum):
	"""Type of tick tocked"""

	MAJOR = enum.auto()
	MINOR = enum.auto()
	HINT  = enum.auto()

@dataclasses.dataclass(frozen=True)
class BSGridTickInfo:
	"""Grid tick info.  Like, a grid line or something I guess."""

	local_offset: int|float
	"""Pixel offset from widget rect"""

	scene_offset: int|float
	"""Scene offset from origin"""

	tick_label:   str
	"""Label to print"""

	tick_type:    BSGridTickType = BSGridTickType.MAJOR
	"""Type o' the tick"""

@dataclasses.dataclass(frozen=True)
class BSGridSystemInfo:
	"""Grid info for drawing a BSBinFrameView"""

	unit_size       :QtCore.QSizeF
	"""Distance per unit"""

	unit_divisions  :QtCore.QPoint
	"""Divisions per unit"""

	@property
	def unit_step(self) -> QtCore.QPointF:
		"""Distance per unit division"""

		return QtCore.QPointF(
			self.unit_size.width() / self.unit_divisions.x(),
			self.unit_size.height() / self.unit_divisions.y()
		)

	def snapToGrid(self, unsnapped_coords:QtCore.QPointF, use_divisions:bool=False) -> QtCore.QPointF:
		"""Find the coordinate of the grid unit containing a given coordinate"""

		unit_width  = self.unit_step.x() if use_divisions else self.unit_size.width()
		unit_height = self.unit_step.y() if use_divisions else self.unit_size.height()

		return QtCore.QPointF(
			unsnapped_coords.x() - unsnapped_coords.x() % unit_width,
			unsnapped_coords.y() - unsnapped_coords.y() % unit_height
		)