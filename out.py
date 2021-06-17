import sys
import numpy as np
import mediapipe as mp
import time
import cv2



def out(cap):
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils
    pTime = 0
    cTime = 0

    # success, img = cap.read()
    try :
        imgRGB = cv2.cvtColor(cap, cv2.COLOR_BGR2RGB)
    except:return None
    results = hands.process(imgRGB)
    # print(results.multi_hand_landmarks)
    olist = list()
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                # print(id, lm)
                h, w, c = cap.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                # print(id, cx, cy)
                # if id == 4:
                # cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                cv2.putText(cap, str(int(id)), (cx, cy), cv2.FONT_HERSHEY_PLAIN, 3,
                            (255, 0, 255), 3)
                olist.append([cx, cy])
        # mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)
    else:
        print("error invalid picture\nexiting");sys.exit()
    # print(olist)

    hop = olist[0]
    for i, _ in enumerate(olist):
        if not i: olist[i] = [0, 0];continue
        x = olist[i][0] - hop[0]
        y = olist[i][1] - hop[1]
        # print(i,' ',x,' ',y)
        olist[i] = [x, y]
    features = [int(o) for f in olist for o in f]

    cv2.imshow("Image", cap)
    cv2.waitKey(1000)
    return np.absolute(features / np.linalg.norm(features))
    print(olist)
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime


