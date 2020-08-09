import ctypes
import json
import os
import queue
import sys
import threading
import urllib.request
from collections import OrderedDict
from ftplib import FTP
from io import BytesIO

import cv2
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# load both ui file
uifile_1 = 'Start.ui'  # start
form_1, base_1 = uic.loadUiType(uifile_1)

uifile_2 = 'loginui.ui'  # login
form_2, base_2 = uic.loadUiType(uifile_2)

uifile_3 = 'Sign.ui'  # sign up
form_3, base_3 = uic.loadUiType(uifile_3)

uifile_4 = 'simple.ui'  # main
form_4, base_4 = uic.loadUiType(uifile_4)


class Start(base_1, form_1):
    def __init__(self):
        super(base_1, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('MYFIT START')
        self.login.clicked.connect(self.change)
        self.SignUp.clicked.connect(self.change_2)
        self.Exit_button()

    def Exit_button(self):
        exit = QAction('Exit', self)
        exit.setShortcut('Ctrl+Q')  # 단축키 설정
        exit.triggered.connect(qApp.quit)  # quit() 메서드와 연결
        self.statusBar()
        menu = self.menuBar()  # 메뉴바 생성
        menu.setNativeMenuBar(False)
        menubutton = menu.addMenu('&File')
        menubutton.addAction(exit)  # 동작 추가
        self.show()

    def change(self):
        self.main = loginPage()
        self.main.show()
        self.close()

    def change_2(self):
        self.main = SignPage()
        self.main.show()
        self.close()


class loginPage(base_2, form_2):
    userid = ''
    username = ''

    def __init__(self):
        super(base_2, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('MYFIT LOGIN')
        self.btnBack.clicked.connect(self.change)
        self.btnLogin.clicked.connect(self.login)
        self.Exit_button()

    def Exit_button(self):
        exit = QAction('Exit', self)
        exit.setShortcut('Ctrl+Q')  # 단축키 설정
        exit.triggered.connect(qApp.quit)
        self.statusBar()
        menu = self.menuBar()
        menu.setNativeMenuBar(False)
        menubutton = menu.addMenu('&File')
        menubutton.addAction(exit)
        self.show()

    def change(self):  # 시작화면으로 돌아가기
        self.window = Start()
        self.window.show()
        self.close()

    def change_2(self):  # 메인 페이지로 화면 전환
        self.window = MainPage()
        self.window.show()
        self.close()

    def login(self):  # 로그인
        loginOk = False  # 로그인 성공 여부
        userid = self.inputId.text()
        userpw = self.inputPw.text()
        if userid != '' and userpw != '':
            serverData = readServerData("users")  # 서버 데이터 읽어옴
            for i in serverData:
                if serverData[i]['id'] == userid:  # check id
                    if serverData[i]['pw'] == userpw:  # check pw
                        loginPage.userid = userid
                        loginPage.username = serverData[i]['name']
                        loginOk = True
                        break

        if loginOk:  # 로그인 성공
            self.change_2()  # 메인 페이지로 이동
        else:  # 로그인 실패
            messageBox("로그인 실패", "ID 또는 PW가 틀렸습니다.", 0)


class SignPage(base_3, form_3):
    def __init__(self):
        super(base_3, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('MYFIT SIGNUP')
        self.btnBack.clicked.connect(self.change)
        self.btnSignup.clicked.connect(self.signUp)
        self.Exit_button()

    def Exit_button(self):
        exit = QAction('Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.triggered.connect(qApp.quit)
        self.statusBar()
        menu = self.menuBar()
        menu.setNativeMenuBar(False)
        menubutton = menu.addMenu('&File')
        menubutton.addAction(exit)
        self.show()

    def change(self):
        self.window = Start()
        self.window.show()
        self.close()

    def signUp(self):  # signup 회원가입
        userid = self.inputId.text()
        userpw = self.inputPw.text()
        username = self.inputName.text()

        if userid == '' or userpw == '' or username == '':
            messageBox("경고", "ID, PASSWORD와 이름은 필수 항목입니다.", 0)
        else:
            file_data = readServerData("users")
            count = 0
            for i in file_data:  # id 중복 검사
                if file_data[i]['id'] == userid:  # check id
                    count = 1
                    messageBox("경고", "ID 중복", 0)
            if count == 0:
                userNum = 'user' + str(len(file_data))
                file_data.setdefault('t', {})  # key 값에 변수로는 왜 바로 안되는지 모르겠네
                file_data['t']['id'] = userid
                file_data['t']['pw'] = userpw
                file_data['t']['name'] = username
                file_data['t']['age'] = self.spinBox.value()
                file_data['t']['balance'] = 0  # default
                file_data['t']['challenge'] = False  # default
                file_data[userNum] = file_data.pop('t')  # user 번호 설정

                upload(file_data, "users")  # 서버에 새로운 회원 정보 업로드
                i = messageBox("가입완료", "회원가입이 완료되었습니다.", 0)
                if i == 1:
                    self.change()


# upload data file to server _ 서버에 업로드
def upload(file_data, fileName):
    os.system("wget http://soyeong99.dothome.co.kr/web/" + fileName + ".json")
    ftp = FTP('112.175.184.79', 'soyeong99', 'thdud4869!')
    ftp.cwd("/html/web/")
    tempF = json.dumps(file_data, indent="\t")
    tempF = bytes(tempF, "utf8")
    file_like = BytesIO(tempF)
    ftp.storbinary('STOR users.json', file_like)


# server Data를 읽어옴
def readServerData(fileName):
    file_data = OrderedDict()
    data = urllib.request.urlopen("http://soyeong99.dothome.co.kr/web/" + fileName + ".json").read()
    file_data = json.loads(data)
    return file_data


# Main Page - Camera
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
    userid = ''
    username = ''

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle('MYFIT USER\'S PAGE')

        # login한 user의 이름 표시
        MainPage.userid = loginPage.userid  # loginData['id']
        MainPage.username = loginPage.username  # loginData['name']
        self.loginName.setText(MainPage.username)

        self.btnCamera.clicked.connect(self.startCamera)
        self.btnChallenge.clicked.connect(self.challenge)
        self.btnTurn.clicked.connect(self.myTurn)
        self.btnNext.clicked.connect(self.chooseNext)
        self.btnLogout.clicked.connect(self.logout)
        self.groupBox_ch.hide()

        self.window_width = self.ImgWidget.frameSize().width()
        self.window_height = self.ImgWidget.frameSize().height()
        self.ImgWidget = OwnImageWidget(self.ImgWidget)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

        self.Exit_button()
        # TODO: 아래는 게임 버튼 눌렀을 때 적용
        self.checkFirst()

    def Exit_button(self):
        exit = QAction('Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.triggered.connect(qApp.quit)
        self.statusBar()
        menu = self.menuBar()
        menu.setNativeMenuBar(False)
        menubutton = menu.addMenu('&File')
        menubutton.addAction(exit)
        self.show()

    def checkFirst(self):
        fileData = readServerData("users")
        for i in fileData:  # id 중복 검사
            if fileData[i]['id'] == loginPage.userid:
                if fileData[i]['balance'] == 0:
                    i = messageBox("자세 측정 필요", "최초 자세 측정 데이터가 필요합니다.", 0)
                    break

    # TODO: challengeBoard.json, users.json 연동 방법
    def challenge(self):
        self.groupBox.setTitle("            'S CHALLENGE BOARD")
        self.groupBox_ch.show()
        self.ImgWidget.hide()
        self.btnCamera.setEnabled(False)

        challengeData = readServerData('challengeBoard')

        model = QStandardItemModel()
        for c in challengeData:
            model.appendRow(QStandardItem(challengeData[c]['id']))
        self.listView.setModel(model)

    # TODO: MAIN 버튼 클릭

    # TODO: 내 차례 challenge 수행
    def myTurn(self):
        return 0

    # TODO: 다음 차례 challenge 수행할 user 선택
    def chooseNext(self):
        return 0

    def logout(self):
        # self.window = Start()
        # self.window.show()
        self.close()

    def startCamera(self):
        global running
        running = True
        capture_thread.start()
        self.btnCamera.setEnabled(False)
        self.btnCamera.setText('Loading...')
    # TODO: Camera OFF

    def update_frame(self):
        if not q.empty():
            self.btnCamera.setText('ON')
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


# 메시지박스(알림창) 함수
def messageBox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(None, text, title, style)
    # style 인자에 따라 생김새 지정 가능
    # 0: 확인(1)
    # 1: 확인(1), 취소(2)
    # 2: 중단(3), 다시시도(4), 무시(5)
    # 3: 예(6), 아니오(7), 취소(2)
    # 4: 예(6), 아니오(7)
    # 5: 다시시도(4), 취소(2)
    # 6: 취소(2), 다시시도(10), 계속(11)


# 로그인 정보 저장 파일 삭제 함수
def removeLogfile(file):
    if os.path.isfile(file):
        os.remove(file)


if __name__ == '__main__':
    capture_thread = threading.Thread(target=grab, args=(0, q, 1920, 1080, 30))
    app = QApplication(sys.argv)
    ex = Start()
    ex.show()
    sys.exit(app.exec_())
