import dataclasses
from PySide6 import QtGui, QtWidgets

@dataclasses.dataclass(frozen=True)
class TRTStatItem():
	"""Item to display in a `TRTSummary` bar"""

	label:str
	"""The label for this item"""

	value:str
	"""The value of this item"""

class TRTStatView(QtWidgets.QWidget):


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setSizePolicy(QtWidgets.QSizePolicy(self.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.Maximum))

		self._fnt_label = QtGui.QFont()
		self._fnt_value = QtGui.QFont()

		self._stat_items = dict()

		self._fnt_label.setCapitalization(QtGui.QFont.Capitalization.AllUppercase)
		self._fnt_label.setPointSizeF(8)

		self._fnt_value.setBold(True)
		self._fnt_value.setPointSizeF(18)

		self.setLayout(QtWidgets.QGridLayout())
		self.layout().setHorizontalSpacing(24)
	
	def add_stat_item(self, item:TRTStatItem):

		if str(item.label) in self._stat_items:
			label, value = self._stat_items[str(item.label)]
			value.setText(str(item.value))
		
		else:
			
			lbl_value = QtWidgets.QLabel(str(item.value))
			lbl_value.setFont(self._fnt_value)
			lbl_value.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
			lbl_value.setTextInteractionFlags(QtGui.Qt.TextInteractionFlag.TextSelectableByMouse|QtGui.Qt.TextInteractionFlag.TextSelectableByKeyboard)

			lbl_label = QtWidgets.QLabel(str(item.label))
			lbl_label.setFont(self._fnt_label)
			lbl_label.setAlignment(QtGui.Qt.AlignmentFlag.AlignCenter)
			lbl_label.setBuddy(lbl_value)

			self._stat_items.update({
				str(item.label): (lbl_label, lbl_value)
			})
			
			self.layout().addWidget(lbl_value, 0, self.layout().columnCount())
			self.layout().addWidget(lbl_label, 1, self.layout().columnCount()-1)
	
	def add_spacer(self):

		self.layout().addItem(QtWidgets.QSpacerItem(1,1, QtWidgets.QSizePolicy.Policy.MinimumExpanding), 1, self.layout().columnCount())