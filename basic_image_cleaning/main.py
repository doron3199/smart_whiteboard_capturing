import cv2 as cv
import numpy as np
from basic_image_cleaning.transform import four_point_transform
from basic_image_cleaning.clean import clean
from basic_image_cleaning.edges import choose_edges

# read the image
image = cv.imread('assets/wb1.jpg')
# get the point of the corners of the wb and transform them to np array
pts = np.array(choose_edges(image.copy()), dtype="float32")
# image of just the wb
warped = four_point_transform(image, pts)
# image of the clean wb
cleaned = clean(warped)
cv.namedWindow('Board', cv.WINDOW_GUI_NORMAL)

while True:
    # display the image and wait for a keypress
    cv.imshow('Board', cleaned)

    key = cv.waitKey(1) & 0xFF
    # if the 'c' key is pressed, break from the loop
    if key == ord("c"):
        cv.destroyWindow('Board')
        break
