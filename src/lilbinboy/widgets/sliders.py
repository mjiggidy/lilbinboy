from PySide6 import QtCore, QtWidgets

class ViewModeSlider(QtWidgets.QSlider):
	"""ViewMode Slider for consistency"""
		
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setOrientation(QtCore.Qt.Orientation.Horizontal)
		self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
		self.setTickInterval(1)
		self.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBothSides)