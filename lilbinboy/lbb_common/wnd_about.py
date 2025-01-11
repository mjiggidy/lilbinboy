from PySide6 import QtCore, QtGui, QtWidgets

class LBAboutWindow(QtWidgets.QDialog):

	PATH_ABOUT_TEXT = "/Users/mjordan/dev/lilbinboy/about.html"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.setWindowTitle("About")
		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)

		# Such a good dancer!
		layout_logo = QtWidgets.QVBoxLayout()

		self._boy_icon = QtWidgets.QLabel()
		self._boy_icon.setMovie(QtGui.QMovie(":/app/dance_64.gif"))
		self._boy_icon.movie().start()

		layout_logo.addWidget(self._boy_icon)
		layout_logo.addStretch()
		self.layout().addLayout(layout_logo)

		# Main Info

		layout_info = QtWidgets.QVBoxLayout()

		# Title Label
		self._about_title = QtWidgets.QLabel("Lil' Bin Boy!")
		font = self._about_title.font()
		font.setPointSizeF(font.pointSizeF()*2)
		font.setBold(True)
		self._about_title.setFont(font)

		# Version Label
		self._about_version = QtWidgets.QLabel("Version " + QtWidgets.QApplication.instance().applicationVersion())
		#font = self._about_version.font()
		#font.setItalic(True)
		#self._about_version.setFont(font)
		self._about_version.setTextInteractionFlags(QtGui.Qt.TextInteractionFlag.TextSelectableByKeyboard|QtGui.Qt.TextInteractionFlag.TextSelectableByMouse)

		# Slogan Label
		self._about_slogan = QtWidgets.QLabel("\"Go into those Avid bins and do real good things to all that is inside for me and also you -- yes ok!\"")
		font = self._about_slogan.font()
		font.setItalic(True)
		self._about_slogan.setWordWrap(True)
		self._about_slogan.setFont(font)

		# Credit
		self._about_me = QtWidgets.QLabel("Written by Michael Jordan")
		self._about_me.setToolTip("no not that one")

		self._special_kissies = QtWidgets.QLabel("Extra special kissies to Joy Fu for her help and feedback")

		layout_info.addWidget(self._about_title)
		layout_info.addWidget(self._about_version)
		layout_info.addSpacing(10)
		layout_info.addWidget(self._about_slogan)
		layout_info.addSpacing(10)
		layout_info.addWidget(self._about_me)
		layout_info.addWidget(self._special_kissies)
		layout_info.addSpacing(10)

		# Lankz
		layout_links = QtWidgets.QGridLayout()
		
		layout_links.addWidget(QtWidgets.QLabel("Github:"), 0, 0)
		lbl_github = QtWidgets.QLabel("<a href=\"https://github.com/mjiggidy/lilbinboy/\">https://github.com/mjiggidy/lilbinboy/</a>")
		lbl_github.setTextInteractionFlags(QtGui.Qt.TextInteractionFlag.LinksAccessibleByKeyboard|QtGui.Qt.TextInteractionFlag.LinksAccessibleByMouse)
		lbl_github.setOpenExternalLinks(True)
		layout_links.addWidget(lbl_github, 0, 1)
		
		layout_links.addWidget(QtWidgets.QLabel("Contact:"), 1, 0)
		lbl_contact = QtWidgets.QLabel("<a href=\"mailto:michael@glowingpixel.com?subject=Lil'%20Bin%20Boy%20Ruined%20My%20Life\">michael@glowingpixel.com</a>")
		lbl_contact.setTextInteractionFlags(QtGui.Qt.TextInteractionFlag.LinksAccessibleByKeyboard|QtGui.Qt.TextInteractionFlag.LinksAccessibleByMouse)
		lbl_contact.setOpenExternalLinks(True)
		layout_links.addWidget(lbl_contact, 1, 1)

		layout_links.addWidget(QtWidgets.QLabel("Donations:"), 2, 0)
		lbl_kofi = QtWidgets.QLabel("<a href=\"https://ko-fi.com/lilbinboy\">https://ko-fi.com/lilbinboy</a>")
		lbl_kofi.setToolTip("Oh boy!!  Thank you!!")
		lbl_kofi.setTextInteractionFlags(QtGui.Qt.TextInteractionFlag.LinksAccessibleByKeyboard|QtGui.Qt.TextInteractionFlag.LinksAccessibleByMouse)
		lbl_kofi.setOpenExternalLinks(True)
		layout_links.addWidget(lbl_kofi, 2, 1)
		
		layout_info.addLayout(layout_links)
		layout_info.addSpacing(10)

		layout_info.addStretch()

		self._btnbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok)
		self._btnbox.accepted.connect(self.accept)
		layout_info.addWidget(self._btnbox)

		self.layout().addLayout(layout_info)
