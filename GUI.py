from __future__ import print_function
from PIL import ImageTk, Image
import tkinter as tki
import threading
import datetime
import imutils
import cv2
import os
import math
from imutils.video import VideoStream
import argparse
import time
import numpy as np

class PhotoBoothApp:
    def __init__(self, vs, outputPath):
        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        self.vs = vs
        self.outputPath = outputPath
        self.frame = None
        self.thread = None
        self.stopEvent = None
        # initialize the root window and image panel
        self.root = tki.Tk()
        self.panel = None
        btn = tki.Button(self.root, text="Snapshot!",command=self.takeSnapshot)
        btn.pack(side="bottom", fill="both", expand="yes", padx=10,
                 pady=10)
        # start a thread that constantly pools the video sensor for
        # the most recently read frame
        lf = tki.Label(self.root,  bg='MistyRose4', fg='white')
        lf.pack(fill='both')
        inputframe = tki.Frame(lf)
        menu_bar = tki.Menu(self.root)
        file_menu = tki.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='UpdateDB', accelerator='Alt+F4')
        file_menu.add_separator()
        file_menu.add_command(label='Exit', accelerator='Alt+F4', command=exit)
        menu_bar.add_cascade(label='File', menu=file_menu)
        self.root.config(menu=menu_bar)
        self.InputImg = tki.Label(lf, bg='MistyRose3', relief=tki.RAISED, bd=5)
        OutputFrame = tki.LabelFrame(self.root,height='10', bd=2, text="Result", background='MistyRose', fg="gray14")
        self.InputImg.grid(column=4, row=0, rowspan=4, padx=70)  # pack(expand='yes', fill='both')
        self.ResultImg = tki.Text(OutputFrame, takefocus=0, relief=tki.SUNKEN, background='MistyRose4', bd=2)
        # text.bind('<Any-KeyPress>', on_content_changed)
        inputframe.grid(row=0, column=4, rowspan=4)  # pack(expand='yes', fill='both')
        self.ResultImg.pack(expand=True, fill='both')
        OutputFrame.pack(expand='yes', fill='both')

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        #self.thread2=threading.Thread(target=self.gesture(), args=())
        self.thread.start()
        #self.thread2.start()
        # set a callback to handle when the window is closed
        self.root.wm_title("PyImageSearch PhotoBooth")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

    def gesture(self):
        while(True):
            # read image
            img =self.vs.read()

            # get hand data from the rectangle sub window on the screen
            cv2.rectangle(img, (300,300), (100,100), (0,255,0),0)
            crop_img = img[100:300, 100:300]

            # convert to grayscale
            grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

            # applying gaussian blur
            value = (35, 35)
            blurred = cv2.GaussianBlur(grey, value, 0)

            # thresholdin: Otsu's Binarization method
            _, thresh1 = cv2.threshold(blurred, 127, 255,
                                       cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

            # show thresholded image
            cv2.imshow('Thresholded', thresh1)

            # check OpenCV version to avoid unpacking error
            (version, _, _) = cv2.__version__.split('.')

            if version == '3':
                image, contours, hierarchy = cv2.findContours(thresh1.copy(), \
                       cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            elif version == '4':
                contours, hierarchy = cv2.findContours(thresh1.copy(),cv2.RETR_TREE, \
                       cv2.CHAIN_APPROX_NONE)

            # find contour with max area
            cnt = max(contours, key = lambda x: cv2.contourArea(x))

            # create bounding rectangle around the contour (can skip below two lines)
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(crop_img, (x, y), (x+w, y+h), (0, 0, 255), 0)

            # finding convex hull
            hull = cv2.convexHull(cnt)

            # drawing contours
            drawing = np.zeros(crop_img.shape,np.uint8)
            cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)
		
            cv2.drawContours(drawing, [hull], 0,(0, 0, 255), 0)

            # finding convex hull
            hull = cv2.convexHull(cnt, returnPoints=False)

            # finding convexity defects
            defects = cv2.convexityDefects(cnt, hull)
            count_defects = 0
            cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)

            # Apply Cos Law to find angle for all defects (between fingers)
		
            # with angle greater than 90 degrees and ignore defects
            for i in range(defects.shape[0]):
                s,e,f,d = defects[i,0]

                start = tuple(cnt[s][0])
                end = tuple(cnt[e][0])
                far = tuple(cnt[f][0])

                # find length of all edges of triangle
                a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)

                # apply cosine rule here
		
                angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57

                # ignore angles > 90 and highlight rest with red dots
                if angle <= 90:
                    count_defects += 1
                    cv2.circle(crop_img, far, 1, [0,0,255], -1)
                #dist = cv2.pointPolygonTest(cnt,far,True)

                # draw a line from start to end i.e. the convex points (finger tips)
                # (can skip this part)
                cv2.line(crop_img,start, end, [0,255,0], 2)
		
                #cv2.circle(crop_img,far,5,[0,0,255],-1)

            # define actions required
            if count_defects == 1:
                cv2.putText(img,"This means that we could detect 1 finger", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
                print("This means that we could detect 1 finger")
            elif count_defects == 2:
                str = "This means that we could detect 2 fingers"
                cv2.putText(img, str, (5, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                print("This means that we could detect 2 finger")
            elif count_defects == 3:
                cv2.putText(img,"This means that we could detect 3 fingers", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
                print("This means that we could detect 3 finger")

            elif count_defects == 4:
                cv2.putText(img,"This means that we could detect 4 fingers", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
                print("This means that we could detect 4 finger")

            else:
                cv2.putText(img,"This means an entire hand", (50, 50),\
                            cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
                print("This means that we could detect 5 finger")


            # show appropriate images in windows
            cv2.imshow('Gesture', img)
            all_img = np.hstack((drawing, crop_img))
            cv2.imshow('Contours', all_img)

            k = cv2.waitKey(10)
            if k == 27:
                break
    def showerror(self,Txt):
        self.ResultImg.delete(1.0,tki.END)
        self.ResultImg.insert(tki.INSERT, Txt + '\n')


    def videoLoop(self):
            # DISCLAIMER:
            # I'm not a GUI developer, nor do I even pretend to be. This
            # try/except statement is a pretty ugly hack to get around
            # a RunTime error that Tkinter throws due to threading
            try:
                # keep looping over frames until we are instructed to stop
                while not self.stopEvent.is_set():
                    # grab the frame from the video stream and resize it to
                    # have a maximum width of 300 pixels
                    self.frame = self.vs.read()
                    # read image
                    img =self.frame

                    # get hand data from the rectangle sub window on the screen
                    cv2.rectangle(img, (300,300), (100,100), (0,255,0),0)
                    crop_img = img[100:300, 100:300]

                    # convert to grayscale
                    grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

                    # applying gaussian blur
                    value = (35, 35)
                    blurred = cv2.GaussianBlur(grey, value, 0)

                    # thresholdin: Otsu's Binarization method
                    _, thresh1 = cv2.threshold(blurred, 127, 255,
                                               cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

                    # show thresholded image
                    cv2.imshow('Thresholded', thresh1)

                    # check OpenCV version to avoid unpacking error
                    (version, _, _) = cv2.__version__.split('.')

                    if version == '3':
                        image, contours, hierarchy = cv2.findContours(thresh1.copy(), \
                               cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
                    elif version == '4':
                        contours, hierarchy = cv2.findContours(thresh1.copy(),cv2.RETR_TREE, \
                               cv2.CHAIN_APPROX_NONE)

                    # find contour with max area
                    cnt = max(contours, key = lambda x: cv2.contourArea(x))

                    # create bounding rectangle around the contour (can skip below two lines)
                    x, y, w, h = cv2.boundingRect(cnt)
                    cv2.rectangle(crop_img, (x, y), (x+w, y+h), (0, 0, 255), 0)

                    # finding convex hull
                    hull = cv2.convexHull(cnt)

                    # drawing contours
                    drawing = np.zeros(crop_img.shape,np.uint8)
                    cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)
                    cv2.drawContours(drawing, [hull], 0,(0, 0, 255), 0)

                    # finding convex hull
                    hull = cv2.convexHull(cnt, returnPoints=False)

                    # finding convexity defects
                    defects = cv2.convexityDefects(cnt, hull)
                    count_defects = 0
                    cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)

                    # applying Cosine Rule to find angle for all defects (between fingers)
                    # with angle > 90 degrees and ignore defects
                    for i in range(defects.shape[0]):
                        s,e,f,d = defects[i,0]

                        start = tuple(cnt[s][0])
                        end = tuple(cnt[e][0])
                        far = tuple(cnt[f][0])

                        # find length of all sides of triangle
                        a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                        b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                        c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)

                        # apply cosine rule here
                        angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57

                        # ignore angles > 90 and highlight rest with red dots
                        if angle <= 90:
                            count_defects += 1
                            cv2.circle(crop_img, far, 1, [0,0,255], -1)
                        #dist = cv2.pointPolygonTest(cnt,far,True)

                        # draw a line from start to end i.e. the convex points (finger tips)
                        # (can skip this part)
                        cv2.line(crop_img,start, end, [0,255,0], 2)
                        #cv2.circle(crop_img,far,5,[0,0,255],-1)

                    # define actions required
                    if count_defects == 1:
                        self.showerror("This means that we could detect 1 finger")
                    elif count_defects == 2:
                        str = "This means that we could detect 2 fingers"
                        self.showerror(str)
                    elif count_defects == 3:

                        self.showerror("This means that we could detect 3 fingers")


                    elif count_defects == 4:
                        self.showerror("This means that we could detect 4 fingers")

                    else:
                        pass


                    # show appropriate images in windows
                    #cv2.imshow('Gesture', img)
                    all_img = np.hstack((drawing, crop_img))
                    cv2.imshow('Contours', all_img)

                    k = cv2.waitKey(10)
                    if k == 27:
                        break

                    self.frame = imutils.resize(self.frame, width=500)

                    # OpenCV represents images in BGR order; however PIL
                    # represents images in RGB order, so we need to swap
                    # the channels, then convert to PIL and ImageTk format
                    image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    image = Image.fromarray(image)
                    image = ImageTk.PhotoImage(image)

                    # if the panel is not None, we need to initialize it
                    if self.panel is None:
                        self.panel = self.InputImg
                        self.panel.image = image

                    # otherwise, simply update the panel
                    else:
                        self.panel.configure(image=image)
                        self.panel.image = image
            except RuntimeError as e:
                print("[INFO] caught a RuntimeError")
    def takeSnapshot(self):
                # grab the current timestamp and use it to construct the
                # output path
                ts = datetime.datetime.now()
                filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
                p = os.path.sep.join((self.outputPath, filename))
                print(p)
                # save the file
                cv2.imwrite(p, self.frame.copy())
                print("[INFO] saved {}".format(filename))

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.stopEvent.set()
        self.vs.stop()
        self.root.quit()


# construct the argument parse and parse the arguments
"""ap = argparse.ArgumentParser()

ap.add_argument("-p", "--picamera", type=int, default=-1,
	help="whether or not the Raspberry Pi camera should be used")
args = vars(ap.parse_args())"""
# initialize the video stream and allow the camera sensor to warmup
print("[INFO] warming up camera...")
vs = VideoStream().start()
time.sleep(2.0)
# start the app
pba = PhotoBoothApp(vs, "/output")
pba.root.mainloop()

