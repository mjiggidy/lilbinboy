from __future__ import annotations
import typing

from PySide6 import QtWidgets, QtGui, QtCore

from . import editorproxymodel
from ..binview import binviewitemtypes
from ..utils import palettes
import avbutils

if typing.TYPE_CHECKING:
	from . import editorwidget

class BSBinViewColumnDelegate(QtWidgets.QStyledItemDelegate):

	sig_hide_column_index         = QtCore.Signal(int, QtCore.QModelIndex)
	sig_remove_selected_bin_columns = QtCore.Signal()
	sig_rename_column_for_index   = QtCore.Signal(int, QtCore.QModelIndex, str)

	DEFAULT_BUTTON_MARGINS = QtCore.QMargins(1,1,1,1)

	DEFAULT_BUTTON_ICONS = \
	{
		editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn:{
			True:  QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.WeatherClear),
			False: QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.WeatherFewClouds),
		},

		editorproxymodel.BSBinViewColumnEditorFeature.DeleteColumn: {
			True: QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditClear),
		}
	}

	DEFAULT_FORMAT_ICONS = \
	{
		avbutils.bins.BinColumnFormat.UserText:   QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.UserOffline),
		avbutils.bins.BinColumnFormat.CodecInfo:  QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.CameraVideo),
		avbutils.bins.BinColumnFormat.DateTime:   QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.AppointmentSoon),
		avbutils.bins.BinColumnFormat.Frame:      QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.VideoDisplay),
		avbutils.bins.BinColumnFormat.FrameCount: QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.AddressBookNew),
		avbutils.bins.BinColumnFormat.FrameRate:  QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.AppointmentMissed),
		avbutils.bins.BinColumnFormat.Icon:       QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.MediaFlash),
		avbutils.bins.BinColumnFormat.Perf:       QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.EditCut),
		avbutils.bins.BinColumnFormat.Strict:     QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.SystemLockScreen),
		avbutils.bins.BinColumnFormat.Timecode:   QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.MediaSeekForward),
	}

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._button_icon_provider = self.DEFAULT_BUTTON_ICONS
		self._format_icon_provider = self.DEFAULT_FORMAT_ICONS

		self._btn_aspect_ratio = 1.3

	def buttonIconForFeature(self, editor_feature:editorproxymodel.BSBinViewColumnEditorFeature, data:typing.Any) -> QtGui.QIcon:

		return self._button_icon_provider.get(editor_feature, dict()).get(data, QtGui.QIcon())
	
	def buttonIconForFormat(self, format:avbutils.bins.BinColumnFormat) -> QtGui.QIcon:

		return self._format_icon_provider.get(format, QtGui.QIcon())

	def setButtonIconProvider(self, icon_provider:dict[editorproxymodel.BSBinViewColumnEditorFeature, dict[typing.Any, QtGui.QIcon]]):

		if self._button_icon_provider == icon_provider:
			return
		
		self._button_icon_provider = icon_provider

	def paint(self, painter:QtGui.QPainter, option_item:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex):

		self.initStyleOption(option_item, index)
#		print(option_item.state)

		view_widget:QtWidgets.QAbstractItemView = option_item.widget
		editor_feature = index.model().headerData(index.column(), QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

		
		can_be_hidden = index.data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)
		is_hidden     = index.siblingAtColumn(1).data(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

		option_item.state &= ~QtWidgets.QStyle.StateFlag.State_HasFocus

		# Show hidden as dimmed
		if can_be_hidden:

			option_item.state &= ~QtWidgets.QStyle.StateFlag.State_Enabled

			font = QtGui.QFont(option_item.font)
			font.setItalic(True)
			option_item.font = font
			option_item.fontmetrics = QtGui.QFontMetrics(font)
			
#		if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn and option.state & QtWidgets.QStyle.StateFlag.State_HasFocus:
#			option.palette.setCurrentColorGroup(QtGui.QPalette.ColorGroup.Active)

		if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn:

			can_be_hidden =  index.data(QtCore.Qt.ItemDataRole.UserRole)

			if not can_be_hidden:
				return super().paint(painter, option_item, index)
			
			option_empty = QtWidgets.QStyleOptionViewItem(option_item)
			option_empty.text = None
			super().paint(painter, option_empty, index)

#			print(is_hidden)

			#min_size = min(option_item.rect.width(), option_item.rect.height())
			button_rect = QtCore.QRect(option_item.rect).marginsRemoved(self.DEFAULT_BUTTON_MARGINS)
			button_icon  = self.buttonIconForFeature(editor_feature, is_hidden)


			button_option          = QtWidgets.QStyleOptionButton()
			button_option.rect     = button_rect
			button_option.icon     = button_icon
			button_option.iconSize = QtCore.QSize(*[view_widget.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_SmallIconSize) * 0.75]*2)
			button_option.state    = option_item.state

			if all((
				option_item.state & QtWidgets.QStyle.StateFlag.State_Selected,
				QtWidgets.QApplication.mouseButtons() & QtCore.Qt.MouseButton.LeftButton,
				view_widget.currentIndex().column() == index.column()
			)):
				button_option.state |= QtWidgets.QStyle.StateFlag.State_Sunken
			
			style = option_item.widget.style()
			style.drawControl(QtWidgets.QStyle.ControlElement.CE_PushButton, button_option, painter)

		elif editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.DeleteColumn:

			is_deletable = index.data(QtCore.Qt.ItemDataRole.UserRole)

			if not is_deletable:
				return super().paint(painter, option_item, index)
			
			option_empty = QtWidgets.QStyleOptionViewItem(option_item)
			option_empty.text = None
			super().paint(painter, option_empty, index)
			
			button_rect = QtCore.QRect(option_item.rect)
			button_rect = QtCore.QRect(option_item.rect).marginsRemoved(self.DEFAULT_BUTTON_MARGINS)
			button_icon  = self.buttonIconForFeature(editor_feature, is_deletable)

			is_dark_mode = palettes.colors_are_dark_mode(option_item.palette.color(QtGui.QPalette.ColorRole.WindowText),option_item.palette.color(QtGui.QPalette.ColorRole.Window))

			button_palette = QtGui.QPalette(option_item.palette)
			button_palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(128,64,64) if is_dark_mode else QtGui.QColor(255,64,64))   # Border
			button_palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(64,32,32)  if is_dark_mode else QtGui.QColor(255,200,200)) # Button base

			button_option = QtWidgets.QStyleOptionButton()
			button_option.rect = button_rect
			button_option.icon = button_icon
			button_option.palette = button_palette
			button_option.iconSize = QtCore.QSize(*[view_widget.style().pixelMetric(QtWidgets.QStyle.PixelMetric.PM_SmallIconSize)*.75]*2)
			button_option.state = option_item.state

			if all((
				option_item.state & QtWidgets.QStyle.StateFlag.State_Selected,
				QtWidgets.QApplication.mouseButtons() & QtCore.Qt.MouseButton.LeftButton,
				view_widget.currentIndex().column() == index.column()
			)):
#				print(view_widget.currentIndex().column() == index.column())
				button_option.state |= QtWidgets.QStyle.StateFlag.State_Sunken

			style = option_item.widget.style()
			style.drawControl(QtWidgets.QStyle.ControlElement.CE_PushButton, button_option, painter)

		elif editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.DataFormatColumn:

			option_empty = QtWidgets.QStyleOptionViewItem(option_item)
			option_empty.text = ""
			super().paint(painter, option_empty, index)

			format_icon = self.buttonIconForFormat(index.data(QtCore.Qt.ItemDataRole.UserRole))

			format_icon.paint(
				painter,
				option_item.rect.marginsRemoved(QtCore.QMargins(3,1,3,1)),
				QtCore.Qt.AlignmentFlag.AlignCenter,
				QtGui.QIcon.Mode.Disabled if is_hidden else QtGui.QIcon.Mode.Selected if option_item.state & QtWidgets.QStyle.StateFlag.State_Selected else QtGui.QIcon.Mode.Normal,
				QtGui.QIcon.State.Off if is_hidden else QtGui.QIcon.State.On,
			)

		else:
		
			super().paint(painter, option_item, index)

	def editorEvent(self, event:QtCore.QEvent, model:QtCore.QAbstractItemModel, option_item:QtWidgets.QStyleOptionViewItem, index:QtCore.QModelIndex) -> bool:

		if event.type() not in (QtCore.QEvent.Type.MouseButtonRelease, QtCore.QEvent.Type.MouseButtonPress, QtCore.QEvent.Type.MouseMove):
#			print("Discarding ", event.type().name)
			return False
		
		# NOTE: Boy this was awful.  The index gets mappedFromSource so the column always = 0
		# Need to ask the view instead I guess...?
		
		view_widget:QtWidgets.QAbstractItemView = option_item.widget
		actual_index   = view_widget.indexAt(event.pos())
		editor_feature = model.headerData(actual_index.column(), QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

#		print("delegate editorEvent got index ", actual_index)




		if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn:  # TODO: Use checked State?
		
			# NO DRAGGIN IF THEY BUTTINS
			if event.type() == QtCore.QEvent.Type.MouseMove:
				return True
			
			if event.type() == QtCore.QEvent.Type.MouseButtonPress and event.button() == QtCore.Qt.MouseButton.LeftButton:
				

				for selected_button_index in view_widget.selectionModel().selectedRows(actual_index.column()):
					view_widget.update(selected_button_index)
				

			elif event.type() == QtCore.QEvent.Type.MouseButtonRelease and event.button() == QtCore.Qt.MouseButton.LeftButton:

				#view_widget.update(actual_index)
				
				selected_row_indexes = view_widget.selectionModel().selectedRows(actual_index.column())
				
				if not selected_row_indexes:
					
					# Hmmmm....
					return True
				
				
				# NOTE: Doin' this in reverse row order so as not to change row indexes
				
				for selected_button_index in sorted(selected_row_indexes, key=lambda i: i.row(), reverse=True):

					if selected_button_index.data(QtCore.Qt.ItemDataRole.UserRole):
						self.sig_hide_column_index.emit(selected_button_index.row(), QtCore.QModelIndex())

					view_widget.update(selected_button_index)

			#return True
		
		elif editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.DeleteColumn:

			can_delete = actual_index.data(QtCore.Qt.ItemDataRole.UserRole)

			# NONNA THAT DRAGGIN THE BATTIN
			if can_delete and event.type() == QtCore.QEvent.Type.MouseMove:
				return True

			elif can_delete and event.type() == QtCore.QEvent.Type.MouseButtonPress and event.button() == QtCore.Qt.MouseButton.LeftButton:

				for selected_button_index in view_widget.selectionModel().selectedRows(actual_index.column()):

					if not selected_button_index.data(QtCore.Qt.ItemDataRole.UserRole):
						view_widget.selectionModel().select(selected_button_index, QtCore.QItemSelectionModel.SelectionFlag.Deselect|QtCore.QItemSelectionModel.SelectionFlag.Rows)
					else:
						view_widget.update(selected_button_index)
			
			elif can_delete and event.type() == QtCore.QEvent.Type.MouseButtonRelease and event.button() == QtCore.Qt.MouseButton.LeftButton:

				self.sig_remove_selected_bin_columns.emit()

				return True


		return super().editorEvent(event, model, option_item, index)
	
	def sizeHint(self, option, index) -> QtCore.QSize:

		height = super().sizeHint(option, index).height()

		return QtCore.QSize(height * self._btn_aspect_ratio, height)

	
	def setModelData(self, editor:QtWidgets.QWidget, model:QtCore.QAbstractItemModel, index:QtCore.QModelIndex):
		
		editor_feature = model.headerData(index.column(), QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

		if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.NameColumn:

			column_name = editor.text()
			self.sig_rename_column_for_index.emit(index, column_name)
	
	def setEditorData(self, editor:QtWidgets.QLineEdit, index:QtCore.QModelIndex):
		
		editor_feature = index.model().headerData(index.column(), QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)

		if editor_feature == editorproxymodel.BSBinViewColumnEditorFeature.NameColumn:
			column_name = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
			editor.setText(column_name)