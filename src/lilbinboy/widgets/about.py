"""
Big ol' mess for now
"""

from PySide6 import QtCore, QtGui, QtWidgets
from ..res import icons_app

class BSAboutWidget(QtWidgets.QWidget):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QHBoxLayout())

		self._lbl_icon = QtWidgets.QLabel(movie=QtGui.QMovie(":/app/dance_64.gif"))
		self._lbl_icon.movie().start()

		self._lbl_title = QtWidgets.QLabel(QtWidgets.QApplication.instance().applicationDisplayName() + "!")
		self._lbl_version = QtWidgets.QLabel(self.tr("Version ") + QtWidgets.QApplication.instance().applicationVersion())
		self._lbl_version.setTextInteractionFlags(QtGui.Qt.TextInteractionFlag.TextSelectableByKeyboard|QtGui.Qt.TextInteractionFlag.TextSelectableByMouse)

		self._lbl_quote  = QtWidgets.QLabel(
			self.tr("\"To take a look into those bins and see all those little items with their little datas in there until we don't care no mores and that's okay thank you!\"")
		)

		self._lbl_author = QtWidgets.QLabel(self.tr("Written by Michael Jordan"))
		self._lbl_thanks = QtWidgets.QLabel(self.tr("Extra special kissies to Joy Fu for her help and feedback"))

		quote_font = self._lbl_quote.font()
		quote_font.setItalic(True)
		self._lbl_quote.setFont(quote_font)
		self._lbl_quote.setWordWrap(True)
		self._lbl_quote.setSizePolicy(QtWidgets.QSizePolicy.Policy.Maximum, self._lbl_quote.sizePolicy().verticalPolicy())

		
		title_font = self._lbl_title.font()
		title_font.setBold(True)
		self._lbl_title.setFont(title_font)

		self._lbl_link_github = QtWidgets.QLabel("<a href=\"https://github.com/mjiggidy/binspector/\">https://github.com/mjiggidy/binspector/</a>")
		self._lbl_link_github.setTextInteractionFlags(QtGui.Qt.TextInteractionFlag.LinksAccessibleByKeyboard|QtGui.Qt.TextInteractionFlag.LinksAccessibleByMouse)
		self._lbl_link_github.setOpenExternalLinks(True)

		self._lbl_link_email  = QtWidgets.QLabel("<a href=\"mailto:michael@glowingpixel.com?subject=" + QtCore.QUrl.toPercentEncoding("You've ruined my life") + "\">michael@glowingpixel.com</a>")
		self._lbl_link_email.setTextInteractionFlags(QtGui.Qt.TextInteractionFlag.LinksAccessibleByKeyboard|QtGui.Qt.TextInteractionFlag.LinksAccessibleByMouse)
		self._lbl_link_email.setOpenExternalLinks(True)

		self._lbl_link_donate = QtWidgets.QLabel("<a href=\"https://ko-fi.com/lilbinboy\">https://ko-fi.com/lilbinboy</a>")
		self._lbl_link_donate.setTextInteractionFlags(QtGui.Qt.TextInteractionFlag.LinksAccessibleByKeyboard|QtGui.Qt.TextInteractionFlag.LinksAccessibleByMouse)
		self._lbl_link_donate.setOpenExternalLinks(True)

		self._lay_links = QtWidgets.QFormLayout()
		self._lay_links.setSpacing(0)
		self._lay_links.addRow(self.tr("Github: "),    self._lbl_link_github)
		self._lay_links.addRow(self.tr("Contact: "),   self._lbl_link_email)
		self._lay_links.addRow(self.tr("Donations: "), self._lbl_link_donate)
		
		self.setupWidgets()
	
	def setupWidgets(self):

		layout_icon = QtWidgets.QVBoxLayout()
		layout_icon.addWidget(self._lbl_icon)
		layout_icon.addStretch()

		self.layout().addLayout(layout_icon)

		layout_text = QtWidgets.QVBoxLayout()


		layout_text.addWidget(self._lbl_title)
		layout_text.addWidget(self._lbl_version)

		layout_text.addWidget(self._lbl_quote)
		layout_text
		layout_text.addWidget(self._lbl_author)
		layout_text.addWidget(self._lbl_thanks)

		layout_text.addLayout(self._lay_links)

		self.layout().addLayout(layout_text)

class BSAboutDialog(QtWidgets.QDialog):

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self.setWindowFlags(QtCore.Qt.WindowType.Tool|QtCore.Qt.WindowType.WindowStaysOnTopHint)
		self.setWindowTitle(self.tr("A Lil' 'Bout The Boy"))

		self._btns = QtWidgets.QDialogButtonBox(standardButtons=QtWidgets.QDialogButtonBox.StandardButton.Ok)
		
		self.layout().addWidget(BSAboutWidget())
		self.layout().addWidget(self._btns)

		self._btns.accepted.connect(self.close)
	
		self.layout().setSizeConstraints(self.layout().SizeConstraint.SetFixedSize, self.layout().SizeConstraint.SetFixedSize)