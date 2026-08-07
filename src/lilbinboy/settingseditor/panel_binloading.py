from PySide6 import QtWidgets

class BSSettingsBinLoading(QtWidgets.QWidget):
	"""Bin Loading Options Panel"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._chk_bin_view = QtWidgets.QCheckBox()
		self._chk_bin_theme = QtWidgets.QCheckBox()
		self._chk_bin_viewmode = QtWidgets.QCheckBox()
		self._chk_bin_display = QtWidgets.QCheckBox()
		self._chk_column_widths = QtWidgets.QCheckBox()

		self._sld_queue_size = QtWidgets.QSlider()

		self.setupWidgets()

	def setupWidgets(self):

		pass