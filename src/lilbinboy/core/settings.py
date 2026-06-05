from PySide6 import QtCore

"""
Manage QSettings location & format
"""

import logging, enum
from os import PathLike
from PySide6 import QtCore

class BSStartupBehavior(enum.StrEnum):

	EMPTY_WINDOW = "Show Empty Window"
	SHOW_BROWSER = "Show File Browser"
	LAST_BIN     = "Open Last Bin"

LATEST_CONFIG_VERSION = 1
"""Latest config version"""

class BSSettingsManager:

	def __init__(self, format:QtCore.QSettings.Format=QtCore.QSettings.Format.IniFormat, basepath:PathLike|None=None, subfolder_name:str|None="config"):

		self._format   = format
		self._basepath = QtCore.QDir(QtCore.QDir(basepath or ".").filePath(subfolder_name))

		logging.getLogger(__name__).debug("Initialized settings manager at %s", self._basepath.absolutePath())

		self._checkVersion()
	
	def basePath(self) -> PathLike:
		"""The current path"""
		return self._basepath
	
	def format(self) -> QtCore.QSettings.Format:
		"""The file format used for settings"""
		return self._format
	
	def settings(self, feature_name:str) -> QtCore.QSettings:
		"""Get a settings handler for a given feature"""

		if self.format() == QtCore.QSettings.Format.IniFormat:
			settings = QtCore.QSettings(self.settingsPath(feature_name), QtCore.QSettings.Format.IniFormat)
			#logging.getLogger(__name__).debug("Initialized settings for %s at %s", feature_name, self.settingsPath(feature_name))
			return settings
		else:
			return QtCore.QSettings(self.format())
	
	def settingsPath(self, feature_name:str) -> PathLike[str]:
		return self._basepath.filePath(feature_name + "_config.ini")
	
	def _checkVersion(self):
		"""Check settings version and migrate if needed"""

		user_settings_ver = self.settings("bs").value("Config/config_version", None, int)

		if not user_settings_ver:
			self.settings("bs").setValue("Config/config_version", LATEST_CONFIG_VERSION)
		elif user_settings_ver != LATEST_CONFIG_VERSION:
			# TODO
			logging.getLogger(__name__).debug("Migrate user config from %i to %i", user_settings_ver, LATEST_CONFIG_VERSION)
	
	def currentSettingsVersion(self) -> int|None:

		current_settings_version = self.settings("bs").value("Config/config_version", None, int)
		logging.getLogger(__name__).debug("Returning config_version: %s", current_settings_version)
		return current_settings_version

	@QtCore.Slot(object)
	def setLastBinPath(self, bin_path:PathLike):

		self.settings("bs").setValue("Session/last_bin", str(bin_path))
		logging.getLogger(__name__).debug("Set last_bin: %s", bin_path)

	def lastBinPath(self) -> PathLike[str]:

		bin_path = self.settings("bs").value("Session/last_bin", None, str)
		logging.getLogger(__name__).debug("Returning last_bin: %s", bin_path)
		return bin_path
	
	@QtCore.Slot(QtCore.QRect)
	def setLastWindowGeometry(self, rect:QtCore.QRect):

		rect_list = [rect.left(), rect.top(), rect.width(), rect.height()]

		self.settings("bs").setValue("Session/last_window_geometry", rect_list)
		logging.getLogger(__name__).debug("Set last_window_geometry: %s", rect_list)
	
	def lastWindowGeometry(self) -> QtCore.QRect|None:

		last_rect = self.settings("bs").value("Session/last_window_geometry", [], list)
		#print(last_rect)

		if not len(last_rect) == 4:
			last_rect = QtCore.QRect()
		
		else:
			top_left = QtCore.QPoint(*map(int, last_rect[0:2]))
			size     = QtCore.QSize (*map(int, last_rect[2:4]))
			last_rect = QtCore.QRect(
				top_left,
				size
			)

		logging.getLogger(__name__).debug("Returning last_window_geomoetry: %s", last_rect)
		return last_rect
	
	@QtCore.Slot(bool)
	def setSoftwareUpdateAutocheckEnabled(self, is_enabled:bool):

		self.settings("bs").setValue("SoftwareUpdates/auto_check_for_updates", bool(is_enabled))
		logging.getLogger(__name__).debug("Set auto_check_for_updates: %s", is_enabled)
	
	def softwareUpdateAutocheckEnabled(self) -> bool:

		is_enabled = self.settings("bs").value("SoftwareUpdates/auto_check_for_updates", True, bool)
		logging.getLogger(__name__).debug("Returning auto_check_for_updates: %s", is_enabled)
		return is_enabled
	
	@QtCore.Slot(bool)
	def setAllColumnsVisible(self, all_columns_visible:bool):

		self.settings("bs").setValue("BinSettingsToggles/show_all_columns", all_columns_visible)
		logging.getLogger(__name__).debug("Set show_all_columns: %s", all_columns_visible)
	
	def allColumnsVisible(self) -> bool:
		
		all_visible = self.settings("bs").value("BinSettingsToggles/show_all_columns", False, bool)
		logging.getLogger(__name__).debug("Returning show_all_columns: %s", all_visible)
		return all_visible
	
	@QtCore.Slot(bool)
	def setAllItemsVisible(self, show_all_items:bool):

		self.settings("bs").setValue("BinSettingsToggles/show_all_items", show_all_items)
		logging.getLogger(__name__).debug("Set show_all_items: %s", show_all_items)
	
	def allItemsVisible(self) -> bool:
		
		all_visible = self.settings("bs").value("BinSettingsToggles/show_all_items", False, bool)
		logging.getLogger(__name__).debug("Returning all_visible: %s", all_visible)
		return all_visible
	
	@QtCore.Slot(bool)
	def setUseSystemAppearance(self, use_system:bool):

		self.settings("bs").setValue("BinSettingsToggles/use_system_appearance", use_system)
		logging.getLogger(__name__).debug("Set use_system_appearance: %s", use_system)
	
	def useSystemAppearance(self) -> bool:
		
		use_system = self.settings("bs").value("BinSettingsToggles/use_system_appearance", False, bool)
		logging.getLogger(__name__).debug("Returning use_system_appearance: %s", use_system)
		return use_system
	
	@QtCore.Slot(int)
	def setMobQueueSize(self, queue_size:int):

		self.settings("bs").setValue("BinLoading/mob_queue_size", queue_size)
		logging.getLogger(__name__).debug("Set mob_queue_size: %s", queue_size)

	def mobQueueSize(self) -> int:
		
		queue_size = self.settings("bs").value("BinLoading/mob_queue_size", 500, int)
		logging.getLogger(__name__).debug("Returning mob_queue_size: %s", queue_size)
		return queue_size
	
	@QtCore.Slot(bool)
	def setUseFancyProgressBar(self, use_animation:bool):

		self.settings("bs").setValue("UserInterface/fancy_progress_bar", use_animation)
		logging.getLogger(__name__).debug("Set fancy_progress_bar: %s", use_animation)

	def useFancyProgressBar(self) -> bool:
		
		use_animation = self.settings("bs").value("UserInterface/fancy_progress_bar", True, bool)
		logging.getLogger(__name__).debug("Returning fancy_progress_bar: %s", use_animation)
		return use_animation
	
	@QtCore.Slot(bool)
	def setUseSavedColumnWidths(self, use_column_widths:bool):

		self.settings("bs").setValue("BinLoading/use_column_widths", use_column_widths)
		logging.getLogger(__name__).debug("Set use_column_widths: %s", use_column_widths)

	def useSavedColumnWidths(self) -> bool:
		
		use_column_widths = self.settings("bs").value("BinLoading/use_column_widths", True, bool)
		logging.getLogger(__name__).debug("Returning use_column_widths: %s", use_column_widths)
		return use_column_widths
	
	@QtCore.Slot(object)
	def setStartupBehavior(self, behavior:BSStartupBehavior):

		self.settings("bs").setValue("Session/start_behavior", behavior)
		logging.getLogger(__name__).debug("Set start_behavior: %s", behavior)

	def startupBehavior(self) -> BSStartupBehavior:
		
		behavior_string = self.settings("bs").value("Session/start_behavior", BSStartupBehavior.SHOW_BROWSER.value, str)
		try:
			behavior = BSStartupBehavior(behavior_string)
		except ValueError:
			behavior = BSStartupBehavior.SHOW_BROWSER
			logging.getLogger(__name__).error("Invalid start_behavior=\"%s\"; default to: \"%s\"", behavior_string, behavior)
			
		logging.getLogger(__name__).debug("Returning start_behavior: %s", behavior)
		return behavior
	
	@QtCore.Slot(int)
	def setBottomScrollbarScale(self, scale_factor:int|float):

		self.settings("bs").setValue("UserInterface/bottom_scrollbar_scale", scale_factor)
		logging.getLogger(__name__).debug("Set bottom_scrollbar_scale: %s", scale_factor)

	def bottomScrollbarScale(self) -> float:
		
		scale_factor = max(0.5, self.settings("bs").value("UserInterface/bottom_scrollbar_scale", 1.25, float))
		logging.getLogger(__name__).debug("Returning bottom_scrollbar_scale: %s", scale_factor)
		return scale_factor
	
	@QtCore.Slot(object)
	def setListItemPadding(self, padding:QtCore.QMarginsF):

		padding_list = [padding.left(), padding.top(), padding.right(), padding.bottom()]

		self.settings("bs").setValue("UserInterface/list_item_padding", padding_list)
		logging.getLogger(__name__).debug("Set list_item_padding: %s", padding_list)

	def listItemPadding(self) -> QtCore.QMargins:
		
		padding = self.settings("bs").value("UserInterface/list_item_padding", [12, 6, 12, 6], list)
		padding = QtCore.QMarginsF(*map(float, padding))

		logging.getLogger(__name__).debug("Returning list_item_padding: %s", padding)
		return padding
	
	@QtCore.Slot(bool)
	def setShowFrameRuler(self, show_ruler:bool):

		self.settings("bs").setValue("BinSettingsToggles/show_frame_ruler", show_ruler)
		logging.getLogger(__name__).debug("Set show_frame_ruler: %s", show_ruler)
	
	def showFrameRuler(self) -> bool:
		
		show_ruler = self.settings("bs").value("BinSettingsToggles/show_frame_ruler", False, bool)
		logging.getLogger(__name__).debug("Returning show_frame_ruler: %s", show_ruler)
		return show_ruler
	
	@QtCore.Slot(bool)
	def setShowFrameMap(self, show_map:bool):

		self.settings("bs").setValue("BinSettingsToggles/show_frame_map", show_map)
		logging.getLogger(__name__).debug("Set show_frame_map: %s", show_map)
	
	def showFrameMap(self) -> bool:
		
		show_map = self.settings("bs").value("BinSettingsToggles/show_frame_map", False, bool)
		logging.getLogger(__name__).debug("Returning show_frame_map: %s", show_map)
		return show_map
	
	@QtCore.Slot(bool)
	def setShowFrameGrid(self, show_grid:bool):

		self.settings("bs").setValue("BinSettingsToggles/show_frame_grid", show_grid)
		logging.getLogger(__name__).debug("Set show_frame_grid: %s", show_grid)
	
	def showFrameGrid(self) -> bool:
		
		show_grid = self.settings("bs").value("BinSettingsToggles/show_frame_grid", False, bool)
		logging.getLogger(__name__).debug("Returning show_frame_grid: %s", show_grid)
		return show_grid
	
	@QtCore.Slot(bool)
	def setUseLiveSift(self, use_live_sift:bool):

		self.settings("bs").setValue("BinSettingsToggles/use_live_sift", use_live_sift)
		logging.getLogger(__name__).debug("Set use_live_sift: %s", use_live_sift)
	
	def useLiveSift(self) -> bool:
		
		use_live_sift = self.settings("bs").value("BinSettingsToggles/use_live_sift", False, bool)
		logging.getLogger(__name__).debug("Returning use_live_sift: %s", use_live_sift)
		return use_live_sift
	
	@QtCore.Slot(bool)
	def setUseSiftCriteria(self, use_sift:bool):

		self.settings("bs").setValue("BinSettingsToggles/use_sift_criteria", use_sift)
		logging.getLogger(__name__).debug("Set use_sift_criteria: %s", use_sift)
	
	def useSiftCriteria(self) -> bool:
		
		use_sift = self.settings("bs").value("BinSettingsToggles/use_sift_criteria", False, bool)
		logging.getLogger(__name__).debug("Returning use_sift_criteria: %s", use_sift)
		return use_sift
	
	@QtCore.Slot(bool)
	def setShowFirstRunMessage(self, show_first_run_message:bool):

		self.settings("bs").setValue("UserInterface/show_first_run_message", show_first_run_message)
		logging.getLogger(__name__).debug("Set show_first_run_message: %s", show_first_run_message)
	
	def showFirstRunMessage(self) -> bool:
		
		show_first_run_message = self.settings("bs").value("UserInterface/show_first_run_message", True, bool)
		logging.getLogger(__name__).debug("Returning show_first_run_message: %s", show_first_run_message)
		return show_first_run_message