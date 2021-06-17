import glob
import os
import sys
import threading
import cv2
from utils import out


class Indexer:
    def __init__(self, outputFile="HAND.csv"):
        # open the output index file for writing
        if os.path.exists(outputFile):
            os.remove(outputFile)
        output = open(outputFile, "w")
        # use glob to grab the image paths and loop over them
        for imagePath in glob.glob("dataset" + "/*.*g"):
            print(imagePath)
            # extract the image ID (i.e. the unique filename) from the image
            # path and load the image itself
            image = cv2.imread(imagePath)
            _, featuresOut = out(image)
            # describe the image
            # write the features to file
            featuresOut = [str(f) for f in featuresOut]
            output.write("%s,%s\n" % (imagePath, ",".join(featuresOut)))
        # close the index file
        output.close()
