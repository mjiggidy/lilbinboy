import logging
from PySide6 import QtCore, QtWidgets
from lilbinboy.lbb_common import LBLogDataModel, LBLogHandler

class LBLogRecordViewer(QtWidgets.QTreeView):

	def __init__(self, log_model:LBLogDataModel, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

		self.setAlternatingRowColors(True)
		self.setIndentation(0)
		self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
		
		self.setModel(model)

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

	wnd_main.layout().addWidget(log_shower)

	txt_record_count = QtWidgets.QLabel()
	log_shower.model().modelReset.connect(lambda: txt_record_count.setText(f"Records Displayed: {log_shower.model().rowCount()}"))
	log_shower.model().rowsInserted.connect(lambda: txt_record_count.setText(f"Records Displayed: {log_shower.model().rowCount()}"))
	log_shower.model().rowsRemoved.connect(lambda: txt_record_count.setText(f"Records Displayed: {log_shower.model().rowCount()}"))
	
	wnd_main.layout().addWidget(txt_record_count)

	
	


	#logging.getLogger().setLevel(logging.DEBUG)
	logging.basicConfig(level=logging.NOTSET)
	logging.getLogger().addHandler(handler)
	logging.getLogger().info("Heeyyyy")
	



	timer = QtCore.QTimer(interval=5000)
	timer.timeout.connect(lambda: logging.getLogger().info("Ahaa"))
	timer.start()

	app.exec()