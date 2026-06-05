from PySide6 import QtCore, QtGui, QtWidgets

from ..binviewprovider import providermodel, binviewsources

DEFAULT_MODIFIED_SYMBOL = "*"

class BSBinViewSelectorComboBox(QtWidgets.QComboBox):
	"""A QComboBox for selecting binviews from a given binview provider"""

	sig_binview_source_selected = QtCore.Signal(object)
	"""The user selected a binview from the binview provider"""

	def __init__(self, *args, binview_provider:providermodel.BSBinViewProviderModel|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self._view_is_modified = False
		"""Is the bin view modified?"""

		self._last_selection:binviewsources.BSAbstractBinViewSource|None = None

		self.setModel(binview_provider or providermodel.BSBinViewProviderModel())

		self.activated.connect(self.userSelectedBinViewSource)

	def setModel(self, model:providermodel.BSBinViewProviderModel):
		
		if self.model() == model:
			return
		
		model.sig_session_sources_changed.connect(self.binViewSessionSourcesChanged)


		super().setModel(model)

	@QtCore.Slot()
	def binViewSessionSourcesChanged(self):
		
		self.setCurrentIndex(0)
		self._last_selection = self.currentData()

		if self.currentData():

			self._view_is_modified = self.currentData().isModified()

	@QtCore.Slot(int)
	def userSelectedBinViewSource(self, selected_index:int):


		selected_binview_source = self.currentData()

		if selected_binview_source == self._last_selection:
			return

		self.sig_binview_source_selected.emit(selected_binview_source)

	def paintEvent(self, e:QtGui.QPaintEvent):

		
		painter = QtWidgets.QStylePainter(self)
		options = QtWidgets.QStyleOptionComboBox()
		
		self.initStyleOption(options)
		
		# NOTE: Do this on change and just set a flag for paint
		if self._view_is_modified:
			
			options.currentText += DEFAULT_MODIFIED_SYMBOL

			font = painter.font()
			font.setItalic(True)
			painter.setFont(font)
		

		painter.drawComplexControl(QtWidgets.QStyle.ComplexControl.CC_ComboBox, options)
		painter.drawControl(QtWidgets.QStyle.ControlElement.CE_ComboBoxLabel, options)
		
		#return super().paintEvent(e)