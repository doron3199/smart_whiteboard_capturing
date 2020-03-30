import numpy as np
import cv2  # pip install python-opencv?
from PIL import ImageGrab  # pip install pillow
from video_cleaning.transform import four_point_transform
import imutils
from video_cleaning.clean import clean
import os
import time


def main():
    class Timer:
        def __init__(self):
            self.start_time = time.time()

        def get_time(self):
            return time.time() - self.start_time

        def reset(self):
            self.start_time = time.time()

    # take a full screen shot to get the screen size
    demo_screen = ImageGrab.grab()
    demo_screen = np.array(demo_screen)
    sc_h, sc_w = demo_screen.shape[:2]
    directions = {"l": (0, 0, sc_w // 2, sc_h), "r": (sc_w // 2, 0, sc_w, sc_h), "u": (0, 0, sc_w, sc_h // 2),
                  "d": (0, sc_h // 2, sc_w, sc_h)}
    side = input("pick side ")[0].lower()
    cv2.namedWindow("Board", cv2.WINDOW_NORMAL)
    cv2.namedWindow("clean", cv2.WINDOW_NORMAL)

    is_edges = False
    points = []
    fgbg = cv2.createBackgroundSubtractorKNN()
    fgbg.setDetectShadows(False)
    fgbg.setHistory(250)
    final = []
    path = input('directory name: ')
    img_num = 0
    cleaned = 0
    timer = Timer()

    def click_and_crop(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONUP:
            if len(points) < 4:
                points.append((x, y))

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
                print('please press b to take a clean boardshot \nor u to save regular boardshot')
                is_edges = True
                timer.reset()
            elif key == ord("c"):
                break
        else:
            # get only the whiteboard
            warped = four_point_transform(image, np.array(points, dtype="float32"))
            original = warped.copy()
            warped = imutils.resize(warped, width=500)
            (H, W) = warped.shape[:2]
            num_of_parts = 10  # can be changed
            parts = []
            # return an even distance number by the number of parts from zero to the image width
            dist = np.linspace(0, W, num_of_parts, endpoint=False)
            original_dist, original_step = np.linspace(0, original.shape[1], num_of_parts, endpoint=False, retstep=True)
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
                        final.append(original[:, int(original_dist[i]):])
                    else:
                        final.append(original[:, int(original_dist[i]):int(original_dist[i + 1]) - 1])
            # if the average of the part is zero its mean that there was no movement
            # a while so we can update the board,
            for p in range(len(parts)):
                r = round(np.average(parts[p]), 2)
                if r == 0.0:
                    final[p] = original[:, int(original_step) * p: int(original_step) * (p + 1)]

            # build and display the whiteboard
            final_image = np.concatenate(tuple(final), axis=1)
            cv2.imshow("Board", final_image)

            if timer.get_time() > 60:
                timer.reset()
                cleaned = clean(final_image)
                cv2.imshow("clean", cleaned)

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
                else:
                    print('please press b to take a clean boardshot \nor u to save regular boardshot')
            elif key == ord("u"):  # save without cleaning
                if not os.path.exists(path):
                    os.makedirs(path)
                cv2.imwrite(path + r'\{}.jpg'.format(img_num), final_image)
                print('Image saved to', path + r'\{}.jpg'.format(img_num))
                img_num += 1

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
