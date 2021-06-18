import sys
import numpy as np
import csv
import mediapipe as mp
import time
import glob
import cv2
import os
import threading


# construct the argument parser and parse the arguments
# initialize the color descriptor

class Indexer:
    def __init__(self, Outputfile="HAND.csv"):
        # open the output index file for writing
        if os.path.exists(Outputfile):
            os.remove(Outputfile)
        output = open(Outputfile, "w")
        # use glob to grab the image paths and loop over them
        for imagePath in glob.glob("dataset" + ("/*.*g")):
            print(imagePath)
            # extract the image ID (i.e. the unique filename) from the image
            # path and load the image itself
            imageID = imagePath[imagePath.rfind("/") + 1:]
            image = cv2.imread(imagePath)
            _, features = out(image)
            # describe the image
            # write the features to file
            features = [str(f) for f in features]
            output.write("%s,%s\n" % (imagePath, ",".join(features)))
        # close the index file
        output.close()


class Searcher:
    def __init__(self, indexPath):  # store our index path
        self.results=dict()
        self.indexPath = indexPath
        with open(self.indexPath) as f:
            # initialize the CSV reader
            SList = csv.reader(f)
            for row in SList:
                # parse out the image ID and features, then compute the
                # chi-squared distance between the features in our index
                # and our query features
                features = [float(x) for x in row[1:]]
                self.results[row[0]] = features
            f.close()
        #print(self.results)
    def search(self, queryFeatures, limit=10):
        RESults=dict()
        # initialize our dictionary of results
        # open the index file for reading
        # initialize the CSV reader
        # loop over the rows in the index
        for key,value in self.results.items():

            d = self.chi2_distance(value, queryFeatures)

            # now that we have the distance between the two feature
            # vectors, we can udpate the results dictionary -- the
            # key is the current image ID in the index and the
            # value is the distance we just computed, representing
            # how 'similar' the image in the index is to our query
            RESults[key] = d

        # close the reader
        # sort our results, so that the smaller distances (i.e. the
        # more relevant images are at the front of the list)
        RESults = sorted([(v, k) for (k, v) in RESults.items()])
        # return our (limited) results
        return RESults[0:2]

    def chi2_distance(self, histA, histB, eps=1e-10):
        # compute the chi-squared distance
        d =  np.sum([((a - b) ** 2)/ len(histA) #(a + b + eps)
                          for (a, b) in zip(histA, histB)])

        # return the chi-squared distance
        return d

mpHands = mp.solutions.hands
hands = mpHands.Hands()#,min_detection_confidence=0.9)
mpDraw = mp.solutions.drawing_utils
# cap = cv2.imread('5.jpg')
def out(cap):

    imgRGB = cv2.cvtColor(cap, cv2.COLOR_BGR2RGB)
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
                cv2.circle(cap, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                #cv2.putText(cap, str(int(id)), (cx, cy), cv2.FONT_HERSHEY_PLAIN, 3,
                 #(255, 0, 255), 3)
                olist.append([cx, cy])
            mpDraw.draw_landmarks(cap, handLms, mpHands.HAND_CONNECTIONS)
    else:
        #print("error invalid picture\nexiting");
        return False, []
    # print(olist)

    hop = olist[0]
    for i, _ in enumerate(olist):
        if not i: olist[i] = [0, 0];continue
        x = olist[i][0] - hop[0]
        y = olist[i][1] - hop[1]
        # print(i,' ',x,' ',y)
        olist[i] = [x, y]
    features = [int(o) for f in olist for o in f]

    return True, np.absolute(features / np.linalg.norm(features))

    #return True,[]
#Indexer()
searcher = Searcher("HAND.csv")
#sys.exit()
#print("cameraaaa")
#cap = cv2.VideoCapture(0)
#cap.set(cv2.CAP_PROP_POS_FRAMES, 5)
#count=0

# Indexer()
# searcher = Searcher("HAND.csv")
