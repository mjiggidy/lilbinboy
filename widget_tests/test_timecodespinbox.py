from PySide6 import QtWidgets
from lilbinboy.lbb_common import LBSpinBoxTC

app = QtWidgets.QApplication()

wnd = QtWidgets.QGroupBox()
wnd.setLayout(QtWidgets.QVBoxLayout())

tc_spinbox = LBSpinBoxTC()

btn_24 = QtWidgets.QPushButton(text="24")
btn_24.clicked.connect(lambda: tc_spinbox.setRate(24))

btn_30 = QtWidgets.QPushButton(text="30")
btn_30.clicked.connect(lambda: tc_spinbox.setRate(30))

wnd.layout().addWidget(tc_spinbox)

lay_bnts = QtWidgets.QHBoxLayout()
lay_bnts.addWidget(btn_24)
lay_bnts.addWidget(btn_30)

wnd.layout().addLayout(lay_bnts)

chk_negative = QtWidgets.QCheckBox(text="Allow Negative")
chk_negative.toggled.connect(tc_spinbox.setAllowNegative)

wnd.layout().addWidget(chk_negative)

wnd.show()

app.exec()