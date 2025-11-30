import sys
from PyQt5 import QtWidgets, QtGui, QtCore
import os

# Import VideoThread and HOME_VIDEO_URL from ui/data
try:
    from ui import VideoThread
    from data import HOME_VIDEO_URL
except Exception:
    # try relative import fallback
    from JewelMart.ui import VideoThread
    from JewelMart.data import HOME_VIDEO_URL


class TestWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('VideoThread Test')
        self.resize(960, 600)
        layout = QtWidgets.QVBoxLayout(self)
        self.label = QtWidgets.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.label)

        # start thread
        if HOME_VIDEO_URL and os.path.exists(HOME_VIDEO_URL):
            self.thread = VideoThread(HOME_VIDEO_URL)
            self.thread.frame_ready.connect(self.on_frame)
            self.thread.start()
        else:
            self.label.setText('Video file not found: ' + str(HOME_VIDEO_URL))

    def on_frame(self, qimg: QtGui.QImage):
        if qimg is None or qimg.isNull():
            return
        pix = QtGui.QPixmap.fromImage(qimg)
        if not pix.isNull():
            self.label.setPixmap(pix.scaled(self.label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def closeEvent(self, event):
        try:
            if hasattr(self, 'thread') and self.thread is not None:
                self.thread.stop()
        except Exception:
            pass
        super().closeEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = TestWindow()
    w.show()
    sys.exit(app.exec_())
