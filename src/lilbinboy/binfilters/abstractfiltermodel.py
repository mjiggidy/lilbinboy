from PySide6 import QtCore

class BSAbstractBinSortFilterProxyModel(QtCore.QSortFilterProxyModel):
	"""An abstract sort/filter proxy model"""

	sig_filter_toggled = QtCore.Signal(bool)

	def __init__(self, *args, is_enabled:bool=True, **kwargs):

		super().__init__(*args, **kwargs)

		self._is_enabled = is_enabled

	@QtCore.Slot(bool)
	def setEnabled(self, is_enabled:bool):
		"""To be implemented by subclasses.  Emit `sig_filter_toggled` at end"""
		pass

	def isEnabled(self) -> bool:
		
		return self._is_enabled
	
	@QtCore.Slot(bool)
	def setDisabled(self, is_disabled:bool):
		self.setEnabled(not is_disabled)

	def isDisabled(self) -> bool:
		return not self._is_enabled
	
	def moveColumns(self, sourceParent, sourceColumn, count, destinationParent, destinationChild) -> bool:
		
		# Kinda surprised I need to implement this but OK
		
		return self.sourceModel().moveColumns(
			self.mapToSource(sourceParent),
			sourceColumn,
			count,
			self.mapToSource(destinationParent),
			destinationChild
		)