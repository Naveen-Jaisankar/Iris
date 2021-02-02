from __future__ import print_function
import pyttsx3 #pip install pyttsx3
import speech_recognition as sr #pip install speechRecognition
from googlesearch import search
import datetime
import wikipedia #pip install wikipedia
import webbrowser
import os
import smtplib
import wmi
import bluetooth
import platform,socket,re,uuid,json,psutil

from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2

ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=False,
	help="so.prototxt.txt")
ap.add_argument("-m", "--model", required=False,
	help="coco_vgg16_faster_rcnn_final.caffemodel")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
	help="0.2")
args = vars(ap.parse_args())

import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar']

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
# print(voices[1].id)
engine.setProperty('voice', voices[1].id)

def vision():
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
    rectangle_bgr = (255, 255, 255)
    speak("loading model...")
    net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt.txt","MobileNetSSD_deploy.caffemodel" )

    speak("starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(2.0)
    fps = FPS().start()

    while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        frame = vs.read()
        frame = imutils.resize(frame, width=1000)

        # grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
            0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        net.setInput(blob)
        detections = net.forward()
        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > args["confidence"]:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # draw the prediction on the frame
                label = "{}: {:.2f}%".format(CLASSES[idx],
                    confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                    COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, rectangle_bgr, 2)

        # show the output frame
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

        # update the FPS counter
        fps.update()

    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
    cv2.destroyAllWindows()
    vs.stop()

def calendar():
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
   
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
      
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])
    
    speak("what is the Description, sir")   
    des = takeCommand()
    speak("Location")
    loc = takeCommand()
    
    event = {
        'summary': des,
        'location': loc,
        'description': 'A chance to hear more about Google\'s developer products.',
        'start': {
            'dateTime': '2020-01-28T09:00:00-07:00',
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': '2020-01-28T17:00:00-09:00',
            'timeZone': 'Asia/Kolkata',
        },
        }

    event = service.events().insert(calendarId='primary', body=event).execute()


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning!")

    elif hour>=12 and hour<18:
        speak("Good Afternoon!")   

    else:
        speak("Good Evening!")  

    speak("I am Iris Sir. Please tell me how may I help you")   

def systeminfo():
    hostname = socket.gethostname()
    platform1=platform.system()
    platformrelease=platform.release()
    hostname=socket.gethostname()
    address=socket.gethostbyname(socket.gethostname())
    processor=platform.processor()
    ram=str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"        
    speak(f"Hello sir , This is Iris. My host system name is {hostname} .I work on {platform1} {platformrelease} operating system , I have {ram} of memory capacity and {processor} processor. My IP address is {address}")   

def takeCommand():
    #It takes microphone input from the user and returns string output

    r = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")    
        req = r.recognize_google(audio, language='en-in')
        print(f"User said: {req}\n")

    except Exception as e:
        # print(e)    
        print("Say that again please...")  
        return "None"
    return req

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('naveen.j.2017.ece@rajalakshmi.edu.in', 'Snevijiraghul')
    server.sendmail('naveen.j.2017.ece@rajalakshmi.edu.in', to, content)
    server.close()

if __name__ == "__main__":
    wishMe()
    while True:
    # if 1:
        req = takeCommand().lower()

        # Logic for executing tasks based on req
        if 'who is' in req:
            speak('Searching Wikipedia...')
            req = req.replace("wikipedia", "")
            results = wikipedia.summary(req, sentences=2)
            speak("According to Wikipedia")
            print(results)
            speak(results)

        elif 'your vision'  in req:
            vision()

        elif 'open youtube' in req:
            webbrowser.open("https://youtube.com")

        elif 'are you listening' in req:
            speak('yes sir, I am listening')    

        elif 'battery percentage' in req:
            c = wmi.WMI ()
            for battery in c.Win32_Battery ():
                 per = battery.EstimatedChargeRemaining
                 speak(f"your internal battery percentage is {per}")
        
        elif 'about yourself' in req:
             systeminfo()


        elif 'open google' in req:
            webbrowser.open("https://google.com/")
            speak('What should i search, sir')
            query= takeCommand()   
            for j in search(query, tld="co.in", num=10, stop=1, pause=2): 
                webbrowser.open(j) 


        elif 'open stackoverflow' in req:
            webbrowser.open("https://stackoverflow.com")       

        elif 'github' in req:
            if 'my' in req:
                webbrowser.open("https://github.com/Naveen-Jaisankar")       
            else:
                webbrowser.open("https://github.com/")    
        
        elif 'play music' in req:
            music_dir = 'D:\\Non Critical\\songs\\Favorite Songs2'
            songs = os.listdir(music_dir)
            print(songs)    
            os.startfile(os.path.join(music_dir, songs[0]))

        elif 'the time' in req:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")    
            speak(f"Sir, the time is {strTime}")

        elif 'open code' in req:
            codePath = "C:\\Users\\Haris\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
            os.startfile(codePath)

        elif 'available bluetooth' in req:
            nearby_devices = bluetooth.discover_devices(lookup_names=True)
            speak(f"I found {nearby_devices} nearby devices, sir")    

        elif 'send email' in req:
            try:
                speak("What should I say?")
                content = takeCommand()
                to = "harryyourEmail@gmail.com"    
                sendEmail(to, content)
                speak("Email has been sent!")
            except Exception as e:
                print(e)
                speak("Sorry my friend harry bhai. I am not able to send this email")    

