import dataclasses
from PySide6 import QtCore, QtGui
from ...lbb_features.trt.wdg_sequence_treeview import TRTTreeViewHeaderItem

def export_delimited(model:QtCore.QAbstractItemModel, path:str, format:str):

	import csv
	headeritems:list[TRTTreeViewHeaderItem] = model.headers()
	headers:list[str] = [model.headerData(idx, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.DisplayRole) for idx in range(model.columnCount(QtCore.QModelIndex()))]

	rows:list[dict[str,str]] = []
	row_total:dict[str,str] = {}

	for row in range(model.rowCount(QtCore.QModelIndex())):
		row_data:dict[str,str] = dict()
		for col, header in enumerate(headers):
			data = model.data(model.index(row, col, QtCore.QModelIndex()), QtCore.Qt.ItemDataRole.DisplayRole)
			row_data[header.strip()] = str(data).strip() if data else ""

			if headeritems[col].isAccumulatingValue():
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

		writer = csv.DictWriter(tsv_file, fieldnames=headers, delimiter="\t" if format=="tsv" else ",")
		writer.writeheader()
		for row in rows:
			writer.writerow(row)

def export_json(json_info:dict, path:str):
	import json

	with open(path, "w") as json_handle:
		json.dump(json_info, json_handle, indent='\t')




def exportToSnapshot(proxy_model:QtCore.QAbstractProxyModel):
	"""Package timeline info for snapshot"""

	source_model = proxy_model.sourceModel()
	source_model_cols = source_model.columnCount(QtCore.QModelIndex())
	source_headers = [source_model.headerData(col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole) for col in range(source_model_cols)]

	timeline_infos:list[TimelineSnapshotInfo] = []

	# Look up in order according to TreeView rows, but map back to source model for the actual data
	for row in range(proxy_model.rowCount(QtCore.QModelIndex())):
		source_row = proxy_model.mapToSource(proxy_model.index(row, 0, QtCore.QModelIndex())).row()
		
		timeline_info = dict()

		# Clip color
		clip_color = source_model.index(source_row, source_headers.index("sequence_color")).data(QtCore.Qt.ItemDataRole.UserRole)
		timeline_info["clip_color"] = ",".join(str(x) for x in list(QtGui.QColor(clip_color).getRgb())[:3]) if clip_color else None
		
		# Sequence Name
		timeline_info["name"] = source_model.index(source_row, source_headers.index("sequence_name")).data(QtCore.Qt.ItemDataRole.UserRole)
		
		# Trimmed Duration
		duration_trimmed = source_model.index(source_row, source_headers.index("duration_trimmed_tc")).data(QtCore.Qt.ItemDataRole.UserRole)
		timeline_info["duration_frames"] = duration_trimmed.frame_number
		timeline_info["duration_tc"] = str(duration_trimmed)
		
		# F+F From Display Role Maybe?
		timeline_info["duration_ff"] = str(source_model.index(source_row, source_headers.index("duration_trimmed_ff")).data(QtCore.Qt.ItemDataRole.DisplayRole)).strip()

		timeline_infos.append(
			TimelineSnapshotInfo(**timeline_info)
		)
	
	return timeline_infos

@dataclasses.dataclass
class TimelineSnapshotInfo:

	clip_color:str
	name:str
	duration_frames:int
	duration_tc:str
	duration_ff:str