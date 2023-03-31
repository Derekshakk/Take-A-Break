import sys
import cv2
from tkinter import *
from tkinter.ttk import *
import time
import math
import tkinter
from PIL import ImageTk, Image

#Installing anaconda:
#https://learnopencv.com/install-opencv-on-windows/

class Application:
  def __init__(self, faceTimeAllowed, restTime, faceDetectionReset):
    '''
      All vars are in seconds

      faceTimeAllowed: how long before the pop up
      restTime: how long the pop up stays
      faceDectectionReset: how long the the app doesn't see a face before resting the clock
    '''

    # Set up OpenCV and Face Detection
    # https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
    cascPath = 'haarcascade_frontalface_default.xml'
    self.faceCascade = cv2.CascadeClassifier(cascPath)
    self.camera = cv2.VideoCapture(0)

    # Set up main App window
    self.root = Tk()
    self.root.geometry("500x500")
    frame = Frame(self.root, width=350, height=350)
    frame.pack()
    frame.place(anchor='center', relx=0.5, rely=0.5)
    img = ImageTk.PhotoImage(Image.open("Rest_Eyes.jpg"))
    label = Label(frame, image = img)
    label.pack()

    self.root.title("FaceTimeTracker")
    self.root.protocol('WM_DELETE_WINDOW', self.destructor)

    # Set up variables
    self.faceDetectedTimeResetThreshold = faceDetectionReset # in seconds
    self.faceDetectedMaxTime = faceTimeAllowed # in seconds
    self.breakWindowTime = restTime

    self.onBreakScreen = False
    self.faceDetected = False
    self.faceDetectedTime = 0
    self.faceNotDetectedTime = 0
    self.timeLapse = 0 # in seconds
    self.videoUpdateTime = 30 #milliseconds
    self.breakWindow = None

    # Start Video Loop
    #self.root.destroy()
    self.video_loop()


  def showBreakScreen(self):
    '''
    Displays the pop up break window.
    '''
    bw = BreakWindow(self, 30)
    self.breakWindow = bw


  def video_loop(self):
    '''
    Face detection loop
    '''
    # Check if pop up window is not up
    if self.onBreakScreen == False:
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

        print(f"Face: {int(self.faceDetectedTime)} seconds{' '*20}",end="\r")


      else:
        # if face not dected
        self.faceDetected = False

        # increase no face time
        self.faceNotDetectedTime = self.faceNotDetectedTime + detltaTime

        print(f"NoFace: {int(self.faceNotDetectedTime)}  seconds{' '*20}", end="\r")

      if(self.faceNotDetectedTime >= self.faceDetectedTimeResetThreshold):
        # check if user has been away long enough to reset time
        self.faceDetectedTime = 0
        self.faceNotDetectedTime = 0
      elif(self.faceDetectedTime >= self.faceDetectedMaxTime):
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
  def __init__(self, mainApplication, duration = 60):
    '''
      duration is in seconds
    '''
    # main window app set up
    self.app = mainApplication
    self.app.onBreakScreen = True
    self.root = self.app.root

    # pop up window set up
    self.window = (self.root)
    self.window.title("Take A Break")
    self.window.protocol('WM_DELETE_WINDOW', self.destructor)

    # Set up variables 
    self.duration = duration
    self.timeLapse = 0
    self.startTime = time.perf_counter()
    '''
    self.window.minsize(width = 200, height = 250)
    canvas = Canvas(self.window, width = 200, height = 200)
    canvas.pack()
    img = tkinter.PhotoImage(file = './Rest_Eyes.jpg')
    canvas.image = img
    canvas.create_image(100, 100, image = img)
    '''
    self.build() # build window 
    self.timerLoop() # window update loop


  def timerLoop(self):
    # update time
    currentTime = time.perf_counter()
    delta = currentTime - self.startTime
    self.timeLapse = self.timeLapse + delta

    # calucalte percent for the progress bar
    percent = round ((1 - self.timeLapse/self.duration) * 100)

    # calculate time remaining
    timeRemaining = self.duration - self.timeLapse

    # Convert time remaining to string to display
    timeRemainingSeconds = str(round(timeRemaining % 60))
    if timeRemaining % 60 < 10:
      timeRemainingSeconds = '0'+timeRemainingSeconds
    timeRemainingMinutes = str(math.floor(timeRemaining // 60))

    # update the status text
    self.statusText.set(f' {timeRemainingMinutes}:{timeRemainingSeconds} Time Remaning')

    # update the progress bar
    self.progress['value'] = percent


    # update start time
    self.startTime = currentTime

    # check if time is up else loop
    if(self.timeLapse >= self.duration):
      self.destructor()
    else:
      self.window.after(500, self.timerLoop)  # called in milliseconds



  def build(self):
    # set window size
    self.window.geometry('500x200')

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


  def addTime(self, seconds = 60):
    '''
    adds time to the duration of break
    '''
    self.duration = self.duration + seconds


  def removeTime(self, seconds = -60):
    '''
    removes time to the duration of break
    '''
    self.addTime(seconds)


  def destructor(self):
    """ Destroy the pop up break window object and release all resources """
    self.app.onBreakScreen = False
    self.app.timeLapse = time.perf_counter()
    self.app.breakWindow = None
    self.window.destroy()


if __name__ == '__main__':
  faceTimeAllowed = int(input("Enter how many seconds your face has to be shown:"))
  restTime = int(input("Enter how many seconds your rest time should be:"))
  faceDetectionReset = int(input("Enter how many seconds the app doesn't see a face before resetting the clock:"))
  app = Application(faceTimeAllowed, restTime, faceDetectionReset)
  app.root.iconify() # minimized main window
  frame = Frame(app.root, width = 350, height = 350)
  frame.pack()
  frame.place(anchor='center', relx=0.5, rely=0.5)
  img = ImageTk.PhotoImage(Image.open("Rest_Eyes.jpg"))
  label = Label(frame, image = img)
  label.pack()
  app.root.mainloop()
