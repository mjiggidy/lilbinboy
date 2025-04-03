from PySide6 import QtCore, QtSql

class TRTHistorySQLQueryModel(QtSql.QSqlQueryModel):
	"""QSqlQueryModel which returns the row record as the UserRole"""

	def data(self, item:QtCore.QModelIndex, role:QtCore.Qt.ItemDataRole):		
		# Return the row's record as UserRole; otherwise whatever
		if item.isValid() and role == QtCore.Qt.ItemDataRole.UserRole:
			return self.record(item.row())
		else:
			return super().data(item, role)