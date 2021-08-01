#   Gary Davenport functions 7/9/2021
#
#   Plays wav files using the methods I typically use to play waves.
#   Basically, I consider maintenance of code, ease of use, reliability
#   and so forth and use these methods below as they seem to be the best 
#   choices, considering the above factors.  See the README.md file 
#   at the project site for more on why I've chosen these methods.
#   
#   This module has no dependencies, other than what comes with Windows 10, 
#       the standard Linux kernel, MacOS 10.5 or later, and the 
#       Python Standard Library.
#      
#   Windows10 functions use the winmm.dll Windows Multimedia API calls 
#       using c function calls to play sounds.
#
#       See references:
#       “Programming Windows: the Definitive Guide to the WIN32 API, 
#           Chapter 22 Sound and Music Section III Advanced Topics 
#           ‘The MCI Command String Approach.’”
#           Programming Windows: the Definitive Guide to the WIN32 API, 
#           by Charles Petzold, Microsoft Press, 1999. 
#       https://github.com/michaelgundlach/mp3play
#       & https://github.com/TaylorSMarks/playsound/blob/master/playsound.py
#       
#   Linux uses ALSA which is part of the Linux kernel since version 2.6 and later
#   MacOS uses the afplay module which is present OS X 10.5 and later
#   

from random import random
from platform import system
import subprocess
from subprocess import Popen, PIPE
import os
from threading import Thread
from time import sleep
import sndhdr

if system()=="Windows":
    from ctypes import c_buffer, windll
    from sys import getfilesystemencoding
    from threading import Thread
    from time import sleep

# This module creates a single sound with winmm.dll API and returns the alias to the sound
class WinMMSoundPlayer:
    def __init__(self):
        self.isSongPlaying=False
        self.sync=False
        self.P=None
        self.fileName=""
        self.isSongPlaying=False
        self.alias=""
        self.loopAlias=""
        self.aliasList=[]
        
    # typical process for using winmm.dll
    def _processWindowsCommand(self,commmandString):
        #print(commmandString)
        buf = c_buffer(255)
        command = commmandString.encode(getfilesystemencoding())
        windll.winmm.mciSendStringA(command, buf, 254, 0)
        return buf.value

    def _collectGarbarge(self):
        #
        #   Garbage Collection
        #
        #   go through alias list
        #       if song not playing
        #           close it
        #           remove it from list
        #  
        #aliasListLength=len(self.aliasList)
        #for i in range(aliasListLength):
        #    if self.getIsPlaying(self.aliasList[i])==False:

        #make a list of sounds that are no longer playing
        removalList=[]
        for i in range(len(self.aliasList)):
            if self.getIsPlaying(self.aliasList[i])==False:
                #print("adding",self.aliasList[i],"to garbage collector removal list.")
                removalList.append(i)

        # issues stop(not necessary) and close commands to that list
        for i in range(len(removalList)-1,-1,-1):
            #print("closing",self.aliasList[removalList[i]],"at index",removalList[i])#<-----unprint
            self.stopsound(self.aliasList[removalList[i]])
            del self.aliasList[removalList[i]]

    # make an alias, play the song.
    # For Sync play - use the wait flag, then stop and close alias.
    # For Async - unable to close.

    def playwave(self,fileName, block=False):

        self._collectGarbarge()

        self.fileName=fileName
        #make an alias
        self.alias = 'soundplay_' + str(random())
        #print("adding ", self.alias)# <------- unprint
        self.aliasList.append(self.alias)

        str1="open \"" + os.path.abspath(self.fileName) + "\""+" alias "+self.alias
        self._processWindowsCommand(str1)
        
        #use the wait feature to block or not block when constructing mciSendString command
        if block==False:
            str1="play "+self.alias
            #play the sound
            self._processWindowsCommand(str1)
        else:
            #construct mciSendString command to wait i.e. blocking
            str1="play "+self.alias +" wait"
            #play the sound (blocking)
            self._processWindowsCommand(str1)
            #stop and close the sound after done
            str1="stop "+self.alias
            self._processWindowsCommand(str1)
            str1="close "+self.alias
            self._processWindowsCommand(str1)

        #return the alias of the sound
        return self.alias

    # this function uses the mci/windows api with a repeat call to loop sound
    def loopsound(self,fileName):
        self._collectGarbarge()
        self.loopAlias = 'loopalias_' + str(random())
        #print("looper alias",self.loopAlias) #<-------unprint
        self.aliasList.append(self.loopAlias)
        str1="open \"" + os.path.abspath(fileName) + "\" type mpegvideo alias " + self.loopAlias
        self._processWindowsCommand(str1)
        str1="play " + self.loopAlias + " repeat"
        self._processWindowsCommand(str1)
        return self.loopAlias

    # issue stop and close commands using the sound's alias
    def stopsound(self,sound):
        #print("------------------------")
        try:    
            str1="stop "+sound
            self._processWindowsCommand(str1)
            str1="close "+sound
            self._processWindowsCommand(str1)
        except:
            pass

    # return True or False if song alias 'status' is 'playing'
    def getIsPlaying(self,song):
        try:
            str1="status "+song+" mode"
            myvalue=self._processWindowsCommand(str1)
            if myvalue==b"playing":
                self.isSongPlaying=True
            else:
                self.isSongPlaying=False
        except:
            self.isSongPlaying=False
        return self.isSongPlaying

class MusicLooper:
    def __init__(self, fileName):
        self.fileName = fileName
        self.playing = False
        self.songProcess = None

    def _playwave(self):
        self.songProcess=playwave(self.fileName)

    def _playloop(self):
        while self.playing==True:
            self.songProcess=playwave(self.fileName)
            sleep(self._getWavDurationFromFile())

    # start looping a wave
    def startMusicLoopWave(self):
        if self.playing==True: # don't allow more than one background loop per instance of MusicLooper
            print("Already playing, stop before starting new.")
            return
        else:
            self.playing=True
            t = Thread(target=self._playloop)
            t.setDaemon(True)
            t.start()

    # stop looping a wave
    def stopMusicLoop(self):
        if self.playing==False:
            print(str(self.songProcess)+" already stopped, play before trying to stop.")
            return
        else:
            self.playing=False  # set playing to False, which stops loop
            stopwave(self.songProcess) #issue command to stop the current wave file playing also, so song does not finish out

    # get length of wave file in seconds
    def _getWavDurationFromFile(self):
        frames = sndhdr.what(self.fileName)[3]
        rate = sndhdr.what(self.fileName)[1]
        duration = float(frames)/rate
        return duration

    def getSongProcess(self):
        return(self.songProcess)

    def getPlaying(self):
        return(self.playing)

#########################################################################
# These function definitions are intended to be used by the end user,   #
# but an instance of the class players above can be used also.          #
#########################################################################       

# plays a wave file and also returns the alias of the sound being played, async method is default
# 3 separate methods allows for the Windows module to initialize an instance of 'WinMMSoundPlayer' class
# this way only one windows type player allows to keep track of all aliases made and garbage can be collected
# when songs have finished playing

def _playwaveWindows(fileName, block=False):
    song=windowsPlayer.playwave(fileName, block)
    return(song) 

def _playwaveLinux(fileName, block=False):
    command = "exec aplay --quiet " + os.path.abspath(fileName)
    if block==True: P = subprocess.Popen(command, universal_newlines=True, shell=True,stdout=PIPE, stderr=PIPE).communicate()
    else: P = subprocess.Popen(command, universal_newlines=True, shell=True,stdout=PIPE, stderr=PIPE)
    return P

def _playwaveMacOs(fileName, block=False):
    command = "exec afplay \'" + os.path.abspath(fileName)+"\'"
    if block==True: P = subprocess.Popen(command, universal_newlines=True, shell=True,stdout=PIPE, stderr=PIPE).communicate()
    else: P = subprocess.Popen(command, universal_newlines=True, shell=True,stdout=PIPE, stderr=PIPE)
    return P

# stops the wave being played, 'process' in the case of windows is actually the alias to the song
# otherwise process is a process in other operating systems.
def stopwave(process):
    if process is not None:
        try:
            if process is not None:
                if system()=="Windows":
                    windowsPlayer.stopsound(process)          
                else: process.terminate()
        except:
            pass
            #print("process is not playing")
    else:
        pass
        #print("process ", str(process), " not playing")

# pass the process or alias(windows) to the song and return True or False if it is playing
def getIsPlaying(process):
    if system()=="Windows":
        return windowsPlayer.getIsPlaying(process)
    isSongPlaying=False
    if process is not None:
        try: return(process.poll() is None)
        except: pass
    return isSongPlaying

# This just references the command 'playsound' to 'playwave' with default to block/sync behaviour in case you want to use this in place
# of the playsound module, which last I checked was not being maintained.
def playsound(fileName, block=True):
    return(playwave(fileName, block))

# this function will loop a wave file and return an instance of a MusicLooper object that loops music,
# or in the case of Windows it returns an object containing variables used to track if the song is playing
def loopwave(fileName):
    if system()=="Windows":
        return(windowsPlayer.loopsound(fileName))
    else:
        looper=MusicLooper(fileName)
        looper.startMusicLoopWave()
        return(looper)

# pass an instance of a MusicLooper object and stop the loop, in Windows, pass an instance of the customVariableTracker that is keeping
# track of whether or not the song is looping.
def stoploop(looperObject):
    if looperObject is not None:
        if system()=="Windows":
            stopsound(looperObject)
        else:
            looperObject.stopMusicLoop()
    else:
        pass
        #print("looperObject ", str(looperObject), " not playing")

# checks to see if song process is playing, (or if song alias's status is 'playing' in the case of Windows), returns True or False
def getIsLoopPlaying(looperObject):
    if looperObject is not None:
        if system()=="Windows":
            return getIsPlaying(looperObject)
        else:
            return(looperObject.getPlaying())
    else:
        return False

if system() == 'Windows':
    windowsPlayer = WinMMSoundPlayer()
    playwave=windowsPlayer.playwave
    
elif system() == 'Darwin':
    playwave = _playwaveMacOs

else:
    playwave = _playwaveLinux

stopsound=stopwave
