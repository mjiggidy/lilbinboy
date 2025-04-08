import logging
from PySide6 import QtCore, QtGui, QtWidgets
from .panel_runtime import LBBRuntimeMetricsPanel

class LBBRuntimeMetricsController(QtCore.QObject):
	"""Controller for Runtime Metrics"""

	def __init__(self, runtime_panel:LBBRuntimeMetricsPanel|None=None, *args, **kwargs):
		super().__init__(*args, **kwargs)

		logging.basicConfig(level=logging.DEBUG)
		self.logger = logging.getLogger(__name__)

		self.panel = runtime_panel or LBBRuntimeMetricsPanel()

		self._setupSignals()
	
	def _setupSignals(self):

		self.panel.sig_request_add_bins.connect(self.addBinsFromPaths)

	@QtCore.Slot(list)
	def addBinsFromPaths(self, paths:list[str]):
		"""Add bins from optional paths, or prompt for paths if none given"""

		# Prompt for paths if none were given
		if not paths:

			self.logger.debug("No bin paths received, prompting...")

			# TODO: From prefs
			last_bin_path = "."   
			paths,_ = QtWidgets.QFileDialog.getOpenFileNames(
				caption="Choose Avid bins for calcuation...",
				dir=last_bin_path,
				filter="Avid Bins (*.avb);;All Files (*)",
				parent=self.panel
			)
			if not paths:
				return
		
		self.logger.info(f"Loading {len(paths)} bin(s): {paths}")

		# Inform the panel
		self.panel.beginLoadingSequences(paths)

		QtCore.QTimer.singleShot(1000, self.panel.doneLoadingSequences)
		#self.panel.doneLoadingSequences()