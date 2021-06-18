from searcher import Searcher
from indexer import Indexer
from utils import out, drawContours, drawDefects
import cv2


def run():
    # Indexer()
    searcher = Searcher("HAND.csv")
    cap = cv2.VideoCapture("test3.MOV")

    # font
    font = cv2.FONT_HERSHEY_SIMPLEX
    # org
    org = (150, 150)
    # fontScale
    fontScale = 1
    # Blue color in BGR
    color = (255, 0, 0)
    # Line thickness of 2 px
    thickness = 2

    count = 0
    strng = ""
    temp = ""

    while cap.isOpened():

        count += 1
        success, img = cap.read()

        img = cv2.resize(img, (800, 800))

        thresh, contoursImg, cnt = drawContours(img)
        defectsImg = drawDefects(cnt, img)

        flag, features = out(img)
        r = searcher.search(features)

        if temp != r[0][1][8:9]:
            temp = r[0][1][8:9]
            strng += r[0][1][8:9]

        cv2.putText(img, strng, org, font, fontScale, color, thickness)
        cv2.imshow("Image", img)
        cv2.imshow("Threshold", thresh)
        cv2.imshow("contours", contoursImg)
        cv2.imshow("Defects", defectsImg)
        cv2.waitKey(50)


if __name__ == "__main__":
    run()
