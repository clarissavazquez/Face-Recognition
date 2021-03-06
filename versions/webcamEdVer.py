import sys
import cv2
import numpy as np
from multiprocessing import Process, Pipe
import thread

mouthCascade = cv2.CascadeClassifier('haarcascade_smile.xml')
x_offset=y_offset=50



def findEyes(conn, data):
    roi_color = frame[data[2]:data[2]+(data[3]/2), data[1]:data[1]+data[4]]
    eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')
    eyes = eyeCascade.detectMultiScale(data[0])
    if(len(eyes) == 0):
	conn.send([0,0,0,0])
	conn.close()
    else:
	for (x, y, w, h) in eyes:
	    conn.send([x,y,x+w,y+h])
	    conn.close()


def findMouth(mouth_roi_gray, roi_color):
    mouth = mouthCascade.detectMultiScale(mouth_roi_gray)
    for(mx, my, mw, mh) in mouth:
        if my >= y_value:
	    cv2.rectangle(roi_color,(mx,my),(mx+mw,my+mh),(0,0,255),2)
    return

def findFace(frame, gray):
    eye_roi_color = frame[y:y+h, x:x+w]
    faces = faceCascade.detectMultiScale(gray, 1.2, 6, minSize = (60, 60))
    for (x,y,w,h) in faces:
	cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
    try:
	thread.start_new_thread(findEyes, (gray, eye_roi_color))
    except:
	print 'Failed eye thread'


# The real program starts to run at this point.
if __name__ == '__main__':
    faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') # opens face data file
    video_capture = cv2.VideoCapture(0)

    video_capture.set(3,1080)
    video_capture.set(4,1024)
    video_capture.set(15,0.1)


    parent_conn, child_conn = Pipe()    # this creates a pipe
    while True:
        #parent_conn, child_conn = Pipe()
        ret, frame = video_capture.read() # get video or access camera?
        
        if (ret):       # If an invalid frame is found then stop!
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # video grayscale?
            faces = faceCascade.detectMultiScale(gray, 1.2, 6, minSize = (60,60)) # searches video for faces

            for (x,y,w,h) in faces:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2) # frame for the face: blue
                roi_gray = gray[y:y+(h/2), x:x+w] # Area to search for the eyes. // this is half the face frame.
                roi_color = frame[y:y+h,x:x+w]


                # thread that finds eyes
                data = [roi_gray,x,y,w,h]
		print 'here'
                p = Process(target=findEyes, args=(child_conn, data,))
		print 'here2'
                p.start()
		print 'here3'
                eye_frame = parent_conn.recv()
                cv2.rectangle(roi_color,(eye_frame[0],eye_frame[1]),(eye_frame[2],eye_frame[3]),(0,255,0),2)
        else:
            break


        cv2.imshow('Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.VideoCapture(0).release
            cv2.destroyAllWindows()
            WaitKey(1)
            break

