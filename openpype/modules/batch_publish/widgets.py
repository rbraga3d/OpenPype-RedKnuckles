from openpype.resources import get_image_path
from qtpy import QtWidgets, QtCore, QtGui, QtSvg
loading_image_path = get_image_path("spinner-200.svg")



class TreeViewSpinner(QtWidgets.QTreeView):
    size = 160

    def __init__(self, parent=None):
        super(TreeViewSpinner, self).__init__(parent=parent)

        loading_image_path = get_image_path("spinner-200.svg")

        self.spinner = QtSvg.QSvgRenderer(loading_image_path)

        self.is_loading = False
        self.is_empty = True

    def paint_loading(self, event):
        rect = event.rect()
        rect = QtCore.QRectF(rect.topLeft(), rect.bottomRight())
        rect.moveTo(
            rect.x() + rect.width() / 2 - self.size / 2,
            rect.y() + rect.height() / 2 - self.size / 2
        )
        rect.setSize(QtCore.QSizeF(self.size, self.size))
        painter = QtGui.QPainter(self.viewport())
        self.spinner.render(painter, rect)

    def paint_empty(self, event):
        painter = QtGui.QPainter(self.viewport())
        rect = event.rect()
        rect = QtCore.QRectF(rect.topLeft(), rect.bottomRight())
        qtext_opt = QtGui.QTextOption(
            QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
        )
        painter.drawText(rect, "No Data", qtext_opt)

    def paintEvent(self, event):
        if self.is_loading:
            self.paint_loading(event)
        elif self.is_empty:
            self.paint_empty(event)
        else:
            super(TreeViewSpinner, self).paintEvent(event)


from qtpy import QtCore, QtGui, QtWidgets

class LoadingButton(QtWidgets.QPushButton):
    def start(self):
        if hasattr(self, "_movie"):
            self._movie.start()

    def stop(self):
        if hasattr(self, "_movie"):
            self._movie.stop()
            self.setIcon(QtGui.QIcon())

    def setGif(self, filename):
        if not hasattr(self, "_movie"):
            self._movie = QtGui.QMovie(self)
            self._movie.setFileName(filename)
            self._movie.frameChanged.connect(self.on_frameChanged)
            if self._movie.loopCount() != -1:
                self._movie.finished.connect(self.start)
        self.stop()

    def on_frameChanged(self, frameNumber):
        self.setIcon(QtGui.QIcon(self._movie.currentPixmap()))

if __name__ == '__main__':
    import sys
    import random
    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    lay = QtWidgets.QVBoxLayout(w)
    for i in range(5):
        button = LoadingButton("Install")
        button.setGif("loading.gif")
        QtCore.QTimer.singleShot(random.randint(3000, 6000), button.start)
        QtCore.QTimer.singleShot(random.randint(8000, 12000), button.stop)
        lay.addWidget(button)
    w.show()
    sys.exit(app.exec_())
