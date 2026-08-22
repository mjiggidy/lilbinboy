from PySide6 import QtCore, QtWidgets

INFO_TEXT_SCALE = 0.8

DEFAULT_LOAD_BIN_VIEW = True
DEFAULT_LOAD_BIN_THEME = True
DEFAULT_LOAD_BIN_VIEW_MODE = True
DEFAULT_LOAD_BIN_DISPLAY = True
DEFAULT_LOAD_COLUMN_WIDTHS = True

DEFAULT_QUEUE_SIZE  = 500
DEFAULT_QUEUE_RANGE = range(50, 2000)

class BSSettingsBinLoading(QtWidgets.QWidget):
	"""Bin Loading Options Panel"""

	sig_load_bin_view_changed      = QtCore.Signal(bool)
	sig_load_column_widths_changed = QtCore.Signal(bool)
	sig_load_bin_theme_changed     = QtCore.Signal(bool)
	sig_load_bin_view_mode_changed = QtCore.Signal(bool)
	sig_load_bin_display_changed   = QtCore.Signal(bool)
	sig_mob_queue_size_changed     = QtCore.Signal(int)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._chk_bin_view = QtWidgets.QCheckBox()
		self._chk_bin_theme = QtWidgets.QCheckBox()
		self._chk_bin_view_mode = QtWidgets.QCheckBox()
		self._chk_bin_display = QtWidgets.QCheckBox()
		self._chk_column_widths = QtWidgets.QCheckBox()

		self._sld_queue_size = QtWidgets.QSlider()
		self._lbl_queue_size = QtWidgets.QLabel()

		self._setupWidgets()
		self._setupSignals()

	def _setupWidgets(self):

		font_info_lbl = self.font()
		font_info_lbl.setPointSizeF(font_info_lbl.pointSizeF() * INFO_TEXT_SCALE)

		# Load saved bin view

		self._chk_bin_view.setChecked(DEFAULT_LOAD_BIN_VIEW)

		lay_load_bin_view = QtWidgets.QHBoxLayout()
		lay_load_bin_view.addWidget(QtWidgets.QLabel(self.tr("Load the stored bin view:")))
		lay_load_bin_view.addStretch()
		lay_load_bin_view.addWidget(self._chk_bin_view)

		lbl_load_bin_view_info = QtWidgets.QLabel(self.tr("Load the bin column view that was last saved with the bin."))
		lbl_load_bin_view_info.setWordWrap(True)
		lbl_load_bin_view_info.setFont(font_info_lbl)

		grp_load_bin_view = QtWidgets.QGroupBox()
		grp_load_bin_view.setLayout(QtWidgets.QVBoxLayout())
		grp_load_bin_view.layout().addLayout(lay_load_bin_view)
		grp_load_bin_view.layout().addWidget(lbl_load_bin_view_info)

		self.layout().addWidget(grp_load_bin_view)

		# Load column widths

		self._chk_column_widths.setChecked(DEFAULT_LOAD_COLUMN_WIDTHS)

		lay_load_column_widths = QtWidgets.QHBoxLayout()
		lay_load_column_widths.addWidget(QtWidgets.QLabel(self.tr("Resize columns to stored widths:")))
		lay_load_column_widths.addStretch()
		lay_load_column_widths.addWidget(self._chk_column_widths)

		lbl_load_column_widths = QtWidgets.QLabel(self.tr("Use column widths last saved with the bin, if available.  Otherwise, columns will be auto-sized to fit contents."))
		lbl_load_column_widths.setWordWrap(True)
		lbl_load_column_widths.setFont(font_info_lbl)

		grp_load_column_widths = QtWidgets.QGroupBox()
		grp_load_column_widths.setLayout(QtWidgets.QVBoxLayout())
		grp_load_column_widths.layout().addLayout(lay_load_column_widths)
		grp_load_column_widths.layout().addWidget(lbl_load_column_widths)

		self.layout().addWidget(grp_load_column_widths)

		# Load saved bin theme

		self._chk_bin_theme.setChecked(DEFAULT_LOAD_BIN_THEME)

		lay_load_bin_theme = QtWidgets.QHBoxLayout()
		lay_load_bin_theme.addWidget(QtWidgets.QLabel(self.tr("Apply the stored bin theme:")))
		lay_load_bin_theme.addStretch()
		lay_load_bin_theme.addWidget(self._chk_bin_theme)

		lbl_load_bin_theme = QtWidgets.QLabel(self.tr("Load the font and color palette last saved with the bin."))
		lbl_load_bin_theme.setWordWrap(True)
		lbl_load_bin_theme.setFont(font_info_lbl)

		grp_load_bin_theme = QtWidgets.QGroupBox()
		grp_load_bin_theme.setLayout(QtWidgets.QVBoxLayout())
		grp_load_bin_theme.layout().addLayout(lay_load_bin_theme)
		grp_load_bin_theme.layout().addWidget(lbl_load_bin_theme)

		self.layout().addWidget(grp_load_bin_theme)

		# Load bin view mode

		self._chk_bin_view_mode.setChecked(DEFAULT_LOAD_BIN_VIEW_MODE)

		lay_load_bin_view_mode = QtWidgets.QHBoxLayout()
		lay_load_bin_view_mode.addWidget(QtWidgets.QLabel(self.tr("Switch to the stored bin view mode:")))
		lay_load_bin_view_mode.addStretch()
		lay_load_bin_view_mode.addWidget(self._chk_bin_view_mode)

		lbl_load_bin_view_mode = QtWidgets.QLabel(self.tr("Switch to the view mode (Text, Frame, or Script) that was last saved with the bin."))
		lbl_load_bin_view_mode.setWordWrap(True)
		lbl_load_bin_view_mode.setFont(font_info_lbl)

		grp_load_bin_view_mode = QtWidgets.QGroupBox()
		grp_load_bin_view_mode.setLayout(QtWidgets.QVBoxLayout())
		grp_load_bin_view_mode.layout().addLayout(lay_load_bin_view_mode)
		grp_load_bin_view_mode.layout().addWidget(lbl_load_bin_view_mode)

		self.layout().addWidget(grp_load_bin_view_mode)

		# Load bin display mode

		self._chk_bin_display.setChecked(DEFAULT_LOAD_BIN_DISPLAY)

		lay_load_bin_display = QtWidgets.QHBoxLayout()
		lay_load_bin_display.addWidget(QtWidgets.QLabel(self.tr("Apply the stored bin display settings:")))
		lay_load_bin_display.addStretch()
		lay_load_bin_display.addWidget(self._chk_bin_display)

		lbl_load_bin_display = QtWidgets.QLabel(self.tr("Load the bin display settings (which bin item types to show) that were last saved with the bin."))
		lbl_load_bin_display.setWordWrap(True)
		lbl_load_bin_display.setFont(font_info_lbl)

		grp_load_bin_display = QtWidgets.QGroupBox()
		grp_load_bin_display.setLayout(QtWidgets.QVBoxLayout())
		grp_load_bin_display.layout().addLayout(lay_load_bin_display)
		grp_load_bin_display.layout().addWidget(lbl_load_bin_display)

		self.layout().addWidget(grp_load_bin_display)

		self.layout().addWidget(QtWidgets.QLabel(self.tr("Advanced Settings")))

		# Mob queue size

		self._sld_queue_size.setRange(DEFAULT_QUEUE_RANGE.start, DEFAULT_QUEUE_RANGE.stop)
		self._sld_queue_size.setValue(DEFAULT_QUEUE_SIZE)
		self._sld_queue_size.setOrientation(QtCore.Qt.Orientation.Horizontal)

		self._lbl_queue_size.setFixedWidth(self._lbl_queue_size.fontMetrics().maxWidth() * 3) # Arbitrary lol
		self._lbl_queue_size.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		self._lbl_queue_size.setText(str(self._sld_queue_size.value()))

		lay_scroll_scale_control = QtWidgets.QHBoxLayout()
		lay_scroll_scale_control.addWidget(QtWidgets.QLabel("Mob queue size:"))
		lay_scroll_scale_control.addWidget(self._sld_queue_size)
		lay_scroll_scale_control.addWidget(self._lbl_queue_size)

		grp_scroll_scale = QtWidgets.QGroupBox()
		grp_scroll_scale.setLayout(QtWidgets.QVBoxLayout())
		grp_scroll_scale.layout().addLayout(lay_scroll_scale_control)

		lbl_scroll_scale_info = QtWidgets.QLabel(self.tr(
"""\
The maximum number of bin items to process at once.  \
A lower number requires less memory, but may decrease UI responsiveness during load.  \
The default value is usually fine.\
"""
		))
		lbl_scroll_scale_info.setWordWrap(True)
		lbl_scroll_scale_info.setFont(font_info_lbl)

		grp_scroll_scale.layout().addWidget(lbl_scroll_scale_info)

		self.layout().addWidget(grp_scroll_scale)

		self.layout().addStretch()

	def _setupSignals(self):

		self._sld_queue_size.valueChanged.connect(self._userChangedQueueSize)

		self._chk_bin_view.checkStateChanged.connect(self._userChangedLoadBinView)
		self._chk_column_widths.checkStateChanged.connect(self._userChangedLoadColumnWidths)
		self._chk_bin_theme.checkStateChanged.connect(self._userChangedLoadBinTheme)
		self._chk_bin_view_mode.checkStateChanged.connect(self._userChangedLoadViewMode)
		self._chk_bin_display.checkStateChanged.connect(self._userChangedLoadBinDisplay)

	@QtCore.Slot(int)
	def _userChangedQueueSize(self, value:int):

		self._lbl_queue_size.setText(str(value))
		self.sig_mob_queue_size_changed.emit(value)

	@QtCore.Slot(QtCore.Qt.CheckState)
	def _userChangedLoadBinView(self, check_state:QtCore.Qt.CheckState):

		self.sig_load_bin_view_changed.emit(check_state == QtCore.Qt.CheckState.Checked)

	@QtCore.Slot(QtCore.Qt.CheckState)
	def _userChangedLoadColumnWidths(self, check_state:QtCore.Qt.CheckState):

		self.sig_load_column_widths_changed.emit(check_state == QtCore.Qt.CheckState.Checked)

	@QtCore.Slot(QtCore.Qt.CheckState)
	def _userChangedLoadBinTheme(self, check_state:QtCore.Qt.CheckState):

		self.sig_load_bin_theme_changed.emit(check_state == QtCore.Qt.CheckState.Checked)

	@QtCore.Slot(QtCore.Qt.CheckState)
	def _userChangedLoadViewMode(self, check_state:QtCore.Qt.CheckState):

		self.sig_load_bin_view_mode_changed.emit(check_state == QtCore.Qt.CheckState.Checked)

	@QtCore.Slot(QtCore.Qt.CheckState)
	def _userChangedLoadBinDisplay(self, check_state:QtCore.Qt.CheckState):

		self.sig_load_bin_display_changed.emit(check_state == QtCore.Qt.CheckState.Checked)