"""
Bin settings views, typically used as toolboxes or sidebars
"""

from PySide6 import QtCore, QtGui, QtWidgets
from ..views import enumview
from ..core import icon_providers, icon_engines, icon_registry
import avbutils

class BSBinDisplaySettingsView(enumview.LBAbstractEnumFlagsView):
	"""Flags for setting Bin Item Display filter"""

	def __init__(self, bin_items_flags:avbutils.BinDisplayItemTypes|None=None, *args, icon_registry:icon_registry.IconRegistryType|None=None, **kwargs):
		
		super().__init__(bin_items_flags if bin_items_flags is not None else avbutils.BinDisplayItemTypes(0), *args, **kwargs)

		self._registry = icon_registry or dict()
		
		self.setLayout(QtWidgets.QVBoxLayout())
		#self.layout().setSpacing(0)
		#self.layout().setContentsMargins(3,0,3,0)

		self.layout().setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)

		grp_clips = QtWidgets.QGroupBox(title=self.tr("Clip Types"))

		grp_clips.setLayout(QtWidgets.QVBoxLayout())
		grp_clips.layout().setSpacing(0)
		grp_clips.layout().setContentsMargins(3,0,3,0)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.MASTER_CLIP]
		chk.setText(self.tr("Master Clips"))
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.LINKED_MASTER_CLIP]
		chk.setText(self.tr("Linked Master Clips"))
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.SUBCLIP]
		chk.setText(self.tr("Subclips"))
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.SEQUENCE]
		chk.setText(self.tr("Sequences"))
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.SOURCE]
		chk.setText(self.tr("Sources"))
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.EFFECT]
		chk.setText(self.tr("Effects"))
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.MOTION_EFFECT]
		chk.setText(self.tr("Motion Effects"))
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.PRECOMP_RENDERED_EFFECT]
		chk.setText(self.tr("Precompute Clips - Rendered Effects"))
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.PRECOMP_TITLE_MATTEKEY]
		chk.setText(self.tr("Precompute Clips - Titles and Matte Keys"))
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.GROUP]
		chk.setText(self.tr("Groups"))
		grp_clips.layout().addWidget(chk)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.STEREOSCOPIC_CLIP]
		chk.setText(self.tr("Stereoscopic Clips"))
		grp_clips.layout().addWidget(chk)

		self.layout().addWidget(grp_clips)

		grp_origins = QtWidgets.QGroupBox(title=self.tr("Clip Origins"))
		grp_origins.setLayout(QtWidgets.QVBoxLayout())
		grp_origins.layout().setSpacing(0)
		grp_origins.layout().setContentsMargins(3,0,3,0)

		chk = self._option_mappings[avbutils.BinDisplayItemTypes.USER_CLIP]
		chk.setText(self.tr("Show clips created by user"))
		grp_origins.layout().addWidget(chk)
		
		chk = self._option_mappings[avbutils.BinDisplayItemTypes.REFERENCE_CLIP]
		chk.setText(self.tr("Show reference clips"))
		grp_origins.layout().addWidget(chk)
		

		self.layout().addWidget(grp_origins)

		self.setupIcons()

		self.layout().addStretch()
	
	def setIconRegistry(self, registry:icon_registry.IconRegistryType):

		if self._registry == registry:
			return
		
		self._registry = registry
		self.setupIcons()
	
	def setupIcons(self):

		for item_flag, chk in self._option_mappings.items():

			item_icon_path = self._registry.get(item_flag, None)

			chk.setIcon(
				QtGui.QIcon(
					icon_engines.BSPalettedSvgIconEngine(item_icon_path)
					  if   item_icon_path
					  else None
				)
			)

			chk.setIconSize(QtCore.QSize(chk.iconSize().width(), chk.iconSize().height() * 3/4))