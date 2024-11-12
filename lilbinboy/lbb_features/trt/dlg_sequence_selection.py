from PySide6 import QtCore, QtWidgets

class TRTSequenceSelection(QtWidgets.QDialog):

	def __init__(self):

		super().__init__()

		self.setWindowTitle("Sequence Selection Settings")

		self.setLayout(QtWidgets.QVBoxLayout())

		self.layout().addWidget(QtWidgets.QLabel("Oh boy I need to do this too"))