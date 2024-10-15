import dataclasses
from PySide6 import QtWidgets, QtCore
from . import model_trt

class TRTMarkerMaker(QtWidgets.QDialog):

	sig_save_preset = QtCore.Signal(model_trt.LBMarkerPreset)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		self.setWindowTitle("Match Marker Criteria")
		self.setLayout(QtWidgets.QVBoxLayout())

		self.cmb_marker_color = QtWidgets.QComboBox()
		self.txt_marker_comment = QtWidgets.QLineEdit()
		self.txt_marker_author  = QtWidgets.QLineEdit()
		self.btn_box = QtWidgets.QDialogButtonBox()

		self._setupWidgets()
		self._setupSignals()
	
	def _setupWidgets(self):

		grp_edit = QtWidgets.QGroupBox("Edit Marker Criteria")
		grp_edit.setLayout(QtWidgets.QGridLayout())

		grp_edit.layout().addWidget(QtWidgets.QLabel("Color"), 0, 0)
		grp_edit.layout().addWidget(self.cmb_marker_color, 1, 0)

		grp_edit.layout().addWidget(QtWidgets.QLabel("Comment"), 0, 1)
		self.txt_marker_comment.setPlaceholderText("(Any)")
		grp_edit.layout().addWidget(self.txt_marker_comment, 1,1)

		grp_edit.layout().addWidget(QtWidgets.QLabel("Author"), 0, 2)
		self.txt_marker_author.setPlaceholderText("(Any)")
		grp_edit.layout().addWidget(self.txt_marker_author, 1, 2)

		self.layout().addWidget(grp_edit)


		self.btn_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
		self.layout().addWidget(self.btn_box)

	def _setupSignals(self):

		self.btn_box.accepted.connect(self.makeMarkerPreset)
		self.btn_box.rejected.connect(self.reject)

		self.cmb_marker_color.currentIndexChanged.connect(lambda x: print(self.cmb_marker_color.currentIndex()))
	
	def addMarker(self, marker:model_trt.LBMarkerIcon):
		self.cmb_marker_color.addItem(marker, marker.name())
		self.cmb_marker_color.update()
	
	@QtCore.Slot()
	def makeMarkerPreset(self) -> model_trt.LBMarkerPreset:
		"""Create a marker preset from the current settings"""
		
		self.sig_save_preset.emit(model_trt.LBMarkerPreset(
			color   = self.cmb_marker_color.currentText(),	# TODO: Use data in preparation for (Any) and such
			comment = self.txt_marker_comment.text() or None,
			author  = self.txt_marker_author.text() or None
		))