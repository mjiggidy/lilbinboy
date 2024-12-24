from PySide6 import QtGui, QtWidgets

class LBErrorLogWindow(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setWindowFlag(QtGui.Qt.WindowType.Tool)
		self.setWindowTitle("Difficulties")
		self.resize(400,260)


		self.setLayout(QtWidgets.QVBoxLayout())
		self.table_errors = LBErrorLogTableView()
		self.layout().addWidget(self.table_errors)


		self.error_detail = QtWidgets.QTextEdit()
		self.error_detail.setReadOnly(True)
		
		self.widgetmapper = QtWidgets.QDataWidgetMapper()
		self.widgetmapper.setModel(self.table_errors.model())
		self.widgetmapper.addMapping(self.error_detail, 2)
		self.widgetmapper.setSubmitPolicy(QtWidgets.QDataWidgetMapper.SubmitPolicy.ManualSubmit)
		self.table_errors.selectionModel().currentRowChanged.connect(self.widgetmapper.setCurrentModelIndex)
		#self.widgetmapper.toFirst()


		self.layout().addWidget(self.error_detail)

class LBErrorLogTableView(QtWidgets.QTreeWidget):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.setSelectionBehavior(QtWidgets.QTreeWidget.SelectionBehavior.SelectRows)
		self.setSortingEnabled(True)
		self.setIndentation(0)
		self.setUniformRowHeights(True)
		self.setAlternatingRowColors(True)
		self.setHeaderLabels([
			"Module",
			"Datetime",
			"Error Message"
		])

		self.addTopLevelItems([
			QtWidgets.QTreeWidgetItem(["TRT Calculator", "Today", "Oh boy I don't even know where to get started"]),
			QtWidgets.QTreeWidgetItem(["TRT Calculator", "Today", "There were markers I didn't know how to read"]),
			QtWidgets.QTreeWidgetItem(["TRT Calculator", "Today", "That bin was just too scary to be honest"]),
		])

		for col in range(0, self.columnCount()):
			self.resizeColumnToContents(col)