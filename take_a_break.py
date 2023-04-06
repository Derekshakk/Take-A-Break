import math
import sys
import time
from tkinter import *
from tkinter.ttk import *

import cv2
from PIL import ImageTk, Image


# Installing anaconda:
# https://learnopencv.com/install-opencv-on-windows/


class Application:
    def __init__(self, faceTimeAllowed, restTime, faceDetectionReset):
        '''
          All vars are in seconds

          faceTimeAllowed: how long before the popup
          restTime: how long the popup stays
          faceDetectionReset: how long the app doesn't see a face before resting the clock
        '''

        # Set up OpenCV and Face Detection
        # https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
        cascPath = 'haarcascade_frontalface_default.xml'
        self.faceCascade = cv2.CascadeClassifier(cascPath)
        self.camera = cv2.VideoCapture(0)

        # Set up main App window
        self.root = Tk()
        self.root.geometry("500x500")

        # =========================Remove frame and add this portion of the code=========================
        self.bgimg = Image.open('Rest_Eyes.jpg')
        self.l = Label(self.root)
        self.l.place(x=0, y=0, relwidth=1, relheight=1)  # make label l to fit the parent window always
        self.l.bind('<Configure>', self.on_resize)
        # =======================================================================

        self.root.title("FaceTimeTracker")
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        # Set up variables
        self.faceDetectedTimeResetThreshold = faceDetectionReset  # in seconds
        self.faceDetectedMaxTime = faceTimeAllowed  # in seconds
        self.breakWindowTime = restTime

        self.onBreakScreen = False
        self.faceDetected = False
        self.faceDetectedTime = 0
        self.faceNotDetectedTime = 0
        self.timeLapse = 0  # in seconds
        self.videoUpdateTime = 30  # milliseconds
        self.breakWindow = None

        # Start Video Loop
        # self.root.destroy()
        self.video_loop()

    # Add this fuction to resize the background image
    def on_resize(self, event):
        # resize the background image to the size of label
        image = self.bgimg.resize((event.width, event.height), Image.LANCZOS)
        # update the image of the label
        self.l.image = ImageTk.PhotoImage(image)
        self.l.config(image=self.l.image)

    def showBreakScreen(self):
        """
        Displays the popup break window.
        """
        # Replace 30seconds  with self.breakWindowTime
        self.l.destroy()
        bw = BreakWindow(self, self.breakWindowTime)
        self.breakWindow = bw

    def video_loop(self):
        """
        Face detection loop
        """
        # Check if pop up window is not up
        if not self.onBreakScreen:
            # Get frame from webcam
            _, frame = self.camera.read()

            # Face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.faceCascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=9)

            # update time
            currentCount = time.perf_counter()
            detltaTime = currentCount - self.timeLapse
            self.timeLapse = currentCount

            # check if at least one face has been detected
            if len(faces) > 0:
                self.faceDetected = True
                # increase face time
                self.faceDetectedTime = self.faceDetectedTime + detltaTime
                # reset time not detecting face.
                self.faceNotDetectedTime = 0
                # update time lapsed
                self.timeLapse = currentCount

                print(f"Face: {int(self.faceDetectedTime)} seconds{' ' * 20}", end="\r")

            else:
                # if face not dected
                self.faceDetected = False

                # increase no face time
                self.faceNotDetectedTime = self.faceNotDetectedTime + detltaTime

                print(f"NoFace: {int(self.faceNotDetectedTime)}  seconds{' ' * 20}", end="\r")

            if self.faceNotDetectedTime >= self.faceDetectedTimeResetThreshold:
                # check if user has been away long enough to reset time
                self.faceDetectedTime = 0
                self.faceNotDetectedTime = 0
            elif self.faceDetectedTime >= self.faceDetectedMaxTime:
                # check if user has been on computer for too long
                self.faceDetectedTime = 0
                self.faceNotDetectedTime = 0
                # show pop up window

                self.showBreakScreen()

        else:
            print("on break window", end='\r')
        # call back loop
        self.root.after(self.videoUpdateTime, self.video_loop)  # call the same function after 30 milliseconds

    def destructor(self):
        """ Destroy the root object and release all resources """
        self.root.destroy()
        self.camera.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application
        sys.exit()


# Pop up window class
class BreakWindow:
    def __init__(self, mainApplication, duration=60):
        """
          duration is in seconds
        """
        # main window app set up
        self.app = mainApplication
        self.app.onBreakScreen = True
        self.root = self.app.root

        # pop up window set up
        self.window = self.root
        self.window.title("Take A Break")
        self.window.protocol('WM_DELETE_WINDOW', self.destructor)
        # set window size
        self.window.geometry('500x200')

        # =========================Remove frame and add this portion of the code=========================
        self.bgimg = Image.open('Rest_Eyes.jpg')
        self.l = Label(self.window)
        self.l.place(x=0, y=0, relwidth=1, relheight=1)  # make label l to fit the parent window always
        self.l.bind('<Configure>', self.on_resize)
        # =======================================================================

        # Set up variables
        self.duration = duration
        self.timeLapse = 0
        self.startTime = time.perf_counter()
        self.build()  # build window
        self.timerLoop()  # window update loop

    # Add this fuction to resize the background image
    def on_resize(self, event):
        # resize the background image to the size of label
        image = self.bgimg.resize((event.width, event.height), Image.LANCZOS)
        # update the image of the label
        self.l.image = ImageTk.PhotoImage(image)
        self.l.config(image=self.l.image)

    def timerLoop(self):
        # update time
        currentTime = time.perf_counter()
        delta = currentTime - self.startTime
        self.timeLapse = self.timeLapse + delta

        # calucalte percent for the progress bar
        percent = round((1 - self.timeLapse / self.duration) * 100)

        # calculate time remaining
        timeRemaining = self.duration - self.timeLapse

        # Convert time remaining to string to display
        timeRemainingSeconds = str(round(timeRemaining % 60))
        if timeRemaining % 60 < 10:
            timeRemainingSeconds = '0' + timeRemainingSeconds
        timeRemainingMinutes = str(math.floor(timeRemaining // 60))

        # update the status text
        self.statusText.set(f' {timeRemainingMinutes}:{timeRemainingSeconds} Time Remaning')

        # update the progress bar
        self.progress['value'] = percent

        # update start time
        self.startTime = currentTime

        # check if time is up else loop
        if (self.timeLapse >= self.duration):
            self.destructor()
        else:
            self.window.after(500, self.timerLoop)  # called in milliseconds

    def build(self):
        # Timer text
        self.statusText = StringVar()
        self.statusText.set('-- Time Remaning')
        self.statusLabel = Label(self.window, textvariable=self.statusText)
        self.statusLabel.grid(column=0, row=0, ipadx=5, pady=5, columnspan=2)

        # progress bar
        self.progress = Progressbar(self.window, orient=HORIZONTAL, length=100, mode='determinate')
        self.progress.grid(column=0, row=1, ipadx=5, pady=5, columnspan=2)

        # resume button
        resumeBtn = Button(self.window, text='Resume Working', command=self.destructor)
        resumeBtn.grid(column=0, row=2, ipadx=5, pady=5)

        # add time button
        addTimeBtn = Button(self.window, text='Add Minute', command=self.addTime)
        addTimeBtn.grid(column=1, row=2, ipadx=5, pady=5)

        # subtract time button
        rmvTimeBtn = Button(self.window, text='Remove Minute', command=self.removeTime)
        rmvTimeBtn.grid(column=2, row=2, ipadx=5, pady=5)

        # quit button
        quitBtn = Button(self.window, text='Quit', command=self.quitApp)
        quitBtn.grid(column=1, row=3, ipadx=5, pady=5)

    def quitApp(self):
        self.app.destructor()

    def addTime(self, seconds=60):
        '''
        adds time to the duration of break
        '''
        self.duration = self.duration + seconds

    def removeTime(self, seconds=-60):
        '''
        removes time to the duration of break
        '''
        self.addTime(seconds)

    def destructor(self):
        """ Destroy the popup break window object and release all resources """
        self.app.onBreakScreen = False
        self.app.timeLapse = time.perf_counter()
        self.app.breakWindow = None
        self.window.destroy()


if __name__ == '__main__':
    faceTimeAllowed = int(input("Enter how many seconds your face has to be shown:"))
    restTime = int(input("Enter how many seconds your rest time should be:"))
    faceDetectionReset = int(input("Enter how many seconds the app doesn't see a face before resetting the clock:"))
    app = Application(faceTimeAllowed, restTime, faceDetectionReset)
    # Remove frame
    app.root.mainloop()
