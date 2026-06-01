import logging

from PySide6 import QtWidgets, QtGui, QtCore

from . import editorview, editorproxymodel

import avbutils

from ..binviewprovider import providermodel, binviewsources
from ..binview import binviewmodel, binviewitemtypes
from ..binfilters import binviewproxymodel
from ..widgets import binviewcombobox

from ..res import icons_binvieweditor

DEFAULT_ILLEGAL_FILENAME_CHARS = ("\\", "/", "<", ">", "?", "*", ":")

class BSBinViewColumnEditor(QtWidgets.QWidget):

	sig_export_binview_requested = QtCore.Signal(object, str)
	"""Export the given binview"""

	sig_delete_binview_requested = QtCore.Signal(object)
	"""Delete the given binview"""

	sig_focus_column_requested   = QtCore.Signal(object)
	"""User requests the given `BSBinColumnInfo` to be brought into focus"""

	sig_bin_view_source_selected = QtCore.Signal(object)
	"""A bin view has been chosen from available sources"""

	sig_user_column_added        = QtCore.Signal(object)
	"""A user column has been added to the current bin view"""

	def __init__(self, *args, bin_view_model:binviewmodel.BSBinViewModel|None=None, bin_view_provider:providermodel.BSBinViewProviderModel|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())
		
		# Bin View Save, Restore, and Delete
		self._cmb_bin_view_list       = binviewcombobox.BSBinViewSelectorComboBox()
		self._btn_view_list_add       = QtWidgets.QPushButton()
		self._btn_view_list_delete    = QtWidgets.QPushButton()

		# Icons 'n' delegates
		self._icon_visible  = QtGui.QIcon(":/icons/editorwidget/visibility_on.svg")
		self._icon_hidden   = QtGui.QIcon(":/icons/editorwidget/visibility_off.svg")
		self._icon_delete   = QtGui.QIcon(":/icons/editorwidget/delete.svg")
		self._icon_none     = QtGui.QIcon()

		# Models
		self._model_binviewprovider   = None
		self._model_binviewfilter     = binviewproxymodel.BSBinViewFilterProxyModel(parent=self)
		self._model_editor            = editorproxymodel.BSBinViewColumnEditorProxyModel(parent=self)

		# Editor View/Model
		self._view_editor = editorview.BSBinViewColumnListView()

		# Filter Options
		self._chk_show_hidden  = QtWidgets.QCheckBox(icon=self._icon_hidden)
		self._chk_show_visible = QtWidgets.QCheckBox(icon=self._icon_visible)
		
		# Action Buttons
#		self._btn_toggle_all = QtWidgets.QPushButton(self.tr("Toggle Visibility"))
		self._btn_add_col        = QtWidgets.QPushButton(self.tr("Add User Column"))
		self._btn_float_visibile = QtWidgets.QPushButton(self.tr("Float Visible To Top"))
		
		self._setupWidgets()
		self._setupSignals()

		self.setBinViewModel   (bin_view_model    or binviewmodel.BSBinViewModel(parent=self))
		self.setBinViewProvider(bin_view_provider or providermodel.BSBinViewProviderModel(parent=self))

	def _setupWidgets(self):

		# Editor View
		
		self._cmb_bin_view_list.setSizePolicy(
			QtWidgets.QSizePolicy(
				QtWidgets.QSizePolicy.Policy.MinimumExpanding,
				self._cmb_bin_view_list.sizePolicy().verticalPolicy()
			)
		)
		
		lay_view_list = QtWidgets.QHBoxLayout()
		lay_view_list.setSpacing(0)
		lay_view_list.addWidget(self._cmb_bin_view_list)
		lay_view_list.addWidget(self._btn_view_list_add)
		lay_view_list.addWidget(self._btn_view_list_delete)


		self._model_editor.setSourceModel(self._model_binviewfilter)
		self._view_editor .setModel(self._model_editor)

		self.layout().addLayout(lay_view_list)
		self.layout().addWidget(QtWidgets.QLabel(self.tr("Add, Modify, and Rearrange Columns:")))
		self.layout().addWidget(self._view_editor)

		# Icons
		self._view_editor.itemDelegate().setButtonIconProvider({
			editorproxymodel.BSBinViewColumnEditorFeature.VisibilityColumn:{
				# Is Hidden?
				True:  self._icon_hidden,
				False: self._icon_visible,
			},

			editorproxymodel.BSBinViewColumnEditorFeature.DeleteColumn: {
				# Allow Delete?
				True: self._icon_delete,
			}
		})


		# Filter Columns By Visibility

#		self._btn_add_col.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
#		self._btn_float_visibile.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.GoUp))

		self._chk_show_hidden .setChecked(self._model_binviewfilter.binViewOptions() & binviewproxymodel.BSBinViewFilterOptions.ShowHidden)
		self._chk_show_hidden .setToolTip(self.tr("Show Hidden Columns"))
		self._chk_show_visible.setChecked(self._model_binviewfilter.binViewOptions() & binviewproxymodel.BSBinViewFilterOptions.ShowVisible)
		self._chk_show_visible .setToolTip(self.tr("Show Visible Columns"))

		lay_mods = QtWidgets.QHBoxLayout()
		lay_mods.addWidget(self._btn_add_col)
		lay_mods.addStretch()
		lay_mods.addWidget(self._btn_float_visibile)
		self.layout().addLayout(lay_mods)

		lay_filters = QtWidgets.QHBoxLayout()
		lay_filters.addWidget(self._chk_show_visible)
		lay_filters.addWidget(self._chk_show_hidden)
		lay_filters.addStretch()
		self.layout().addLayout(lay_filters)

		# Toggle Buttons (eh..?)
		
		self._btn_view_list_add.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListAdd))
		self._btn_view_list_delete.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ListRemove))

	#	lay_buttons = QtWidgets.QHBoxLayout()
	#	lay_buttons.addWidget(s)
	#	lay_buttons.addStretch()
#	#	lay_buttons.addWidget(self._btn_toggle_all)
	#	self.layout().addLayout(lay_buttons)

	def _setupSignals(self):

		self._cmb_bin_view_list.sig_binview_source_selected.connect(self.sig_bin_view_source_selected)
		self._btn_view_list_add.clicked.connect(self.requestExportBinView)
		self._btn_view_list_delete.clicked.connect(self.requestDeleteBinView)
		
		self._view_editor.activated.connect(self.binColumnDoubleClicked)
		
#		self._btn_toggle_all.clicked.connect(self._view_editor.toggleSelectedVisibility)
#		self._cmb_bin_view_list.currentTextChanged.connect(self.updateButtonState)
		self._btn_add_col.clicked.connect(self.addUserColumn)
		self._btn_float_visibile.clicked.connect(self.floatVisibleToTop)
		
		self._chk_show_hidden.clicked.connect(self.userChangedFilters)
		self._chk_show_visible.clicked.connect(self.userChangedFilters)

	@QtCore.Slot()
	def floatVisibleToTop(self):

		self._model_editor.sort(binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole, QtCore.Qt.SortOrder.AscendingOrder)

	@QtCore.Slot()
	def addUserColumn(self):

		name, did_it = QtWidgets.QInputDialog.getText(
			self,
			self.tr("Add User Column"),
			self.tr("Enter a name for the new user column:")
		)

		if not did_it:
			return
		
		new_row = self._model_editor.rowCount(QtCore.QModelIndex())

		self._model_editor.insertRow(
			new_row, QtCore.QModelIndex()
		)

		new_user_row_idx = self._model_editor.index(new_row, 1, QtCore.QModelIndex())
		#print(f"Inserted {new_item}, {name}")
		self._model_editor.setData(new_user_row_idx, name, QtCore.Qt.ItemDataRole.DisplayRole)
		self._model_editor.setData(new_user_row_idx, avbutils.bins.BinColumnFieldIDs.User, binviewitemtypes.BSBinViewColumnInfoRole.FieldIdRole)
		self._model_editor.setData(new_user_row_idx, avbutils.bins.BinColumnFormat.UserText, binviewitemtypes.BSBinViewColumnInfoRole.FormatIdRole)
		self._model_editor.setData(new_user_row_idx, False, binviewitemtypes.BSBinViewColumnInfoRole.IsHiddenRole)

		self._view_editor.selectionModel().select(new_user_row_idx, QtCore.QItemSelectionModel.SelectionFlag.ClearAndSelect|QtCore.QItemSelectionModel.SelectionFlag.Rows)

		self.sig_user_column_added.emit(new_user_row_idx)

		# NOTE: View defers its little layout updates until the next event loop
		# so I'mma need to do it manually before we can scroll

		self._view_editor.updateGeometries()
		self._view_editor.scrollTo(new_user_row_idx, QtWidgets.QAbstractItemView.ScrollHint.EnsureVisible)

		self.sig_user_column_added.emit(new_user_row_idx)

	@QtCore.Slot()
	def userChangedFilters(self):

		bin_view_options = binviewproxymodel.BSBinViewFilterOptions(0)

		if self._chk_show_hidden.isChecked():
			bin_view_options |= binviewproxymodel.BSBinViewFilterOptions.ShowHidden

		if self._chk_show_visible.isChecked():
			bin_view_options |= binviewproxymodel.BSBinViewFilterOptions.ShowVisible

		self._model_binviewfilter.setBinViewOptions(bin_view_options)
	
	@QtCore.Slot(QtCore.QModelIndex)
	def binColumnDoubleClicked(self, index:QtCore.QModelIndex):
		"""User requesting column focus"""

		self.sig_focus_column_requested.emit(index.data(binviewitemtypes.BSBinViewColumnInfoRole.RawColumnInfo))

	def setBinViewModel(self, bin_view_model:binviewmodel.BSBinViewModel):

#		if self._model_editor.sourceModel() == bin_view_model:
#			return
#		
		logging.getLogger(__name__).debug("Setting editor model to %s", repr(bin_view_model))

		self._model_binviewfilter.setSourceModel(bin_view_model)
	
	def setBinViewProvider(self, bin_view_provider:providermodel.BSBinViewProviderModel):

		if self._model_binviewprovider == bin_view_provider:
			return
		
		if self._model_binviewprovider is not None:
			self._model_binviewprovider.disconnect(self)
		
		bin_view_provider.rowsInserted.connect(self.updateButtonState)
		bin_view_provider.rowsRemoved .connect(self.updateButtonState)
		bin_view_provider.modelReset  .connect(self.updateButtonState)
		
		self._model_binviewprovider = bin_view_provider

		self._cmb_bin_view_list.setModel(self._model_binviewprovider)

	@QtCore.Slot()
	def updateButtonState(self):
		"""Update buttons on view change"""

#		print("Haha yeah I know oh boy")

		binview_source = self._model_binviewprovider.sessionBinViewSources()[0] if self._model_binviewprovider.sessionBinViewSources() else None

		if binview_source is None:
#			print("**Well gall darn")
			self._btn_view_list_delete.setEnabled(False)
			return

#		print(f"{binview_source.name()=} in {[b.name() for b in self._bin_view_provider.storedBinViewSources()]} ?  {binview_source.name() in (bvs.name() for bvs in self._bin_view_provider.storedBinViewSources())}")

		self._btn_view_list_delete.setEnabled(
			binview_source is not None \
			and not binview_source.isModified() \
			and binview_source.name() in (bvs.name() for bvs in self._model_binviewprovider.storedBinViewSources()) \
		)

	@QtCore.Slot()
	def requestExportBinView(self):
		"""Prepare binview as a dict for export"""

		if not self._model_editor.sourceModel():
			raise ValueError("No bin view to save")

		# NOTE: This is real fragile but ugh
		binview_source:binviewitemtypes.BSBinViewInfo|None = self._cmb_bin_view_list.currentData()
		if binview_source is None or not binview_source.binViewInfo():
			raise ValueError("No bin view to save")
		
		binview_info = binview_source.binViewInfo()
		save_name    = self._promptForBinViewName(self._cmb_bin_view_list.currentText())

		if not save_name:
			return
		
		file_info = self._model_binviewprovider.saveAsStoredBinView(binview_info, save_name)

		if file_info:

			self.sig_bin_view_source_selected.emit(

				binviewsources.BSBinViewSourceBin(
					binviewitemtypes.BSBinViewInfo(
						name = save_name,
						columns = binview_info.columns
					)
				)
			)

	@QtCore.Slot()
	def requestDeleteBinView(self):

		binview_source:binviewsources.BSAbstractBinViewSource = self._cmb_bin_view_list.currentData()

		if not binview_source:

			logging.getLogger(__name__).error("No bin view selected for deletion")
			return

		if QtWidgets.QMessageBox.question(
			self,
			self.tr("Delete Bin View"),
			self.tr("Are you sure you want to delete the stored bin view {binview_name}?").format(binview_name=binview_source.name())
		) != QtWidgets.QMessageBox.StandardButton.Yes:
			
			return
		
		self._model_binviewprovider.deleteStoredBinViewSource(binview_source)

	def _isValidFileName(self, filename:str) -> bool:

		if not filename:
			return False
		
		if not filename.isprintable():
			return False
		
		if filename.startswith("."):
			return False
		
		if any(c in DEFAULT_ILLEGAL_FILENAME_CHARS for c in filename):
			return False
		
		return True
	
	def _promptForBinViewName(self, suggestion:str) -> str|None:

		while True:

			# NOTE: Gonnanita validate that strank

			# Ask for name
			save_name, was_serious_about_it = QtWidgets.QInputDialog.getText(
				self,
				self.tr("View Name"),
				self.tr("Name your view:"),
				text = suggestion
			)

			if not was_serious_about_it:
				return None
			
			# Check for illegal characters
			if not self._isValidFileName(save_name):

				user_choice = QtWidgets.QMessageBox.warning(
					self,
					self.tr("Invalid Bin Name"),
					self.tr("The given bin name contains characters that are not allowed.  Please use alphanumeric characters, and do not start names with a period.")
				)

				continue

			
			# Start over if overwrite is "undesirable" to the "user"
			if save_name in [bvs.name() for bvs in self._model_binviewprovider.storedBinViewSources()]:

				user_choice = QtWidgets.QMessageBox.question(
					self,
					self.tr("Bin View Already Exists"),
					self.tr("Replace the existing bin view named \"{save_name}\"?").format(save_name=save_name)
				)

				if user_choice == QtWidgets.QMessageBox.StandardButton.No:
					continue
			
			return save_name


	def binViewSelector(self) -> binviewcombobox.BSBinViewSelectorComboBox:

		return self._cmb_bin_view_list