import logging, typing
import avb, avbutils
from PySide6 import QtCore

TEMP_POSITION_OFFSET_THING = 10

#class BSBinViewModeManager(QtCore.QObject):
#	"""Manage them viewmodes"""
#
#	sig_view_mode_changed = QtCore.Signal(object)
#	"""The view mode has been changed"""
#
#	def __init__(self, initial_mode:avbutils.BinDisplayModes=avbutils.BinDisplayModes.LIST, *args, **kwargs):
#
#		super().__init__(*args, **kwargs)
#
#		self._current_mode = initial_mode
#
#	@QtCore.Slot(object)
#	def setViewMode(self, view_mode:avbutils.BinDisplayModes):
#		"""Set the current bin view mode"""
#
#		if view_mode != self._current_mode:
#			self._current_mode = view_mode
#			self.sig_view_mode_changed.emit(self._current_mode)
#	
#	def viewMode(self) -> avbutils.BinDisplayModes:
#		return self._current_mode

class BSBinViewManager(QtCore.QObject):

	sig_view_mode_toggled = QtCore.Signal(object)
	"""Binview has been toggled on/off"""

	sig_all_columns_toggled = QtCore.Signal(object)
	"""All columns have been toggled on/off (opposite of `sig_view_mode_toggled`)"""

	sig_bin_filters_toggled = QtCore.Signal(object)
	"""Filters have been toggled on/off"""

	sig_all_items_toggled = QtCore.Signal(object)
	"""All items have been toggled on/off (opposite of `sig_bin_filters_toggled`)"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._default_sort_columns:list[list[int,str]] = []

		self._binview_is_enabled = True
		self._filters_enabled    = True

		# Emit the opposites
		self.sig_view_mode_toggled  .connect(lambda bv_enabled: self.sig_all_columns_toggled.emit(not bv_enabled))
		self.sig_bin_filters_toggled.connect(lambda fl_enabled: self.sig_all_items_toggled  .emit(not fl_enabled))

#	@QtCore.Slot(object)
#	def setDefaultSortColumns(self, sort_settings:list[list[int,str]]):
#
#		self._default_sort_columns = sort_settings

#	def defaultSortColumns(self) -> list[list[int,str]]:
#
#		return self._default_sort_columns
	
	@QtCore.Slot(object)
	def setBinViewEnabled(self, is_enabled:bool):

		if is_enabled != self._binview_is_enabled:

			self._binview_is_enabled = is_enabled
			self.sig_view_mode_toggled.emit(self._binview_is_enabled)
	
	@QtCore.Slot(object)
	def setAllColumnsVisible(self, all_visibile:bool):
		"""Convenience method: Opposite of setBinViewEnabled"""

		self.setBinViewEnabled(not all_visibile)

	@QtCore.Slot(object)
	def setBinFiltersEnabled(self, is_enabled:bool):

		if is_enabled != self._filters_enabled:

			self._filters_enabled = is_enabled
			self.sig_bin_filters_toggled.emit(self._filters_enabled)
	
	@QtCore.Slot(object)
	def setAllItemsVisible(self, all_visible:bool):

		self.setBinFiltersEnabled(not all_visible)


class BSBinDisplaySettingsManager(QtCore.QObject):

	sig_bin_display_changed = QtCore.Signal(object)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

	@QtCore.Slot(object)
	def setBinDisplayFlags(self, bin_display:avbutils.BinDisplayItemTypes):
		
		self.sig_bin_display_changed.emit(bin_display)
		
#class BSBinSortingPropertiesManager(QtCore.QObject):
#	"""Bin sorting"""
#
#	sig_bin_sorting_changed   = QtCore.Signal(object)
#
#	@QtCore.Slot(object)
#	def setBinSortingProperties(self, sorting:list[int,str]):
#		
#		self.sig_bin_sorting_changed.emit([(QtCore.Qt.SortOrder(direction), column_name) for direction, column_name in sorting])

#class BSBinSiftSettingsManager(QtCore.QObject):
#
#	sig_sift_enabled          = QtCore.Signal(bool)
#	sig_bin_view_changed      = QtCore.Signal(object)
#	sig_sift_settings_changed = QtCore.Signal(object)
#
#	@QtCore.Slot(object)
#	def setBinView(self, bin_view:avb.bin.BinViewSetting):
#		self.sig_bin_view_changed.emit(bin_view)
#
#
#	@QtCore.Slot(bool, object)
#	def setSiftSettings(self, sift_enabled:bool, sift_settings:list[avbutils.bins.BinSiftOption]):
#		
#		self.sig_sift_settings_changed.emit(sift_settings)		
#		self.sig_sift_enabled.emit(sift_enabled)

#class BSBinItemsManager(QtCore.QObject):
#	
#	sig_mob_added = QtCore.Signal(object)
#	"""A mob was added to the bin items"""
#
#	sig_mob_count_changed = QtCore.Signal(int)
#	"""Mobs were added or removed"""
#
#	sig_bin_view_changed = QtCore.Signal(object, object)
#
#	def __init__(self, *args, **kwargs):
# 
#		super().__init__(*args, **kwargs)
#
#		self._view_model = viewmodels.BSBinItemViewModel()
#
##		self._frame_scene = QtWidgets.QGraphicsScene()
#		
#		self._view_model.rowsInserted .connect(lambda: self.sig_mob_count_changed.emit(self._view_model.rowCount()))
#		self._view_model.rowsRemoved  .connect(lambda: self.sig_mob_count_changed.emit(self._view_model.rowCount()))
#		self._view_model.modelReset   .connect(lambda: self.sig_mob_count_changed.emit(self._view_model.rowCount()))
#
#	def viewModel(self) -> viewmodels.BSBinItemViewModel:
#		"""Return the internal view model"""
#		return self._view_model
#	
##	@QtCore.Slot(object)
##	def addRow(self, row_data:dict[binitemtypes.BSAbstractViewHeaderItem|str,binitemtypes.BSAbstractViewItem|typing.Any], add_new_headers:bool=False):
##		
##		return self.addRows([row_data], add_new_headers)
#	
#	@QtCore.Slot(object)
#	def addMob(self, mob_info:binitemtypes.BSBinItemInfo):
#		"""Add a single mob (convience method for `self.addMobs(mob_info_list:list[binparser.BinItemInfo])`)"""
#
#		self.addMobs([mob_info])
#		#self.sig_mob_added.emit(mob_info)
#	
#	@QtCore.Slot(object)
#	def addMobs(self, mob_info_list:list[binitemtypes.BSBinItemInfo]):
#		"""Given a `list[binparser.BinItemInfo]` of parsed mobs, add their viewitems to the model"""
#
#		# NOTE: ViewItems are currently determined in BinParser but then double-checked here
#		# Figure out where to actually do that.  I think probably here instead.
#
#		mobs_viewitems = []
#		mobs_framepositions = []
#
#		for mob_info in mob_info_list:
#
#			mobs_framepositions.append(mob_info.frame_coordinates)
#
#			mob_viewitems = dict()
#
#			for field_id, mob_viewitem in mob_info.view_items.items():
#
#				if field_id == 40 and isinstance(mob_viewitem, dict): # User column
#
#					mob_viewitem = {
#						str(user_col_name): binitemtypes.get_viewitem_for_item(user_col_data)
#						for user_col_name, user_col_data in mob_viewitem.items()
#					}
#				
#				else:
#					mob_viewitem = binitemtypes.get_viewitem_for_item(mob_viewitem)
#					
#				mob_viewitems[field_id] = mob_viewitem
#
#			mobs_viewitems.append(mob_viewitems)
#		
#		self._view_model.addBinItems(mobs_viewitems, mobs_framepositions)