from PySide6 import QtGui, QtWidgets
from . import wdg_sequence_treeview, wdg_sequence_trims, wdg_stats, wdg_loadingbar, wdg_sequence_selection
from ...lbb_common import LBTimelineView, LBSpinBoxTC

class LBBRuntimeMetricsPanel(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
	
		self.setLayout(QtWidgets.QVBoxLayout())

		# Declare top controls
		self.btn_add_bins = QtWidgets.QPushButton()
		self.btn_refresh_bins = QtWidgets.QPushButton()
		self.btn_clear_bins = QtWidgets.QPushButton()
		
		# Stacked widget to toggle between progress bar and bin/sequence mode
		self.stack_bin_loading = QtWidgets.QStackedWidget()
		self.prog_loading = wdg_loadingbar.TRTBinLoadingProgressBar()
		self.bin_mode = wdg_sequence_selection.TRTModeSelection()

		# Declare main treeview
		self.tree_sequenceview = wdg_sequence_treeview.TRTTreeView()
		self.stats_trt = wdg_stats.TRTStatView()

		# Longplay view
		self.timeline_longplay = LBTimelineView()

		# Declare trims
		self.trt_trims = wdg_sequence_trims.TRTControlsTrims()
		self.trim_total = LBSpinBoxTC()

		# Exporters
		self.btn_export_data = QtWidgets.QPushButton()
		self.btn_snapshots = QtWidgets.QPushButton()

		self._setupWidgets()
	
	def _setupWidgets(self):

		# ---
		# Top controls
		self.btn_add_bins.setText("Add From Bins...")
		self.btn_add_bins.setToolTip("Add the latest sequence(s) from one or more bins")
		self.btn_add_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))

		# Stacked widget for progress vs sequence selection
		self.stack_bin_loading.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Maximum))
		self.stack_bin_loading.addWidget(self.prog_loading)
		self.stack_bin_loading.addWidget(self.bin_mode)
		self.stack_bin_loading.setCurrentWidget(self.bin_mode)

		# Refresh & Clear controls
		self.btn_refresh_bins.setToolTip("Reload the existing bins for updates")
		self.btn_refresh_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRefresh))

		self.btn_clear_bins.setToolTip("Clear the existing sequences")
		self.btn_clear_bins.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditClear))
		
		lay_loader_controls = QtWidgets.QHBoxLayout()
		lay_loader_controls.addWidget(self.btn_add_bins)
		lay_loader_controls.addWidget(self.stack_bin_loading)
		lay_loader_controls.addWidget(self.btn_refresh_bins)
		lay_loader_controls.addWidget(self.btn_clear_bins)

		self.layout().addLayout(lay_loader_controls)

		# ---
		# Main treeview
		# NOTE: Go back and get fit_headers(), header() context menu setup, need to set model
		self.layout().addWidget(self.tree_sequenceview)

		# ---
		# Longplay view
		self.layout().addWidget(self.timeline_longplay)

		# ---
		# Stats/Summary View
		grp_stats = QtWidgets.QGroupBox()
		grp_stats.setLayout(QtWidgets.QVBoxLayout())
		grp_stats.layout().setContentsMargins(0,0,0,0)
		grp_stats.layout().addWidget(self.stats_trt)
		self.layout().addWidget(grp_stats)

		# ---
		# Exporters
		self.btn_export_data.setText("Export As...")
		self.btn_export_data.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentSave))

		self.btn_snapshots.setText("Show Snapshots...")
		self.btn_snapshots.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewRestore))
		
		lay_exporters = QtWidgets.QHBoxLayout()
		lay_exporters.addWidget(self.btn_export_data)
		lay_exporters.addWidget(self.btn_snapshots)
		self.layout().addLayout(lay_exporters)
		
		# ---
		# Trim controls
		self.layout().addWidget(self.trt_trims)