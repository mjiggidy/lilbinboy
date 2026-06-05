import sys
from PySide6 import QtCore, QtGui, QtWidgets
from lilbinboy.utils import stylewatcher, palettes

from lilbinboy.binwidget import binwidget

ORDERED_COLOR_ROLES = [
	QtGui.QPalette.ColorRole.Base,
	QtGui.QPalette.ColorRole.AlternateBase,
	QtGui.QPalette.ColorRole.Window,
	QtGui.QPalette.ColorRole.ToolTipBase,

	QtGui.QPalette.ColorRole.Text,
	QtGui.QPalette.ColorRole.WindowText,
	QtGui.QPalette.ColorRole.ToolTipText,
	QtGui.QPalette.ColorRole.PlaceholderText,
	QtGui.QPalette.ColorRole.ButtonText,
	QtGui.QPalette.ColorRole.BrightText,

	QtGui.QPalette.ColorRole.Light,
	QtGui.QPalette.ColorRole.Midlight,
	QtGui.QPalette.ColorRole.Button,
	QtGui.QPalette.ColorRole.Mid,
	QtGui.QPalette.ColorRole.Dark,
	QtGui.QPalette.ColorRole.Shadow,

	QtGui.QPalette.ColorRole.Accent,
	QtGui.QPalette.ColorRole.Highlight,
	QtGui.QPalette.ColorRole.HighlightedText,

	QtGui.QPalette.ColorRole.Link,
	QtGui.QPalette.ColorRole.LinkVisited,
]

class ColorPaletteLabel(QtWidgets.QLabel):

	def __init__(self, color_role:QtGui.QPalette.ColorRole, color_group:QtGui.QPalette.ColorGroup=QtGui.QPalette.ColorGroup.Active):

		super().__init__()

		self._color_role   = color_role
		self._color_group  = color_group

		self._stylewatcher = stylewatcher.BSWidgetStyleEventFilter(parent=self)
		self._stylewatcher.sig_palette_changed.connect(self._updateColor)
		self.installEventFilter(self._stylewatcher)

		self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.setAutoFillBackground(True)

		self._updateColor()
	
	def sizeHint(self) -> QtCore.QSize:
		return QtCore.QSize(128,64) / 2
	
	@QtCore.Slot()
	def _updateColor(self):

		palette = self.palette()
		color   = self.palette().color(self._color_group, self._color_role)
		palette.setColor(QtGui.QPalette.ColorRole.Window, color)
		
		self.setPalette(palette)
		self.setText(f"R: {color.red()}  G: {color.green()}  B: {color.blue()} A: {color.alpha()}")
		self.setToolTip(color.name())

		print(f"{palettes.palette_is_dark_mode(self.palette())=}")
	
	@QtCore.Slot(QtGui.QPalette.ColorRole)
	def setColorRole(self, role:QtGui.QPalette.ColorRole):

		self._color_role = role
		self._updateColor()
	
	@QtCore.Slot(QtGui.QPalette.ColorGroup)
	def setColorGroup(self, group:QtGui.QPalette.ColorGroup):

		self._color_group = group
		self._updateColor()

class PaletteMaker(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QFormLayout())

		self._txt_fg = QtWidgets.QSpinBox(value=self.palette().windowText().color().lightness(), minimum=0, maximum=255)
		self._txt_bg = QtWidgets.QSpinBox(value=self.palette().window().color().lightness(), minimum=0, maximum=255)

		self.layout().addRow(
			QtWidgets.QLabel("FG:"),
			self._txt_fg
		)

		self.layout().addRow(
			QtWidgets.QLabel("BG"),
			self._txt_bg
		)


class MyKewlPaletteViewer(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QGridLayout())

		self._cmb_colorgroups = QtWidgets.QComboBox()
		
		for group in QtGui.QPalette.ColorGroup:
			self._cmb_colorgroups.addItem(group.name, group)

		self.layout().addWidget(self._cmb_colorgroups, 0, 0, 1, 2)

		# Store swatches so we can update them all when color group changes
		self._swatches = []

		for row, color_role in enumerate(ORDERED_COLOR_ROLES):

			swatch = ColorPaletteLabel(color_role)
			self._swatches.append(swatch)

			self.layout().addWidget(QtWidgets.QLabel(color_role.name), row+1, 0)
			self.layout().addWidget(swatch, row+1, 1)
		
		# Connect after all swatches are created
		self._cmb_colorgroups.currentIndexChanged.connect(self.setSwatchColorGroups)
	
	@QtCore.Slot()
	def setSwatchColorGroups(self):

		color_group = self._cmb_colorgroups.currentData()

		for swatch in self._swatches:
			swatch.setColorGroup(color_group)
	
if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = MyKewlPaletteViewer()
	wnd.show()

	ctrl = PaletteMaker()
	ctrl.show()

	ctrl._txt_bg.valueChanged.connect(lambda:
		wnd.setPalette(
			palettes.build_palette(
				fg_color=QtGui.QColor(*[ctrl._txt_fg.value()]*3),
				bg_color=QtGui.QColor(*[ctrl._txt_bg.value()]*3),
			)
		))
	
	ctrl._txt_fg.valueChanged.connect(lambda:
		wnd.setPalette(
			palettes.build_palette(
				fg_color=QtGui.QColor(*[ctrl._txt_fg.value()]*3),
				bg_color=QtGui.QColor(*[ctrl._txt_bg.value()]*3),
			)
		))
	
	bw = binwidget.BSBinContentsWidget()
	bw.show()

	

	sys.exit(app.exec())