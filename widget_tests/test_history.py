import sys
from PySide6 import QtCore, QtWidgets, QtSql
from lilbinboy.lbb_features.trt.wnd_history import TRTHistoryViewer

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd_history = TRTHistoryViewer()

db = QtSql.QSqlDatabase("QSQLITE")
db.setDatabaseName(sys.argv[1])
db.open()

if not db.open():
	print("Nah lol", db.lastError().text())

model = QtSql.QSqlQueryModel()
model.setQuery("SELECT * FROM trt_snapshot_labels ORDER BY datetime_created DESC", db)

wnd_history._lst_saved.setModel(model)

wnd_history.show()

app.exec()