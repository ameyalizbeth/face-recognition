import cv2
import numpy as np
import face_recognition
import os
import time
from datetime import datetime
import csv

# from PIL import ImageGrab
import mysql.connector
import urllib.request
mydb=mysql.connector.connect(
    host="localhost",
    user="root",
    password="ameya",
    database="design"
)
mycursor = mydb.cursor()
mycursor.execute("select image from users where image is not null")
myresult = mycursor.fetchall()
for x in myresult:
    url = str(x[0])
    url = url.replace("\\" , "/")
    y = url.split('/')[1];
    # print(y);
    url = 'http://localhost:3000/'+url

    urllib.request.urlretrieve(url,'imagesAttendence/'+y);


path = 'ImagesAttendence'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

with open('../Attendence.csv', 'r+') as f:
    f.writelines(f'NAME,DATE AND TIME')

def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

# def executesomething():
#     with open('Attendence.csv', 'r+') as f:
#         f.truncate()
#     time.sleep(60)


def markAttendance(name):
    with open('../Attendence.csv', 'r+') as f:
        # r = open('new.csv','r+')

        myDataList = f.readlines()
        # csv_reader = csv.reader(f)
        # for row in csv_reader:
        #     if not row[0]:
        #         continue
        nameList = []
        timestamp = []

        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])


        # executesomething()

            timestamp.append(entry[1])

        if name in nameList:
            now = datetime.now().strftime('%d/%m/%y %H:%M:%S')

            y=datetime.strptime(now,'%d/%m/%y %H:%M:%S')
        #
            index = len(nameList) - 1 - nameList[::-1].index(name)
            date_time_obj = datetime.strptime(timestamp[index], '%d/%m/%y %H:%M:%S')
            if((y - date_time_obj ).total_seconds() > 60):
                f.writelines(f'\n{name},{now}')










        if name not in nameList:
            now = datetime.now().strftime('%d/%m/%y %H:%M:%S')

            f.writelines(f'\n{name},{now}')
            # r.writelines(f'\n{name},{now}')


#### FOR CAPTURING SCREEN RATHER THAN WEBCAM
# def captureScreen(bbox=(300,300,690+300,530+300)):
#     capScr = np.array(ImageGrab.grab(bbox))
#     capScr = cv2.cvtColor(capScr, cv2.COLOR_RGB2BGR)
#     return capScr

encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    # img = captureScreen()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)
    # names=[]

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace,tolerance=0.5)
        print(matches)
        #
        name="unknown"
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print(faceDis)
        # matchIndex = np.argmin(faceDis)
# if matches[matchIndex]:

        if True in matches:
            matchIndex = np.argmin(faceDis)
            name = classNames[matchIndex].upper()
            # print(name)

            markAttendance(name)
        # names.append(name)

            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
        else:
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Webcam', img)
    cv2.waitKey(1)

# f.close()
