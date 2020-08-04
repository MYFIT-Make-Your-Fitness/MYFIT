import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon
from PyQt5 import uic

#load both ui file
uifile_1 = 'Start.ui'
form_1, base_1 = uic.loadUiType(uifile_1)

uifile_2 = 'loginui.ui'
form_2, base_2 = uic.loadUiType(uifile_2)

uifile_3 = 'Sign.ui'
form_3, base_3 = uic.loadUiType(uifile_3)

uifile_4 = 'Main.ui'
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

class MainPage(base_4, form_4):
    def __init__(self):
        super(base_4, self).__init__()
        self.setupUi(self)

if __name__ == '__main__':
       app = QApplication(sys.argv)
       ex = Start()
       ex.show()
       sys.exit(app.exec_())