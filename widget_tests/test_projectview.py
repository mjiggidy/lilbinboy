from PySide6 import QtCore, QtWidgets

class AvidProjectFileSystemModel(QtWidgets.QFileSystemModel):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def columnCount(self, parent:QtCore.QModelIndex) -> int:
		return super().columnCount(parent) + 1
	
	def data(self, index:QtCore.QModelIndex, role:int):

		if index.column() < super().columnCount(index.parent()):
			return super().data(index, role)
		
		if role == QtCore.Qt.ItemDataRole.DisplayRole:
			return "What's uuuuuuppppp"
	
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, role:int):
		if section <= self.columnCount(QtCore.QModelIndex())+1:
			print("Section is ", str(section), "of", self.columnCount(QtCore.QModelIndex()))
			return super().headerData(section, orientation, role)
		
		if role == QtCore.Qt.ItemDataRole.DisplayRole and orientation==QtCore.Qt.Orientation.Horizontal:
			print("Hell naw") 
			return "Current Lock"

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wdg_main = QtWidgets.QWidget()
txt_path = QtWidgets.QLineEdit()
tree_view = QtWidgets.QTreeView()
mdl_filesystem = AvidProjectFileSystemModel()

txt_path.textChanged.connect(mdl_filesystem.setRootPath)
mdl_filesystem.rootPathChanged.connect(lambda path: tree_view.setRootIndex(mdl_filesystem.index(mdl_filesystem.rootPath())))
mdl_filesystem.setOption(QtWidgets.QFileSystemModel.Option.DontUseCustomDirectoryIcons)
mdl_filesystem.setFilter(QtCore.QDir.Filter.AllDirs|QtCore.QDir.Filter.Files|QtCore.QDir.Filter.NoDotAndDotDot)
mdl_filesystem.setNameFilters(["*.avb"])
tree_view.setModel(mdl_filesystem)
tree_view.setUniformRowHeights(True)
tree_view.setAlternatingRowColors(True)
tree_view.setSortingEnabled(True)

wdg_main.setLayout(QtWidgets.QVBoxLayout())
wdg_main.layout().addWidget(txt_path)
wdg_main.layout().addWidget(tree_view)

wdg_main.show()

app.exec()
