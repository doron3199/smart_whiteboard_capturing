import cv2 as cv
import numpy as np


def clean(image):
    """clean get an image of a whiteboard and returns an improved colored image"""
    #  get an image of the blank whiteboard
    blank = cv.medianBlur(image, 11)

    # you should read the microsoft research for this lines
    image = np.minimum(image / blank, 1)
    image = np.subtract(0.5, np.multiply(0.5, np.cos(np.power(image, 2.5) * np.pi)))

    # transform the image back to 0 to 255, it transform to 0-1 when it divided.
    image = np.multiply(image, 255)
    image = image.astype(np.uint8)

    return image
