import sys
from PySide6 import QtCore, QtWidgets, QtSql
from lilbinboy.lbb_features.trt.hist_main import TRTHistoryViewer

app = QtWidgets.QApplication()
app.setStyle("Fusion")


db = QtSql.QSqlDatabase.addDatabase("QSQLITE", "trt")
db.setDatabaseName(sys.argv[1])
db.open()

if not db.open():
	print("Nah lol", db.lastError().text())


#query_sequences = QtSql.QSqlQuery(QtSql.QSqlDatabase.database("trt"))
#wnd_history._temp_history_panel.model().setQuery(query_sequences)

wnd_history = TRTHistoryViewer(db)
#wnd_history.updateLiveSnapshot([])
#wnd_history.saveLiveToSnapshot("Taa Haa!!")
wnd_history.show()

app.exec()