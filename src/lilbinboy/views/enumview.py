import enum
from PySide6 import QtCore, QtWidgets

class LBAbstractEnumFlagsView(QtWidgets.QWidget):

	sig_flag_toggled  = QtCore.Signal(object, bool)
	sig_flags_changed = QtCore.Signal(object)

	def __init__(self, initial_values:enum.Flag, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._option_mappings:dict[enum.Flag, QtWidgets.QCheckBox] = dict()

		self._flags = initial_values

		# Set initial values
		for option in self._flags.__class__.__members__.values():

			chk_option = QtWidgets.QCheckBox(text=option.name.replace("_"," ").title())
			chk_option.setProperty("checkvalue", option)
			
			chk_option.clicked.connect(lambda is_checked, option=option:self._option_changed(option, is_checked))
			
			self._option_mappings[option] = chk_option

		self.updateCheckStates()
		
	@QtCore.Slot(object)
	def _option_changed(self, option:enum.Flag, is_enabled:bool):


		if is_enabled:
			self._flags |= option
		else:
			self._flags &= ~option

		self.sig_flag_toggled.emit(option, is_enabled)
		self.sig_flags_changed.emit(self._flags)
	
	def flags(self) -> enum.Flag:

		return self._flags
	
	def setFlags(self, options:enum.Flag):
		"""Set all options from a given flags enum"""

		if not isinstance(options, type(self._flags)):
			raise TypeError(f"Flags must be type {type(self._flags).__name__} (not ({type(options).__name__}))")
		
		self._flags = options
		
		self.updateCheckStates()
	
	def updateCheckStates(self):
		"""Update the check states"""

		for option, chk in self._option_mappings.items():
			chk.setCheckState(QtCore.Qt.CheckState.Checked if bool(self._flags & option) else QtCore.Qt.CheckState.Unchecked)