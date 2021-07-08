# PreferredWavePlayer
This is my preferential player when I need to play just .wav files in a project.

It is multi-platform and has no dependencies, other than what comes with Windows 10, the standard Linux kernel, MacOS 10.5 or later, and the Python Standard Library.

It contains enough functions to be useful, but not too many to be confusing, and I tried to keep the syntax and implementation
super-simple and human readable.

When I built this module, I considered many factors that were important to me, 
like maintenance of code, ease of use, reliability and so forth.  I used these methods below as they seem to be the best 
choices, considering the above factors.

In a nutshell:

#### -Windows 10 uses the Windows winmm.dll Multimedia API to play sounds and the Python Winsound module to loop background sounds.  
(Windows will only loop one background sound at a time.)
#### -Linux uses ALSA which is part of the Linux kernel since version 2.6 and later
#### -MacOS uses the afplay module which is present OS X 10.5 and later

To use the module simply add:
```
from preferredwave.preferredwaveplayer import *
```
and this will import all its functions.

The module essentially contains 3 functions for playing .wav files:
```
playwave("yourfilename.wav")

stopwave(yourSound)

getIsPlaying(yourSound)
```
And a few more for looping .wav files:

```
backgroundSong = loopwave("yourfilename.wav")

and

stoploop(backgroundSong)
```

Here are some examples on how to use them.
Note that with 'playwave' it can be used as a standalone function, but if you want to stop the file from playing,
you will have to use the return value of playwave.  Read a little further and the examples hopefully will make sense.

### Examples:

#### To play a wave file:
```
playwave("coolhipstersong.wav") #-> this plays the wav file

mysong=playwave("coolhipstersong.wav") #-> this plays the wav file and also returns a reference to the song.
```

#### To stop your song:
```
stopwave(mysong) # -> this stops mysong, which you created in the line above
```

#### To find out if your wave file is playing:

```
isitplaying = getIsPlaying(mysong) -> sets a variable to True or False, depending on if process is running

print(getIsPlaying(mysong)) -> prints True or False depending on if process is running

if getIsPlaying(mysong)==True:
    print("Yes, your song is playing")
else:
    print("Your song is not playing")
```

#### To play a wave file synchronously:
```
playwave("coolhipsong.wav",1) #-> this plays the wav file synchronously

or

playwave("coolhipsong.wav",block=True)


* Note: commands below will work, but you cannot stop the song, because your progam will be blocked until the song is done playing

mysong=playwave("coolhipstersong.wav",1) #-> this plays the wav file synchronously and also returns the song subprocess

or 

mysong=playwave("coolhipstersong.wav",block=True) #-> this plays the wav file synchronously and also returns the song subprocess


```
#### To play a wave file in a continous loop:

```
myloop=loopwave("mybackgroundsong.wav")

```
This starts a background loop playing, but also returns a reference to the background process so it can be stopped.
#### To stop the continuous loop from playing:

```
stoploop(myloop)

```

### Discussion - A little more about why I picked these methods:

### Windows 10
Windows10 functions use the winmm.dll Windows Multimedia API calls using c function calls to play sounds.

See references:

“Programming Windows: the Definitive Guide to the WIN32 API, Chapter 22 Sound and Music Section III Advanced Topics ‘The MCI Command String Approach.’” Programming Windows: the Definitive Guide to the WIN32 API, by Charles Petzold, Microsoft Press, 1999. 
    
https://github.com/michaelgundlach/mp3play

& https://github.com/TaylorSMarks/playsound/blob/master/playsound.py

#### Playing Sounds in Windows:
This method of playing sounds allows for multiple simultaneous sounds, works well and has been used successfully in seveal projects.  As long as this dynamically linked library is bundled with the current version of Windows, I plan to use this as the preferred method of playing sounds unless there is a compelling reason to change.  In this case I am using the reasoning "If it's not broke, don't fix it.".  Another advantage is it plays mp3s and other formats as well, not just .wav files.  It works well, is stable, loads and executes quickly, and has essentially never caused me any problems.  

The Python Winsound module on the other hand, is at least to me a bit odd in its syntax, less intuitive, and only uses wave files.  You basically can't play async more than one wave at a time.  This is severely limiting, so I don't prefer it for playing sounds.

Calling the winsound.PlaySound module through the OS system works, but not does not execute as quickly.  This is not a bad approach however for background sounds.

#### Looping Sounds in Windows:

In this case, I do use the Python winsound module to loop sounds.  This is easy to implement, it does not conflict with sounds produced with the winmm.dll library, and starts and stops quickly.  It is however, limited to just one background at a time, but considering alternatives, this seems like the best choice (see below if you really need more than one background loop at at time).

##### Problems using winmm.dll to loop sounds.

It is possible to use windmm.dll for looping also with multiprocessing.  However, this requires very careful consideration when implementing the code in a GUI, as the multiprocessing module behaves differently under the Windows OS.

For example, I have used the winmm.dll sound playing function to loop sounds and I used the Python multiprocessing module to achieve this.  I started off by making a looping process with a while loop.  I started and stopped the process using the multiprocessing module.  I used process.terminate() to stop the loop.  This did work, but the problem with this method is you have to be really careful about how you are implementing the process in a user interface.  If you are using tkinter for example, when you start the process, the process will inheret its parent's resources.  Sometimes for example, a whole new root window will appear when a process is launched.  This can be worked around, but it requires structuring your GUI in a very specific way, so as to initialize the GUI outside of the main process (eg.  `if __name__ ==__'main'__: put your GUI here`, etc).  So I don't think this is a good solution - forcing someone only to design a GUI in a certain way just to use your sound module.  So I have avoided this approach.  Really the main issue is that multiprocessing is not actually implemented exactly in all 3 operating systems (Windows, MacOS, and Linux.)

##### Using OS System calls in Windows to loop sounds.

You can loop sounds by using OS system calls in the style of using command line instructions.

See https://pypi.org/project/oswaveplayer/ for an example.

This is not a bad approach, but there is a little delay  with the sound launch using the command line version.  This may not be a big issue for you when playing background music.  If you really need multiple background sounds at once, your best bet would be to use another module or to add the oswaveplayer to your project with the import statement:
           
           from oswave import oswaveplayer 
           then use:

           backgroundSong = oswaveplayer.loopwave("yourfilename")

           and

           oswaveplayer.stoploop(backgroundSong)

This is not a bad approach, but due to the perceptible delay in playing the sound, it is not preferred to me.  You can also, look over the source code to see how to launch sounds using this approach, as it is very basic.

#### You may not need a looping function to loop sounds:
##### A note on looping sounds in general:
If you using a game loop in game building, you don't actually need to use these looping functions at all (although it may be a little more convenient).  You may notice that these modules all contain a function called getIsPlaying(yoursound).  You can simply implement a check in your game loop to see if yoursong is playing.  If it is, don't do anything.  If it is not, play the sound with `yoursound=playwave("yourfilename.wav")`.  Maybe check every 10 frames or something like that.

### Notes about using this module as a replacement in the playsound module:

Additionally, I included an alias to the function named 'playsound', and if used, the default block will be true, or synchronous play.  This way, the
module can be used in place of the playsound module (https://github.com/TaylorSMarks/playsound/blob/master/playsound.py) with the same syntax.  If the playsound module does not work for you, as it is no longer maintained, you can load this module and use the import statement below for .wav files only.

Use:
```
from preferredwave.preferredwaveplayer import playsound

```
for backwards compatibility with the playsound module - .wav files only.
