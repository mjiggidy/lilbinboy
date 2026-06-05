import logging
from PySide6 import QtCore, QtGui, QtWidgets

class BSColumnSelectWatcher(QtCore.QObject):

	DEFAULT_SELECTION_MODIFIER = QtGui.Qt.KeyboardModifier.AltModifier

	sig_column_selection_activated = QtCore.Signal(bool)
	sig_column_selected            = QtCore.Signal(object)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		# Start out accurate!
		self._column_selection_active = bool(QtWidgets.QApplication.keyboardModifiers() & self.DEFAULT_SELECTION_MODIFIER)

	def columnSelectionIsActive(self) -> bool:
		"""Column selection mode currently active"""

		return self._column_selection_active

	def setColumnSelectionActive(self, is_active:bool):
		"""Indicate column selection has begun"""

		if is_active != self._column_selection_active:

			self._column_selection_active = is_active

			logging.getLogger(__name__).debug("Column selection changed to %s", self.columnSelectionIsActive())
			self.sig_column_selection_activated.emit(is_active)

	def eventFilter(self, watched:QtCore.QObject, event:QtCore.QEvent) -> bool:

		if event.type() == QtCore.QEvent.Type.MouseButtonPress:

			if not event.button() & QtCore.Qt.MouseButton.LeftButton:
				return super().eventFilter(watched, event)

			# If clicked with modifier key: Column select begin!
			if not event.modifiers() & self.DEFAULT_SELECTION_MODIFIER:
				return super().eventFilter(watched, event)

			self.setColumnSelectionActive(True)


			if self.columnSelectionIsActive():
				event = QtGui.QMouseEvent(event)
				self.sig_column_selected.emit(event.localPos())

			return True

		if event.type() == QtCore.QEvent.Type.MouseButtonRelease and self.columnSelectionIsActive():

			# On mouse release, we done wit dat column selection
			self.setColumnSelectionActive(False)
			return True

		return super().eventFilter(watched, event)