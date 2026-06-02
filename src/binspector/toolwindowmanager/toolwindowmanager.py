import enum, typing, weakref

from PySide6 import QtWidgets, QtCore

class BSToolWindowTypes(enum.IntEnum):

	SiftToolWindow   = enum.auto()
	BinViewEditor    = enum.auto()
	BinDisplayEditor = enum.auto()

class BSToolWindowManager(QtCore.QObject):

	# NOTE: I need this for tool windows now,but obviously this works as a good generic
	# manager of ephemeral things

	def __init__(self, *args, parent:QtCore.QObject, **kwargs):
		
		super().__init__(*args, parent=parent, **kwargs)

		self._tool_windows:dict[enum.Enum, weakref.ReferenceType[QtWidgets.QWidget]] = {}

	def toolWindow(self, tool_window_type:enum.Enum) -> QtWidgets.QWidget|None:
		"""Get the requested tool window for a given tool window type, or `None`"""

		tool_ref = self._tool_windows.get(tool_window_type, None)

		if not tool_ref:
			return None
		
		tool_window = tool_ref()

		if not tool_window:
			del self._tool_windows[tool_window_type]
		
		return tool_window

	def toolWindows(self) -> typing.Iterable[QtWidgets.QWidget]:
		"""Get all valid tool windows"""

		for tool_type in self._tool_windows:

			tool_window = self.toolWindow(tool_type)

			if tool_window is None:
				continue

			yield tool_type, self.toolWindow(tool_window)

	def registerToolWindow(self, tool_window_type:enum.Enum, tool_window:QtWidgets.QWidget):

		self._tool_windows[tool_window_type] = weakref.ref(tool_window)