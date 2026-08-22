from PySide6 import QtWidgets

INFO_TEXT_SCALE = 0.8

class BSSettingsStartup(QtWidgets.QWidget):
	"""Startup Options Panel"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._cmb_initial_bin          = QtWidgets.QComboBox()
		self._cmb_initial_bin_view     = QtWidgets.QComboBox()
		self._btngrp_initial_view_mode = QtWidgets.QButtonGroup()
		self._cmb_bin_display          = QtWidgets.QComboBox()
		self._cmb_bin_theme            = QtWidgets.QComboBox()
		self._chk_restore_window_size  = QtWidgets.QCheckBox()

		self._setupWidgets()

	def _setupWidgets(self):

		font_info_lbl = self.font()
		font_info_lbl.setPointSizeF(font_info_lbl.pointSizeF() * INFO_TEXT_SCALE)

		# Initial Bin
		lay_initial_bin = QtWidgets.QHBoxLayout()
		lay_initial_bin.addWidget(QtWidgets.QLabel(self.tr("At startup, show:")))
		lay_initial_bin.addStretch()
		lay_initial_bin.addWidget(self._cmb_initial_bin)

		lbl_load_bin_view_mode = QtWidgets.QLabel(self.tr("Switch to the view mode (Text, Frame, or Script) that was last saved with the bin."))
		lbl_load_bin_view_mode.setWordWrap(True)
		lbl_load_bin_view_mode.setFont(font_info_lbl)

		grp_initial_bin = QtWidgets.QGroupBox()
		grp_initial_bin.setLayout(QtWidgets.QVBoxLayout())
		grp_initial_bin.layout().addLayout(lay_initial_bin)
		grp_initial_bin.layout().addWidget(lbl_load_bin_view_mode)

		self.layout().addWidget(grp_initial_bin)

		# Initial Bin View
		lay_initial_bin_view = QtWidgets.QHBoxLayout()
		lay_initial_bin_view.addWidget(QtWidgets.QLabel(self.tr("Default bin view:")))
		lay_initial_bin_view.addStretch()
		lay_initial_bin_view.addWidget(self._cmb_initial_bin_view)

		lbl_initial_bin_view = QtWidgets.QLabel(self.tr("Default bin view to use at startup"))
		lbl_initial_bin_view.setWordWrap(True)
		lbl_initial_bin_view.setFont(font_info_lbl)

		grp_initial_bin_view = QtWidgets.QGroupBox()
		grp_initial_bin_view.setLayout(QtWidgets.QVBoxLayout())
		grp_initial_bin_view.layout().addLayout(lay_initial_bin_view)
		grp_initial_bin_view.layout().addWidget(lbl_initial_bin_view)

		self.layout().addWidget(grp_initial_bin_view)

		# Initial Bin View Mode
		lay_initial_bin_view_mode = QtWidgets.QHBoxLayout()
		lay_initial_bin_view_mode.addWidget(QtWidgets.QLabel(self.tr("Default bin view mode:")))
		lay_initial_bin_view_mode.addStretch()
		#lay_initial_bin_view_mode.addWidget(self._btngrp_initial_view_mode)

		lbl_initial_bin_view_mode = QtWidgets.QLabel(self.tr("Default bin view mode to use at startup"))
		lbl_initial_bin_view_mode.setWordWrap(True)
		lbl_initial_bin_view_mode.setFont(font_info_lbl)

		grp_initial_bin_view_mode = QtWidgets.QGroupBox()
		grp_initial_bin_view_mode.setLayout(QtWidgets.QVBoxLayout())
		grp_initial_bin_view_mode.layout().addLayout(lay_initial_bin_view_mode)
		grp_initial_bin_view_mode.layout().addWidget(lbl_initial_bin_view_mode)

		self.layout().addWidget(grp_initial_bin_view_mode)

		# Initial Bin Display Settings
		lay_initial_bin_display = QtWidgets.QHBoxLayout()
		lay_initial_bin_display.addWidget(QtWidgets.QLabel(self.tr("Default bin display settings:")))
		lay_initial_bin_display.addStretch()
		lay_initial_bin_display.addWidget(self._cmb_bin_display)

		lbl_initial_bin_display = QtWidgets.QLabel(self.tr("Default bin display settings to use at startup"))
		lbl_initial_bin_display.setWordWrap(True)
		lbl_initial_bin_display.setFont(font_info_lbl)

		grp_initial_bin_display = QtWidgets.QGroupBox()
		grp_initial_bin_display.setLayout(QtWidgets.QVBoxLayout())
		grp_initial_bin_display.layout().addLayout(lay_initial_bin_display)
		grp_initial_bin_display.layout().addWidget(lbl_initial_bin_display)

		self.layout().addWidget(grp_initial_bin_display)

		# Initial theme
		lay_initial_bin_theme = QtWidgets.QHBoxLayout()
		lay_initial_bin_theme.addWidget(QtWidgets.QLabel(self.tr("Default bin theme:")))
		lay_initial_bin_theme.addStretch()
		lay_initial_bin_theme.addWidget(self._cmb_bin_theme)

		lbl_initial_bin_theme = QtWidgets.QLabel(self.tr("Default bin font and colors"))
		lbl_initial_bin_theme.setWordWrap(True)
		lbl_initial_bin_theme.setFont(font_info_lbl)

		grp_initial_bin_theme = QtWidgets.QGroupBox()
		grp_initial_bin_theme.setLayout(QtWidgets.QVBoxLayout())
		grp_initial_bin_theme.layout().addLayout(lay_initial_bin_theme)
		grp_initial_bin_theme.layout().addWidget(lbl_initial_bin_theme)

		self.layout().addWidget(grp_initial_bin_theme)

		# Restore window size
		lay_restore_window_size = QtWidgets.QHBoxLayout()
		lay_restore_window_size.addWidget(QtWidgets.QLabel(self.tr("Restore last window size and position:")))
		lay_restore_window_size.addStretch()
		lay_restore_window_size.addWidget(self._chk_restore_window_size)

		lbl_restore_window_size = QtWidgets.QLabel(self.tr("Restore the window size and position from the last session."))
		lbl_restore_window_size.setWordWrap(True)
		lbl_restore_window_size.setFont(font_info_lbl)

		grp_restore_window_size = QtWidgets.QGroupBox()
		grp_restore_window_size.setLayout(QtWidgets.QVBoxLayout())
		grp_restore_window_size.layout().addLayout(lay_restore_window_size)
		grp_restore_window_size.layout().addWidget(lbl_restore_window_size)

		self.layout().addWidget(grp_restore_window_size)

		self.layout().addStretch()