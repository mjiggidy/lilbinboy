from PySide6 import QtCore, QtGui, QtWidgets
from ..core.settings import BSStartupBehavior

class BSSettingsPanel(QtWidgets.QWidget):

	sig_use_animations_changed   = QtCore.Signal(bool)
	sig_mob_queue_size_changed   = QtCore.Signal(int)
	sig_startup_behavior_changed = QtCore.Signal(object)
	sig_scrollbar_scale_changed  = QtCore.Signal(object)
	sig_item_padding_changed     = QtCore.Signal(object)
	sig_use_column_widths_changed= QtCore.Signal(bool)
	sig_use_live_sift_changed    = QtCore.Signal(bool)
	sig_use_sift_settings_changed= QtCore.Signal(bool)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		self.setLayout(QtWidgets.QFormLayout())

		self._cmb_startup_behavior = QtWidgets.QComboBox()
		self._cmb_startup_behavior.currentIndexChanged.connect(
			lambda: self.sig_startup_behavior_changed.emit(self._cmb_startup_behavior.currentData())
		)
		
		for b in BSStartupBehavior:
			self._cmb_startup_behavior.addItem(b.value, b)

		self._chk_use_animations = QtWidgets.QCheckBox()
		self._chk_use_animations.clicked.connect(self.sig_use_animations_changed)

		self._chk_use_column_widths = QtWidgets.QCheckBox()
		self._chk_use_column_widths.clicked.connect(self.sig_use_column_widths_changed)

		self._chk_use_live_sift     = QtWidgets.QCheckBox()
		self._chk_use_live_sift.clicked.connect(self.sig_use_live_sift_changed)

		self._chk_use_sift_settings = QtWidgets.QCheckBox()
		self._chk_use_sift_settings.clicked.connect(self.sig_use_sift_settings_changed)

		self._spn_padding_width  = QtWidgets.QSpinBox()
		self._spn_padding_width.valueChanged.connect(self.calculateNewPadding)
		self._spn_padding_height = QtWidgets.QSpinBox()
		self._spn_padding_height.valueChanged.connect(self.calculateNewPadding)

		self._sld_scrollbar_scale = QtWidgets.QSlider()
		self._sld_scrollbar_scale.valueChanged.connect(lambda val: self.sig_scrollbar_scale_changed.emit(val/100))
		self._sld_scrollbar_scale.valueChanged.connect(lambda val: self._sld_scrollbar_scale.setToolTip(str(round(val/100,2))))
		self._sld_scrollbar_scale.setRange(100,200)
		self._sld_scrollbar_scale.setOrientation(QtCore.Qt.Orientation.Horizontal)
		self._sld_scrollbar_scale.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
		self._sld_scrollbar_scale.setTickInterval(10)
		
		self._sld_mob_queue      = QtWidgets.QSlider()
		self._sld_mob_queue.valueChanged.connect(self.sig_mob_queue_size_changed)
		self._sld_mob_queue.valueChanged.connect(lambda val: self._sld_mob_queue.setToolTip(str(val)))

		self._sld_mob_queue.setRange(1, 2_000)
		self._sld_mob_queue.setOrientation(QtCore.Qt.Orientation.Horizontal)
		self._sld_mob_queue.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
		self._sld_mob_queue.setTickInterval(500)

		self.layout().addRow(self.tr("On Startup"), self._cmb_startup_behavior)
		self.layout().addRow(self.tr("Use Saved Column Widths"), self._chk_use_column_widths)
		self.layout().addRow(self.tr("Use Live Sift"), self._chk_use_live_sift) # NOTE: Also gets saved via Sift Settings window...?
		self.layout().addRow(self.tr("Use Sift Settings From Bin"), self._chk_use_sift_settings)
		self.layout().addRow(self.tr("List Item (W)"), self._spn_padding_width)
		self.layout().addRow(self.tr("List Item (H)"), self._spn_padding_height)
		self.layout().addRow(self.tr("Use Fancy Animations"), self._chk_use_animations)
		self.layout().addRow(self.tr("Bottom Scrollbar Scale"), self._sld_scrollbar_scale)
		self.layout().addRow(self.tr("Mob Queue Size"), self._sld_mob_queue)

	@QtCore.Slot(int)
	def calculateNewPadding(self, _:int):
		
		w = self._spn_padding_width.value()
		h = self._spn_padding_height.value()
		
		margs = QtCore.QMargins(w,h,w,h)
		
		self.sig_item_padding_changed.emit(margs)
	
	@QtCore.Slot(object)
	def setListItemPadding(self, padding:QtCore.QMargins):

		self._spn_padding_width .setValue(padding.left())
		self._spn_padding_height.setValue(padding.top())
	
	@QtCore.Slot(bool)
	def setUseAnimations(self, use_animations:bool):

		self._chk_use_animations.setChecked(use_animations)

	@QtCore.Slot(bool)
	def setUseSavedColumnWidths(self, use_column_widths:bool):

		self._chk_use_column_widths.setChecked(use_column_widths)

	@QtCore.Slot(float)
	def setBottomScrollBarScale(self, scale_factor:float):

		self._sld_scrollbar_scale.setValue(round(scale_factor * 100))
	
	@QtCore.Slot(int)
	def setMobQueueSize(self, queue_size:int):

		self._sld_mob_queue.setValue(queue_size)
	
	@QtCore.Slot(object)
	def setStartupBehavior(self, behavior:BSStartupBehavior):

		self._cmb_startup_behavior.setCurrentText(behavior.value)

	@QtCore.Slot(bool)
	def setLiveSiftEnabled(self, is_enabled:bool):

		self._chk_use_live_sift.setChecked(is_enabled)

	@QtCore.Slot(bool)
	def setUseSiftSettingsFromBin(self, is_enabled:bool):

		self._chk_use_sift_settings.setChecked(is_enabled)