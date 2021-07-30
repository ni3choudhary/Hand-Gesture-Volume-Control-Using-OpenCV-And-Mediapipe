import numpy as np
import cv2
import mediapipe as mp
import time
import math
import handDetection as hd

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


widthCam, heightCam = 1280, 720

cap = cv2.VideoCapture(1)  # for webcam
cap.set(3, widthCam)
cap.set(4, heightCam)

previous_time = 0
current_time = 0

handdetect = hd.handDetector(detection_confident=0.8)

# pycaw library used for operating system volume control

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()

volume_range = volume.GetVolumeRange()
# volume.SetMasterVolumeLevel(0, None) # set volume to 100%

minvol = volume_range[0]
maxvol = volume_range[1]

vol = 0
volper = 0
volbar = 500

while True:
    _, frame = cap.read()
    frame = handdetect.findhands(frame, draw_landmark=False)
    lmlist = handdetect.gethandlocation(frame, draw_landmark=False)
    
    if len(lmlist) != 0:
        
        x1,y1 = lmlist[4][1], lmlist[4][2]
        x2,y2 = lmlist[8][1], lmlist[8][2]
        cx,cy = (x1+x2) // 2, (y1+y2) // 2
        
        cv2.circle(frame, (x1,y1), 10, (255,255,0), cv2.FILLED)
        cv2.circle(frame, (x2,y2), 10, (255,255,0), cv2.FILLED)
        cv2.circle(frame, (cx,cy), 10, (255,255,0), cv2.FILLED)
        cv2.line(frame, (x1,y1), (x2,y2), (0,255,0), 4)
        
        handrange = math.hypot(x2-x1, y2-y1)
        
        """ numpy.interp() function returns the one-dimensional piecewise 
        linear interpolant to a function with given discrete data points (xp, fp), evaluated at x. """
        
        vol = np.interp(handrange, [50,400],[minvol,maxvol])
        volbar = np.interp(handrange, [50,400],[500,250])
        volper = np.interp(handrange, [50,400],[0,100])
        
        volume.SetMasterVolumeLevel(vol, None)
        
        if handrange < 50:
            cv2.circle(frame, (cx,cy), 10, (255,0,0), cv2.FILLED)
            
        cv2.rectangle(frame, (50,250), (85,500),(255,0,0),3)
        cv2.rectangle(frame, (50,int(volbar)), (85,500),(255,0,0),cv2.FILLED)
        cv2.putText(frame, str(int(volper))+"%", (50,550), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,255), 2)
        
    current_time = time.time()
    fps = 1 / (current_time - previous_time)
    previous_time = current_time

    cv2.putText(frame, "FPS: "+str(int(fps)), (40,50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,255), 2)
    cv2.imshow('Gesture volume control', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()