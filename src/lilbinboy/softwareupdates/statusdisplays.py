from PySide6 import QtCore, QtGui, QtWidgets
from . import releaseinfo

class BSUpdateDisplayMessage(QtWidgets.QGroupBox):
	"""Display a simple message"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._lbl_status = QtWidgets.QLabel()

		self.setLayout(QtWidgets.QHBoxLayout())
		self.layout().addWidget(self._lbl_status)

	def setMessage(self, text:str):
		self._lbl_status.setText(text)

	def message(self) -> str:

		return self._lbl_status.text()


class BSUpdateDisplayNewReleaseAvailable(QtWidgets.QGroupBox):
	"""Display info for a new release"""

	def __init__(self, *args, **kwargs):

		super().__init__(*args, *kwargs)

		self.setLayout(QtWidgets.QVBoxLayout())

		self._lbl_new_version_name  = QtWidgets.QLabel()
		self._lbl_new_release_date  = QtWidgets.QLabel()
		self._txt_new_release_notes = QtWidgets.QTextBrowser()

		font = self._lbl_new_version_name.font()
		font.setBold(True)
		self._lbl_new_version_name.setFont(font)

		self._txt_new_release_notes.setReadOnly(True)
		self._txt_new_release_notes.setOpenLinks(False)
		self._txt_new_release_notes.setOpenExternalLinks(False)
		self._txt_new_release_notes.anchorClicked.connect(QtGui.QDesktopServices.openUrl)

		self.layout().addWidget(self._lbl_new_version_name)
		self.layout().addWidget(self._lbl_new_release_date)
		self.layout().addWidget(self._txt_new_release_notes)

	def setReleaseInfo(self, release_info:releaseinfo.ReleaseInfo):

		self._lbl_new_version_name.setText(release_info.name)

		self._lbl_new_release_date.setText(self.tr("Released {date_of_release}").format(
			date_of_release=release_info.date.toLocalTime().toString(
				QtCore.QLocale().dateFormat(QtCore.QLocale.FormatType.LongFormat)
			))
		)

		self._txt_new_release_notes.setMarkdown(release_info.release_notes)