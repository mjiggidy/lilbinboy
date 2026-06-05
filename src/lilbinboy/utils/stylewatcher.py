from PySide6 import QtCore, QtGui, QtWidgets

class BSWidgetStyleEventFilter(QtCore.QObject):
	"""Watch a widget for visual style updates"""

	sig_palette_changed = QtCore.Signal(QtGui.QPalette)
	sig_font_changed    = QtCore.Signal(QtGui.QFont)

	def eventFilter(self, watched:QtWidgets.QWidget, event:QtCore.QEvent) -> bool:

		if event.type() == QtCore.QEvent.Type.PaletteChange:
			self.sig_palette_changed.emit(watched.palette())
		
		elif event.type() == QtCore.QEvent.Type.FontChange:
			self.sig_font_changed.emit(watched.font())

		return False