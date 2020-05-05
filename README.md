# Smart Whiteboard Capturing
A software to smart whiteboard record.

The goal is to input a wb video from a class,
and the output will be images of full white board

# Usage
## Prerequisites
Install the packages
- openCV
- pillow
- imutils
- numpy

## Running the program
### Parameters
1. The part of your screen you want to record. Valid options are left, right, up and down.
You can also use the abbreviations l, r, u and d.
2. The directory that the images should be saved to.

### Start the program
On the window with the recorded screen, click on the corners of the whiteboard, then press `c`.
Then click on the lecturer. The screen will reload. After pressing `b`, you will be able to view
the "cleaned" image. Press `s` to save, and `u` to save the original image.

# Resources
- [Microsoft](https://www.microsoft.com/en-us/research/uploads/prod/2016/12/Whiteboard-It.pdf)
- [PyImageSearch](https://www.pyimagesearch.com/)
