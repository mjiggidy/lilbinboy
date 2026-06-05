from __future__ import annotations
import sys, enum, typing, os, dataclasses
import avb, avbutils
from PySide6 import QtCore, QtGui, QtWidgets

from lilbinboy.binitems import binitemtypes

class BSBinViewColumnEditorColumns(enum.Enum):

	GRIPPER     = enum.auto()
	COLUMN_NAME = enum.auto()
	DATA_FORMAT = enum.auto()
	HIDDEN  = enum.auto()
	DELETE      = enum.auto()

class BSBinViewModel(QtCore.QAbstractItemModel):

	sig_bin_view_name_changed = QtCore.Signal(str)

	def __init__(self, *args, name:str|None, items:list[binitemtypes.BSAbstractViewHeaderItem]|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._bin_view_column_columns:list[BSBinViewColumnEditorColumns] = [
#			BSBinViewColumnEditorColumns.GRIPPER,
			BSBinViewColumnEditorColumns.COLUMN_NAME,
			BSBinViewColumnEditorColumns.DELETE,
			BSBinViewColumnEditorColumns.DATA_FORMAT,
			BSBinViewColumnEditorColumns.HIDDEN,
		]

		print("Name was", name)
		self._bin_view_name = name or "Poop"
		
		self._bin_view_column_items:list[binitemtypes.BSAbstractViewHeaderItem] = items or list()

		self.sig_bin_view_name_changed.emit(self._bin_view_name)

	def parent(self, child:QtCore.QModelIndex) -> QtCore.QModelIndex:

		return QtCore.QModelIndex()
	
	def rowCount(self, parent:QtCore.QModelIndex) -> int:

		if parent.isValid():
			return 0

		return len(self._bin_view_column_items)
	
	def columnCount(self, parent:QtCore.QModelIndex) -> int:

		return len(self._bin_view_column_columns)
	
	def headerRoleForIndex(self, index:QtCore.QModelIndex) -> BSBinViewColumnEditorColumns|None:
		"""Given an index, figure out which header (as in, the listview editor section) it's under"""

		if not index.isValid() or index.column() > self.columnCount(index.parent()):
			return None
		
		return self._bin_view_column_columns[index.column()]
	
	@QtCore.Slot()
	def setBinViewName(self, name:str):

		if self._bin_view_name == name:
			return
		
		self._bin_view_name = name
		self.sig_bin_view_name_changed.emit(name)
	
	def binViewName(self) -> str:
		return self._bin_view_name
	
	def itemForIndex(self, index:QtCore.QModelIndex) -> binitemtypes.BSAbstractViewHeaderItem:
		"""Given an index, return the item"""
		
		if not index.isValid() or index.row() > self.rowCount(index.parent()):
			return None
		
		return self._bin_view_column_items[index.row()]
	
	def setData(self, index:QtCore.QModelIndex, value:typing.Any, /, role:QtCore.Qt.ItemDataRole|binitemtypes.BSBinColumnDataRoles):

		display_item = self._bin_view_column_items[index.row()]
		display_item.setData(value, role)
		
		print("Set ", value, " for role ", role," on ", display_item.display_name())
		self.dataChanged.emit(index.siblingAtColumn(0), index.siblingAtColumn(self.columnCount(index.parent())-1), [role])
		return True

		#return super().setData(index, value, role)
	
	def data(self, index:QtCore.QModelIndex, /, role:QtCore.Qt.ItemDataRole) -> typing.Any:
		
		if not index.isValid():
			return None
		
		# User role returns header view item
		if role == QtCore.Qt.ItemDataRole.UserRole:
			return self.itemForIndex(index)
		
		column_data_role = self.headerRoleForIndex(index)
		item             = self.itemForIndex(index)

		if not column_data_role:
			raise ValueError(f"Strange index requesting data: {index=} {role=}")
		
		# Column Name
		if column_data_role == BSBinViewColumnEditorColumns.COLUMN_NAME:

			if role == QtCore.Qt.ItemDataRole.DisplayRole:
				return item.data(QtCore.Qt.ItemDataRole.DisplayRole)
		
		# Data Format
		elif column_data_role == BSBinViewColumnEditorColumns.DATA_FORMAT:

			if role == QtCore.Qt.ItemDataRole.DisplayRole:
				return str(item.data(binitemtypes.BSBinColumnDataRoles.BSDataFormat))[0]
		
		# Visibility Button
		elif column_data_role == BSBinViewColumnEditorColumns.HIDDEN:

			is_hidden = item.data(binitemtypes.BSBinColumnDataRoles.BSColumnIsHidden)
			
			if role == QtCore.Qt.ItemDataRole.DecorationRole:
				return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd) if is_hidden else QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove)
			
		# Delete Button
		elif column_data_role == BSBinViewColumnEditorColumns.DELETE:

			if role == QtCore.Qt.ItemDataRole.DecorationRole:

				is_user = item.data(binitemtypes.BSBinColumnDataRoles.BSColumnID) == avbutils.BinColumnFieldIDs.User
				return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.WindowClose) if is_user else QtGui.QIcon()
			
		elif column_data_role == BSBinViewColumnEditorColumns.GRIPPER:
			
			if role == QtCore.Qt.ItemDataRole.DecorationRole:
				return QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ViewFullscreen)
			
	def headerData(self, section:int, orientation:QtCore.Qt.Orientation, /, role:QtCore.Qt.ItemDataRole|binitemtypes.BSBinColumnDataRoles):
		
		if orientation == QtCore.Qt.Orientation.Vertical or role != QtCore.Qt.ItemDataRole.UserRole:
			return super().headerData(section, orientation, role)
		
		return self._bin_view_column_columns[section]
			
	def index(self, row:int, column:int, /, parent:QtCore.QModelIndex) -> QtCore.QModelIndex:

		if parent.isValid():
			return QtCore.QModelIndex()

		return self.createIndex(row, column, None)
	
	def flags(self, index:QtCore.QModelIndex) -> QtCore.Qt.ItemFlag:

		role = self.headerRoleForIndex(index)
		item = self.itemForIndex(index)

		base_flags = super().flags(index)
		base_flags |= QtCore.Qt.ItemFlag.ItemIsDragEnabled | QtCore.Qt.ItemFlag.ItemIsDropEnabled
		
		
#		if role == BSBinViewColumnEditorColumns.GRIPPER:
#			base_flags |= QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsDragEnabled
#			return base_flags
#		
		if role == BSBinViewColumnEditorColumns.COLUMN_NAME and item.data(binitemtypes.BSBinColumnDataRoles.BSColumnID) == avbutils.bins.BinColumnFieldIDs.User:
			base_flags |= QtCore.Qt.ItemFlag.ItemIsEditable
#		
#		elif role == BSBinViewColumnEditorColumns.VISIBILITY:
#			return base_flags & QtCore.Qt.ItemFlag.ItemIsUserCheckable
		

		return base_flags
	
	def supportedDropActions(self):
		
		return QtCore.Qt.DropAction.MoveAction
	
#	def dropMimeData(self, data, action, row, column, parent) -> bool:
#		print("Drop Mime")
#		return True
#		return super().dropMimeData(data, action, row, column, parent)
#	
#	def canDropMimeData(self, data, action, row, column, parent):
#		print("Can Drop", data.data(data.formats()[0]))
#		
#		return True
	
		return super().canDropMimeData(data, action, row, column, parent)

class BSBinViewColumnDelegate(QtWidgets.QStyledItemDelegate):


	def paint(self, painter:QtGui.QPainter, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		# NOTE: This gets confusing
		# The column editor view model returns the bin view column view item from its UserRole
		# which isn't even clear as I write it here. lol TODO: Refactor
		
		item:binitemtypes.BSAbstractViewHeaderItem = index.data(QtCore.Qt.ItemDataRole.UserRole)
		role =index.model().headerRoleForIndex(index)
		
		is_hidden = item.data(binitemtypes.BSBinColumnDataRoles.BSColumnIsHidden)

		#option.state &= ~QtWidgets.QStyle.StateFlag.State_HasFocus

		# Show hidden as dimmed
		if is_hidden:
			option.state &= ~QtWidgets.QStyle.StateFlag.State_Enabled

		if role == BSBinViewColumnEditorColumns.HIDDEN and option.state & QtWidgets.QStyle.StateFlag.State_HasFocus:
			option.palette.setCurrentColorGroup(QtGui.QPalette.ColorGroup.Active)
		
		super().paint(painter, option, index)

	def handleEditorEvent(self, object, event):
		print("Editor", event)
		return super().handleEditorEvent(object, event)

	def editorEvent(self, event:QtCore.QEvent, model:BSBinViewModel, option:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		role = model.headerRoleForIndex(index)
		item = model.itemForIndex(index)

		if role == BSBinViewColumnEditorColumns.HIDDEN:  # TODO: Use checked State?

			if event.type() == QtCore.QEvent.Type.MouseButtonRelease:

				is_hidden = not item.data(binitemtypes.BSBinColumnDataRoles.BSColumnIsHidden)
				model.setData(index, is_hidden, binitemtypes.BSBinColumnDataRoles.BSColumnIsHidden)

			return True

		return super().editorEvent(event, model, option, index)
	
	def setModelData(self, editor:QtWidgets.QWidget, model:BSBinViewModel, index:QtCore.QModelIndex):
		
		role = model.headerRoleForIndex(index)

		if role == BSBinViewColumnEditorColumns.COLUMN_NAME:

			column_name = editor.text()
			model.setData(index, column_name, binitemtypes.BSBinColumnDataRoles.BSColumnDisplayName)

		return super().setModelData(editor, model, index)
	
	def setEditorData(self, editor:QtWidgets.QLineEdit, index:QtCore.QModelIndex):
		
		role = index.model().headerRoleForIndex(index)

		if role == BSBinViewColumnEditorColumns.COLUMN_NAME:
			column_name = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
			editor.setText(column_name)
		#return super().setEditorData(editor, index)
		

@dataclasses.dataclass(frozen=True)
class BSBinViewColumnInfo:

	name      :str
	field_id  :avbutils.bins.BinColumnFieldIDs
	format_id :avbutils.bins.BinColumnFormat
	is_hidden :bool
	width     :int

	@classmethod
	def from_column(cls, column_info:dict, width:int|None=None):

		if column_info["type"] not in avbutils.bins.BinColumnFieldIDs:
			raise ValueError(f"Unknown field ID: {column_info['type']}")
		
		elif column_info["format"] not in avbutils.bins.BinColumnFormat:
			raise ValueError(f"Unknown column format ID: {column_info['format']}")

		return cls(
			name = column_info["title"],
			field_id  = avbutils.bins.BinColumnFieldIDs(column_info["type"]),
			format_id = avbutils.bins.BinColumnFormat(column_info["format"]),
			is_hidden = column_info["hidden"],
			width = width
		)
	
@dataclasses.dataclass(frozen=True)
class BSBinViewInfo:

	name:str
	columns:list[BSBinViewColumnInfo]

	@classmethod
	def from_binview(cls, binview:avb.bin.BinViewSetting) -> typing.Self:

		cols = list()

		for column in binview.columns:
			
			try:
				cols.append(BSBinViewColumnInfo.from_column(column))
			except ValueError as e:
				print(e)
				continue
		
		return cls(
			binview.name,
			cols
		)

def get_binview(bin_path:os.PathLike[str]) -> BSBinViewInfo:

	with avb.open(bin_path) as bin_handle:

		bin_contents = bin_handle.content
		bin_view     = bin_contents.view_setting

		return BSBinViewInfo.from_binview(bin_view)
	
class BSBinViewColumnListView(QtWidgets.QTableView):

	def __init__(self):

		super().__init__()

		self.setItemDelegate(BSBinViewColumnDelegate())
		self.setShowGrid(False)
		self.setAlternatingRowColors(True)
		self.setWordWrap(False)
		self.setAutoScroll(True)
		
		self.setSelectionBehavior(QtWidgets.QTableView.SelectionBehavior.SelectRows)
		self.setSelectionMode(QtWidgets.QTableView.SelectionMode.ExtendedSelection)
		
		self.setDropIndicatorShown(True)
		self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
		self.setDefaultDropAction(QtCore.Qt.DropAction.MoveAction)
		self.setDragEnabled(True)
		
		self.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
		self.verticalHeader().hide()
		self.horizontalHeader().hide()

		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

class BSBinViewColumnEditor(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())
		
		self._cmb_bin_view_list       = QtWidgets.QComboBox()
		self._btn_view_list_add       = QtWidgets.QPushButton()
		self._btn_view_list_modify = QtWidgets.QPushButton()
		self._btn_view_list_delete     = QtWidgets.QPushButton()
		
		self._view_editor = BSBinViewColumnListView()

		self._lay_view_list = QtWidgets.QHBoxLayout()
		self._lay_view_list.setSpacing(0)

		self._lay_view_list.addWidget(self._cmb_bin_view_list)
		self._lay_view_list.addWidget(self._btn_view_list_modify)
		self._lay_view_list.addWidget(self._btn_view_list_add)
		self._lay_view_list.addWidget(self._btn_view_list_delete)

		btn_width = 16*2
		self._cmb_bin_view_list.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.MinimumExpanding, self._cmb_bin_view_list.sizePolicy().verticalPolicy()))
		self._btn_view_list_modify.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.DocumentSave))
		self._btn_view_list_add.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
		self._btn_view_list_delete.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove))
		self.layout().addLayout(self._lay_view_list)

		self.layout().addWidget(QtWidgets.QLabel(self.tr("Add, Modify, and Rearrange Columns:")))
		self.layout().addWidget(self._view_editor)

		self._lay_buttons = QtWidgets.QHBoxLayout()

		self._btn_toggle_all = QtWidgets.QPushButton(self.tr("Show All/None"))
		self._btn_add_col    = QtWidgets.QPushButton(self.tr("Add User Column"))

		self._lay_buttons.addWidget(self._btn_add_col)
		self._lay_buttons.addStretch()
		self._lay_buttons.addWidget(self._btn_toggle_all)

		self.layout().addLayout(self._lay_buttons)
	
	def setBinViewModel(self, bin_view_model:BSBinViewModel):

		if self._view_editor.model() == bin_view_model:
			return
		
		print("Adding bin view", bin_view_model.binViewName())

		bin_view_model.sig_bin_view_name_changed.connect(self._cmb_bin_view_list.addItem)
		self._cmb_bin_view_list.addItem(bin_view_model.binViewName())
		self._view_editor.setModel(bin_view_model)

		for col in range(self._view_editor.horizontalHeader().count()):

			column_type = self._view_editor.model().headerData(col, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

			#print(column_type)
			
			if column_type == BSBinViewColumnEditorColumns.COLUMN_NAME:
			#	print(f"Set {column_type} to {QtWidgets.QHeaderView.ResizeMode.Stretch}")
				self._view_editor.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)
			
			else:
			#	print(f"Set {column_type} to {QtWidgets.QHeaderView.ResizeMode.ResizeToContents}")
				self._view_editor.horizontalHeader().setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
	



	
def main(bin_path:os.PathLike[str]):

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")
	
	binview_info = get_binview(bin_path)

	binview_col_views = []

	for col in binview_info.columns:

		col_view = binitemtypes.BSAbstractViewHeaderItem(
			field_name=str(col.field_id.value) + "_" + col.name,
			display_name=col.name,
			field_id = col.field_id,
			format_id=col.format_id,
			is_hidden=col.is_hidden
		)

		binview_col_views.append(col_view)

	viewmodel_binview = BSBinViewModel(name=binview_info.name, items=binview_col_views)

	wnd_editor = BSBinViewColumnEditor()
	wnd_editor.setBinViewModel(viewmodel_binview)
	wnd_editor.show()
	wnd_editor.resize(
		QtCore.QSize(
			wnd_editor.width(),
			wnd_editor.width() * 16/11
		)
	)

	
	return app.exec()
	
if __name__ == "__main__":

	if not len(sys.argv) > 1:
	
		import pathlib
		sys.exit(f"Usage: {pathlib.Path(__file__).name} bin_path.avb")
	
	sys.exit(main(sys.argv[1]))