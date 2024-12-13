from PySide6 import QtCore

def export_tab_delimited(model:QtCore.QAbstractItemModel, path:str):

	import csv

	headers:list[str] = [model.headerData(idx, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole) for idx in range(model.columnCount(QtCore.QModelIndex()))]

	rows:list[dict[str,str]] = []

	for row in range(model.rowCount(QtCore.QModelIndex())):
		row_data:dict[str,str] = dict()
		for idx, header in enumerate(headers):
			data = model.data(model.index(row, idx, QtCore.QModelIndex()), QtCore.Qt.ItemDataRole.DisplayRole)
			row_data[header.strip()] = str(data).strip() if data else ""
		rows.append(row_data)

	with open(path, "w", newline="") as tsv_file:

		writer = csv.DictWriter(tsv_file, fieldnames=headers, delimiter="\t")
		writer.writeheader()
		for row in rows:
			writer.writerow(row)

	print(rows)