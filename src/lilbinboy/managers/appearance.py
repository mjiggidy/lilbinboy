from PySide6 import QtCore, QtGui, QtWidgets


class BSBinAppearanceSettingsManager(QtCore.QObject):

	# Mostly use these -- will update with bin or system appearance
	sig_active_font_changed           = QtCore.Signal(QtGui.QFont)
	"""Current font to use (may be system or bin font)"""

	sig_palette_changed               = QtCore.Signal(QtGui.QPalette)
	"""Current palette to sue (may be system or bin palette)"""

	sig_use_bin_appearance_toggled    = QtCore.Signal(object) # NOTE: Inverse
	sig_use_system_appearance_toggled = QtCore.Signal(object) # of each other

	# More for internal/tool use
	sig_bin_colors_changed            = QtCore.Signal(QtGui.QColor, QtGui.QColor)
	"""Bin colors, as opposed to system colors"""

	sig_bin_font_changed              = QtCore.Signal(QtGui.QFont)
	"""Bin font, as opposed to system font"""

	sig_column_widths_changed         = QtCore.Signal(object)
	sig_window_rect_changed           = QtCore.Signal(object)
	sig_was_iconic_changed            = QtCore.Signal(object)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._use_bin_appearance = True
		
		self._bin_palette = QtWidgets.QApplication.palette()
		self._bin_font    = QtWidgets.QApplication.font()

	def activeFont(self) -> QtGui.QFont:
		"""The currently-active font"""

		return self._bin_font if self._use_bin_appearance else QtWidgets.QApplication.font()
	
	def activePalette(self) -> QtGui.QPalette:
		"""The currently-active palette"""

		return self._bin_palette if self._use_bin_appearance else QtWidgets.QApplication.palette()
	
	@QtCore.Slot(object, object, object, object, object, object, object)
	def setAppearanceSettings(self,
		mac_font_family:str|int,
		mac_font_size:int,
		foreground_color:list[int],
		background_color:list[int],
		column_widths:dict[str,int],
		window_rect:list[int],
		was_iconic:bool
	):
	
		# Appearance settings from avb

#		self.setColumnWidths(column_widths)
		self.setWindowRect(window_rect)
		self.sig_was_iconic_changed.emit(was_iconic)

		# JUST A NOTE:
		# I could be wrong, but I have a suspicion that these mac_* properties are 
		# specifically for frame view even though mac_font_size seems global
		bin_font = QtWidgets.QApplication.font()
		bin_font.setPointSizeF(mac_font_size) # NOTE: Setting PointSize sets PixelSize to -1 and vice versa!
		if isinstance(mac_font_family, str) and QtGui.QFontDatabase.hasFamily(mac_font_family):
			bin_font.setFamily(mac_font_family)

		
		self.setBinFont(bin_font)
		self.setBinColors(
			QtGui.QColor.fromRgba64(*foreground_color),
			QtGui.QColor.fromRgba64(*background_color),
		)



	@QtCore.Slot(QtGui.QFont)
	def setBinFont(self, bin_font:QtGui.QFont):

		if self._bin_font == bin_font:
			return
		
		self._bin_font = bin_font
		
		self.sig_bin_font_changed.emit(bin_font)
		if self._use_bin_appearance:
			self.sig_active_font_changed.emit(bin_font)

	def binFont(self) -> QtGui.QFont:

		return self._bin_font


	@QtCore.Slot(QtGui.QColor, QtGui.QColor)
	def setBinColors(self, fg_color:QtGui.QColor, bg_color:QtGui.QColor):
		"""Build a bin palette based on foreground and background colors"""

		#print("Got:", fg_color, bg_color)

		# NOTE: This was kinda old, want to base everything off setBinPalette/QPalette

		from ..utils import palettes
		self.setBinPalette(palettes.build_palette(fg_color, bg_color))

	def binColors(self) -> tuple[QtGui.QColor, QtGui.QColor]:
		"""Return `(fg_color, bg_color)`"""

		fg_color = self._bin_palette.color(QtGui.QPalette.ColorRole.Text)
		bg_color = self._bin_palette.color(QtGui.QPalette.ColorRole.Base)

		return (fg_color, bg_color,)
	
	def binPalette(self) -> QtGui.QPalette:
		"""Return the resolved `QPalette` for the bin"""

		return self._bin_palette

	@QtCore.Slot(QtGui.QPalette)
	def setBinPalette(self, bin_palette:QtGui.QPalette):
		"""Set the bin palette (as opposed to system palette)"""

		if self._bin_palette == bin_palette:
			return
		
		self._bin_palette = bin_palette
		
		self.sig_bin_colors_changed.emit(
			bin_palette.text().color(),
			bin_palette.base().color()
		)

		if self._use_bin_appearance:
			self.sig_palette_changed.emit(bin_palette)

	@QtCore.Slot(object)
	def setWindowRect(self, window_rect:list[int]):

		self.sig_window_rect_changed.emit(QtCore.QRect(
			QtCore.QPoint(*window_rect[:2]),
			QtCore.QPoint(*window_rect[2:])
		))

	@QtCore.Slot(object)
	def setColumnWidths(self, column_widths:dict[str,int]):
		"""Display column width settings"""

		# NOTE: DEPRECATE TO BIN VIEW

		self.sig_column_widths_changed.emit(column_widths)

	@QtCore.Slot(object)
	def setUseBinAppearance(self, use_bin:bool):
		"""Toggle between system appearance and stored bin appearance"""

		if self._use_bin_appearance == use_bin:
			return
		
		self._use_bin_appearance = use_bin

		if use_bin:
			self.sig_palette_changed.emit(self._bin_palette)
			self.sig_active_font_changed.emit(self._bin_font)
		else:
			self.sig_palette_changed.emit(QtWidgets.QApplication.palette())
			self.sig_active_font_changed.emit(QtWidgets.QApplication.font())

		self.sig_use_bin_appearance_toggled   .emit(use_bin)
		self.sig_use_system_appearance_toggled.emit(not use_bin)

	@QtCore.Slot(object)
	def setUseSystemAppearance(self, use_system:bool):

		self.setUseBinAppearance(not use_system)