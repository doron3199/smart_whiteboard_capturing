import cv2 as cv
import numpy as np


def filter_images(images):
    """
    this function should get a list of whiteboard images and
    return small list of images with the important matter without
    duplications
    """
    # may change for different whiteboards or resolution
    difference_factor = 1
    averages = []
    # create an array with the average pen strikes
    for image in images:
        # threshold the image so the pen strikes will be uniform
        temp = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
        _, temp = cv.threshold(temp, 240, 255, cv.THRESH_BINARY)
        # bitwise so more strikes = bigger average (background = 0, pen = 1)
        averages.append(np.average(cv.bitwise_not(temp)))
    # convert to averages, find max points
    maxi = []
    is_going_down = False
    # add to maxi all the points that the points after them is different more then the different factor
    # and their are not just the continue of the erasing
    for i in range(len(averages) - 1):
        if averages[i] > averages[i+1] + difference_factor:
            if not is_going_down:
                is_going_down = True
                maxi.append(i)
        else:
            is_going_down = False
    final = []
    # argera returns a tuple, so we choose the x axis
    for i in maxi:
        final.append(images[i])
    # always add the last image
    final.append(images[-1])
    return final

