import json
import os
import urllib.request
from collections import OrderedDict
from ftplib import FTP
from io import BytesIO

# read json data file from server
file_data = OrderedDict()
data = urllib.request.urlopen("http://soyeong99.dothome.co.kr/web/jsonTest.json").read()
file_data = json.loads(data)
# print(json.dumps(file_data))

# input user info
print('id: ')
userid = input()
print("pw: ")
userpw = input()
userBalance = 0 # default 0
userChallenge = False # default False

userNum = 'user' + str(len(file_data)) # user 번호 계산
file_data.setdefault('t', {}) # key값에 변수로는 왜 바로 안되는지 모르겠네
# save user data
file_data['t']['id'] = userid
file_data['t']['pw'] = userpw
file_data['t']['balance'] = userBalance
file_data['t']['challenge'] = userChallenge
file_data[userNum] = file_data.pop('t') # user 번호 설정

# upload data file to server
os.system("wget http://soyeong99.dothome.co.kr/web/jsonTest.json")

ftp = FTP('112.175.184.79', 'soyeong99', 'thdud4869!')
ftp.cwd("/html/web/")
# convert data to file-like object
tempF = json.dumps(file_data, indent="\t")
tempF = bytes(tempF, "utf8")
file_like = BytesIO(tempF)
ftp.storbinary('STOR jsonTest.json', file_like)
