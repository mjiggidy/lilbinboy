"""
The big fella
"""

import logging, typing
import avb, avbutils

from PySide6 import QtCore, QtGui, QtWidgets

from ..core import icon_registry

from . import proxystyles, scrollwidgets, widgetbars

from ..textview import bincompositemodel, textview
from ..frameview import frameview
from ..scriptview import scriptview, scriptproxy

from ..binview import binviewitemtypes, binviewmodel
from ..binitems import binitemtypes, binitemsmodel

from ..binfilters import bindisplayproxymodel, binviewproxymodel
from ..binfilters.siftfilter import siftproxymodel, sifters, siftmatchtypes

from ..siftwidget import scopesmodel

from ..core.config import BSTextViewModeConfig, BSFrameViewModeConfig, BSScriptViewModeConfig

from ..widgets import binviewcombobox

class BSBinContentsWidget(QtWidgets.QWidget):
	"""Display bin contents and controls"""

	sig_view_mode_changed        = QtCore.Signal(object)
	sig_bin_palette_changed      = QtCore.Signal(QtGui.QPalette)
	sig_bin_font_changed         = QtCore.Signal(QtGui.QFont)
	sig_bin_model_changed        = QtCore.Signal(object)
	sig_focus_set_on_column      = QtCore.Signal(int)	# Logical column index
	sig_bin_stats_updated        = QtCore.Signal(str)
	sig_bin_view_enabled         = QtCore.Signal(bool)
	sig_bin_view_source_selected = QtCore.Signal(object)
	sig_live_sift_enabled        = QtCore.Signal(bool)

	def __init__(self, *args, bin_items_model:binitemsmodel.BSBinItemModel, bin_view_model:binviewmodel.BSBinViewModel, **kwargs):

		super().__init__(*args, **kwargs)

		self.setAutoFillBackground(True)

		self.setLayout(QtWidgets.QVBoxLayout())
		self.layout().setContentsMargins(0,0,0,0)
		self.layout().setSpacing(0)
		
		# Initial bin items and bin columns data models and their filters

		self._bin_items_model  = bin_items_model
		self._bin_items_filter = bindisplayproxymodel.BSBinDisplayFilterProxyModel(
			bin_items_model=self._bin_items_model,
			parent=self
		)
		
		self._bin_view_model   = bin_view_model
		self._bin_view_filter  = binviewproxymodel.BSBinViewFilterProxyModel(
			bin_columns_model=self._bin_view_model,
			parent=self
		)

		# Filtered bin items and bin view columns get combined into a composite table view model

		self._bin_composite_model = bincompositemodel.BSBinCompositeModel(
			item_model=self._bin_items_filter,
			view_model=self._bin_view_filter,
			parent=self
		)

		# The composite model gets filtered by Sift and Find In Bin

		self._bin_sift_filter = siftproxymodel.BSBinSiftFilterProxyModel(parent=self)	# TODO
		self._bin_sift_filter.setSourceModel(self._bin_composite_model)

		self._bin_find_filter = siftproxymodel.BSBinSiftFilterProxyModel(parent=self, sift_criteria=[[sifters.BSAnyColumnSifter()]])
		self._bin_find_filter.setSourceModel(self._bin_sift_filter)

		# Final model is QIdentityProxyModel, which does nothing new but serves as the 
		# intentional end of the chain to which views may subscribe.  Indubitably!  Pip pip!
		
		self._bin_model_final = QtCore.QIdentityProxyModel(parent=self)
		self._bin_model_final.setSourceModel(self._bin_find_filter)

		self._test_scriptmodel = scriptproxy.BSScriptViewProxyModel(parent=self)
		self._test_scriptmodel.setSourceModel(self._bin_model_final)


		self._selection_model     = QtCore.QItemSelectionModel(
			model=self._bin_model_final,
			parent=self
		)

		# Save initial palette for later togglin'
		self._default_palette   = self.palette()
		self._bin_palette       = self.palette()
		self._default_font      = self.font()
		self._bin_font          = self.font()
		
		self._use_bin_appearance    = True
		self._use_bin_column_widths = BSTextViewModeConfig.USE_BIN_COLUMN_WIDTHS

		self._section_top       = widgetbars.BSBinContentsTopWidgetBar()
		self._section_main      = QtWidgets.QStackedWidget()
		
		# Main View Mode Widgets
		self._viewmode_text     = textview.BSBinTextView()
		self._viewmode_frame    = frameview.BSBinFrameView()
		self._viewmode_script   = scriptview.BSBinScriptView()

		# Footers
		self._binstats_text = scrollwidgets.BSBinStatsLabel(
			filter_model       = self._bin_model_final,
			source_items_model = self._bin_items_model,
			source_cols_model  = self._bin_view_model
		)
		self._binstats_frame = scrollwidgets.BSBinStatsLabel(
			filter_model       = self._bin_model_final,
			source_items_model = self._bin_items_model,
			source_cols_model  = self._bin_view_model,
			stat_strings       = [self.tr("Showing {filtered_item_count} of {source_item_count} items")]
		)

		# Create proxy style from application style for potential horizontal scrollbar height mods
		self._proxystyle_hscroll = proxystyles.BSScrollBarStyle(parent=self)

		self._setupWidgets()

		self._setupTextViewMode()
		self._setupFrameViewMode()
		self._setupScriptViewMode()

		self._setupSignals()
#		self._setupActions()
		
#		self._setupBinModel()

	def _setupWidgets(self):

		# Top Tool Bar
		self._section_top._sld_frame_scale .setRange(BSFrameViewModeConfig.DEFAULT_FRAME_ZOOM_RANGE.start,   BSFrameViewModeConfig.DEFAULT_FRAME_ZOOM_RANGE.stop)
		self._section_top._sld_script_scale.setRange(BSScriptViewModeConfig.DEFAULT_SCRIPT_ZOOM_RANGE.start, BSScriptViewModeConfig.DEFAULT_SCRIPT_ZOOM_RANGE.stop)

		self.layout().addWidget(self._section_top)

		# Main Text, Frame, and Script views
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.LIST),   self._viewmode_text)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.FRAME),  self._viewmode_frame)
		self._section_main.insertWidget(int(avbutils.BinDisplayModes.SCRIPT), self._viewmode_script)
		
		self.layout().addWidget(self._section_main)

	def _setupTextViewMode(self):
		

		# Models
		self._viewmode_text.setModel(self._bin_model_final)
		self._viewmode_text.setSelectionModel(self._selection_model) # NOTE: Call after setModel()
		
		# Delegates
		self._viewmode_text.setBinItemIconRegistry(icon_registry.BIN_ITEM_TYPE_ICON_REGISTRY)

		# Scroll bars
		self._viewmode_text.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._viewmode_text.horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._viewmode_text.addScrollBarWidget(self._binstats_text,  QtCore.Qt.AlignmentFlag.AlignLeft)

		# Signals
		self._viewmode_text.sig_hide_column_requested.connect(self.hideBinColumn)

	def _setupFrameViewMode(self):

		# Scene from model
		bin_frame_scene     = frameview.BSBinFrameScene(
			bin_filter_model = self._bin_model_final,
			brushes_manager  = frameview.painters.BSFrameItemBrushManager(parent=self._viewmode_frame),
		)
		self._viewmode_frame.setScene(bin_frame_scene)

		# Initial settings sync
		self._viewmode_frame.setZoomRange(BSFrameViewModeConfig.DEFAULT_FRAME_ZOOM_RANGE)
		self._viewmode_frame.setZoom(BSFrameViewModeConfig.DEFAULT_FRAME_ZOOM_START)

		# Scroll bars
		self._viewmode_frame .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._viewmode_frame.addScrollBarWidget(self._binstats_frame, QtCore.Qt.AlignmentFlag.AlignLeft)
		
		# Signals
		self._viewmode_frame.sig_zoom_level_changed.connect(self._section_top._sld_frame_scale.setValue)
		self._viewmode_frame.sig_zoom_range_changed.connect(lambda r: self._section_top._sld_frame_scale.setRange(r.start, r.stop))

	def _setupScriptViewMode(self):

		# Models
		self._viewmode_script.setModel(self._test_scriptmodel)
#		self._viewmode_script.setSelectionModel(self._selection_model)

		# Delegates
		self._viewmode_script.setBinItemIconRegistry(icon_registry.BIN_ITEM_TYPE_ICON_REGISTRY)
		
		# Scroll bars
		self._viewmode_script.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._viewmode_script.horizontalScrollBar().setStyle(self._proxystyle_hscroll)

		# Signals
		self._viewmode_script.sig_frame_scale_changed      .connect(self._section_top._sld_script_scale.setValue)
#		self._viewmode_script.sig_frame_scale_range_changed.connect(lambda r: self._section_top._sld_script_scale.setRange(r.start, r.stop))
		self._viewmode_script.sig_hide_column_requested .connect(self.hideBinColumn)



	def _setupSignals(self):

		self._section_top.sig_frame_scale_changed.connect(self._viewmode_frame.setZoom)
		self._section_top.sig_script_scale_changed.connect(self._viewmode_script.setFrameScale)

		# NOTE: Maybe do this different?
		self._bin_view_model.sig_bin_view_info_set.connect(self.binViewChanged)

	def setShowColumnEditorAction(self, action:QtGui.QAction):
		"""Show column editor needs a global action"""

		self._viewmode_text.setShowColumnEditorAction(action)
		self._viewmode_script.setShowColumnEditorAction(action)

	###
	# View Mode Widgets
	###

	def binViewSelector(self) -> binviewcombobox.BSBinViewSelectorComboBox:
		"""You know.  The little bin view drop-down thingy."""
		
		return self._section_top.binViewSelector()

	def textView(self) -> textview.BSBinTextView:
		"""Text View Mode widget"""

		return self._viewmode_text
	
	def frameView(self) -> frameview.BSBinFrameView:
		"""Frame View Mode widget"""

		return self._viewmode_frame

	def scriptView(self) -> scriptview.BSBinScriptView:
		"""Script View Mode widget"""
		
		return self._viewmode_script
	
	def beginChangeViewMode(self):

		current_view_mode = self.viewMode()

		if current_view_mode == avbutils.BinDisplayModes.LIST:

			self._viewmode_text.setUpdatesEnabled(False)

		elif current_view_mode == avbutils.BinDisplayModes.FRAME:

			# Sync selection back to selection model

			self._selection_model.clearSelection()

			item_selection = QtCore.QItemSelection()

			for row, item in enumerate(self._viewmode_frame.scene()._bin_items):

				if not item.isSelected():
					continue

				item_selection.append(QtCore.QItemSelectionRange(
					self._bin_model_final.index(row, 0, QtCore.QModelIndex())
				))
			
			self._selection_model.select(
				item_selection,
				QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect | \
				QtCore.QItemSelectionModel.SelectionFlag.Rows
			)

			self._viewmode_frame.setUpdatesEnabled(False)
		
		elif current_view_mode == avbutils.BinDisplayModes.SCRIPT:

			# Sync selection back to selection model

			self._selection_model.select(
				self._viewmode_script.model().mapSelectionToSource(
					self._viewmode_script.selectionModel().selection()
				),
				QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect
			)

			self._viewmode_script.setUpdatesEnabled(False)
	
	def viewModeChanged(self):
		
		current_view_mode = self.viewMode()

		if current_view_mode  == avbutils.bins.BinDisplayModes.LIST:

			self._viewmode_text.setUpdatesEnabled(True)

		elif current_view_mode == avbutils.bins.BinDisplayModes.FRAME:

			self._viewmode_frame.scene().setSelectedItems(
				set(x.row() for x in self._selection_model.selectedIndexes())
			)

			self._viewmode_frame.setUpdatesEnabled(True)

		elif current_view_mode == avbutils.bins.BinDisplayModes.SCRIPT:

			# Sync header widths
			for col in filter(
				lambda c: not self._viewmode_text.header().isSectionHidden(c),
				range(self._viewmode_text.header().count())
			):

				col_size = self._viewmode_text.header().sectionSize(col)
				self._viewmode_script.header().resizeSection(col+1, col_size)

			# Sync selection models
			self._viewmode_script.selectionModel().select(
				self._test_scriptmodel.mapSelectionFromSource(
					self._viewmode_text.selectionModel().selection()
				),
				QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect,
			)

			self._viewmode_script.setUpdatesEnabled(True)

		self.sig_view_mode_changed.emit(current_view_mode)

	
	@QtCore.Slot(object)
	def setViewMode(self, view_mode:avbutils.BinDisplayModes):
		"""Set the current bin view mode"""

		logging.getLogger(__name__).debug("Setting bin view mode to %s", str(view_mode))
		
		old_view_mode = avbutils.bins.BinDisplayModes(self._section_main.currentIndex())
		
		if old_view_mode == view_mode:
			return

		self.beginChangeViewMode()

		self._section_main.setCurrentIndex(view_mode)
		self._section_top .setViewMode(view_mode)

		self.viewModeChanged()

	def viewMode(self) -> avbutils.BinDisplayModes:
		"""Current view mode"""

		return avbutils.BinDisplayModes(self._section_main.currentIndex())
	

	###
	# Bin Views and Filters
	###

#	@QtCore.Slot(avbutils.bins.BinDisplayItemTypes)
#	def setBinDisplayItemTypes(self, item_types:avbutils.bins.BinDisplayItemTypes):
#		
#		self._bin_items_filter.setAcceptedItemTypes(item_types)

	@QtCore.Slot(object)
	def binViewChanged(self):

		self.setTextColumnWidthsFromBin()

#		self.siftFilter().resetSiftCriteria()

	@QtCore.Slot(bool)
	def setBinColumnFiltersDisabled(self, are_disabled:bool):

		self.setBinColumnFiltersEnabled(not are_disabled)

	@QtCore.Slot(bool)
	def setBinColumnFiltersEnabled(self, are_enabled:bool):

		self._bin_view_filter.setEnabled(are_enabled)

		self.sig_bin_view_enabled.emit(are_enabled)

	@QtCore.Slot(bool)
	def setBinItemFiltersEnabled(self, are_enabled:bool):

		#print("TO DO")
		self._bin_items_filter.setEnabled(are_enabled)
		self._bin_sift_filter.setEnabled(are_enabled)

	@QtCore.Slot(int)
	def hideBinColumn(self, logical_index:int):

		self._bin_model_final.setHeaderData(logical_index, QtCore.Qt.Orientation.Horizontal, True, binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

	@QtCore.Slot()
	@QtCore.Slot(str)
	def setSearchText(self, search_text:str):

		search_text = search_text if search_text.strip() else ""

		sift_criterion = sifters.BSAnyColumnSifter(
			sift_string = search_text,
			match_type = siftmatchtypes.BSSiftMatchTypes.Contains,
		)
		
		self._bin_find_filter.setSiftCriteria([[sift_criterion]])

	@QtCore.Slot(dict)
	def setTextColumnWidthsFromBin(self, column_widths:dict[str,int]|None=None):
		"""Set text view column widths from avid bin `dict[column_name:str, width:int]` or autosize if not there"""

		if column_widths and self._use_bin_column_widths:

			logging.getLogger(__name__).debug("Setting column widths from: %s", column_widths)

			for idx_logical in range(self.textView().header().count()):

				column_name = self.textView().model().headerData(idx_logical, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.DisplayNameRole)

				if column_name in column_widths:

					logging.getLogger(__name__).debug("Setting column %s (%s) to width %s", column_name, idx_logical, column_widths[column_name])
					self.textView().setColumnWidth(idx_logical, column_widths[column_name])
					
				
				else:

					self.textView().resizeColumnToContents(idx_logical)
					logging.getLogger(__name__).debug("Set column %s (%s) to auto-fit width %s", column_name, idx_logical, self.textView().header().sectionSize(idx_logical))


		else:
			# Resize all columns to contents
			logging.getLogger(__name__).debug("Auto-sizing all columns")
			self.textView().header().resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)


	###
	# The filters
	###
	
	def siftFilter(self) -> siftproxymodel.BSBinSiftFilterProxyModel:
		"""Bin sift filter"""

		return self._bin_sift_filter
	
	def itemDisplayFilter(self) -> bindisplayproxymodel.BSBinDisplayFilterProxyModel:
		"""Bin display items filter"""

		return self._bin_items_filter
	
	def columnsFilter(self) -> binviewproxymodel.BSBinViewFilterProxyModel:
		"""Bin view columns filter"""

		return self._bin_view_filter


	###
	# Bin Appearance
	###

	def useSavedBinColumnWidths(self) -> bool:
		"""Initially load saved bin column widths or nah"""

		return self._use_bin_column_widths
	
	@QtCore.Slot(bool)
	def setUseSavedBinColumnWidths(self, use_saved_widths:bool):
		"""Initially load saved bin column widths or nah.  False will auto-fit columns."""

		if self._use_bin_column_widths == use_saved_widths:
			return
		
		self._use_bin_column_widths = use_saved_widths

	@QtCore.Slot(QtGui.QPalette)
	def setBinPalette(self, palette:QtGui.QPalette):
		"""Set the color palette for the bin"""

		if self._bin_palette == palette:
			return
		
		self.setPalette(palette)
		self._bin_palette = palette
		self.sig_bin_palette_changed.emit(palette)
	
	@QtCore.Slot(QtGui.QFont)
	def setBinFont(self, bin_font:QtGui.QFont):
		"""Set the font for the bin"""
		
		if self._bin_font == bin_font:
			return
		
		self._bin_font = bin_font # TODO: Neeeded?
		
		self._viewmode_text   .setFont(bin_font)
		self._viewmode_frame  .setFont(bin_font)
		self._viewmode_script .setFont(bin_font)
		
		self.sig_bin_font_changed.emit(bin_font)

	###
	# Misc
	###

	@QtCore.Slot(object)
	def setItemPadding(self, padding:QtCore.QMarginsF):
		"""Set text item padding"""

		self._viewmode_text  .setItemPadding(padding)
		self._viewmode_script.setItemPadding(padding)

	@QtCore.Slot(object)
	def focusBinColumn(self, column_info:binviewitemtypes.BSBinViewColumnInfo) -> bool:

		for col in range(self._bin_model_final.columnCount(QtCore.QModelIndex())):

			if self._bin_model_final.headerData(col, QtCore.Qt.Orientation.Horizontal, binviewitemtypes.BSBinViewColumnInfoRole.RawColumnInfo) == column_info:

				self._section_main.currentWidget().setFocus()
				self._viewmode_text.selectSection(col)

				# Get the index of the top visible row
				vertical_offset = self._viewmode_text.verticalScrollBar().value()

				self._viewmode_text.scrollTo(
					self._bin_model_final.index(0, col, QtCore.QModelIndex()),
					QtWidgets.QTreeView.ScrollHint.PositionAtCenter
				)

				self._viewmode_text.verticalScrollBar().setValue(vertical_offset)

				self.sig_focus_set_on_column.emit(col)

				return
		
		QtWidgets.QApplication.beep()

		return False

	###
	# Scrollbar widgets
	###

	def addScrollBarWidget(self, widget:QtWidgets.QWidget, view_mode:avbutils.bins.BinDisplayModes):

		widget.setFixedWidth(self._proxystyle_hscroll.pixelMetric(QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent))
		self._section_main.widget(view_mode).scrollArea().addScrollBarWidget(widget, QtCore.Qt.AlignmentFlag.AlignLeft)

	
	@QtCore.Slot(int)
	@QtCore.Slot(float)
	def setBottomScrollbarScaleFactor(self, scale_factor:int|float):

		self._proxystyle_hscroll.setScrollbarScaleFactor(scale_factor)

		# .update()/.polish() doesn't work. Need to re-set each time?
		self._viewmode_text  .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._viewmode_frame .horizontalScrollBar().setStyle(self._proxystyle_hscroll)
		self._viewmode_script.horizontalScrollBar().setStyle(self._proxystyle_hscroll)
	
	def scrollbarScaler(self) -> proxystyles.BSScrollBarStyle:
		"""The scaler for the horizontal scroll bar"""

		return self._proxystyle_hscroll
	
	def topWidgetBar(self) -> widgetbars.BSBinContentsTopWidgetBar:
		return self._section_top