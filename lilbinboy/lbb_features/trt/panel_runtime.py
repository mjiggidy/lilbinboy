from PySide6 import QtCore, QtGui, QtWidgets
from . import treeview_trt, wdg_summary, trims_trt
from .panel_trt import TRTBinLoadingProgressBar, TRTModeSelection
from lilbinboy.lbb_common import LBTimelineView, LBSpinBoxTC

class LBBRuntimeMetrics(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
	
		self.setLayout(QtWidgets.QVBoxLayout())

		# Declare top controls
		self.btn_add_bins = QtWidgets.QPushButton()
		self.btn_refresh_bins = QtWidgets.QPushButton()
		self.btn_clear_bins = QtWidgets.QPushButton()
		
		# Stacked widget to toggle between progress bar and bin/sequence mode
		self.stack_bin_loading = QtWidgets.QStackedWidget()
		self.prog_loading = TRTBinLoadingProgressBar()
		self.bin_mode = TRTModeSelection()

		# Declare main treeview
		self.tree_sequenceview = treeview_trt.TRTTreeView()
		self.trt_summary = wdg_summary.TRTSummary()

		# Longplay view
		self.timeline_longplay = LBTimelineView()

		# Declare trims
		self.trt_trims = trims_trt.TRTControlsTrims()
		self.trim_total = LBSpinBoxTC()

		# Exporters
		self.btn_export_data = QtWidgets.QPushButton()
		self.btn_snapshots = QtWidgets.QPushButton()

		self.setupWidgets()
	
	def setupWidgets(self):

		# Setup top controls
		lay_loader_controls = QtWidgets.QHBoxLayout()
		
		self.btn_add_bins.setText("Add From Bins...")
		self.btn_add_bins.setToolTip("Add the latest sequence(s) from one or more bins")
		self.btn_add_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
		lay_loader_controls.addWidget(self.btn_add_bins)
		
		# Stacked widget for progress vs sequence selection
		self.stack_bin_loading.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Maximum))
		self.stack_bin_loading.addWidget(self.prog_loading)
		self.stack_bin_loading.addWidget(self.bin_mode)
		self.stack_bin_loading.setCurrentWidget(self.bin_mode)
		lay_loader_controls.addWidget(self.stack_bin_loading)

		# Refresh/Clear controls
		self.btn_refresh_bins.setToolTip("Reload the existing bins for updates")
		self.btn_refresh_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRefresh))
		lay_loader_controls.addWidget(self.btn_refresh_bins)

		self.btn_clear_bins.setToolTip("Clear the existing sequences")
		self.btn_clear_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditClear))
		lay_loader_controls.addWidget(self.btn_clear_bins)

		self.layout().addLayout(lay_loader_controls)

		# Setup main treeview
		# NOTE: Go back and get fit_headers(), header() context menu setup, need to set model
		self.layout().addWidget(self.tree_sequenceview)

		# Longplay view
		self.layout().addWidget(self.timeline_longplay)


		# TODO: Summaries

		# Exporters
		lay_exporters = QtWidgets.QHBoxLayout()
		
		lay_exporters.addWidget(self.btn_export_data)

		self.btn_snapshots.setText("Show Snapshots...")
		self.btn_snapshots.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRestore))
		lay_exporters.addWidget(self.btn_snapshots)
		self.layout().addLayout(lay_exporters)
		
		# Set up sequence trim controls
		self.layout().addWidget(self.trt_trims)