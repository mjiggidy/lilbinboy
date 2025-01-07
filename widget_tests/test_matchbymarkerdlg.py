from PySide6 import QtCore, QtGui, QtWidgets
from lilbinboy.lbb_features.trt.dlg_marker import TRTMarkerMaker # Ha!  Did that from memory
from lilbinboy import Config

app = QtWidgets.QApplication()
app.setStyle("Fusion")

app.setOrganizationName(Config.ORG_NAME)
app.setOrganizationDomain(Config.ORG_DOMAIN)
app.setApplicationName(Config.APP_NAME)
app.setApplicationVersion(Config.APP_VERSION)

model = QtCore.QSettings().value("lbb/marker_presets", dict())

wnd = TRTMarkerMaker()
wnd.setMarkerPresets(model)

wnd.show()

app.exec()