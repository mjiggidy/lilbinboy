import sys
from PySide6 import QtWidgets, QtCore

APP_NAME = "Lil' Bin Boy"

class LBUtilityTab(QtWidgets.QWidget):
	"""Lil' Utility Container Boy"""

class LBTRTCalculator(LBUtilityTab):
	"""TRT Calculator"""

	class TRTList(QtWidgets.QTreeWidget):
		"""TRT Readout"""
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)

			self.setHeaderLabels([
				"Reel Name",
				"Reel TRT",
				"Reel LFOA",
				"Date Modified",
				"Bin Lock"
			])

			self.setAlternatingRowColors(True)

	class TRTControls(QtWidgets.QGroupBox):
		"""TRT Control Abstract"""
	
	class TRTControlsTrims(TRTControls):

		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)

			self.setTitle("Trimming")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())
		self._setupWidgets()
	
	def _setupWidgets(self):

		self.layout().addWidget(self.__class__.TRTList())
		self.layout().addWidget(QtWidgets.QLabel("<font style='font-size:small;'>TOTAL RUNTIME</font> <font style='font-weight:bold;'>01:43:12:13</font>"))

		self.layout().addWidget(self.__class__.TRTControlsTrims())

class LBMainTabs(QtWidgets.QTabWidget):
	"""Lil' Tab Manager Boy"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.addTab(LBTRTCalculator(), "TRT Calculator")
		self.addTab(LBUtilityTab(), "Continuity Generator")
		self.addTab(LBUtilityTab(), "Lock Jockey")
		self.addTab(LBUtilityTab(), "Batch Bin Boy")



class LBMainWindow(QtWidgets.QMainWindow):
	"""Lil' Main Window Boy"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setCentralWidget(LBMainTabs())



app = QtWidgets.QApplication()

app.setApplicationDisplayName(APP_NAME)
app.setStyle("Fusion")

wnd_main = LBMainWindow()
wnd_main.show()

app.exec()