from PySide6 import QtCore, QtGui, QtWidgets
from .panel_runtime import LBBRuntimeMetricsPanel

class LBBRuntimeMetricsController(QtCore.QObject):
	"""Controller for Runtime Metrics"""

	def __init__(self, runtime_panel:LBBRuntimeMetricsPanel|None=None, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.panel = runtime_panel or LBBRuntimeMetricsPanel()