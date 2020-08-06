import sys
from PyQt5.QtWidgets import QApplication, QWidget, QAction, qApp
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5 import QtCore, QtGui, uic, QtWidgets
import sys
import cv2
import numpy as np
import threading
import time
import queue
#load both ui file
uifile_1 = 'Start.ui'
form_1, base_1 = uic.loadUiType(uifile_1)

uifile_2 = 'loginui.ui'
form_2, base_2 = uic.loadUiType(uifile_2)

uifile_3 = 'Sign.ui'
form_3, base_3 = uic.loadUiType(uifile_3)

uifile_4 = 'simple.ui'
form_4, base_4 = uic.loadUiType(uifile_4)

class Start(base_1, form_1):
       def __init__(self):
           super(base_1,self).__init__()
           self.setupUi(self)
           self.login.clicked.connect(self.change)
           self.SignUp.clicked.connect(self.change_2)

       def change(self):
           self.main = loginPage()
           self.main.show()
           self.close()
       def change_2(self):
           self.main=SignPage()
           self.main.show()
           self.close()

class loginPage(base_2, form_2):
       def __init__(self):
           super(base_2, self).__init__()
           self.setupUi(self)
           self.Back.clicked.connect(self.change)
           self.OK.clicked.connect(self.change_2)
       def change(self):
           self.window=Start()
           self.window.show()
           self.close()
       def change_2(self):
           self.window=MainPage()
           self.window.show()
           self.close()


class SignPage(base_3, form_3):
    def __init__(self):
        super(base_3, self).__init__()
        self.setupUi(self)
        self.Back.clicked.connect(self.change)

    def change(self):
        self.window = Start()
        self.window.show()
        self.close()

running = False
capture_thread = None
q = queue.Queue()


def grab(cam, queue, width, height, fps):
    global running
    capture = cv2.VideoCapture(cam)
    # capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    # capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    # capture.set(cv2.CAP_PROP_FPS, fps)

    while (running):
        frame = {}
        capture.grab()
        retval, img = capture.retrieve(0)
        # 카메라 캡쳐 이미지 위에 도형 그리기
        cv2.circle(img, (40, 60), 15, (255, 0, 0), 10)

        frame["img"] = img

        if queue.qsize() < 10:
            queue.put(frame)
        else:
            print
            queue.qsize()


class OwnImageWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(OwnImageWidget, self).__init__(parent)
        self.image = None

    def setImage(self, image):
        self.image = image
        sz = image.size()
        self.setMinimumSize(sz)
        self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        if self.image:
            qp.drawImage(QtCore.QPoint(0, 0), self.image)
        qp.end()


class MainPage(QtWidgets.QMainWindow, form_4):
    def __init__(self, parent=None):

        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.btnCamera.clicked.connect(self.start_clicked)
        self.btnlog.clicked.connect(self.log_out)

        self.window_width = self.ImgWidget.frameSize().width()
        self.window_height = self.ImgWidget.frameSize().height()
        self.ImgWidget = OwnImageWidget(self.ImgWidget)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)


    def log_out(self):
        self.window = Start()
        self.window.show()
        self.close()

    def start_clicked(self):
        global running
        running = True
        capture_thread.start()
        self.btnCamera.setEnabled(False)
        self.btnCamera.setText('Loading...')

    def update_frame(self):
        if not q.empty():
            self.btnCamera.setText('Camera is running')
            frame = q.get()
            img = frame["img"]

            img_height, img_width, img_colors = img.shape
            scale_w = float(self.window_width) / float(img_width)
            scale_h = float(self.window_height) / float(img_height)
            scale = min([scale_w, scale_h])

            if scale == 0:
                scale = 1

            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width, bpc = img.shape
            bpl = bpc * width
            image = QtGui.QImage(img.data, width, height, bpl, QtGui.QImage.Format_RGB888)
            self.ImgWidget.setImage(image)

    def closeEvent(self, event):
        global running
        running = False


if __name__ == '__main__':
       capture_thread = threading.Thread(target=grab, args=(0, q, 1920, 1080, 30))
       app = QApplication(sys.argv)
       ex = Start()
       ex.show()
       sys.exit(app.exec_())