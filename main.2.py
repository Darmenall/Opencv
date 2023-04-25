import math
import cv2
import autopy
import mediapipe as mp
import numpy as np

cap = cv2.VideoCapture(0)

width, height = autopy.screen.size()

hands = mp.solutions.hands.Hands(static_image_mode=False,
                         max_num_hands=1,
                         min_tracking_confidence=0.5,
                         min_detection_confidence=0.5)

mpDraw = mp.solutions.drawing_utils

from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
volume.SetMasterVolumeLevel(0, None)
minVol = volRange[0]
maxVol = volRange[1]
volBar = 400
vol = 0
volPer = 0

while True:
    _, img = cap.read()
    result = hands.process(img)
    # print(result)
    if result.multi_hand_landmarks:
        for id, lm in enumerate(result.multi_hand_landmarks[0].landmark):
            h, w, _ = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(img, (cx, cy), 3, (250, 0, 255))
            if id == 4:
                x1 = cx
                y1 = cy
                # print(x1, y1)
                cv2.circle(img, (cx, cy), 20, (250, 0, 255), cv2.FILLED)
            if id == 8:
                x2 = cx
                y2 = cy
                cx1, cy1 = (x1+x2) // 2, (y1+y2) // 2
                # print(x2, y2)
                cv2.circle(img, (cx, cy), 20, (250, 0, 255), cv2.FILLED)
                cv2.circle(img, (cx1, cy1), 20, (250, 0, 255), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                length = math.hypot(x2-x1, y2-y1)
                # print(length)

                vol = np.interp(length, [50, 300], [minVol, maxVol])
                volBar = np.interp(length, [50, 300], [400, 150])
                volPer = np.interp(length, [50, 300], [0, 100])
                print(int(length), vol)
                volume.SetMasterVolumeLevel(vol, None)

                if length < 50:
                    cv2.circle(img, (cx1, cy1), 15, (0, 255, 0), cv2.FILLED)

            cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 2)
            cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
            cv2.putText(img, f"{int(volPer)} %", (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                        1, (255, 0, 0), 2)

        mpDraw.draw_landmarks(img, result.multi_hand_landmarks[0], mp.solutions.hands.HAND_CONNECTIONS)

    cv2.imshow("darmen", img)
    k = cv2.waitKey(1)
    if k == ord("q"):
        break
