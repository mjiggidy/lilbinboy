from PySide6 import QtWidgets

class LBUtilityTab(QtWidgets.QWidget):
	"""Lil' Utility Container Boy"""



class LBMainTabs(QtWidgets.QTabWidget):
	"""Lil' Tab Manager Boy"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		#self.addTab(LBTRTCalculator(), "TRT Calculator")
		#self.addTab(LBUtilityTab(), "Continuity Generator")
		#self.addTab(LBUtilityTab(), "Lock Jockey")
		#self.addTab(LBUtilityTab(), "Batch Bin Boy")



class LBMainWindow(QtWidgets.QMainWindow):
	"""Lil' Main Window Boy"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setCentralWidget(LBMainTabs())
