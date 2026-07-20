import enum, typing, weakref, logging

from PySide6 import QtWidgets, QtCore

class BSToolWindowTypes(enum.IntEnum):

	SiftSettingsEditor  = enum.auto()
	BinViewEditor       = enum.auto()
	BinDisplayEditor    = enum.auto()
	BinAppearanceEditor = enum.auto()

class BSToolWindowManager(QtCore.QObject):

	# NOTE: I need this for tool windows now,but obviously this works as a good generic
	# manager of ephemeral things

	def __init__(self, *args, parent:QtCore.QObject, **kwargs):
		
		super().__init__(*args, parent=parent, **kwargs)

		logging.getLogger(__name__).debug("Hello from myself")

		self._tool_windows:dict[enum.Enum, QtWidgets.QWidget] = dict()

	def toolWindow(self, tool_window_type:enum.Enum) -> QtWidgets.QWidget|None:
		"""Get the requested tool window for a given tool window type, or `None`"""

		tool_window = self._tool_windows.get(tool_window_type)

		if not tool_window:

			logging.getLogger(__name__).debug("Requested tool window %s is not registered", tool_window_type)
		
		return tool_window

	def toolWindows(self) -> typing.Iterable[tuple[enum.Enum, QtWidgets.QWidget]]:
		"""Get all valid tool windows"""

		for tool_window_type, tool_window in self._tool_windows.items():

			logging.getLogger(__name__).debug("Yielding tool window %s", tool_window_type)

			yield tool_window_type, tool_window

	def registerToolWindow(self, tool_window_type:enum.Enum, tool_window:QtWidgets.QWidget):

		logging.getLogger(__name__).debug("Registering tool window for %s", tool_window_type)

		tool_window.setAttribute(QtCore.Qt.WidgetAttribute.WA_DeleteOnClose, True)
		
		from functools import partial
		tool_window.destroyed.connect(partial(self.unregisterToolWindow, tool_window_type))

		self._tool_windows[tool_window_type] = tool_window

	def unregisterToolWindow(self, tool_window_type:BSToolWindowTypes):

		if not tool_window_type in self._tool_windows:

			logging.getLogger(__name__).debug("Attempted to unregister un-registered tool window %s", tool_window_type)
			return
		
		logging.getLogger(__name__).debug("Un-registering tool window type %s", tool_window_type)
		
		del self._tool_windows[tool_window_type]