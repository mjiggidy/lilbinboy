import sys
from PySide6 import QtCore, QtWidgets, QtSql
from lilbinboy.lbb_features.trt.hist_main import TRTHistoryViewer

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd_history = TRTHistoryViewer()

db = QtSql.QSqlDatabase.addDatabase("QSQLITE", "trt")
db.setDatabaseName(sys.argv[1])
db.open()

if not db.open():
	print("Nah lol", db.lastError().text())

query_labels = QtSql.QSqlQuery("SELECT * FROM trt_snapshot_labels ORDER BY datetime_created DESC", QtSql.QSqlDatabase.database("trt"))
wnd_history._lst_saved.model().setQuery(query_labels)


#query_sequences = QtSql.QSqlQuery(QtSql.QSqlDatabase.database("trt"))
#wnd_history._temp_history_panel.model().setQuery(query_sequences)


wnd_history.show()

app.exec()