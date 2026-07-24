import sys
from PySide6 import QtCore, QtWidgets
from lilbinboy.appearanceeditor import appearancewidget
from lilbinboy.binwidget import binwidget
from lilbinboy.binview import binviewmodel
from lilbinboy.binitems import binitemsmodel

from lilbinboy.utils import palettes

app = QtWidgets.QApplication()
app.setStyle("Fusion")

wnd_appearance = appearancewidget.BSBinAppearanceSettingsView()

wnd_binwidget = binwidget.BSBinContentsWidget(bin_items_model=binitemsmodel.BSBinItemModel(), bin_view_model=binviewmodel.BSBinViewModel())

wnd_binwidget.show()

wnd_appearance.show()
wnd_appearance.raise_()
wnd_appearance.activateWindow()

wnd_appearance.sig_colors_changed.connect(lambda fg, bg: wnd_binwidget.setBinPalette(palettes.build_palette(fg, bg)))
wnd_appearance.sig_colors_changed.connect(print)
wnd_appearance.sig_was_iconic_changed.connect(print)
wnd_appearance.sig_geometry_changed.connect(print)
wnd_appearance.sig_font_changed.connect(print)

sys.exit(app.exec())