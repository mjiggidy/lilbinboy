from PySide6 import QtWidgets, QtCore
from . import markers_trt

class TRTMarkerMaker(QtWidgets.QDialog):

	sig_save_preset = QtCore.Signal(str, markers_trt.LBMarkerPreset)

	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)
		
		self.setWindowTitle("Match Marker Criteria")
		self.setLayout(QtWidgets.QVBoxLayout())

		self._marker_presets = dict()

		self.cmb_marker_color = QtWidgets.QComboBox()
		self.txt_marker_comment = QtWidgets.QLineEdit()
		self.txt_marker_author  = QtWidgets.QLineEdit()
		self.txt_preset_name = QtWidgets.QLineEdit()
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

		grp_edit.layout().addWidget(QtWidgets.QLabel("Preset Name"), 0, 3)
		self.txt_preset_name.setPlaceholderText("Required")
		grp_edit.layout().addWidget(self.txt_preset_name, 1, 3)

		self.layout().addWidget(grp_edit)


		self.btn_box.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
		self.layout().addWidget(self.btn_box)

	def _setupSignals(self):

		self.btn_box.accepted.connect(self.makeMarkerPreset)
		self.btn_box.accepted.connect(self.accept)
		self.btn_box.rejected.connect(self.reject)

		self.cmb_marker_color.currentIndexChanged.connect(lambda x: print(self.cmb_marker_color.currentIndex()))
	
	def addMarker(self, marker:markers_trt.LBMarkerIcon):
		self.cmb_marker_color.addItem(marker, marker.name())
		self.cmb_marker_color.update()
	
	@QtCore.Slot()
	def makeMarkerPreset(self) -> markers_trt.LBMarkerPreset:
		"""Create a marker preset from the current settings"""

		self.sig_save_preset.emit(self.txt_preset_name.text() or "temp", markers_trt.LBMarkerPreset(
			color   = self.cmb_marker_color.currentText(),	# TODO: Use data in preparation for (Any) and such
			comment = self.txt_marker_comment.text() or None,
			author  = self.txt_marker_author.text() or None
		))
	
	def set_marker_presets(self, marker_presets:dict[str, markers_trt.LBMarkerPreset]):
		self._marker_presets = marker_presets

		self.update_completers()
	
	def update_completers(self):

		completer_comments = QtWidgets.QCompleter(sorted(set([m.comment for m in self._marker_presets.values() if m.comment is not None])))
		completer_comments.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
		completer_comments.setCompletionMode(QtWidgets.QCompleter.CompletionMode.UnfilteredPopupCompletion)

		completer_authors = QtWidgets.QCompleter(sorted(set([m.author for m in self._marker_presets.values() if m.author is not None])))
		completer_authors.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
		completer_authors.setCompletionMode(QtWidgets.QCompleter.CompletionMode.UnfilteredPopupCompletion)

		self.txt_marker_comment.setCompleter(completer_comments)
		self.txt_marker_author.setCompleter(completer_authors)