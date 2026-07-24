import avbutils
from PySide6 import QtCore, QtWidgets

class BSApplicationConfig:
	"""Lil' Bin Boy Global Config"""

	APPLICATION_NAME    = "Lil' Bin Boy"
	"""Name o' the app"""

	APPLICATION_VERSION = QtCore.QVersionNumber(0,0,27)
	"""Version Number (major.minor.revision)"""

	APPLICATION_STORAGE_PATH = QtCore.QStandardPaths.StandardLocation.AppDataLocation
	"""`QtCore.QStandardPaths.StandardLocation` for settings, logs, and databases"""

	LOG_FILE_NAME       = "bs_main.log"
	
	ORGANIZATION_NAME   = "GlowingPixel"
	"""Maybe it should just be Michael"""

	ORGANIZATION_DOMAIN = "glowingixel.com"
	"""NOT reverse-domain I guess"""

	UI_THEME            = "Fusion"
	"""`QStyle` theme name"""

class BSTextViewModeConfig:
	"""Bin Text View Mode Config"""

	DEFAULT_ITEM_PADDING:QtCore.QMargins = QtCore.QMargins(16,4,16,4)
	"""Default padding inside view item"""

	DEFAULT_SELECTION_BEHAVIOR = QtWidgets.QTreeView.SelectionBehavior.SelectRows
	"""Default selection behavior (select rows, columns, or items)"""

	DEFAULT_SELECTION_MODE     = QtWidgets.QTreeView.SelectionMode.ExtendedSelection
	"""Default selection mode (continuous, extended, etc)"""

	USE_BIN_COLUMN_WIDTHS = True
	"""Apply initial column widths saved with the bin, if available"""

	ALLOW_KEEP_CURRENT_SELECTION_BETWEEN_MODES = False
	"""Maintain selected items when changing between selection modes (rows/colums/items)"""
	# NOTE: There's a bool at work in the logic as well -- both'll need to be True

	# NOT USED? =====
	SELECTION_BEHAVIOR_MODIFIER_KEY:QtCore.Qt.KeyboardModifier = QtCore.Qt.KeyboardModifier.AltModifier # NOT USED?
	BINVIEW_COLUMN_WIDTH_ADJUST:int = 64	# NOT USED?
	"""Adjust binview-specified column widths for better fit"""

class BSFrameViewModeConfig:
	"""Bin Frame View Mode Config"""

	GRID_UNIT_SIZE     = QtCore.QSizeF(17,14) # 18x12 in scene units
	"""Unit size in scene coordinates"""

	GRID_DIVISIONS     = QtCore.QPoint(3,3)   # 3 ticks along X and Y
	"""Divisions per grid unit"""

	DEFAULT_ITEM_FLAGS = \
		QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable|\
		QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable|\
		QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable
	"""Default item flags"""

	DEFAULT_FRAME_ZOOM_RANGE  = avbutils.bins.THUMB_FRAME_MODE_RANGE
	DEFAULT_FRAME_ZOOM_START  = DEFAULT_FRAME_ZOOM_RANGE.start

	DEFAULT_ITEM_MARGINS = QtCore.QMarginsF(*[0.25]*4)


class BSScriptViewModeConfig:
	"""Bin Script View Mode Config"""

	DEFAULT_SCRIPT_ZOOM_RANGE   = avbutils.bins.THUMB_SCRIPT_MODE_RANGE
	DEFAULT_SCRIPT_ZOOM_START   = avbutils.bins.THUMB_SCRIPT_MODE_RANGE.start
	DEFAULT_SCRIPT_ASPECT_RATIO = QtCore.QSizeF(16,9)
	DEFAULT_ITEM_PADDING:QtCore.QMargins = QtCore.QMargins(16,4,16,4)
	"""Default padding inside view item"""

	FRAME_SIZE_SCALER = 1.25
	"""Additional scaler to control frame size -- possibly pixel density-dependent"""

	DEFAULT_COLUMN_RESIZE_MODE = QtWidgets.QHeaderView.ResizeMode.ResizeToContents
	"""Default mode for Script view column resizing"""

class BSSoftwareUpdatesConfig:
	"""Config for software updates"""

	URL_RELEASES = "https://api.github.com/repos/mjiggidy/lilbinboy/releases"
	"""GitHub API Releases URL"""