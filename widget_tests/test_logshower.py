import logging
from PySide6 import QtCore, QtGui, QtWidgets
from lilbinboy.lbb_common import LBLogDataModel, LBLogHandler

class LBLogRecordViewer(QtWidgets.QTreeView):

	def __init__(self, log_model:LBLogDataModel, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

		self.setAlternatingRowColors(True)
		self.setIndentation(0)
		self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
		
		self.setModel(model)

@QtCore.Slot()
def setMaxRecordsFromInput():
	
	if spin_remember_last.hasAcceptableInput():
		model.setMaxRecords(int(spin_remember_last.text()))
		logging.getLogger(__name__).info("Set max records to %i", model.maxRecords())

@QtCore.Slot(bool)
def toggleTimer(set_enabled:bool):

	if set_enabled:
		timer.start()
		logging.getLogger(__name__).info("Started auto-logger at %ims intervals", timer.interval())
	else:
		timer.stop()
		logging.getLogger(__name__).info(f"Stopped auto-logger")

@QtCore.Slot(int)
def setAutoLoggerInterval(interval_ms:int):

	timer.setInterval(interval_ms)
	logging.getLogger(__name__).info("Auto-logger interval set to %ims", interval_ms)

if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd_main = QtWidgets.QWidget()
	wnd_main.setWindowTitle("Lil' Log Viewer Boy")
	wnd_main.setLayout(QtWidgets.QVBoxLayout())
	wnd_main.resize(500, 200)
	wnd_main.show()

	
	model = LBLogDataModel(max_records=5)
	handler = LBLogHandler(model)
	log_shower = LBLogRecordViewer(log_model=model)


	timer = QtCore.QTimer(interval=5000)
	timer.timeout.connect(lambda: logging.getLogger().info("Ahaa"))
	timer.start()

	wnd_main.layout().addWidget(log_shower)

	
	# Counts
	lay_counts = QtWidgets.QHBoxLayout()

	lbl_record_count = QtWidgets.QLabel()
	log_shower.model().modelReset.connect(lambda: lbl_record_count.setText(f"Records Displayed: {log_shower.model().rowCount()}"))
	log_shower.model().rowsInserted.connect(lambda: lbl_record_count.setText(f"Records Displayed: {log_shower.model().rowCount()}"))
	log_shower.model().rowsRemoved.connect(lambda: lbl_record_count.setText(f"Records Displayed: {log_shower.model().rowCount()}"))

	lbl_remember_last = QtWidgets.QLabel("Remember Last:")
	spin_remember_last = QtWidgets.QSpinBox(minimum=0, maximum=9999, value=model.maxRecords())
	spin_remember_last.setFixedWidth(60)
	spin_remember_last.valueChanged.connect(setMaxRecordsFromInput)
	model.sig_max_records_changed.connect(spin_remember_last.setValue)

	
	lay_counts.addWidget(lbl_record_count)
	lay_counts.addStretch()
	lay_counts.addWidget(lbl_remember_last)
	lay_counts.addWidget(spin_remember_last)

	wnd_main.layout().addLayout(lay_counts)

	
	# Auto logger config

	lay_autologger = QtWidgets.QHBoxLayout()
	chk_enable_auto_logger = QtWidgets.QCheckBox("Autologger Enabled")
	chk_enable_auto_logger.setChecked(timer.isActive())
	chk_enable_auto_logger.checkStateChanged.connect(lambda state: toggleTimer(state == QtCore.Qt.CheckState.Checked))
	lay_autologger.addWidget(chk_enable_auto_logger)

	lbl_auto_interval = QtWidgets.QLabel("Auto-Logger Interval:")
	spin_auto_interval = QtWidgets.QSpinBox(minimum=100, maximum=9 * 1_000_000, value=timer.interval(), suffix="ms")
	spin_auto_interval.setFixedWidth(100)
	spin_auto_interval.valueChanged.connect(setAutoLoggerInterval)

	lay_autologger.addStretch()
	lay_autologger.addWidget(lbl_auto_interval)
	lay_autologger.addWidget(spin_auto_interval)

	wnd_main.layout().addLayout(lay_autologger)

	


	#logging.getLogger().setLevel(logging.DEBUG)
	logging.basicConfig(level=logging.NOTSET)
	logging.getLogger().addHandler(handler)
	logging.getLogger().info("Heeyyyy")
	





	app.exec()