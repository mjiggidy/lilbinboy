from PySide6 import QtCore, QtWidgets

INFO_TEXT_SCALE = 0.8

DEFAULT_BOTTOM_SCALE  = 150
DEFAULT_BOTTOM_RANGE  = range(100, 200)

DEFAULT_PADDING_RANGE = range(0, 256)
DEFAULT_PADDING       = (12, 6)

DEFAULT_TOOLS_FOLLOW  = True

DEFAULT_FANCY_ANIMATIONS = True

class BSSettingsUserInterface(QtWidgets.QWidget):
	"""User Interface Options Panel"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		# List padding spinnyboys
		self._spn_list_pad_w      = QtWidgets.QSpinBox()
		self._spn_list_pad_h      = QtWidgets.QSpinBox()

		self._sld_scroll_scale    = QtWidgets.QSlider()
		self._lbl_scroll_scale    = QtWidgets.QLabel()

		self._chk_tools_follow    = QtWidgets.QCheckBox()
		self._chk_fancy_animation = QtWidgets.QCheckBox()

		self.setupWidgets()

	def setupWidgets(self):

		font_info_lbl = self.font()
		font_info_lbl.setPointSizeF(font_info_lbl.pointSizeF() * INFO_TEXT_SCALE)

		# Bottom scroll scale

		self._sld_scroll_scale.setRange(DEFAULT_BOTTOM_RANGE.start, DEFAULT_BOTTOM_RANGE.stop)
		self._sld_scroll_scale.setValue(DEFAULT_BOTTOM_SCALE)
		self._sld_scroll_scale.setOrientation(QtCore.Qt.Orientation.Horizontal)

		self._lbl_scroll_scale.setMinimumWidth(self._lbl_scroll_scale.fontMetrics().averageCharWidth() * 4)
		self._lbl_scroll_scale.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)
		self._lbl_scroll_scale.setText(f"{self._sld_scroll_scale.value()}%")

		lay_scroll_scale_control = QtWidgets.QHBoxLayout()
		lay_scroll_scale_control.addWidget(QtWidgets.QLabel("Bottom Scroll Bar Scale:"))
		#lay_scroll_scale_control.addStretch()
		lay_scroll_scale_control.addWidget(self._sld_scroll_scale)
		lay_scroll_scale_control.addWidget(self._lbl_scroll_scale)

		grp_scroll_scale = QtWidgets.QGroupBox()
		grp_scroll_scale.setLayout(QtWidgets.QVBoxLayout())
		grp_scroll_scale.layout().addLayout(lay_scroll_scale_control)

		lbl_scroll_scale_info = QtWidgets.QLabel(self.tr("Adjust the size of the bottom buttons and scroll bar"))
		lbl_scroll_scale_info.setWordWrap(True)
		lbl_scroll_scale_info.setFont(font_info_lbl)

		grp_scroll_scale.layout().addWidget(lbl_scroll_scale_info)

		self.layout().addWidget(grp_scroll_scale)

		# List item padding

		self._spn_list_pad_w.setRange(DEFAULT_PADDING_RANGE.start, DEFAULT_BOTTOM_RANGE.stop)
		self._spn_list_pad_w.setSuffix(" px")
		self._spn_list_pad_w.setValue(DEFAULT_PADDING[0])

		self._spn_list_pad_h.setRange(DEFAULT_PADDING_RANGE.start, DEFAULT_BOTTOM_RANGE.stop)
		self._spn_list_pad_h.setSuffix(" px")
		self._spn_list_pad_h.setValue(DEFAULT_PADDING[1])

		lay_list_pad = QtWidgets.QHBoxLayout()
		lay_list_pad.addWidget(QtWidgets.QLabel(self.tr("Additional List Padding:")))
		lay_list_pad.addStretch()
		lay_list_pad.addWidget(self._spn_list_pad_w)
		lay_list_pad.addWidget(QtWidgets.QLabel("x"))
		lay_list_pad.addWidget(self._spn_list_pad_h)

		grp_list_pad = QtWidgets.QGroupBox()
		grp_list_pad.setLayout(QtWidgets.QVBoxLayout())
		grp_list_pad.layout().addLayout(lay_list_pad)

		lbl_list_pad_info = QtWidgets.QLabel(self.tr("Adjust spacing between columns and rows in Text and Script View Modes"))
		lbl_list_pad_info.setWordWrap(True)
		lbl_list_pad_info.setFont(font_info_lbl)

		grp_list_pad.layout().addWidget(lbl_list_pad_info)
		self.layout().addWidget(grp_list_pad)

		# Tools follow main window

		self._chk_tools_follow.setText(self.tr("Tools follow main window"))
		self._chk_tools_follow.setChecked(DEFAULT_TOOLS_FOLLOW)

		grp_tools_follow = QtWidgets.QGroupBox()
		grp_tools_follow.setLayout(QtWidgets.QVBoxLayout())
		grp_tools_follow.layout().addWidget(self._chk_tools_follow)

		lbl_tools_follow_info = QtWidgets.QLabel(self.tr("As main bin viewer is moved around, any open tool windows will follow"))
		lbl_tools_follow_info.setWordWrap(True)
		lbl_tools_follow_info.setFont(font_info_lbl)
		grp_tools_follow.layout().addWidget(lbl_tools_follow_info)
		
		self.layout().addWidget(grp_tools_follow)

		self._chk_fancy_animation.setText(self.tr("Use fancy and extra-cool animations"))
		self._chk_fancy_animation.setChecked(DEFAULT_FANCY_ANIMATIONS)

		grp_fancy_animations = QtWidgets.QGroupBox()
		grp_fancy_animations.setLayout(QtWidgets.QVBoxLayout())
		grp_fancy_animations.layout().addWidget(self._chk_fancy_animation)

		lbl_fancy_animations = QtWidgets.QLabel(self.tr("Some elements are animated or updated live; disable if the UI feels sluggish"))
		lbl_fancy_animations.setWordWrap(True)
		lbl_fancy_animations.setFont(font_info_lbl)
		grp_fancy_animations.layout().addWidget(lbl_fancy_animations)

		self.layout().addWidget(grp_fancy_animations)