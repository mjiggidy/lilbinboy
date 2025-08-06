import logging
from PySide6 import QtCore, QtWidgets
from lilbinboy.lbb_common import LBLogDataModel, LBLogHandler

if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	logging.basicConfig(level=logging.NOTSET)
	
	model = LBLogDataModel()
	handler = LBLogHandler(model)

	#logging.getLogger().setLevel(logging.DEBUG)

	logging.getLogger().addHandler(handler)
	logging.getLogger().info("Heeyyyy")
	log_shower = QtWidgets.QTreeView()
	log_shower.setAlternatingRowColors(True)
	log_shower.setIndentation(0)
	log_shower.setModel(model)
	log_shower.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
	log_shower.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

	log_shower.show()

	timer = QtCore.QTimer(interval=5000)
	timer.timeout.connect(lambda: logging.getLogger().info("Ahaa"))
	timer.start()

	app.exec()