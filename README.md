# Smart Whiteboard Capturing
A software to smart whiteboard record.

The goal is to input a video from a class with a whiteboard,
the output will be images of the clean whiteboard with all the stuff
written on it.

# Usage
## Prerequisites
Install the packages
- openCV
- pillow
- kivy
- numpy

# Run the program
It should run if all the libraries are installed.
when the window open, if you have high resolution camera connected it may
take time to load. notice that the camera light will be on even if you choose
screenshot. its a bug and the camera is not recording. if the whiteboard doesn't
look rectangular choose four points. after choosing the options click start and 
a opencv window will be shown. mark the area of the whiteboard in this window. it will
close automatically. then just relax and watch the lecture. return to the program 
when the lecture ends, choose the pics you wand to save, enter the path where
you want to save them and click save.
notice that if you watch the lecture on zoom or something else, take a screenshot
with full screen, and then go to the program. and not side to side like the screenshot,
the resolution will be higher. of course return to see the lecture in full screen after you 
started the program. 

# Resources
- [Microsoft](https://www.microsoft.com/en-us/research/uploads/prod/2016/12/Whiteboard-It.pdf)
