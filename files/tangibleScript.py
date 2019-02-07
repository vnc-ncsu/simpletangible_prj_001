import RPi.GPIO as GPIO
import time, pygame, os, subprocess
from time import sleep
from subprocess import Popen
import pygame.display

#Set your GPIO pins here.
GPIOPins = [17, 27, 22]

#Set your video paths here.
videoFolderPath = "/home/pi/Videos/ShapeVideos/"
baseVideoName = "base.mp4"
videoNames = ["circle.mp4", "square.mp4", "hex.mp4"]

#Sets up your specified GPIO pins to listen for input.
GPIO.setmode(GPIO.BCM)
for pin in GPIOPins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#Initializes Pygame and turns on fullscreen.
pygame.display.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode([0,0], pygame.FULLSCREEN)
screen.fill((255, 255, 255))
pygame.display.flip()

#Initialize some variables which will be used in the main loop.
readArray = []
bufferArray = []
stateArray = []
lastStateArray = []
for pin in GPIOPins:
    readArray.append(False)
    bufferArray.append(1)
    stateArray.append(False)
    lastStateArray.append(False)

#Defining some functions which will trigger our video playback.
#We'll use these functions down in the main loop.
def playVideo(videoID):    #Plays a video.
    if videoID == 0:
        Popen("omxplayer --no-osd --loop " + videoFolderPath + baseVideoName, shell=True)
    else:
        Popen("omxplayer --no-osd --loop " + videoFolderPath + videoNames[videoID - 1], shell=True)
    
def stopVideo():        #General-purpose function which will stop any video being currently played.
    os.system('killall omxplayer.bin')

def checkForReplace(stateArray):
    for idx,item in enumerate(stateArray):
        if item:
            return idx + 1
    return 0

#Starts out the code by playing the base video.
videoState = 0
playVideo(videoState)

#Main loop. This code will run once every tenth of a second.
running = True;
while running:
    
    #Receive the raw input from the GPIO ports.
    for idx,item in enumerate(GPIOPins):
        readArray[idx] = not GPIO.input(item)
        #Buffering.
        if readArray[idx]:
            if bufferArray[idx] < 10:
                bufferArray[idx] += 1
        else:
            if bufferArray[idx] > 1:
                bufferArray[idx] -= 1
        #Set state.
        stateArray[idx] = bufferArray[idx] > 5
    
    #Check last states against current states for triggers.
    for idx,item in enumerate(stateArray):
        if item:
            if not lastStateArray[idx]:
                stopVideo()
                videoState = idx + 1
                playVideo(videoState)
        else:
            if lastStateArray[idx]:
                if videoState == idx + 1:
                    stopVideo()
                    videoState = checkForReplace(stateArray)
                    playVideo(videoState)
    
    #Set last states for reference during the next loop.
    for idx,item in enumerate(stateArray):
        lastStateArray[idx] = item
        
    #Listen for escape key to terminate this loop and end the program.
    for event in pygame.event.get():
         if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False;
    
    #Wait a tenth of a second.
    sleep(.1)

#If you've gotten to this point, you've hit the Escape key and terminated the loop.
#This just stops playing the current video and ties up some loose ends.
stopVideo()
pygame.quit()
GPIO.cleanup()
os.system('reset')