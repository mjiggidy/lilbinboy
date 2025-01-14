import random
from PySide6 import QtCore, QtGui, QtWidgets

class TRTHistoryPanel(QtWidgets.QFrame):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self.lbl = QtWidgets.QLabel("Hi")
	#	self.lbl.setFixedHeight(50)

		self.layout().addWidget(self.lbl)
		self.layout().addWidget(QtWidgets.QTreeView())
		self.layout().addWidget(QtWidgets.QGroupBox())

		self.setFrameShape(QtWidgets.QFrame.Shape.Panel)
		self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
	
	#def sizeHint(self) -> QtCore.QSize:
	#	return QtCore.QSize(super().sizeHint().width(), 100)

class TRTHistoryViewer(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setWindowTitle("History Viewer")
		#self.setWindowFlag(QtCore.Qt.WindowType.Tool)
		self.setLayout(QtWidgets.QHBoxLayout())

		self._lst_saved = QtWidgets.QListView()
		self._scroll_panels = QtWidgets.QScrollArea()

		self._setupWidgets()
	
	def _setupWidgets(self):

		self._lst_saved.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, self.sizePolicy().verticalPolicy())

		self.layout().addWidget(self._lst_saved)

		self._scroll_panels.setLayout(QtWidgets.QVBoxLayout())
		self._scroll_panels.setVerticalScrollBarPolicy(QtGui.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._scroll_panels.setWidgetResizable(True)
		#self._scroll_panels.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, self.sizePolicy().verticalPolicy())

		self._scroll_area = QtWidgets.QWidget()
		self._scroll_area.setLayout(QtWidgets.QVBoxLayout())

		for _ in range(random.randrange(3,5)):
			self._scroll_area.layout().addWidget(TRTHistoryPanel())
		self._scroll_area.layout().addStretch()

		self._scroll_panels.setWidget(self._scroll_area)

		self.layout().addWidget(self._scroll_panels)