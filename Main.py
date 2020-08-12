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
                userNum = 'user' + str(len(users))
                users.setdefault('t', {})  # key 값에 변수로는 왜 바로 안되는지 모르겠네
                users['t']['id'] = userid
                users['t']['pw'] = userpw
                users['t']['name'] = username
                users['t']['age'] = self.spinBox.value()
                users['t']['balance'] = []  # default
                users['t']['challengeNum'] = -1  # default
                users[userNum] = users.pop('t')  # user 번호 설정

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
    # capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    # capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    # capture.set(cv2.CAP_PROP_FPS, fps)
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
    if len(shoulderResult) != 0:
        result = round((sum(shoulderResult) / len(shoulderResult)), 1)  # 어깨 기울임 측정의 평균
        print(result)
        # TODO: 서버에 result값 저장


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
        # MainPage.capture_thread = threading.Thread(target=grab, args=(0, q, 1920, 1080, 30))

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
        self.groupBox_ch.hide()
        self.groupBox_us.hide()
        self.btnCamera_2.hide()

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

    # TODO: MAIN 버튼 클릭
    def mainBalance(self):
        self.groupBox.setTitle("            'S CAMERA")
        self.groupBox_ch.hide()  # challenge 가리기
        self.groupBox_us.hide()  # user 가리기
        # game 가리기
        self.ImgWidget.show()
        self.btnCamera.show()
        self.btnCamera_2.hide()

    # TODO: challengeBoard.json, users.json 연동 방법
    def challenge(self):
        self.groupBox.setTitle("            'S CHALLENGE BOARD")
        self.groupBox_ch.show()
        self.groupBox_us.hide()  # user 가리기
        self.cameraOff()
        self.ImgWidget.hide()  # main 가리기
        self.btnCamera.hide()
        # game 가리기
        self.btnTurn.setEnabled(True)

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

    # TODO: 내 차례 challenge 수행
    def myTurn(self):
        if MainPage.chNum != -1: # 진행 중 챌린지 있음
            self.btnTurn.setEnabled(True)
            # game 화면으로 이동, 이때 game화면에는 challenge 중임을 표시
            # 1 게임 종료 후, challenge 화면으로 돌아옴
            # 챌린지 참여 완료 표시
            # 참여 완료 후, self.btnTurn.setEnabled(False)
        else: # 진행 중 챌린지 없음
            messageBox("챌린지 없음", "현재 참여 중인 챌린지가 없습니다.", 0)


    def challengeNum(self):  # 참여 중인 챌린지 번호 확인
        userdata = readServerData("users")
        for u in userdata:
            if MainPage.userid == userdata[u]['id']:
                MainPage.chNum = userdata[u]['challengeNum']
                break

    # TODO: 다음 차례 challenge 수행할 user 선택
    def chooseNext(self):
        # 새 창을 띄움 - user목록 나열 // list or table 사용
        self.challengeNum()
        if MainPage.chNum == -1:
            messageBox("챌린지 없음", "현재 참여 중인 챌린지가 없습니다.", 0)
        else:
            # if 챌린지 참여 완료 시
            self.dialog = nextDialog()
            self.dialog.show()
            # else:
            #     messageBox("챌린지 오류", "진행하지 않은 챌린지가 있습니다.", 0)

    # TODO: 새로운 challenge 생성
    def newCh(self):
        # 새 창을 띄움 - 챌린지 인원, 게임 선택(어차피 하나지만ㅎ)
        # 완료버튼을 누름으로써 challengeBoard.json에 새로운 챌린지 data 추가
        return 0

    # TODO: USER 버튼 클릭
    def userData(self):
        self.groupBox.setTitle("            'S DATA")
        self.groupBox_ch.hide()  # challenge 가리기
        self.groupBox_us.show()
        # game 가리기
        self.cameraOff()
        self.ImgWidget.hide()  # main 가리기
        self.btnCamera.hide()
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

    # TODO: GAME 버튼 클릭
    def game(self):
        self.groupBox.setTitle("            'S GAME")
        self.groupBox_ch.hide()
        self.groupBox_us.hide()
        self.btnCamera_2.show()

    def logout(self):
        self.close()

    def camera(self):  # main일때
        global running
        if running:  # Camera OFF
            self.cameraOff()
            # self.ImgWidget.hide()
        else:  # Camera ON
            # self.ImgWidget.show()
            MainPage.capture_thread = threading.Thread(target=grab, args=(0, q, 1920, 1080, 30))
            running = True
            MainPage.capture_thread.start()
        self.btnCamera.setEnabled(False)
        self.btnCamera.setText('Loading...')

    def camera_2(self):  # game일때
        # TODO: GAME에서 카메라 버튼을 눌렀을때 동작
        global running

    def cameraOff(self):
        global running
        running = False
        MainPage.capture_thread = None

    def update_frame(self):
        if not q.empty():
            self.btnCamera.setEnabled(True)
            if running:
                self.btnCamera.setText('ON')
            else:
                self.btnCamera.setText('CAMERA')
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
                    userData[u]['challengeNum'] = -1 # 진행 중인 챌린지 없음으로 표시
                if nextUserid == userData[u]['id']:
                    userData[u]['challengeNum'] = MainPage.chNum # 진행 중 챌린지 번호 표시
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
