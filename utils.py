import mediapipe as mp
import numpy as np
import cv2


def out(capIn):
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()

    imgRGB = cv2.cvtColor(capIn, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)
    olist = list()
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for idHand, lm in enumerate(handLms.landmark):
                h, w, c = capIn.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.putText(capIn, str(int(idHand)), (cx, cy), cv2.FONT_HERSHEY_PLAIN, 3,
                            (255, 0, 255), 3)
                olist.append([cx, cy])
    else:
        print("error invalid picture\nexiting")
        return False, []

    hop = olist[0]
    for i, _ in enumerate(olist):
        if not i:
            olist[i] = [0, 0]
            continue
        x = olist[i][0] - hop[0]
        y = olist[i][1] - hop[1]
        olist[i] = [x, y]
    featuresList = [int(o) for f in olist for o in f]

    return True, np.absolute(featuresList / np.linalg.norm(featuresList))


def drawContours(capIn):

    img = np.copy(capIn)

    # convert to grayscale
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # applying gaussian blur
    value = (35, 35)
    blurred = cv2.GaussianBlur(grey, value, 0)

    # thresholding: Otsu's Binarization method
    _, thresh1 = cv2.threshold(blurred, 127, 255,
                               cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    contours, hierarchy = cv2.findContours(thresh1.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours_image = np.copy(img)

    # find contour with max area
    maxContour = max(contours, key=lambda x: cv2.contourArea(x))
    cv2.drawContours(contours_image, maxContour, -1, (255, 0, 255), 3)

    return thresh1, contours_image, maxContour


def drawDefects(maxContour, img):

    hull = cv2.convexHull(maxContour, returnPoints=False)
    hull[::-1].sort(axis=0)
    convexityDefects = cv2.convexityDefects(maxContour, hull)

    defectsImg = np.copy(img)

    for defect in convexityDefects:
        s, e, f, d = defect[0]
        start = tuple(maxContour[s][0])
        end = tuple(maxContour[e][0])
        far = tuple(maxContour[f][0])

        defectsImg = cv2.line(defectsImg, start, end, (0, 0, 255), 3)
        defectsImg = cv2.line(defectsImg, start, far, (255, 0, 0), 3)
        defectsImg = cv2.line(defectsImg, end, far, (0, 255, 0), 3)

    return defectsImg
