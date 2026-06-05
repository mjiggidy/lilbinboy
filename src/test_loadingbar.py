import sys, random
from PySide6 import QtCore, QtWidgets
from lilbinboy.widgets import loadingbar

class ProgressTester(QtWidgets.QWidget):
	
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._progbar = loadingbar.BSAnimatedProgressBar()
		sp = self._progbar.sizePolicy()
		sp.setRetainSizeWhenHidden(True)
		self._progbar.setSizePolicy(sp)
		self._progbar.hide()

		self.layout().addWidget(self._progbar)

		self._timer = QtCore.QTimer()
		self._timer.timeout.connect(self.incrementMobs)

		self._btn_load_properties = QtWidgets.QPushButton("Start Load Properties")
		self._btn_start_mobs      = QtWidgets.QPushButton("Start Load Mobs")
		self._btn_reset        = QtWidgets.QPushButton("Reset")

		self._btn_load_properties.clicked.connect(self.startBinProperties)
		self._btn_start_mobs.clicked.connect(self.startMobs)
		self._btn_reset.clicked.connect(self.reset)

		btn_layout = QtWidgets.QHBoxLayout()

		btn_layout.addWidget(self._btn_load_properties)
		btn_layout.addWidget(self._btn_start_mobs)
		btn_layout.addWidget(self._btn_reset)
		
		self.layout().addLayout(btn_layout)

	@QtCore.Slot()
	def startBinProperties(self):
		self._progbar.show()
		self._progbar.setRange(0,0)

	@QtCore.Slot()
	def startMobs(self):

		self._progbar.show()

		self._progbar.setValue(0)
		self._progbar.setMaximum(random.randrange(2_500, 25_000))
		self._progbar.setFormat("Loading mob %v of %m")

		self.incrementMobs()

	@QtCore.Slot()
	def incrementMobs(self):
		
		end_val = self._progbar.value() + random.randrange(50,500)
		
		self._progbar.animateToValue(end_val, duration_msec=random.randrange(100, 5_000))

		if end_val <= self._progbar.maximum():
			self._timer.start(random.randrange(1_000, 10_000))
	
	@QtCore.Slot()
	def reset(self):

		self._progbar.hide()


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = ProgressTester()
	wnd.show()

	sys.exit(app.exec())