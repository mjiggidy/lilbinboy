from PySide6 import QtCore, QtGui

class BSFrameViewActions(QtCore.QObject):
	
	def __init__(self,  parent:QtCore.QObject, *args,**kwargs):

		super().__init__(*args, parent=parent, **kwargs)

		# Navigation

		self.act_zoom_in  = QtGui.QAction("Zoom In")
		self.act_zoom_in.setShortcut(QtGui.QKeySequence.StandardKey.ZoomIn)
		self.act_zoom_in.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ZoomIn))

		self.act_zoom_out  = QtGui.QAction("Zoom Out")
		self.act_zoom_out.setShortcut(QtGui.QKeySequence.StandardKey.ZoomOut)
		self.act_zoom_out.setIcon(QtGui.QIcon.fromTheme(QtGui.QIcon.ThemeIcon.ZoomOut))

		self._actgrp_navigation = QtGui.QActionGroup(self)
		self._actgrp_navigation.setExclusive(False)
		self._actgrp_navigation.addAction(self.act_zoom_in)
		self._actgrp_navigation.addAction(self.act_zoom_out)

		# Overlay Toggles

		self.act_toggle_ruler = QtGui.QAction("Toggle Ruler")
		self.act_toggle_ruler.setCheckable(True)
		self.act_toggle_ruler.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ShiftModifier| QtCore.Qt.Key.Key_R))
		self.act_toggle_ruler.setProperty("icon_paletted", ":/icons/gui/toggle_frame_ruler.svg")

		self.act_toggle_map  = QtGui.QAction("Toggle Bin Map")
		self.act_toggle_map.setCheckable(True)
		self.act_toggle_map.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ShiftModifier|QtCore.Qt.Key.Key_M))
		self.act_toggle_map.setProperty("icon_paletted", ":/icons/gui/toggle_frame_map.svg")

		self.act_toggle_grid = QtGui.QAction("Toggle Background Grid")
		self.act_toggle_grid.setCheckable(True)
		self.act_toggle_grid.setShortcut(QtGui.QKeySequence(QtCore.Qt.KeyboardModifier.ShiftModifier|QtCore.Qt.Key.Key_G))
		self.act_toggle_grid.setProperty("icon_paletted", ":/icons/gui/toggle_frame_grid.svg")

		self._actgrp_overlays = QtGui.QActionGroup(self)
		self._actgrp_overlays.setExclusive(False)
		self._actgrp_overlays.addAction(self.act_toggle_ruler)
		self._actgrp_overlays.addAction(self.act_toggle_map)
		self._actgrp_overlays.addAction(self.act_toggle_grid)
	
	def navigationActions(self) -> QtGui.QActionGroup:

		return self._actgrp_navigation
	
	def overlayActions(self) -> QtGui.QActionGroup:

		return self._actgrp_overlays