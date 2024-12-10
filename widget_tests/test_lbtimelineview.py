import random, math
from PySide6 import QtWidgets, QtCore, QtGui
from timecode import Timecode
from lilbinboy.lbb_common import LBTimelineView

app = QtWidgets.QApplication()
app.setStyle("Fusion")
wnd_main = QtWidgets.QMainWindow()

wdg_main = QtWidgets.QWidget()
wdg_main.setLayout(QtWidgets.QVBoxLayout())

view_timeline = LBTimelineView()
view_timeline.setItems([("Item",random.randint(1,10)) for _ in range(random.randint(1,10))])
view_timeline.setBottomMargin(20)

wdg_main.layout().addWidget(view_timeline)
wdg_main.layout().addWidget(QtWidgets.QPushButton(text="Random", clicked=lambda: view_timeline.setItems([("Item",random.randint(1,10)) for _ in range(random.randint(1,10))])))

spin_adjusted = QtWidgets.QSpinBox()
spin_adjusted.setRange(-500,500)
spin_adjusted.valueChanged.connect(view_timeline.setTotalAdjust)
wdg_main.layout().addWidget(spin_adjusted)

wnd_main.setCentralWidget(wdg_main)
wnd_main.show()
app.exec()