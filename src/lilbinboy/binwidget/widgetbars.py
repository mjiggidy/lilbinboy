"""
Widget bar for the top o' the bin widget
"""

import avbutils

from PySide6 import QtCore, QtGui, QtWidgets
from ..widgets import buttons, sliders, binviewcombobox, loadingbar

# I Think I Overthought This: The Module
#
# But at one point I imagined a modular tool bar implemented 
# as a `QToolBar` that could be pulled out or rearranged
# or docked at the bottom or maybe you have two or whatever
#
# But QToolBars are for actions and I don't really like 
# most of these as actions soooo

class BSAbstractBinContentsWidgetBar(QtWidgets.QWidget):
	"""Widget bar to display above/below"""

	# TODO: I don't know lol might want this later

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setSizePolicy(
			self.sizePolicy().horizontalPolicy(),
			QtWidgets.QSizePolicy.Policy.Maximum
		)

	def addWidget(self, widget:QtWidgets.QWidget):
		"""
		Add a widget to the layout.
		Doing this while I decide if this is a QToolBar or not.
		"""

		if isinstance(self, QtWidgets.QToolBar):
			super().addWidget(widget)
		else:
			self.layout().addWidget(widget)

class BSBinContentsTopWidgetBar(BSAbstractBinContentsWidgetBar):
	"""Default top widget bar"""

	sig_search_text_changed  = QtCore.Signal(object)
	"""Search text has changed"""

	sig_binview_selected     = QtCore.Signal(object)
	"""User changed the binview"""

	sig_frame_scale_changed  = QtCore.Signal(int)
	"""User changed frame thumb scale slider"""

	sig_script_scale_changed = QtCore.Signal(int)
	"""User changed script thumb scale slider"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		#if not isinstance(self, QtWidgets.QToolBar):
		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setContentsMargins(QtCore.QMargins(*[4]*4))

		self._btngrp_file         = QtWidgets.QButtonGroup()
		self._btn_open            = buttons.BSActionPushButton()
		self._btn_reload          = buttons.BSActionPushButton(show_text=False)
		self._btn_stop            = buttons.BSActionPushButton(show_text=False)

		self._prg_loading         = loadingbar.BSAnimatedProgressBar()

		self._btngrp_viewmode     = QtWidgets.QButtonGroup()
		self._btn_viewmode_list   = buttons.BSPalettedActionPushButton(show_text=False)
		self._btn_viewmode_frame  = buttons.BSPalettedActionPushButton(show_text=False)
		self._btn_viewmode_script = buttons.BSPalettedActionPushButton(show_text=False)

		# View Mode-Specific Controls
		self._mode_controls       = QtWidgets.QStackedWidget()
		self._cmb_binviews        = binviewcombobox.BSBinViewSelectorComboBox()   # Shown on List and Script
		self._sld_frame_scale     = sliders.ViewModeSlider() # Shown on Frame
		self._sld_script_scale    = sliders.ViewModeSlider() # Shown on Script

		self._txt_search          = QtWidgets.QLineEdit()

		self._setupWidgets()
		self._setupSignals()

	def _setupWidgets(self):

		self._btngrp_file.addButton(self._btn_open)
		self._btngrp_file.addButton(self._btn_reload)
		self._btngrp_file.addButton(self._btn_stop)

		self.addWidget(buttons.BSPushButtonActionBar(self._btngrp_file))

		pol = self._prg_loading.sizePolicy()
		pol.setRetainSizeWhenHidden(True)
		self._prg_loading.setSizePolicy(pol)
		self._prg_loading.setRange(0,0)
		self._prg_loading.setHidden(True)

		self.addWidget(self._prg_loading)

		self._cmb_binviews.setSizePolicy(self._cmb_binviews.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		self._cmb_binviews.setMinimumWidth(self._cmb_binviews.fontMetrics().averageCharWidth() * 24)
		self._cmb_binviews.setMaximumWidth(self._cmb_binviews.fontMetrics().averageCharWidth() * 32)
		self._cmb_binviews.addItem("")
		self._cmb_binviews.insertSeparator(1)

		# View Mode-Specific Controls
		self._mode_controls.addWidget(self._cmb_binviews)
		self._mode_controls.addWidget(self._sld_frame_scale)
		self._mode_controls.addWidget(self._sld_script_scale)
		self._mode_controls.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.MinimumExpanding)

		self.addWidget(self._mode_controls)

		self._btn_viewmode_list  .setIconSize(QtCore.QSize(16,16))
		self._btn_viewmode_frame .setIconSize(QtCore.QSize(16,16))
		self._btn_viewmode_script.setIconSize(QtCore.QSize(16,16))

		self._btngrp_viewmode.setExclusive(True)
		self._btngrp_viewmode.addButton(self._btn_viewmode_list)
		self._btngrp_viewmode.addButton(self._btn_viewmode_frame)
		self._btngrp_viewmode.addButton(self._btn_viewmode_script)
		
		self.addWidget(buttons.BSPushButtonActionBar(self._btngrp_viewmode))

		self._txt_search.setSizePolicy(self.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		self._txt_search.setMinimumWidth(self._txt_search.fontMetrics().averageCharWidth() * 24)
		self._txt_search.setMaximumWidth(self._txt_search.fontMetrics().averageCharWidth() * 32)
		self._txt_search.setPlaceholderText(self.tr("Find in bin"))
		self._txt_search.setClearButtonEnabled(True)

		self.addWidget(self._txt_search)

	def _setupSignals(self):

		self._sld_frame_scale.sliderMoved  .connect(self.sig_frame_scale_changed)
		self._sld_frame_scale.valueChanged .connect(lambda s: self._sld_frame_scale.setToolTip(str(s)))

		self._sld_script_scale.sliderMoved .connect(self.sig_script_scale_changed)

	def setOpenBinAction(self, action:QtGui.QAction):
		"""Set the action for Open Bin"""

		self._btn_open.setAction(action)

	def setReloadBinAction(self, action:QtGui.QAction):
		"""Set the action for Reload Bin"""

		self._btn_reload.setAction(action)

	def setStopLoadAction(self, action:QtGui.QAction):
		"""Set the action for Stop Load"""

		self._btn_stop.setAction(action)

	def setViewModeListAction(self, action:QtGui.QAction):
		"""Set the action for view mode: list"""

		self._btn_viewmode_list.setAction(action)

	def setViewModeFrameAction(self, action:QtGui.QAction):
		"""Set the action for iew mode: frame"""

		self._btn_viewmode_frame.setAction(action)

	def setViewModeScriptAction(self, action:QtGui.QAction):
		"""Set the action for iew mode: script"""

		self._btn_viewmode_script.setAction(action)

	def searchBox(self) -> QtWidgets.QLineEdit:
		"""Return the search box"""

		return self._txt_search

	def binViewSelector(self) -> binviewcombobox.BSBinViewSelectorComboBox:
		"""BinView Selection `QComboBox`"""

		return self._cmb_binviews

	def progressBar(self) -> QtWidgets.QProgressBar:
		"""Progress bar widget"""

		return self._prg_loading

	@QtCore.Slot(object)
	def setViewMode(self, view_mode:avbutils.BinDisplayModes):
		"""Set the current view mode"""

		self._mode_controls.setCurrentIndex(int(view_mode))