import sys
from PySide6 import QtCore, QtGui, QtWidgets
from lilbinboy.frameview import frameview, sceneitems, painters
from lilbinboy.overlays import manager
from lilbinboy.overlays import frameruler, framemap

class CoolFrameOverlayView(QtWidgets.QMainWindow):
	
	def __init__(self, *args, **kwargs):

		super().__init__(*args, **kwargs)

		self._frameview = frameview.BSBinFrameView()
		self._frameview.setInteractive(True)
		
		self._frameview.scene().setSceneRect(QtCore.QRectF(
			QtCore.QPointF(-100, -100),
			QtCore.QSizeF(1000, 500)
		))

		self._frameview._overlay_map.setThumbnailSize(
			QtCore.QSizeF(300,400)
		)
		
		self._frameview.setZoom(4)
		self._frameview.setZoomRange(range(4,16))
		self._frameview._overlay_map._setEnabled(True)

		#self._frameview._background_painter.setActiveGridUnit(QtCore.QPointF(5,5))

		self.b = painters.BSFrameItemBrushManager(self._frameview.viewport())
		self.b.setPalette(QtWidgets.QApplication.palette())

		# Add some fellas
		for idx in range(10):
			i = sceneitems.BSFrameModeItem(brush_manager=self.b)
			i.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
			i.setFlag(QtWidgets.QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
			i.setName("Clip " + str(i))
			i.setPos(
				QtCore.QPointF(idx*17,0)
			)
			self._frameview.scene().addItem(i)

		self._frameview._overlay_map.sig_view_reticle_panned.connect(self.setCenterPoint)

		self.setCentralWidget(self._frameview)

		
		
	@QtCore.Slot(object)
	def setCenterPoint(self, center_point:QtCore.QPointF):

		print(center_point)

		self._frameview.centerOn(center_point)


if __name__ == "__main__":

	app = QtWidgets.QApplication()
	app.setStyle("Fusion")

	wnd = CoolFrameOverlayView()
	wnd.show()
	#wnd.updateRulerTicks()

	sys.exit(app.exec())