from __future__ import annotations
import typing, logging
import avbutils

from PySide6 import QtGui

from . import icon_engines


if typing.TYPE_CHECKING:
	import os

PROPERTY_ICON_PALETTED = "icon_paletted"
"""Custom Property Key containing a resource path to a paletted SVG"""

def getPalettedIconEngine(action:QtGui.QAction) -> icon_engines.BSAbstractPalettedIconEngine|None:
	"""A QAction could have a path to a paletted SVG set as a custom propery: `PROPERTY_ICON_PALETTED`"""

	path_icon = action.property(PROPERTY_ICON_PALETTED)
	return icon_engines.BSPalettedSvgIconEngine(path_icon) if path_icon else None


class BSIconProvider:
	"""Provide `QIcon` handles based on key lookup"""

	# NOTE: Basically a cache for related QIconEngines
	# For example: One IconProvider handles all "clip type" icons in a treeview
	# Another would handle all view mode icons for a main window.  That kinda thing.

	def __init__(self):

		self._icons:dict[typing.Hashable, QtGui.QIcon] = dict()
		"""QIcon per key"""

	def icons(self) -> dict[typing.Hashable, QtGui.QIcon]:
		return self._icons

	def addIcon(self, key:typing.Hashable, icon:QtGui.QIcon):
		"""Add a `QIcon` for a key"""
		self._icons[key] = icon

	# NOTE: Plan to override this is subclasses I think
	def getIcon(self, key:typing.Hashable) -> QtGui.QIcon:
		"""Given a key, lookup and return an existing `QIcon`, or return invalid"""

		if key not in self._icons:
			# NOTE: Returns invalid `QIcon()`
			# TODO: Generate and add icon
			return QtGui.QIcon()

		return self._icons[key]
	
class BSStyledIconProvider(BSIconProvider):

	def getIcon(self, bin_item_hash:typing.Hashable) -> QtGui.QIcon:
		"""Virtual Function: Return an icon for the current palette"""

		return self._icons[bin_item_hash]
	
class BSStyledMarkerIconProvider(BSStyledIconProvider):

	def getIcon(self, marker_color:QtGui.QColor, palette:QtGui.QPalette):

		#print("Del got ", marker_color)

		marker_color_hash = hash(marker_color.toTuple() if marker_color.isValid() else -1) + palette.cacheKey()

		if not marker_color_hash in self._icons:

			self.addIcon(
				marker_color_hash,
				icon_engines.BSPalettedMarkerIconEngine(
					marker_color=marker_color,
					border_width=1,
					palette=palette
				)
			)

		return super().getIcon(marker_color_hash)
	
class BSStyledClipColorIconProvider(BSStyledIconProvider):

	def getIcon(self, clip_color:QtGui.QColor, palette:QtGui.QPalette) -> QtGui.QIcon:

		clip_color_hash = hash(clip_color.toTuple() if clip_color.isValid() else -1) + palette.cacheKey()

		if not clip_color_hash in self._icons:

			self.addIcon(
				clip_color_hash,
				icon_engines.BSPalettedClipColorIconEngine(
					palette=palette,
					clip_color=clip_color,
					border_width=1 # NOTE: Maybe set this in the constructor or something
				)
			)
			logging.getLogger(__name__).debug("%s created icon %s", repr(self), repr(self._icons[clip_color_hash]))

		return super().getIcon(clip_color_hash)

class BSStyledBinItemTypeIconProvider(BSStyledIconProvider):

	# TODO: More like a generic SVG lookup probably

	EXTRA_FLAGS = avbutils.bins.BinDisplayItemTypes.USER_CLIP | avbutils.bins.BinDisplayItemTypes.REFERENCE_CLIP
	"""Extra bin item flags to remove before icon lookup"""

	def __init__(self, *args, path_registry:dict[avbutils.bins.BinDisplayItemTypes, os.PathLike[str]]|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._item_paths_registry: dict[avbutils.bins.BinDisplayItemTypes, os.PathLike[str]] = path_registry or dict()
		"""SVG Resource Path Lookup per `BinDisplayItemTypes` thingy"""

		self._default_svg_path:os.PathLike[str] = None
		"""Optional default path (or `None`) if no icon registered for type"""
	
	def iconPathForBinItemType(self, bin_item:avbutils.bins.BinDisplayItemTypes) -> os.PathLike[str]|None:
		"""Get the path for a given bin item type"""

		# Remove any extra flags before lookup
		bin_item_flags = bin_item & ~self.EXTRA_FLAGS
		
		# NOTE: Being that `BinDisplayItemTypes` is a flag, maybe do this fancier
		# by compositing different decorations together
		return self._item_paths_registry.get(bin_item_flags, self._default_svg_path)
	
	def setIconPathForBinItemType(self, bin_item:avbutils.bins.BinDisplayItemTypes, icon_path:os.PathLike[str]):
		"""Set an icon path for a given bin item type"""

		logging.getLogger(__name__).debug("Adding icon path %s for %s", icon_path, repr(bin_item))
		self._item_paths_registry[bin_item] = icon_path

	def getIcon(self, bin_item_type:avbutils.bins.BinDisplayItemTypes, palette:QtGui.QPalette):

		bin_item_hash = hash(bin_item_type) + palette.cacheKey()

		if bin_item_hash not in self._icons:

			icon_path = self.iconPathForBinItemType(bin_item_type) or self._default_svg_path
			
			if icon_path:
				icon = QtGui.QIcon(
					icon_engines.BSPalettedSvgIconEngine(svg_path=icon_path, palette=palette)
				)
			else:
				icon = QtGui.QIcon()
			
			self.addIcon(bin_item_hash, icon)

		return super().getIcon(bin_item_hash)