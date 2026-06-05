import sys
import avb, avbutils

from PySide6 import QtCore, QtWidgets, QtTest

from lilbinboy.binview import binviewmodel, binviewitemtypes
from lilbinboy.binvieweditor import editorproxymodel, editorview, editorwidget

if not len(sys.argv) > 1:

	import pathlib
	sys.exit(f"Usage: {pathlib.Path(__file__).name} file.avb")

app = QtWidgets.QApplication()
app.setStyle("Fusion")

with avb.open(sys.argv[1]) as handle_bin:
	bin_view = binviewitemtypes.BSBinViewInfo.from_binview(handle_bin.content.view_setting)

model_binview = binviewmodel.BSBinViewModel(bin_view=bin_view)

wnd_editor = editorwidget.BSBinViewColumnEditor(bin_view_model=model_binview)
#wnd_editor.setBinViewModel(model_binview)
wnd_editor.show()

tester = QtTest.QAbstractItemModelTester(wnd_editor._cmb_bin_view_list.model(), QtTest.QAbstractItemModelTester.FailureReportingMode.Fatal)

#wnd_view.move(wnd_binviews.pos() + QtCore.QPoint(wnd_binviews.width() + 24, 0))

sys.exit(app.exec())