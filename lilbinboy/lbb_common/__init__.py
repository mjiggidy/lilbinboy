import re
from PySide6 import QtWidgets, QtCore, QtGui
from timecode import Timecode
from lilbinboy.lbb_common import resources, wnd_about, wnd_main, dlg_errorlog, wnd_checkforupdates, windowmanager
from lilbinboy.lbb_common.wdg_clipcolorpicker import LBClipColorPicker
from lilbinboy.lbb_common.wdg_timelineview import LBTimelineView
from lilbinboy.lbb_common.wdg_timecodespinbox import LBSpinBoxTC
from lilbinboy.lbb_common.wdg_utilitytab import LBUtilityTab

from lilbinboy.lbb_common.helper_funcs import *