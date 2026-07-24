import logging
from PySide6 import QtCore, QtGui, QtWidgets

DEFAULT_FONT_FAMILIES = ["Open Sans", "Tuffy", "Arial", "Helvetica", "sans-serif"]
DEFAULT_FONT_SIZE_PT  = 10

class BSBinAppearanceSettingsView(QtWidgets.QWidget):
	"""Fonts, colors, and dimensions"""

	sig_font_changed       = QtCore.Signal(QtGui.QFont)
	sig_colors_changed     = QtCore.Signal(QtGui.QColor, QtGui.QColor)
	sig_geometry_changed   = QtCore.Signal(QtCore.QRect)
	sig_was_iconic_changed = QtCore.Signal(bool)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

#		self.layout().setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)

		# Fonts
		self._cmb_fonts = QtWidgets.QFontComboBox()
		self._spn_size  = QtWidgets.QSpinBox(minimum=8, maximum=100) # Avid font dialog extents

		# Colors
		self._btn_fg_color = QtWidgets.QPushButton()
		self._btn_bg_color = QtWidgets.QPushButton()

		# Window geometry
		self._spn_geo_x = QtWidgets.QSpinBox()
		self._spn_geo_y = QtWidgets.QSpinBox()

		self._spn_geo_w = QtWidgets.QSpinBox()
		self._spn_geo_h = QtWidgets.QSpinBox()

		self._chk_was_iconic = QtWidgets.QCheckBox(self.tr("Was Iconic"))

		self._setupWidgets()
		self._setupSignals()

	def _setupWidgets(self):

		lay_fonts = QtWidgets.QHBoxLayout()

		default_font = QtGui.QFont()
		default_font.setFamilies(DEFAULT_FONT_FAMILIES)
		default_font.setPointSize(DEFAULT_FONT_SIZE_PT)

		self._spn_size.setValue(default_font.pointSize())
		self._cmb_fonts.setCurrentFont(default_font)

		self._spn_size.setSuffix(" pt")
		self._spn_size.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		
		lay_fonts.addWidget(self._cmb_fonts)
		lay_fonts.addWidget(self._spn_size)

		self.layout().addWidget(QtWidgets.QLabel(self.tr("Font And Colors")))
		self.layout().addLayout(lay_fonts)

		lay_colors = QtWidgets.QHBoxLayout()

		self._btn_fg_color.setText(self.tr("Text"))
		self._btn_bg_color.setText(self.tr("Background"))
		lay_colors.addWidget(self._btn_fg_color)
		lay_colors.addWidget(self._btn_bg_color)

		self.layout().addLayout(lay_colors)

		lay_geo= QtWidgets.QGridLayout()

		self._spn_geo_x.setSuffix(self.tr(" px"))
		self._spn_geo_x.setMaximum(9999)
		self._spn_geo_x.setMinimum(-9999)
		self._spn_geo_x.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

		self._spn_geo_y.setSuffix(self.tr(" px"))
		self._spn_geo_y.setMaximum(9999)
		self._spn_geo_y.setMinimum(-9999)
		self._spn_geo_y.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

		self._spn_geo_w.setSuffix(self.tr(" px"))
		self._spn_geo_w.setMaximum(9999)
		self._spn_geo_w.setMinimum(128)
		self._spn_geo_w.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

		self._spn_geo_h.setSuffix(self.tr(" px"))
		self._spn_geo_h.setMaximum(9999)
		self._spn_geo_h.setMinimum(128)
		self._spn_geo_h.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)

		lay_geo.addWidget(QtWidgets.QLabel(self.tr("X:")), 0, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		lay_geo.addWidget(self._spn_geo_x, 0, 1)
		lay_geo.addWidget(QtWidgets.QLabel(self.tr("Y:")), 1, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		lay_geo.addWidget(self._spn_geo_y, 1, 1)

		lay_geo.setColumnStretch(2, 1)

		lay_geo.addWidget(QtWidgets.QLabel(self.tr("W:")), 0, 3, QtCore.Qt.AlignmentFlag.AlignRight)
		lay_geo.addWidget(self._spn_geo_w, 0, 4)
		lay_geo.addWidget(QtWidgets.QLabel(self.tr("H:")), 1, 3, QtCore.Qt.AlignmentFlag.AlignRight)
		lay_geo.addWidget(self._spn_geo_h, 1, 4)

		self.layout().addWidget(QtWidgets.QLabel(self.tr("Window Geometry")))
		self.layout().addLayout(lay_geo)
		self.layout().addWidget(self._chk_was_iconic)

	def _setupSignals(self):

		self._cmb_fonts.currentFontChanged.connect(self.sig_font_changed)
		self._spn_size.valueChanged.connect(lambda: self.sig_font_changed.emit(self.binFont()))

		self._btn_fg_color.clicked.connect(self.fgColorPickerRequested)
		self._btn_bg_color.clicked.connect(self.bgColorPickerRequested)

	# TODO I'm sure this can be one method
	@QtCore.Slot()
	def bgColorPickerRequested(self):
		"""Request background color"""

		dlg_color = QtWidgets.QColorDialog(
			parent=self._btn_bg_color,
			currentColor=self.binBackgroundColor(),
			options=QtWidgets.QColorDialog.ColorDialogOption.NoButtons
		)

		dlg_color.currentColorChanged.connect(self.setBinBackgroundColor)
		dlg_color.setWindowTitle(self.tr("Choose a background color"))
#		dlg_color.finished.connect(lambda x: print("DONE:", x))

		dlg_color.exec()
		dlg_color.disconnect(self)

#		_,bg_color = self.binColors()
#		new_color = QtWidgets.QColorDialog.getColor(bg_color, self._btn_bg_color, self.tr("Choose a background color"))
#
#		if new_color.isValid():
#			self.setBinBackgroundColor(new_color)

	@QtCore.Slot()
	def fgColorPickerRequested(self):
		"""Request foreground (text) color"""

		dlg_color = QtWidgets.QColorDialog(
			parent=self._btn_bg_color,
			currentColor=self.binForegroundColor(),
			options=QtWidgets.QColorDialog.ColorDialogOption.NoButtons
		)

		dlg_color.currentColorChanged.connect(self.setBinForegroundColor)
		dlg_color.setWindowTitle(self.tr("Choose a foreground color"))
#		dlg_color.finished.connect(lambda x: print("DONE:", x))

		dlg_color.exec()
		dlg_color.disconnect(self)

#		fg_color,_ = self.binColors()
#		new_color = QtWidgets.QColorDialog.getColor(fg_color, self._btn_fg_color, self.tr("Choose a text color"))
#
#		if new_color.isValid():
#			self.setBinForegroundColor(new_color)
#
	@QtCore.Slot(QtCore.QRect)
	def setBinWindowGeometry(self, rect:QtCore.QRect):
		"""Set the bin window size and position"""

		if self.binWindowGeometry() == rect:
			return

		self._spn_geo_x.setValue(rect.x())
		self._spn_geo_y.setValue(rect.y())
		self._spn_geo_w.setValue(rect.width())
		self._spn_geo_h.setValue(rect.height())

		logging.getLogger(__name__).debug("Window geometry set to %s", rect)
		self.sig_geometry_changed.emit(self.binWindowGeometry())

	def binWindowGeometry(self) -> QtCore.QRect:

		return QtCore.QRect(
			QtCore.QPoint(
				self._spn_geo_x.value(),
				self._spn_geo_y.value(),
			),
			QtCore.QSize(
				self._spn_geo_w.value(),
				self._spn_geo_h.value(),
			),
		)

	@QtCore.Slot(bool)
	def setWasIconic(self, was_iconic:bool):
		"""Set bin was minimized"""

		if self.wasIconic() == was_iconic:
			return

		self._chk_was_iconic.setChecked(was_iconic)

		logging.getLogger(__name__).debug("Is Iconic set to %s", was_iconic)
		self.sig_was_iconic_changed.emit(self.wasIconic())

	def wasIconic(self) -> bool:
		"""Is Was Icon Checked"""

		return self._chk_was_iconic.isChecked()

	###
	# Fonts
	###

	@QtCore.Slot(QtGui.QFont)
	def setBinFont(self, font:QtGui.QFont):
		"""Set the bin font"""

		old_font = self.binFont()
		if old_font.pointSize() == font.pointSize() and old_font.family() == font.family():
			return
		
		self.blockSignals(True)

		self._cmb_fonts.setCurrentFont(font)
		self._spn_size.setValue(font.pointSize())

		self.blockSignals(False)

		logging.getLogger(__name__).debug("Bin font changed to %s", font)
		self.sig_font_changed.emit(self.binFont())

	def binFont(self) -> QtGui.QFont:
		"""The currently-selected bin font"""

		font = self._cmb_fonts.currentFont()
		font.setPointSizeF(self._spn_size.value())

		return font

	###
	# Colors
	###

	@QtCore.Slot(QtGui.QColor)
	def setBinForegroundColor(self, color:QtGui.QColor):
		"""Set the foreground color selection"""

		if self.binForegroundColor() == color:
			return

		fg = self._btn_fg_color.palette()
		fg.setColor(QtGui.QPalette.ColorRole.Button, color)

		self._btn_fg_color.setPalette(fg)
		self._btn_fg_color.setToolTip(
			"<strong>{color_role}</strong><hr/>{color_rgb}".format(
				color_role=self.tr("Text Color"),
				color_rgb=self._format_color_text(color)
			)
		)

		logging.getLogger(__name__).debug("Foreground color set to %s", color)
		self.sig_colors_changed.emit(*self.binColors())

	@QtCore.Slot(QtGui.QColor)
	def setBinBackgroundColor(self, color:QtGui.QColor):
		"""Set the background color selection"""

		if self.binBackgroundColor() == color:
			return

		bg = self._btn_bg_color.palette()
		bg.setColor(QtGui.QPalette.ColorRole.Button, color)

		self._btn_bg_color.setPalette(bg)
		self._btn_bg_color.setToolTip(
			"<strong>{color_role}</strong><hr/>{color_rgb}".format(
				color_role=self.tr("Background Color"),
				color_rgb=self._format_color_text(color)
			)
		)

		logging.getLogger(__name__).debug("Background color set to %s", color)
		self.sig_colors_changed.emit(*self.binColors())

	def binForegroundColor(self) -> QtGui.QColor:
		"""Currently-selected foreground color"""

		return self._btn_fg_color.palette().color(QtGui.QPalette.ColorRole.Button)

	def binBackgroundColor(self) -> QtGui.QColor:
		"""Currently-selected background color"""
		
		return self._btn_bg_color.palette().color(QtGui.QPalette.ColorRole.Button)

	@QtCore.Slot(QtGui.QColor,QtGui.QColor)
	def setBinColors(self, fg_color:QtGui.QColor, bg_color:QtGui.QColor):
		"""Set all bin colors"""

		old_fg, old_bg = self.binColors()

		if fg_color == old_fg and bg_color == old_bg:
			return

		self.blockSignals(True)

		self.setBinForegroundColor(fg_color)
		self.setBinBackgroundColor(bg_color)

		self.blockSignals(False)

		self.sig_colors_changed.emit(*self.binColors())

	def binColors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
		"""Returns a tuple of `(fg_color:QtGui.QColor, bg_color:QtGui.QColor)`.  Weird notation lol"""

		return (
			self.binForegroundColor(),
			self.binBackgroundColor(),
		)

	@staticmethod
	def _format_color_text(color:QtGui.QColor) -> str:
		"""Format the color description for the color button label"""

		return f"R: {color.red()}  G: {color.green()}  B: {color.blue()}"