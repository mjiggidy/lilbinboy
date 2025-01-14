import random
from PySide6 import QtCore, QtGui, QtWidgets

class TRTHistoryPanel(QtWidgets.QFrame):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._sequence_name = QtWidgets.QLabel("Hi")
		self._tree_sequences = QtWidgets.QTreeView()
	#	self.lbl.setFixedHeight(50)

		self.layout().addWidget(self._sequence_name)
		self.layout().addWidget(self._tree_sequences)
		self.layout().addWidget(QtWidgets.QGroupBox())

		self.setFrameShape(QtWidgets.QFrame.Shape.Panel)
		self.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)

	def setModel(self, model:QtCore.QAbstractItemModel):

		self._tree_sequences.setModel(model)
	
	#def sizeHint(self) -> QtCore.QSize:
	#	return QtCore.QSize(super().sizeHint().width(), 100)

class TRTHistorySnapshotLabelDelegate(QtWidgets.QStyledItemDelegate):

	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		margin = QtCore.QPoint(30, 5)
		
		
		super().paint(painter, option, index)
		
		painter.save()

		label_info = index.model().record(index.row())

		rect = option.rect

		font = painter.font()
		font.setPointSizeF(font.pointSizeF() * 1.2)
		font.setBold(True)

		painter.setFont(font)
		painter.drawText(rect.adjusted(margin.x(), margin.y(), -margin.y(), -margin.y()), label_info.field("name").value())

		font = QtGui.QFont()
		# font = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.SystemFont.FixedFont)
		#font.setPointSizeF(font.pointSizeF() * 1.2)
		sub_rect = rect.adjusted(margin.x(), margin.y() + 20, -margin.y(), -margin.y())

		painter.setFont(font)
		painter.drawText(sub_rect, "01:47:23:12", QtCore.Qt.AlignmentFlag.AlignLeft|QtCore.Qt.AlignmentFlag.AlignBottom)

		datetime_str = QtCore.QDateTime.fromString(label_info.field("datetime_created").value(), QtCore.Qt.DateFormat.ISODate)
		#print(datetime_str.toString(QtCore.Qt.DateFormat.TextDate))
		painter.drawText(sub_rect, datetime_str.toString(QtCore.Qt.DateFormat.TextDate), QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignBottom)

		painter.restore()
	
	def sizeHint(self, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex) -> QtCore.QSizeF:
		return QtCore.QSize(super().sizeHint(option, index).width(), 46)




class TRTHistoryViewer(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setWindowTitle("History Viewer")
		#self.setWindowFlag(QtCore.Qt.WindowType.Tool)
		self.setLayout(QtWidgets.QHBoxLayout())

		self._lst_saved = QtWidgets.QListView()
		self._scroll_panels = QtWidgets.QScrollArea()

		self._setupWidgets()
	
	def _setupWidgets(self):

		self._lst_saved.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, self.sizePolicy().verticalPolicy())
		self._lst_saved.setItemDelegate(TRTHistorySnapshotLabelDelegate())
		self._lst_saved.setAlternatingRowColors(True)

		self.layout().addWidget(self._lst_saved)

		self._scroll_panels.setLayout(QtWidgets.QVBoxLayout())
		self._scroll_panels.setVerticalScrollBarPolicy(QtGui.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._scroll_panels.setWidgetResizable(True)
		#self._scroll_panels.setSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, self.sizePolicy().verticalPolicy())

		self._scroll_area = QtWidgets.QWidget()
		self._scroll_area.setLayout(QtWidgets.QVBoxLayout())

		for _ in range(random.randrange(3,5)):
			self._scroll_area.layout().addWidget(TRTHistoryPanel())
		self._scroll_area.layout().addStretch()

		self._scroll_panels.setWidget(self._scroll_area)

		self.layout().addWidget(self._scroll_panels)