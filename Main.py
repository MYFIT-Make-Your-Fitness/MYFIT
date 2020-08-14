import ctypes
import json
import os
import queue
import random
import sys
import threading
import time
import urllib.request
from collections import OrderedDict
from ftplib import FTP
from io import BytesIO

import cv2
import numpy as np
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pyqtgraph import PlotWidget, plot  # 그래프 그리기 위해서

# load both ui file
uifile_1 = 'Start.ui'  # start
form_1, base_1 = uic.loadUiType(uifile_1)

uifile_2 = 'loginui.ui'  # login
form_2, base_2 = uic.loadUiType(uifile_2)

uifile_3 = 'Sign.ui'  # sign up
form_3, base_3 = uic.loadUiType(uifile_3)

uifile_4 = 'simple.ui'  # main
form_4, base_4 = uic.loadUiType(uifile_4)

uifile_5 = 'turn2.ui'  # next
form_5, base_5 = uic.loadUiType(uifile_5)

uifile_6 = 'new.ui'  # new
form_6, base_6 = uic.loadUiType(uifile_6)


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
        userid = self.inputId.text()  # local value
        userpw = self.inputPw.text()
        if userid != '' and userpw != '':
            users = readServerData("users")  # 서버 데이터 읽어옴
            for i in users:
                if users[i]['id'] == userid:  # check id
                    if users[i]['pw'] == userpw:  # check pw
                        loginPage.userid = userid
                        loginPage.username = users[i]['name']
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
            users = readServerData("users")

            count = 0
            for i in users:  # id 중복 검사
                if users[i]['id'] == userid:  # check id
                    count = 1
                    messageBox("경고", "ID 중복", 0)
            if count == 0:
                userNum = str(len(users))
                users.setdefault(userNum, {})  # key 값에 변수로는 왜 바로 안되는지 모르겠네
                users[userNum]['id'] = userid
                users[userNum]['pw'] = userpw
                users[userNum]['name'] = username
                users[userNum]['age'] = self.spinBox.value()
                users[userNum]['balance'] = []  # default
                users[userNum]['challengeNum'] = -1  # default
                users[userNum]['challengeF'] = False  # default
                upload(users, "users")  # 서버에 새로운 회원 정보 업로드
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
    str = "STOR " + fileName + ".json"
    ftp.storbinary(str, file_like)


# server Data를 읽어옴
def readServerData(fileName):
    file_data = OrderedDict()
    data = urllib.request.urlopen("http://soyeong99.dothome.co.kr/web/" + fileName + ".json").read()
    file_data = json.loads(data)
    return file_data


# Main Page - Camera
running = False
# capture_thread = None
q = queue.Queue()

MODE = "COCO"
if MODE is "COCO":
    protoFile = "pose/coco/pose_deploy_linevec.prototxt"
    weightsFile = "pose/coco/pose_iter_440000.caffemodel"
    nPoints = 18
    POSE_PAIRS = [[1, 0], [1, 2], [1, 5], [2, 3], [3, 4], [5, 6], [6, 7], [1, 8], [8, 9], [9, 10], [1, 11], [11, 12],
                  [12, 13], [0, 14], [0, 15], [14, 16], [15, 17]]
# elif MODE is "MPI":
#     protoFile = "pose/mpi/pose_deploy_linevec_faster_4_stages.prototxt"
#     weightsFile = "pose/mpi/pose_iter_160000.caffemodel"
#     nPoints = 15
#     POSE_PAIRS = [[0, 1], [1, 2], [2, 3], [3, 4], [1, 5], [5, 6], [6, 7], [1, 14], [14, 8], [8, 9], [9, 10], [14, 11],
#                   [11, 12], [12, 13]]
# vid_writer = cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 10,
# (frame.shape[1], frame.shape[0]))
net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)


# 스레드 돌아가는 함수
def grab(cam, queue, width, height, fps):
    shoulderResult = []  # 어깨 측정 list
    global running
    capture = cv2.VideoCapture(cam)
    inWidth = 368
    inHeight = 368
    threshold = 0.1

    while (running):
        frame = {}
        capture.grab()  # 재귀X: VideoCapture 내장 함수
        retval, img = capture.retrieve(0)  # grab한 프레임을 decode하여 반환

        imgCopy = np.copy(img)
        if not retval:
            cv2.waitKey()
            break

        imgWidth = img.shape[1]
        imgHeight = img.shape[0]

        inpBlob = cv2.dnn.blobFromImage(img, 1.0 / 255, (inWidth, inHeight),
                                        (0, 0, 0), swapRB=False, crop=False)
        net.setInput(inpBlob)
        output = net.forward()

        H = output.shape[2]
        W = output.shape[3]

        # Empty list to store the detected keypoints
        points = []

        for i in range(nPoints):
            # confidence map of corresponding body's part.
            probMap = output[0, i, :, :]

            # Find global maxima of the probMap.
            minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

            # Scale the point to fit on the original image
            x = (imgWidth * point[0]) / W
            y = (imgHeight * point[1]) / H

            if prob > threshold:
                cv2.circle(imgCopy, (int(x), int(y)), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
                cv2.putText(imgCopy, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                            lineType=cv2.LINE_AA)

                # Add the point to the list if the probability is greater than the threshold
                points.append((int(x), int(y)))
            else:
                points.append(None)

        temp_a = 0  # Right shoulder
        temp_b = 0  # left shoulder
        temp = 0
        temp2 = 0

        # Draw Skeleton
        for pair in POSE_PAIRS:
            partA = pair[0]
            partB = pair[1]

            if points[partA] and points[partB]:
                if (partA == 1 and partB == 2) or (
                        partA == 1 and partB == 5):  # Neck-Right Shoulder, Neck-left Shoulder일 경우
                    cv2.line(img, points[partA], points[partB], (255, 0, 0), 3, lineType=cv2.LINE_AA)  # 다른 색으로 표시
                    cv2.circle(img, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
                    cv2.circle(img, points[partB], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
                    if partB == 2:  # Right Shoulder인 경우 좌표 저장
                        temp_a = points[partB]
                    if partB == 5 and temp_a != 0:  # left Shoulder인 경우 좌표 저장
                        temp_b = points[partB]
                        temp = temp_a[0] - temp_b[0]  # 기울기 구하기 위하여 x증가량
                        temp2 = temp_a[1] - temp_b[1]  # 기울기 구하기 위하여 y증가량
                        shoulderResult.append(abs(temp2) / abs(temp))  # 절대값을 이용하여 기울기를 구한 후 list에 저장

                else:
                    cv2.line(img, points[partA], points[partB], (0, 255, 255), 3, lineType=cv2.LINE_AA)
                    cv2.circle(img, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
                    cv2.circle(img, points[partB], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
        # vid_writer.write(frame)

        frame["img"] = img
        if queue.qsize() < 10:
            queue.put(frame)
        else:
            print(queue.qsize())

    # server에 balance 저장
    if len(shoulderResult) != 0:
        result = round((sum(shoulderResult) / len(shoulderResult)), 2)  # 어깨 기울임 측정의 평균
        users = readServerData('users')
        for u in users:
            if users[u]['id'] == MainPage.userid:
                users[u]['balance'].append(result)
                break
        upload(users, 'users')
        messageBox("ok", "Balance 업로드 완료", 0)


# vid_writer.release()

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


class newChDialog(base_6, form_6):
    def __init__(self):
        super(base_6, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('CREATE NEW')
        self.btnCreate.clicked.connect(self.create)
        self.btnCancel.clicked.connect(self.cancel)

    def create(self):
        chBoard = readServerData('challengeBoard')
        chNum = str(len(chBoard))

        users = readServerData('users')
        i = -1
        for u in users:
            if users[u]['id'] == MainPage.userid and users[u]['challengeNum'] == -1:
                users[u]['challengeNum'] = chNum
                chBoard.setdefault(chNum, {})
                chBoard[chNum]['challengers'] = [MainPage.userid]
                upload(chBoard, "challengeBoard")  # 서버에 업로드
                upload(users, "users")  # 유저 정보에 업로드
                i = messageBox("챌린지 생성", "새로운 챌린지가 생성되었습니다.", 0)
                if i == 1:
                    self.close()
        messageBox("챌린지 생성 실패", "이미 참여 중인 챌린지가 있습니다.", 0)

    def cancel(self):
        self.close()


class MainPage(QtWidgets.QMainWindow, form_4):
    userid = ''
    username = ''
    userage = ''
    capture_thread = None
    chNum = -1
    chturnclose = False

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setWindowTitle('MYFIT USER\'S PAGE')

        # login한 user의 이름 표시
        MainPage.userid = loginPage.userid
        MainPage.username = loginPage.username
        self.loginName.setText(MainPage.username)

        self.btnCamera.clicked.connect(self.camera)
        self.btnCamera_2.clicked.connect(self.camera_2)
        self.btnMain.clicked.connect(self.mainBalance)
        self.btnGame.clicked.connect(self.game)
        self.btnChallenge.clicked.connect(self.challenge)
        self.btnTurn.clicked.connect(self.myTurn)
        self.btnNext.clicked.connect(self.chooseNext)
        self.btnNew.clicked.connect(self.newCh)
        self.btnUser.clicked.connect(self.userData)
        self.btnLogout.clicked.connect(self.logout)
        self.btnOk.clicked.connect(self.ok)
        self.groupBox_ch.hide()
        self.groupBox_us.hide()
        self.btnCamera_2.hide()
        self.groupBox_G.hide()
        self.lblChMode.hide()

        self.window_width = self.ImgWidget.frameSize().width()
        self.window_height = self.ImgWidget.frameSize().height()
        self.ImgWidget = OwnImageWidget(self.ImgWidget)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1)

        self.Exit_button()
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

    def mainBalance(self):
        self.groupBox.setTitle("            'S CAMERA")
        self.groupBox_ch.hide()  # challenge 가리기
        self.lblChMode.hide()
        self.groupBox_us.hide()  # user 가리기
        self.ImgWidget.show()
        self.btnCamera.show()
        self.btnCamera_2.hide() # game 가리기

    def game(self):
        self.groupBox.setTitle("            'S GAME")
        self.groupBox_ch.hide()  # challenge
        self.lblChMode.hide()
        self.groupBox_us.hide()  # user
        self.btnCamera.hide()  # main
        self.ImgWidget.show()  # game
        self.btnCamera_2.show()
        self.btnCamera_2.setEnabled(True)

    def challenge(self):
        self.groupBox.setTitle("            'S CHALLENGE BOARD")
        self.groupBox_ch.show()
        self.groupBox_us.hide()  # user 가리기
        self.cameraOff()
        self.ImgWidget.hide()  # main 가리기
        self.btnCamera.hide()
        self.btnCamera_2.hide()  # game 가리기
        self.lblChMode.hide()
        self.groupBox_G.hide()
        self.btnTurn.setEnabled(True)

        self.loadChallengeBoard()

    def loadChallengeBoard(self):
        userData = readServerData('users')
        for u in userData:
            if MainPage.userid == userData[u]['id']:
                challengeNum = userData[u]['challengeNum']
        if challengeNum != -1:
            challengeData = readServerData('challengeBoard')
            model = QStandardItemModel()
            for c in challengeData:
                if str(challengeNum) == c:
                    challengers = challengeData[c]['challengers']
                    for chUserid in challengers:
                        model.appendRow(QStandardItem(chUserid))
                    break
            if chUserid != MainPage.userid:  # challengeBoard.json에서 해당 챌린지의 마지막 주자 확인
                self.btnTurn.setEnabled(False)
            self.listView.setModel(model)
        self.challengeNum()

    challengeNow = False

    # TODO: 내 차례 challenge 수행
    def myTurn(self):
        users = readServerData('users')
        for u in users:
            if users[u]['id'] == MainPage.userid:
                chBool = users[u]['challengeF']
                break
        if MainPage.chNum != -1:  # 진행 중 챌린지 있음
            if chBool is True:
                messageBox("챌린지 진행 완료", "이미 현재 챌린지 게임을 수행했습니다. 다음 챌린저를 선택하세요.", 0)
            else:
                self.btnTurn.setEnabled(True)
                MainPage.challengeNow = True  # 참여 중 표시
                MainPage.capture_thread = threading.Thread(target=self.grabGame, args=(0, q, 1920, 1080, 30))
                self.lblChMode.show()  # game화면에는 challenge 중임을 표시
                self.ImgWidget.show()
                self.btnCamera_2.show()
                self.groupBox_ch.hide()
                self.btnTurn.setEnabled(False)
        else:  # 진행 중 챌린지 없음
            messageBox("챌린지 없음", "현재 참여 중인 챌린지가 없습니다.", 0)

    def challengeNum(self):  # 참여 중인 챌린지 번호 확인
        userdata = readServerData("users")
        for u in userdata:
            if MainPage.userid == userdata[u]['id']:
                MainPage.chNum = userdata[u]['challengeNum']
                break

    def chooseNext(self):
        self.challengeNum()
        if MainPage.chNum == -1:
            messageBox("챌린지 없음", "현재 참여 중인 챌린지가 없습니다.", 0)
        else:
            users = readServerData('users')
            for u in users:
                if users[u]['id'] == MainPage.userid:
                    if users[u]['challengeF']:
                        self.dialog = nextDialog()
                        self.dialog.show()
                    else:
                        messageBox("챌린지 오류", "진행하지 않은 챌린지가 있습니다.", 0)
                    break

    def newCh(self):
        self.dialog = newChDialog()
        self.dialog.show()

    def userData(self):  # USER 화면
        self.groupBox.setTitle("            'S DATA")
        self.groupBox_ch.hide()  # challenge 가리기
        self.lblChMode.hide()
        self.groupBox_us.show()
        self.cameraOff()
        self.ImgWidget.hide()  # main 가리기
        self.btnCamera.hide()
        self.groupBox_G.hide()  # game 가리기
        self.btnCamera_2.hide()
        self.btnId_input.setText(MainPage.userid)
        self.btnName_input.setText(MainPage.username)
        userData = readServerData('users')
        for u in userData:  # age 가져오기
            if MainPage.userid == userData[u]['id']:
                MainPage.userage = userData[u]['age']
                break
        self.btnAge_input.setText(str(MainPage.userage))
        graph = []
        for u in userData:  # 저장된 balance data 가져오기
            if MainPage.userid == userData[u]['id']:
                graph = userData[u]['balance']
        self.Graph.plot(graph)  # widget을 class:PlotWidget, header: pyqtgraph로 하여 승격 후 graph그리기

    def logout(self):
        self.close()

    def camera(self):  # main일때
        global running
        if running:  # Camera OFF하기
            self.cameraOff()
        else:  # Camera ON하기
            MainPage.capture_thread = threading.Thread(target=grab, args=(0, q, 1920, 1080, 30))
            running = True
            MainPage.capture_thread.start()
        self.btnCamera.setEnabled(False)
        self.btnCamera.setText('Loading...')

    def camera_2(self):
        global running
        if running:
            self.cameraOff()
        else:
            MainPage.capture_thread = threading.Thread(target=self.grabGame, args=(0, q, 1920, 1080, 30))
            running = True
            MainPage.capture_thread.start()
        self.btnCamera_2.setEnabled(False)
        self.btnCamera_2.setText('Loading...')

    def cameraOff(self):
        global running
        running = False
        MainPage.capture_thread = None

    def update_frame(self):
        if not q.empty():
            self.btnCamera.setEnabled(True)
            if running:
                self.btnCamera.setText('ON')
                self.btnCamera_2.setText('ON')
            else:
                self.btnCamera.setText('CAMERA')
                self.btnCamera_2.setText('START')
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

    def grabGame(self, cam, queue, width, height, fps):
        self.challengeMode.setChecked(False)
        apples = []  # 사과 좌표 생성
        for i in range(5):
            apples.append(random.randrange(20, 480))
        before = len(apples)
        now = len(apples)

        global running
        capture = cv2.VideoCapture(cam)
        inWidth = 368
        inHeight = 368
        threshold = 0.1

        gameScore = 0
        img = None
        apple = random.choice(apples)
        startTime = time.localtime()
        startTime = startTime.tm_hour * 60 * 60 + startTime.tm_min * 60 + startTime.tm_sec
        while running and len(apples) > 0:
            frame = {}
            capture.grab()  # 재귀X: VideoCapture 내장 함수
            retval, img = capture.retrieve(0)  # grab한 프레임을 decode하여 반환

            imgCopy = np.copy(img)
            if not retval:
                cv2.waitKey()
                break

            imgWidth = img.shape[1]
            imgHeight = img.shape[0]

            inpBlob = cv2.dnn.blobFromImage(img, 1.0 / 255, (inWidth, inHeight), (0, 0, 0), swapRB=False, crop=False)
            net.setInput(inpBlob)
            output = net.forward()

            H = output.shape[2]
            W = output.shape[3]

            # Empty list to store the detected keypoints
            points = []

            for i in range(nPoints):
                # confidence map of corresponding body's part.
                probMap = output[0, i, :, :]

                # Find global maxima of the probMap.
                minVal, prob, minLoc, point = cv2.minMaxLoc(probMap)

                # Scale the point to fit on the original image
                x = (imgWidth * point[0]) / W
                y = (imgHeight * point[1]) / H

                if prob > threshold:
                    cv2.circle(imgCopy, (int(x), int(y)), 8, (0, 255, 255), thickness=-1, lineType=cv2.FILLED)
                    cv2.putText(imgCopy, "{}".format(i), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2,
                                lineType=cv2.LINE_AA)

                    # Add the point to the list if the probability is greater than the threshold
                    points.append((int(x), int(y)))
                else:
                    points.append(None)

            handA = None  # Right
            handB = None  # left
            # Draw Skeleton
            for pair in POSE_PAIRS:
                partA = pair[0]
                partB = pair[1]
                if points[partA] and points[partB]:
                    if partA == 3 and partB == 4:  # 오른쪽 손목
                        cv2.line(img, points[partA], points[partB], (0, 255, 255), 3, lineType=cv2.LINE_AA)
                        if partB == 4:
                            cv2.circle(img, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
                            cv2.circle(img, points[partB], 8, (255, 0, 0), thickness=-1, lineType=cv2.FILLED)
                            handA = points[partB]
                            print(str(handA))  # 오른족 손목 좌표 저장
                    if partA == 6 or partB == 7:  # 왼쪽 손목
                        cv2.line(img, points[partA], points[partB], (0, 255, 255), 3, lineType=cv2.LINE_AA)
                        if partB == 7:
                            cv2.circle(img, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
                            cv2.circle(img, points[partB], 8, (255, 0, 0), thickness=-1, lineType=cv2.FILLED)
                            handB = points[partB]  # 좌표 저장
                            print(str(handB))
                    else:
                        cv2.line(img, points[partA], points[partB], (0, 255, 255), 3, lineType=cv2.LINE_AA)
                        cv2.circle(img, points[partA], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)
                        cv2.circle(img, points[partB], 8, (0, 0, 255), thickness=-1, lineType=cv2.FILLED)

            # 사과 게임 테스트
            if before - 1 == now:  # 한 개 줄면, 새로운 위치 생성
                apple = random.choice(apples)
                before = now
            cv2.circle(img, (apple, 100), 14, (0, 0, 255), -1)
            # handA: 오른쪽(실제 나의 몸 오른쪽) handB:왼쪽(실제 나의 몸 왼쪽) =카메라는 반대로 나옴옴
            if handA is not None:
                if (apple - 30 <= handA[0] <= apple + 30) and (75 <= handA[1] <= 125):
                    apples.remove(apple)
                    gameScore += 1
            if handB is not None:
                if (apple - 30 <= handB[0] <= apple + 30) and (75 <= handB[1] <= 125):
                    apples.remove(apple)
                    gameScore += 1
            now = len(apples)

            frame["img"] = img
            if queue.qsize() < 10:
                queue.put(frame)
            else:
                print(queue.qsize())

            now = time.localtime()
            now = now.tm_hour * 60 * 60 + now.tm_min * 60 + now.tm_sec
            if abs(now - startTime) >= 5:  # TODO: 60초로 바꾸기
                self.lblEnd.setText("TIME OUT")
                break

        # challengeMode라면 challengeMode를 체크
        self.groupBox_G.show()
        self.lblId.setText(MainPage.userid)
        self.lblScore.setText(str(gameScore))
        if MainPage.challengeNow is True:
            self.challengeMode.setChecked(True)  # 챌린지 참여 중을 사용자에게 표시

    def ok(self):
        if MainPage.challengeNow is True:  # 챌린지 수행 중인 경우
            MainPage.challengeNow = False  # 챌린지 완료 => 진행 종료
            self.btnTurn.setEnabled(True)
            users = readServerData('users')
            for u in users:
                if users[u]['id'] == MainPage.userid:
                    users[u]['challengeF'] = True  # 챌린지 참여 완료 표시
                    upload(users, 'users')
                    break
            i = messageBox('챌린지 완료', '챌린지를 수행했습니다. 다음 챌린저를 선택을 위해 CHALLENGE로 이동합니다.', 0)
            if i == 1:
                self.challenge()
        else:
            i = messageBox('게임 종료', '게임이 종료되었습니다. USER로 이동하시겠습니까?', 1)
            if i == 1:
                self.userData()


class nextDialog(base_5, form_5):
    def __init__(self):
        super(base_5, self).__init__()
        self.setupUi(self)
        self.setWindowTitle('CHOOSE NEXT')
        self.loadUserData()  # table 출력
        self.btnSelect.clicked.connect(self.choose)
        self.btnCancel.clicked.connect(self.cancel)

    def loadUserData(self):
        users = readServerData("users")  # 딕셔너리로 반환- 길이 = user 수
        items = []
        for u in users:
            if users[u]['challengeNum'] == -1 and users[u]['id'] != MainPage.userid:
                items.append(users[u]['id'])
        self.tableWidget.setRowCount(len(items))
        self.tableWidget.setColumnCount(1)
        for i in items:
            item = QTableWidgetItem(i)
            self.tableWidget.setItem(items.index(i), 0, item)

        self.tableWidget.resizeRowsToContents()  # 행 크기 조절
        self.tableWidget.setHorizontalHeaderItem(0, QTableWidgetItem("USER"))  # 헤더 설정
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 읽기 전용
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)  # 하나만 선택가능

    def choose(self):
        nextUserid = ''
        if self.tableWidget.currentItem() is None:
            messageBox("선택없음", "다음 챌린저를 선택하십시오.", 0)
        else:
            row = self.tableWidget.currentItem().row()
            nextUserid = self.tableWidget.item(row, 0).text()
            # challengeBoard.json 마지막에 지목한 상대의 아이디 추가
            chBoard = readServerData('challengeBoard')
            for c in chBoard:
                if c == str(MainPage.chNum):
                    chBoard[c]['challengers'].append(nextUserid)
                    break
            upload(chBoard, 'challengeBoard')

            userData = readServerData('users')
            for u in userData:
                if MainPage.userid == userData[u]['id']:
                    userData[u]['challengeNum'] = -1  # 진행 중인 챌린지 없음으로 표시
                    userData[u]['challengeF'] = False
                if nextUserid == userData[u]['id']:
                    userData[u]['challengeNum'] = MainPage.chNum  # 진행 중 챌린지 번호 표시
            upload(userData, 'users')
        messageBox("선택 완료", "다음 챌린저를 선택 완료했습니다.", 0)
        self.close()

    def cancel(self):
        self.close()


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
    app = QApplication(sys.argv)
    ex = Start()
    ex.show()
    sys.exit(app.exec_())
