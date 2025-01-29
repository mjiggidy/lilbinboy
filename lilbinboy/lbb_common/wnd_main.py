from PySide6 import QtCore, QtWidgets
from lilbinboy.lbb_common.dlg_errorlog import LBErrorLogWindow
from lilbinboy.lbb_common.wnd_checkforupdates import LBCheckForUpdatesWindow

class LBMainWindow(QtWidgets.QMainWindow):
	"""Lil' Main Window Boy"""

	sig_resized = QtCore.Signal(QtCore.QRect)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.tabs = QtWidgets.QTabWidget()

		self.setCentralWidget(QtWidgets.QWidget())
		self.centralWidget().setLayout(QtWidgets.QVBoxLayout())
		self.centralWidget().layout().setContentsMargins(3,3,3,3)
		self.centralWidget().layout().addWidget(self.tabs)

		lay_id = QtWidgets.QHBoxLayout()

		self.lbl_lbb = QtWidgets.QLabel(f"<strong>Lil' Bin Boy</strong><br/>Pre Alpha Nightmare v{QtWidgets.QApplication.instance().applicationVersion()}<br/>Report good and bad things to <a href=\"mailto:michael@glowingpixel.com\">michael@glowingpixel.com</a>")
		self.lbl_lbb.setOpenExternalLinks(True)
		font = self.lbl_lbb.font()
		font.setPointSizeF(font.pointSize() * 0.8)
		self.lbl_lbb.setFont(font)
		self.lbl_lbb.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight|QtCore.Qt.AlignmentFlag.AlignVCenter)

		self.lbl_lbbicon = QtWidgets.QLabel()
		self.lbl_lbbicon.setPixmap(QtWidgets.QApplication.instance().windowIcon().pixmap(32))

		self.btn_errorlog = QtWidgets.QPushButton("Show Error Log")
		self.btn_errorlog.clicked.connect(self.errorLogRequested)

		lay_id.addWidget(self.lbl_lbbicon)
		lay_id.addWidget(self.btn_errorlog)
		lay_id.addStretch()
		lay_id.addWidget(self.lbl_lbb)
		self.centralWidget().layout().addLayout(lay_id)
	
	@QtCore.Slot()
	def errorLogRequested(self):
		wnd_errors = LBErrorLogWindow(self)
		
		wnd_errors.show()

	def moveEvent(self, event):
		super().moveEvent(event)
		self.sig_resized.emit(self.geometry())


	def resizeEvent(self, event):
		super().resizeEvent(event)
		self.sig_resized.emit(self.geometry())
	
	@QtCore.Slot()
	def checkForUpdates(self):
		self.wnd_check = LBCheckForUpdatesWindow()
		
		self.wnd_check.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)
		
		self.wnd_check.show()
		self.wnd_check.checkForUpdates()
		