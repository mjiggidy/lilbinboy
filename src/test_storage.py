import sys, logging
from PySide6 import QtCore, QtGui, QtWidgets

from lilbinboy.storage import storagemodel, flatfilelistproxy

logging.basicConfig(level=logging.DEBUG)

app = QtWidgets.QApplication()

model_storage = storagemodel.BSFileSystemModel()
model_storage.setRootPath("/Users/mjordan/Library/Application Support/GlowingPixel/Lil' Bin Boy")
model_storage.setFilter(
	QtCore.QDir.Filter.AllDirs|\
	QtCore.QDir.Filter.Files|\
	QtCore.QDir.Filter.NoDotAndDotDot|\
	QtCore.QDir.Filter.Readable
)


#model_storage.directoryLoaded.connect(print)

proxy_file_list = flatfilelistproxy.BSFlatFileListProxy()
proxy_file_list.setSourceModel(model_storage)
#proxy_file_list.setFileFilters("*.json")

list_files = QtWidgets.QTreeView()
list_files.setModel(proxy_file_list)

path_index = proxy_file_list.pathIndex(
	QtCore.QDir(model_storage.rootDirectory()).filePath(".")
)
print("Setting path index to ", path_index)

list_files.setRootIndex(path_index)
list_files.show()

print(proxy_file_list.rowCount(path_index))

sys.exit(app.exec())