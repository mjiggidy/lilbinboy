import typing, logging

from PySide6 import QtCore, QtWidgets

from . import scopesmodel
from ..binfilters.siftfilter import sifters, siftmatchtypes, siftscopetypes

import avbutils


class BSSiftCriterionWidget(QtWidgets.QWidget):
	"""A single sift option widget"""

	sig_criterion_set              = QtCore.Signal(object)
	sig_scope_model_changed        = QtCore.Signal(QtCore.QAbstractItemModel)
	sig_scope_changed              = QtCore.Signal(object)
	sig_match_type_changed         = QtCore.Signal(object)
	sig_text_changed               = QtCore.Signal(str)

	DEFAULT_SIFT_CRITERION         = sifters.BSAnyColumnSifter(sift_string="", match_type=siftmatchtypes.BSSiftMatchTypes.Contains)
	CRITERION_CHANGED_TIMEOUT_MSEC = 100

	def __init__(self, *args, sources_model:scopesmodel.BSSiftScopeViewModel, sift_criterion:sifters.BSAbstractSifter|None=None, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QGridLayout())
		self.layout().setContentsMargins(QtCore.QMargins(0,0,0,0))
		self.layout().setSpacing(2)

		self._txt_match_text  = QtWidgets.QLineEdit()
		self._cmb_match_type  = QtWidgets.QComboBox()
		self._cmb_match_scope = QtWidgets.QComboBox(model=sources_model)

		self._last_selected_criteria = None  # Store selection when model is reset

		# NOTE to self: Not sure I really need to throttle signals here, since siftwidget 
		# does that anyway.  It's just... you know... the typing...
		self._criterion_changed_timer = QtCore.QTimer(parent=self, singleShot=True, interval=self.CRITERION_CHANGED_TIMEOUT_MSEC)

		self._setupWidgets()
		self._setupSignals()
		self.setCriterion(sift_criterion)

	def _setupWidgets(self):

		self._cmb_match_scope.setMinimumContentsLength(12)
		self._cmb_match_scope.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)

		# Set up Match Type list items
		self._cmb_match_type.addItem(self.tr("Contains:"),        siftmatchtypes.BSSiftMatchTypes.Contains)
		self._cmb_match_type.addItem(self.tr("Begins With:"),     siftmatchtypes.BSSiftMatchTypes.BeginsWith)
		self._cmb_match_type.addItem(self.tr("Matches Exactly:"), siftmatchtypes.BSSiftMatchTypes.MatchesExactly)

		self.layout().addWidget(self._cmb_match_type,  0, 0)
		self.layout().addWidget(self._txt_match_text,  0, 1)
		self.layout().addWidget(self._cmb_match_scope, 0, 2)

	def _setupSignals(self):

		self._txt_match_text.textChanged     .connect(self.textChosen)
		self._cmb_match_type.activated       .connect(self.matchTypeChosen)
		self._cmb_match_scope.activated      .connect(self.scopeChosen)

		self._criterion_changed_timer.timeout.connect(self.criterionSettled)

		self._cmb_match_scope.model().modelAboutToBeReset.connect(self.sourceModelAboutToBeReset)
		self._cmb_match_scope.model().modelReset.connect(self.sourceModelReset)

	@QtCore.Slot()
	def sourceModelAboutToBeReset(self):

		self._last_selected_criteria = self.criterion()
#		logging.getLogger(__name__).debug("Before model reset, criteria was %s", repr(self._last_selected_criteria))

	@QtCore.Slot()
	def sourceModelReset(self):

		if not self._last_selected_criteria:
			return
		
		new_idx = self.getScopeIndexForSifter(self._last_selected_criteria)

		self._cmb_match_scope.setCurrentIndex(new_idx if new_idx is not None else 0)

		if new_idx is None:
			logging.getLogger(__name__).debug("Losing scope for criteria %s", self._last_selected_criteria)
		
#		logging.getLogger(__name__).debug("After model reset, criteria was idx=%s, data=%s", new_idx, repr(self._cmb_match_scope.currentData()))

	@QtCore.Slot()
	def criterionSettled(self):
		"""Sift criterion has survived the timer, emit it"""

		self.sig_criterion_set.emit(self.criterion())

	def getScopeIndexForSifter(self, criterion:sifters.BSAbstractSifter) -> int:

		scope_model = self._cmb_match_scope.model()

		if isinstance(criterion, sifters.BSSingleColumnSifter):
			return self.indexForSingleColumn(criterion)

		elif isinstance(criterion, sifters.BSAnyColumnSifter):
			return scope_model.rowOffsetToScope(siftscopetypes.BSSiftScopeType.AnyColumn)

		elif isinstance(criterion, sifters.BSNoColumnSifter):
			return scope_model.rowOffsetToScope(siftscopetypes.BSSiftScopeType.NoColumn)

		elif isinstance(criterion, sifters.BSRangeSifter):
			return self.indexForRangeColumn(criterion)

		else:
			raise ValueError(f"Invalid sifter round here: {criterion}")

	@QtCore.Slot(object)
	def setCriterion(self, sift_criterion:sifters.BSAbstractSifter):
		"""Set the sift criterion for this widget"""

		sift_criterion = sift_criterion or self.DEFAULT_SIFT_CRITERION
		
		if self.criterion() == sift_criterion:

			logging.getLogger(__name__).debug("Criterion remains unchanged")
			return
		
		logging.getLogger(__name__).debug("Setting criterion: %s", sift_criterion)

		self._cmb_match_type.setCurrentIndex(self._cmb_match_type.findData(sift_criterion.matchType()))
		self._txt_match_text.setText(sift_criterion.siftString())
		
		scope_index = self.getScopeIndexForSifter(sift_criterion)
		self._cmb_match_scope.setCurrentIndex(scope_index if scope_index is not None else 0)

		self.sig_criterion_set.emit(sift_criterion)

	def criterion(self) -> sifters.BSAbstractSifter:
		"""Build a `BSAbstractSifter` based on current user input"""

		if not self.siftSource():

			logging.getLogger(__name__).error("Weird thing here")

			return sifters.BSNoColumnSifter(
				sift_string= self.text(),
				match_type = self.matchType(),
			)
		
		source_type, source_id = self.siftSource()

#		print("Got here")

		if source_type == siftscopetypes.BSSiftScopeType.SingleColumn:

			return sifters.BSSingleColumnSifter(
				sift_column_info = source_id,
				sift_string      = self.text(),
				match_type       = self.matchType(),
			)
		
		elif source_type == siftscopetypes.BSSiftScopeType.AnyColumn:

			return sifters.BSAnyColumnSifter(
				sift_string = self.text(),
				match_type  = self.matchType(),
			)

		elif source_type == siftscopetypes.BSSiftScopeType.NoColumn:

			return sifters.BSNoColumnSifter(
				sift_string= self.text(),
				match_type = self.matchType(),
			)
		
		elif source_type == siftscopetypes.BSSiftScopeType.Range:

			return sifters.BSRangeSifter(
				sift_string = self.text(),
				data_role   = source_id,
			)
		
		else:
			raise ValueError("Nuh uh")
		
	def indexForSingleColumn(self, criterion:sifters.BSSingleColumnSifter) -> int:

		scope_model:scopesmodel.BSSiftScopeViewModel = self._cmb_match_scope.model()

		columns_available_count  = scope_model.rowCountForScope(siftscopetypes.BSSiftScopeType.SingleColumn)

		if not columns_available_count:
			return None
#			raise ValueError("No column names available")
		
		index_offset = scope_model.rowOffsetToScope(siftscopetypes.BSSiftScopeType.SingleColumn)

		cmb_idx = None
		
		for row in range(index_offset, columns_available_count + index_offset - 1):  # NOTE: -1?

			_, bin_column_info = self._cmb_match_scope.itemData(row)

			if criterion.siftColumnInfo().field_id == bin_column_info.field_id:
			
				# User columns need to be matched by name as well
				if criterion.siftColumnInfo().field_id == avbutils.bins.BinColumnFieldIDs.User \
					and criterion.siftColumnInfo().display_name != bin_column_info.display_name:
						continue

				cmb_idx = row
				break

#		if cmb_idx is None:
#			raise ValueError("Nope")
		
		return cmb_idx
	
	def indexForRangeColumn(self, criterion:sifters.BSRangeSifter) -> int:

		scope_model:scopesmodel.BSSiftScopeViewModel = self._cmb_match_scope.model()
		
		ranges_available  = scope_model.rowCountForScope(siftscopetypes.BSSiftScopeType.Range)

		if not ranges_available:
			return None
#			raise ValueError("No column names available")
		
		ranges_offset = scope_model.rowOffsetToScope(siftscopetypes.BSSiftScopeType.Range)

		cmb_idx = None
		
		for row in range(ranges_offset, ranges_available + ranges_offset):

			_, range_role = self._cmb_match_scope.itemData(row)

			if criterion.dataRole() == range_role:
			
				cmb_idx = row
				break

#		if cmb_idx is None:
#			raise ValueError("Nope")

		return cmb_idx

	@QtCore.Slot(list)
	def setScopeChooserModel(self, scope_chooser_model:scopesmodel.BSSiftScopeViewModel):
		"""Set the scope chooser model"""

		if self._cmb_match_scope.model() == scope_chooser_model:
			return

		self._cmb_match_scope.setModel(scope_chooser_model)

		self.sig_scope_model_changed.emit(scope_chooser_model)

	def scopeChooserModel(self) -> scopesmodel.BSSiftScopeViewModel:
		"""The scope chooser model"""

		return self._cmb_match_scope.model()

	def setMatchType(self, match_type:siftscopetypes.BSSiftScopeType):
		"""Set the string matching strategy to use during the sift"""

		if self._cmb_match_type.currentData() == match_type:
			return
			
		self._cmb_match_type.setCurrentIndex(
			self._cmb_match_type.findData(match_type)
		)

		self.sig_match_type_changed.emit(match_type)

	def matchType(self) -> siftmatchtypes.BSSiftMatchTypes:
		"""The string matching strategy to use during the sift"""

		return self._cmb_match_type.currentData()
	
	@QtCore.Slot(str)
	def setText(self, sift_text:str) -> str:
		"""Set the text for which to sift"""

		if self._txt_match_text.text() == sift_text:
			return

		self._txt_match_text.setText(sift_text)

		self.sig_text_changed.emit(sift_text)
	
	def text(self) -> str:
		"""The text for which to sift"""

		return self._txt_match_text.text()

	def siftSource(self) -> typing.Tuple[siftscopetypes.BSSiftScopeType, typing.Any]:

		return self._cmb_match_scope.currentData()

	def scope(self) -> siftscopetypes.BSSiftScopeType:
		"""Which scope to sift -- such as a particular column, a particular range, etc."""

		return self._cmb_match_scope.currentData()
	
	@QtCore.Slot()
	def textChosen(self):
		"""User typed something"""

		self._criterion_changed_timer.start()

	@QtCore.Slot()
	def scopeChosen(self):
		"""User set the scope"""

		sift_source_type, _ = self._cmb_match_scope.currentData()
		
		if sift_source_type == siftscopetypes.BSSiftScopeType.Range:
			self.setMatchType(siftmatchtypes.BSSiftMatchTypes.Contains)

		self._criterion_changed_timer.start()

	@QtCore.Slot()
	def matchTypeChosen(self):
		"""User set the sift match type"""

		sift_method = self._cmb_match_type.currentData()
		
		if sift_method != siftmatchtypes.BSSiftMatchTypes.Contains:

			sift_source_type, _ = self.siftSource()
			
			if sift_source_type == siftscopetypes.BSSiftScopeType.Range:
				self._cmb_match_scope.setCurrentIndex(
					self._cmb_match_scope.model().rowOffsetToScope(siftscopetypes.BSSiftScopeType.AnyColumn)
				)

		self._criterion_changed_timer.start()