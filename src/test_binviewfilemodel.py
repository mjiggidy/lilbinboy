import sys
from PySide6 import QtCore, QtWidgets
from lilbinboy.binviewprovider import providermodel
from lilbinboy.storage import storagemodel

PATH = "/Users/mjordan/Library/Application Support/GlowingPixel/Lil' Bin Boy/binviews"

if __name__ == "__main__":

#	if not len(sys.argv) > 1:
#		sys.exit(f"Usage: {pathlib.Path(__file__).name} bin.avb")

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	model_files = storagemodel.BSFileSystemModel()
	model_files.setFilter(
		QtCore.QDir.Filter.Files | \
		QtCore.QDir.Filter.NoDotAndDotDot
	)
	model_files.setNameFilters(["*.json"])
	model_files.setNameFilterDisables(False)

	#model_files.rowsRemoved.connect(print)
	idx_current_path = model_files.setRootPath(PATH)
	print(model_files.rootPath())

	model_provider = providermodel.BSBinViewProviderModel(storage_model=model_files)
	model_provider.rowsRemoved.connect(print)

#	model_files.rowsInserted.connect(print)

#	idx_current_path = model_files.setRootPath(QtCore.QDir(PATH).absoluteFilePath("binviews"))
	
	list_files = QtWidgets.QListView()
	list_files.setModel(model_provider)
#	list_files.setRootIndex(idx_current_path)
	list_files.show()

	sys.exit(app.exec())

