"""
Menus used by things that use menus
"""

from PySide6 import QtWidgets
from ..managers import actions

class BinWindowMenuBar(QtWidgets.QMenuBar):
	"""Menu shown for an active bin window"""

	def __init__(self, action_manager:actions.ActionsManager, *args, **kwargs):
		
		super().__init__(*args, **kwargs)

		mnu_main   = QtWidgets.QMenu(self.tr("&File"))
		mnu_view   = QtWidgets.QMenu(self.tr("&View"))
		mnu_tools  = QtWidgets.QMenu(self.tr("&Tools"))
		mnu_window = QtWidgets.QMenu(self.tr("&Window"))
		mnu_help   = QtWidgets.QMenu(self.tr("&Help"))
		

		mnu_main.addAction(action_manager.newWindowAction())
		mnu_main.addAction(action_manager.fileBrowserAction())
		mnu_main.addSeparator()
		mnu_main.addAction(action_manager.quitApplicationAction())

		mnu_view.addActions(action_manager.viewModesActionGroup().actions())
		mnu_view.addSeparator()
		mnu_view.addActions(action_manager.showBinSettingsActionGroup().actions())
		mnu_view.addSeparator()

		mnu_tools.addActions(action_manager.userToolsActionsGroup().actions())
		mnu_tools.addAction(action_manager.showSettingsWindow())

		mnu_window.addAction(action_manager.closeWindowAction())

		mnu_help.addAction(action_manager.checkForUpdates())
		mnu_help.addAction(action_manager.visitDiscussionBoard())
		mnu_help.addAction(action_manager.visitDonations())
		mnu_help.addSeparator()
		mnu_help.addAction(action_manager.showAboutBoxAction())

		self.addMenu(mnu_main)
		self.addMenu(mnu_view)
		self.addMenu(mnu_tools)
		self.addMenu(mnu_window)
		self.addMenu(mnu_help)

class DefaultMenuBar(QtWidgets.QMenuBar):
	"""Default, minimal menu bar, specifically for macOS when no bin windows are open"""

	def __init__(self, action_manager:actions.ActionsManager, *args, **kwargs):

		super().__init__(*args, **kwargs)

		mnu_main = QtWidgets.QMenu(self.tr("&File"))
		mnu_main.addAction(action_manager.newWindowAction())
		mnu_main.addAction(action_manager.fileBrowserAction())
		mnu_main.addSeparator()
		mnu_main.addAction(action_manager.quitApplicationAction())

		self.addMenu(mnu_main)

		mnu_tools = QtWidgets.QMenu(self.tr("&Tools"))
		mnu_tools.addActions(action_manager.userToolsActionsGroup().actions())
		mnu_tools.addAction(action_manager.showSettingsWindow())

		self.addMenu(mnu_tools)

		mnu_help   = QtWidgets.QMenu(self.tr("&Help"))
		mnu_help.addAction(action_manager.checkForUpdates())
		mnu_help.addAction(action_manager.visitDiscussionBoard())
		mnu_help.addAction(action_manager.visitDonations())
		mnu_help.addSeparator()
		mnu_help.addAction(action_manager.showAboutBoxAction())
		
		self.addMenu(mnu_help)