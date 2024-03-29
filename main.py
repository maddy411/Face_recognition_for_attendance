import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime

path = 'Training_images'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    if cl != '.DS_Store':  # Skip .DS_Store entries
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
print(classNames)


def findEncodings(images):
    encodeList = []

    for img in images:
        if img is not None:  # Check if the image is not empty
            try:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            except IndexError as e:
                print(f"Error encoding image: {e}")
                # Handle the error (e.g., skip this image or log the error)
        else:
            print("Empty image encountered")  # Handle empty image

    return encodeList


def markAttendance(name, img_path):
    if name != '.DS_Store':  # Skip .DS_Store entries
        img_name = os.path.basename(img_path)  # Extract the image name from the path
        with open('Attendance.csv', 'a+') as f:
            f.seek(0)  # Move the cursor to the beginning of the file
            myDataList = f.readlines()

            nameList = [line.split(',')[0].strip() for line in myDataList]
            if name not in nameList:
                now = datetime.now()
                dtString = now.strftime('%Y-%m-%d %H:%M:%S')  # Include date in the timestamp
                f.write(f'{name},{dtString}\n')  # Write name, date, and timestamp
                print(f"Attendance marked for {name}")



encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            img_path = os.path.join(path, myList[matchIndex])  # Construct the image path
            markAttendance(name, img_path)  # Pass both name and image path to markAttendance function

            # Display the recognized face with a name
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Webcam', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()
