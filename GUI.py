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
import os
import math

import argparse
import time
import numpy as np

from csv_uitilts import *
from tkinter import messagebox as t
from tkinter import filedialog as fd
from tkinter import simpledialog

def errormessage(str, event=None):
    t.showerror("Error", str)





def remove_number(s):
	return ''.join([i for i in s if not i.isdigit()])


def display_gestures():
    new= tki.Toplevel(pba.root)
    new.title("display gestures stored")
    scrollbar = tki.Scrollbar(new)
    scrollbar.pack( side = tki.RIGHT, fill = tki.Y )
    mylist = tki.Listbox(new, yscrollcommand = scrollbar.set )
    mylist.pack( side = tki.LEFT, fill = tki.BOTH )
    scrollbar.config( command = mylist.yview )
    names=read_cv() 
    formatted_names=[dataset_formatter(x) for x in names]
    formatted_names_no_numbers=[remove_number(x) for x in formatted_names]        
    formatted_names=list(set(formatted_names_no_numbers))
    for i in formatted_names: 
       mylist.insert(tki.END, i)


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
        self.searcher=Searcher("HAND.csv")
        file_menu.add_separator()
        file_menu.add_command(label='Exit', accelerator='Alt+F4', command=exit)
        menu_bar.add_cascade(label='File', menu=file_menu)
        self.root.config(menu=menu_bar)
        self.InputImg = tki.Label(lf, bg='MistyRose3', relief=tki.RAISED ,bd=5,width=72,height=20)
        tki.Button(lf,text="Gestures Stored",width=10,command=display_gestures).grid(row=5,column=3)
        tki.Button(lf,text="Add Gesture",width=10,command=self.add_gesture).grid(row=5,column=2)
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
        self.root.wm_title("Hand Gesture Recognition")
        self.root.resizable(False, False)
        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)
        self.root.lift()


    def ShowTxt(self,Txt):
        Txt=dataset_formatter(Txt)
        Txt=remove_number(Txt)
        self.ResultImg.delete(1.0,tki.END)
        self.ResultImg.insert(tki.INSERT, Txt + '\n')
       
    
    def add_gesture(self):
         imagePath = fd.askopenfilename()
         img = cv2.imread(imagePath)
         flag, features = out(img)
         if  flag :
             print(features)
             USER_INP = simpledialog.askstring(title="GET Gesture",prompt="What's the Gesture name?:")
             print( USER_INP)
             append_cv(USER_INP,features)
             self.searcher=Searcher("HAND.csv")
         else:
             errormessage("ERROR IMAGE IS INVALID")


    def videoLoop(self):
            count=0
            try:
                while self.vs.isOpened():
                    #count+=1
                # keep looping over frames until we are instructed to stop
                    if not self.stopEvent:
                        Stop=True
                        # grab the frame from the video stream 
                        _,self.frame = self.vs.read()
                        # read image
                        img =self.frame
                        if count%2==0:
                            count=0
                            flag, features = out(img)
                            if  flag :
                                #print(features)
                                r = self.searcher.search(features)
                                if float(r[0][0]) < 0.001 :
                                    self.ShowTxt(str(r[0][1]))
                                else:print(r[0][0]);print(r[0][1])
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
                    else:
                        if Stop:
                            Stop=False
                            self.InputImg.configure(image="")

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
                

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")
        self.vs.release()
        self.stopEvent=True
        #sys.exit()
        self.root.quit()

# initialize the video stream and allow the camera sensor to warmup
vs = cv2.VideoCapture(0)
time.sleep(2.0)
# start the app
pba = PhotoBoothApp(vs, "/output")
pba.root.mainloop()
