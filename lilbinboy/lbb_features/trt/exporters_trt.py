from PySide6 import QtCore
from lilbinboy.lbb_features.trt.treeview_trt import TRTTreeViewHeaderItem

def export_tab_delimited(model:QtCore.QAbstractItemModel, path:str):

	import csv
	headeritems:list[TRTTreeViewHeaderItem] = model.headers()
	
	for item in headeritems:
		print(item.name())

	headers:list[str] = [model.headerData(idx, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole) for idx in range(model.columnCount(QtCore.QModelIndex()))]

	rows:list[dict[str,str]] = []
	row_total:dict[str,str] = {}

	for row in range(model.rowCount(QtCore.QModelIndex())):
		row_data:dict[str,str] = dict()
		for col, header in enumerate(headers):
			data = model.data(model.index(row, col, QtCore.QModelIndex()), QtCore.Qt.ItemDataRole.DisplayRole)
			row_data[header.strip()] = str(data).strip() if data else ""

			if headeritems[col].isNumeric():
				raw_data = model.data(model.index(row, col, QtCore.QModelIndex()), QtCore.Qt.ItemDataRole.UserRole)

				if header.strip() not in row_total:
					row_total[header.strip()] = raw_data
				else:
					row_total[header.strip()] += raw_data

		rows.append(row_data)
	
	if row_total:
		row_total[headers[0].strip()] = "Totals"
		rows.append(row_total)



	with open(path, "w", newline="") as tsv_file:

		writer = csv.DictWriter(tsv_file, fieldnames=headers, delimiter="\t")
		writer.writeheader()
		for row in rows:
			writer.writerow(row)

	print(rows)