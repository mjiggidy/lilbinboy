from PySide6 import QtCore, QtGui, QtWidgets
from ..utils import stylewatcher
from ..core import icon_engines

class BSActionPushButton(QtWidgets.QPushButton):
	"""A QPushButton bound to a QAction"""

	def __init__(self, action:QtGui.QAction|None=None, show_text:bool=True, show_icon:bool=True, show_tooltip:bool=True, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._action = None
		
		self._show_text    = show_text
		self._show_icon    = show_icon
		self._show_tooltip = show_tooltip

		if action:
			self.setAction(action)
	
	def setAction(self, action:QtGui.QAction):
		"""Set the action this button will be bound to"""

		# Disconnect previous action
		if self._action:

			#self._action.enabledChanged.disconnect(self.setEnabled)
			#self._action.visibleChanged.disconnect(self.setVisible)
			#self._action.checkableChanged.disconnect(self.setCheckable)
			#self._action.toggled.disconnect(self.setChecked)
#
			#self.clicked.disconnect(self._action.trigger)

			# NOTE: Can I just do this instead?
			self._action.disconnect(self)
			self.disconnect(self._action)

		
		# Set new action
		self._action = action

		# Sync current state with new action
		self.setEnabled(self._action.isEnabled())
		self.setVisible(self._action.isVisible())
		self.setCheckable(self._action.isCheckable())
		self.setChecked(self._action.isChecked())
		self.setIcon(self._action.icon() if self._show_icon else QtGui.QIcon())
		self.setToolTip(self._action.toolTip() if self._show_tooltip else None)
		self.setText(self._action.text() if self._show_text else None)

		# Sync future state changes
		self._action.enabledChanged.connect(self.setEnabled)
		self._action.visibleChanged.connect(lambda: self.setVisible(self._action.isVisible()))
		self._action.checkableChanged.connect(self.setCheckable)
		self._action.toggled.connect(self.setChecked)

		self.clicked.connect(self._action.trigger)

class BSPalettedActionPushButton(BSActionPushButton):
	"""Perhaps a terrible idea"""

	def __init__(self,
			action:QtGui.QAction|None=None,
			show_text:bool=True,
			#show_icon:bool=True,
			show_tooltip:bool=True,
			*args,
			icon_engine:icon_engines.BSAbstractPalettedIconEngine|None=None,
			**kwargs
		):

		# Using show_icon=False so Action doesn't set it? I feel this is all hacky
		# This whole paletted icon engine thing is ugh
		# Thanks for reading my blog post
		super().__init__(action, show_text, show_icon=False, show_tooltip=show_tooltip)

		self._icon_engine   = icon_engines.BSAbstractPalettedIconEngine(parent=self)
		self._style_watcher = stylewatcher.BSWidgetStyleEventFilter(parent=self)

		self.installEventFilter(self._style_watcher)

		if icon_engine:
			self.setIconEngine(icon_engine)
	
	@QtCore.Slot(object)
	def setIcon(self, icon:QtGui.QIcon):
		"""Should not be used directly. Set things through IconEngine"""

		return super().setIcon(icon)

	def setIconEngine(self, icon_engine:icon_engines.BSAbstractPalettedIconEngine):

		if self._icon_engine == icon_engine:
			return
		
		#self._style_watcher.disconnect(self._icon_engine)
		
		self._icon_engine = icon_engine
		self._icon_engine.setPalette(self.palette())

		self._style_watcher.sig_palette_changed.connect(lambda pal: self._icon_engine.setPalette(pal))

		self.setIcon(
			QtGui.QIcon(self._icon_engine)
		)

class BSPushButtonActionBar(QtWidgets.QWidget):
	"""Unified button bar for a given button group"""

	def __init__(self, button_group:QtWidgets.QButtonGroup, orientation:QtCore.Qt.Orientation=QtCore.Qt.Orientation.Horizontal, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(
			QtWidgets.QHBoxLayout() if orientation==QtCore.Qt.Orientation.Horizontal else QtWidgets.QVBoxLayout()
		)
		
		self.layout().setContentsMargins(0,0,0,0)
		self.layout().setSpacing(0)

		for button in button_group.buttons():
			self.layout().addWidget(button)

