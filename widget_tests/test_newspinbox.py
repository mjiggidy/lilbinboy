import random
from PySide6 import QtWidgets, QtCore
from timecode import Timecode
from lilbinboy.lbb_common import LBSpinBoxTC




	

@QtCore.Slot(Timecode)
def updateTimecodeInfo(info_label:QtWidgets.QLabel, timecode:Timecode):
	info_label.setText(f"{timecode} @ {timecode.rate} fps")


app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd = QtWidgets.QGroupBox()
wnd.setLayout(QtWidgets.QVBoxLayout())

tc_spinbox = LBSpinBoxTC()
wnd.layout().addWidget(tc_spinbox)

btn_random = QtWidgets.QPushButton("Random Timecode")
btn_random.clicked.connect(lambda: tc_spinbox.setFrameNumber(random.randint(tc_spinbox.minimum(), tc_spinbox.maximum())))
wnd.layout().addWidget(btn_random)

btn_24 = QtWidgets.QPushButton(text="24")
btn_24.clicked.connect(lambda: tc_spinbox.setRate(24))

btn_30 = QtWidgets.QPushButton(text="30")
btn_30.clicked.connect(lambda: tc_spinbox.setRate(30))

lay_bnts = QtWidgets.QHBoxLayout()
lay_bnts.addWidget(btn_24)
lay_bnts.addWidget(btn_30)

wnd.layout().addLayout(lay_bnts)

chk_positive = QtWidgets.QCheckBox(text="Allow Positive")
chk_positive.setChecked(tc_spinbox.allowPositive())
chk_positive.toggled.connect(tc_spinbox.setAllowPositive)

chk_negative = QtWidgets.QCheckBox(text="Allow Negative")
chk_negative.setChecked(tc_spinbox.allowNegative())
chk_negative.toggled.connect(tc_spinbox.setAllowNegative)

chk_resample = QtWidgets.QCheckBox(text="Resample On Rate Change")
chk_resample.setChecked(tc_spinbox.resampleOnRateChange())
chk_resample.toggled.connect(tc_spinbox.setResampleOnRateChange)

wnd.layout().addWidget(chk_positive)
wnd.layout().addWidget(chk_negative)
wnd.layout().addWidget(chk_resample)

lbl_latest = QtWidgets.QLabel()
lbl_latest.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter|QtCore.Qt.AlignmentFlag.AlignVCenter)
lbl_latest.setFrameShape(QtWidgets.QFrame.Shape.Box)
lbl_latest.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
tc_spinbox.sig_timecode_changed.connect(lambda tc: updateTimecodeInfo(lbl_latest, tc))
wnd.layout().addWidget(lbl_latest)

wnd.show()

app.exec()