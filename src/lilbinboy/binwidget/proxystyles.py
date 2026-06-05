from PySide6 import QtCore, QtWidgets

class BSScrollBarStyle(QtWidgets.QProxyStyle):
	"""Manage scrollbar height"""

	sig_scale_factor_changed = QtCore.Signal(float)
	"""The scale factor has changed"""

	sig_size_changed         = QtCore.Signal(int)
	"""The size of the scrollbar has changed due to scale"""

	def __init__(self, parent:QtCore.QObject|None, scale_factor:int|float=1.0):

		super().__init__(QtWidgets.QApplication.style().name())
		
		self.setParent(parent)
		self._scale_factor = scale_factor

	def pixelMetric(self, metric:QtWidgets.QStyle.PixelMetric, option:QtWidgets.QStyleOption=None, widget:QtWidgets.QWidget=None):
		"""Scroll bar defaults with modified height metrics"""

		if metric == QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent:
			return self.baseStyle().pixelMetric(metric, option, widget) * self._scale_factor
		
		else:
			return self.baseStyle().pixelMetric(metric, option, widget)
		
	@QtCore.Slot(float)
	def setScrollbarScaleFactor(self, scale_factor:float|int):
		
		if self._scale_factor == scale_factor:
			return
		
		self._scale_factor = scale_factor
		
		self.sig_scale_factor_changed.emit(scale_factor)
		self.sig_size_changed.emit(self.scrollbarSize())

	def scrollbarSize(self, option:QtWidgets.QStyleOption=None, widget:QtWidgets.QWidget=None) -> int:
		"""Current scrollbar size (pixels)"""

		return self.pixelMetric(
			QtWidgets.QStyle.PixelMetric.PM_ScrollBarExtent,
			option=option,
			widget=widget
		)