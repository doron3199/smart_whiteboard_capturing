import numpy as np
import cv2  # pip install python-opencv?
from PIL import ImageGrab  # pip install pillow
from video_cleaning.transform import four_point_transform
import imutils
from video_cleaning.clean import clean
import os


def click_and_crop(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        if len(points) < 4:
            points.append((x, y))


# TODO: find the screen size, this is based on 1920 X 1080 screen
directions = {"l": (0, 0, 960, 1080), "r": (960, 0, 1920, 1080), "u": (0, 0, 1920, 540), "d": (0, 540, 1920, 1080)}
side = input("pick side ")[0].lower()
cv2.namedWindow("Board", cv2.WINDOW_NORMAL)
cv2.namedWindow("clean", cv2.WINDOW_NORMAL)

is_edges = False
points = []
fgbg = cv2.createBackgroundSubtractorKNN()
fgbg.setDetectShadows(False)
fgbg.setHistory(250)
final = []
blank = 0
path = input('directory name: ')
img_num = 0
cleaned = 0

while True:
    # screen shot of some area
    image = ImageGrab.grab(directions[side])
    # that image is in BGR so we need to make it RGB
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)

    # if we didn't choose edges
    if not is_edges:
        # detect mouse stuff
        cv2.setMouseCallback('Board', click_and_crop)
        # circle the corners
        for p in points:
            cv2.circle(image, p, 5, (0, 0, 255), 15)

        cv2.imshow('Board', image)
        key = cv2.waitKey(1) & 0xFF
        # if the 'r' key is pressed, reset the cropping region
        if key == ord("r"):
            points = []
        # if the 'b' key is pressed, break from the loop
        elif key == ord("b"):
            is_edges = True
    else:
        # get only the whiteboard
        warped = four_point_transform(image, np.array(points, dtype="float32"))
        # TODO this resize is for faster computing, we need to show the original image as in the end
        warped = imutils.resize(warped, width=500)
        board = warped.copy()
        (H, W) = warped.shape[:2]
        num_of_parts = 10  # can be changed
        parts = []
        # return an even distance number by the number of parts from zero to the image width
        dist = np.linspace(0, W, num_of_parts, endpoint=False)
        # background subtraction
        fgmask = fgbg.apply(warped)

        # split the background to the its parts
        for i in range(num_of_parts):
            if i == num_of_parts - 1:
                parts.append(fgmask[:, int(dist[i]):])
            else:
                parts.append(fgmask[:, int(dist[i]):int(dist[i + 1]) - 1])

        # create the final image parts
        if len(final) == 0:
            for i in range(num_of_parts):
                if i == num_of_parts - 1:
                    final.append(board[:, int(dist[i]):])
                else:
                    final.append(board[:, int(dist[i]):int(dist[i + 1]) - 1])
        # if the average of the part is zero its mean that there was no movement
        # a while so we can update the board,
        for p in range(len(parts)):
            r = round(np.average(parts[p]), 2)
            if r == 0.0:
                final[p] = board[:, 50 * p:50 * (p + 1)]

        # build and display the whiteboard
        final_image = np.concatenate(tuple(final), axis=1)
        cv2.imshow("Board", final_image)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):
            break
        elif key == ord("b"):  # show the cleaned whiteboard
            cleaned = clean(final_image)
            cv2.imshow("clean", cleaned)
        elif key == ord("s"):  # save the cleaned whiteboard
            if cleaned is not 0:
                if not os.path.exists(path):
                    os.makedirs(path)
                cv2.imwrite(path + r'\{}.jpg'.format(img_num), cleaned)
                print('Image saved to', path + r'\{}.jpg'.format(img_num))
                img_num += 1
                cleaned = 0
            elif key == ord("u"):  # save without cleaning
                if not os.path.exists(path):
                    os.makedirs(path)
                cv2.imwrite(path + r'\{}.jpg'.format(img_num), final_image)
                print('Image saved to', path + r'\{}.jpg'.format(img_num))
                img_num += 1
            else:
                print('please press b to take a clean boardshot \nor u to save regular boardshot')

cv2.destroyAllWindows()
