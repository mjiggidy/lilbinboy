import sys
from PySide6 import QtCore, QtWidgets

from lilbinboy.siftwidget import scopesmodel
from lilbinboy.binview  import binviewitemtypes, binviewmodel, jsonadapter
from lilbinboy.binitems import binitemsmodel
from lilbinboy.textview import bincompositemodel
from lilbinboy.core import binparser

from lilbinboy.binvieweditor import editorwidget
from lilbinboy.textview import textview

from lilbinboy.binfilters import binviewproxymodel, bindisplayproxymodel

import avb, avbutils



@QtCore.Slot(dict)
def exportJson():

	binview_info = bin_view_model.binViewInfo()
	with open(binview_info.name + ".json", "w") as view_handle:

		print(jsonadapter.BSBinViewJsonAdapter.from_binview(binview_info), file=view_handle)
		print("Written to", view_handle.name)

def loadFromBinPath(bin_path):
		
	if bin_path.casefold().endswith(".avb"):
		
		with avb.open(bin_path) as bin_handle:
			bin_view_model.setBinViewInfo(binviewitemtypes.BSBinViewInfo.from_binview(bin_handle.content.view_setting))

			for idx, item in enumerate(bin_handle.content.items):
				thing = binparser.load_item_from_bin(item)
				bin_item_model.addBinItem(thing)
	

	elif bin_path.casefold().endswith(".json"):

		with open(sys.argv[1]) as view_handle:
			bin_view_model.setBinViewInfo(jsonadapter.BSBinViewJsonAdapter.to_binview(view_handle.read()))

	
if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")


	

	bin_view_model      = binviewmodel.BSBinViewModel()
	bin_item_model      = binitemsmodel.BSBinItemModel()

	bin_item_filter     = bindisplayproxymodel.BSBinDisplayFilterProxyModel(bin_items_model=bin_item_model)
	bin_view_filter     = binviewproxymodel.BSBinViewFilterProxyModel(bin_columns_model=bin_view_model)

	bin_composite_model = bincompositemodel.BSBinCompositeModel(item_model=bin_item_filter, view_model=bin_view_filter)

	final_proxy         = QtCore.QIdentityProxyModel()
	final_proxy.setSourceModel(bin_composite_model)

	sift_columns_model  = scopesmodel.BSSiftScopeViewModel(sift_filter_model=bin_view_filter)
	
	###
	
	loadFromBinPath(sys.argv[1])
	
	wnd_editor = editorwidget.BSBinViewColumnEditor()
	wnd_editor.setBinViewModel(bin_view_model)
	wnd_editor.show()

	tree_binviewer = textview.BSBinTextView()
	tree_binviewer.setModel(final_proxy)
	tree_binviewer.move(wnd_editor.geometry().topRight() + QtCore.QPoint(100,0))
	tree_binviewer.show()

	list_sift_columns = QtWidgets.QListView()
	list_sift_columns.setModel(sift_columns_model)
	tree_binviewer.move(wnd_editor.geometry().topLeft() + QtCore.QPoint(-100,0))
	list_sift_columns.show()

	list_sift_columns.activated.connect(lambda: print(list_sift_columns.currentData()))

	#bin_item_filter.setAcceptedItemTypes(avbutils.bins.BinDisplayItemTypes.SOURCE)

	wnd_editor.sig_export_binview_requested.connect(exportJson)
	

	app.exec()