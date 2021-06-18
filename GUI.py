#from __future__ import print_function
import sys
from sys import exit

from hand_tacking_basics import *
from PIL import ImageTk, Image
import tkinter as tki
import threading
import datetime
import imutils
import cv2
#import os
import math
#from imutils.video import VideoStream
import argparse
import time
import numpy as np
print(os.path.dirname(os.path.abspath(__file__)))
class PhotoBoothApp:
    def __init__(self, vs, outputPath):
        self.vs = vs
        self.outputPath = outputPath
        self.frame = None
        # initialize the root window and image panel
        self.root = tki.Tk()
        self.root.geometry('720x700+50+50')
        self.panel = None
        lf = tki.Label(self.root,  bg='MistyRose4', fg='white',width=72,height=60)
        lf.pack(fill='both')
        inputframe = tki.Frame(lf)
        menu_bar = tki.Menu(self.root)
        file_menu = tki.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='UpdateDB', accelerator='Alt+F4')
        file_menu.add_separator()
        file_menu.add_command(label='Exit', accelerator='Alt+F4', command=exit)
        menu_bar.add_cascade(label='File', menu=file_menu)
        self.root.config(menu=menu_bar)
        self.InputImg = tki.Label(lf, bg='MistyRose3', relief=tki.RAISED ,bd=5,width=72,height=20)
        tki.Button(lf,text="Gestures Stored",width=10,).grid(row=5,column=3)
        tki.Button(lf,text="Add Gesture",width=10).grid(row=5,column=2)
        self.RecogButton=tki.Button(lf,text="Start Recognition",width=15,command=self.startRecog)
        self.RecogButton.grid(row=5,column=1)
        OutputFrame = tki.LabelFrame(self.root,height='10', bd=2, text="Result", background='MistyRose', fg="gray14")
        self.InputImg.grid(column=0, row=0, rowspan=4, padx=70,columnspan=5)  # pack(expand='yes', fill='both')
        self.ResultImg = tki.Text(OutputFrame, takefocus=0, relief=tki.SUNKEN, background='MistyRose4', bd=2,height=300,font=("Helvetica", 28))
        # text.bind('<Any-KeyPress>', on_content_changed)
        inputframe.grid(row=0, column=4, rowspan=4)  # pack(expand='yes', fill='both')
        self.ResultImg.pack(expand=True, fill='both')
        OutputFrame.pack(expand='yes', fill='both')
        self.stopEvent = False
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.threadState=False
        # set a callback to handle when the window is closed
        self.root.wm_title("PyImageSearch PhotoBooth")
        self.root.resizable(False, False)
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.lift()


    def ShowTxt(self,Txt):
        self.ResultImg.delete(1.0,tki.END)
        self.ResultImg.insert(tki.INSERT, Txt + '\n')


    def videoLoop(self):
            count=0
            try:
                while True:
                # keep looping over frames until we are instructed to stop
                    if not self.stopEvent:
                        # grab the frame from the video stream and resize it to
                        # have a maximum width of 300 pixels
                        _,self.frame = self.vs.read()
                        # read image
                        img =self.frame
                        if count%40==0:
                            flag, features = out(img)
                            if  flag :
                                #print(features)
                                r = searcher.search(features)
                                self.ShowTxt(str(r[0][1]))
                                #print(r[0][0])
                        #cv2.imshow("Image", img)
                        cv2.waitKey(1)

                        self.frame=imutils.resize(self.frame,width=580,height=350)
                        #self.InputImg.config(width=580,height=350)
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
                    else: self.InputImg.configure(image="")

            except RuntimeError as e:
                print("[INFO] caught a RuntimeError")
    def stopRecog(self):
                self.InputImg.config(width=72,height=20)
                print("stop")
                self.stopEvent=True
                self.RecogButton.config(text="Start Recognition",width=15,command=self.startRecog)

    def startRecog(self):
                print("start")
                self.stopEvent=False

                self.InputImg.config(width=580,height=350)
                img = Image.open("clown.png").resize((300, 270), Image.ANTIALIAS)
                img = ImageTk.PhotoImage(img, Image.ANTIALIAS)
                self.InputImg.configure(image=img)
                self.InputImg.image = img
                if not self.threadState:
                    self.threadState=True
                    self.thread.start()
                self.RecogButton.config(text="Stop Recognition",width=15,command=self.stopRecog)
                # grab t/he current timestamp and use it to construct the
                # output path
                #ts = datetime.datetime.now()
                #filename = p+"hello{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
                #p = os.path.sep.join((self.outputPath, filename))
                #print(p)
                # save the file
                #cv2.imwrite(filename, self.frame.copy())
                #print("[INFO] saved {}".format(filename))

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.stopEvent=True
        #sys.exit()
        self.root.quit()


# construct the argument parse and parse the arguments
# initialize the video stream and allow the camera sensor to warmup
vs = cv2.VideoCapture(0)
time.sleep(2.0)
# start the app
pba = PhotoBoothApp(vs, "/output")
pba.root.mainloop()
