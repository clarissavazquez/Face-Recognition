import cv2
import numpy as np

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')
mouthCascade = cv2.CascadeClassifier('haarcascade_smile.xml')
alien_img = cv2.imread('alien.png', -1)
# Create mask for happy face
orig_mask = alien_img[:,:,3]
# Create inverted mask for happy face
orig_mask_inv = cv2.bitwise_not(orig_mask)
# Convert happy face to BGR and save original image size (will use later)
alien_img = alien_img[:,:,0:3]
orig_height, orig_width = alien_img.shape[:2]

video_capture = cv2.VideoCapture(0)

while True:
	ret, frame = video_capture.read()
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	faces = faceCascade.detectMultiScale(gray, 1.2, 6, minSize = (60, 60))
	count = 0
	#print 'faces:', len(faces)
	for (x,y,w,h) in faces:
		roi_gray = gray[y:y+(h / 2), x:x+w]
		roi_color = frame[y:y+h, x:x+w]
		eyes = eyeCascade.detectMultiScale(roi_gray)
		y_value = y-(2*3/h)
		mouth_roi_gray = gray[y_value:y+h, x:x+w]
		mouth = mouthCascade.detectMultiScale(mouth_roi_gray)
		#cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
		alien_height = h
		alien_width = w
		# Center the happy face
		x1 = x - (alien_width/4)
		x2 = x + w + (alien_width/4)
		y1 = y + h - (alien_height/2)
		y2 = y + h + (alien_height/2)
		# Check for clipping
		if x1 < 0:
			x1 = 0
		if y1 < 0:
			y1 = 0
		if x2 > w:
			x2 = w
		if y2 > h:
			y2 = h
		# Re-calculates width and height of happy face
		alien_width = x2 - x1
		alien_height = y2 - y1
		# Resize the original hapy face and the maske to the happy face
		# sizes from above
		alien = cv2.resize(alien_img, (alien_width,alien_height), interpolation = cv2.INTER_AREA)
		mask = cv2.resize(orig_mask, (alien_width,alien_height), interpolation = cv2.INTER_AREA)
		mask_inv = cv2.resize(orig_mask_inv, (alien_width,alien_height), interpolation = cv2.INTER_AREA)
		# Takes ROI for happy face from background equal to size of the happy face image
		roi = roi_color[y1:y2, x1:x2]
		roi_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
		roi_fg = cv2.bitwise_and(alien,alien,mask = mask)
		dst = cv2.add(roi_bg, roi_fg)
		roi_color[y1:y2, x1:x2] = dst
		#for (ex, ey, ew, eh) in eyes:
			#cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
		#for(mx, my, mw, mh) in mouth:
			#if my >= y_value:
			#	cv2.rectangle(roi_color,(mx,my),(mx+mw,my+mh),(0,0,255),2)
			
	cv2.imshow('Video', frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	
video_capture.release()
cv2.destroyAllWindows()
