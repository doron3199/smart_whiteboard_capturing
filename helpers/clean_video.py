import numpy as np
import cv2
from PIL import ImageGrab
from helpers.transform import four_point_transform
from helpers.clean_image import clean
import time
import threading


class Timer:
    def __init__(self):
        self.start_time = time.time()

    def get_time(self):
        return time.time() - self.start_time

    def reset(self):
        self.start_time = time.time()


class CleanThread(threading.Thread):

    def __init__(self, screen_or_camera, points):
        threading.Thread.__init__(self)
        self.name = "cleanThread"
        self.screen_or_camera = screen_or_camera
        self.points = points
        self.final_image = []
        self.loop = True
        self.clean_images = []

    def run(self):
        cv2.destroyAllWindows()
        time.sleep(2)
        fgbg = cv2.createBackgroundSubtractorKNN()
        fgbg.setHistory(50)
        timer = Timer()
        num_of_parts = 10
        final_points = self.points

        if self.screen_or_camera == 'camera':
            capture = cv2.VideoCapture(0)

        while self.loop:
            was_points_changed = False
            # points will be update only in the start of the loop
            if final_points != self.points:
                time.sleep(2)
                cv2.destroyAllWindows()
                final_points = self.points
                timer.reset()
                self.clean_images.append(clean(self.final_image))
                was_points_changed = True

            if self.screen_or_camera == 'screen':
                image = ImageGrab.grab()
                # that image is in BGR so we need to make it RGB
                image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
            else:
                ret, image = capture.read()

            # get only the whiteboard (or full screen image)
            if len(final_points) < 4:
                warped = image
            else:
                warped = four_point_transform(image, np.array(final_points, dtype="float32"))

            if not len(self.final_image) or was_points_changed:
                self.final_image = warped.copy()
            (H, W) = warped.shape[:2]
            parts = []
            # return an even distance number by the number of parts from zero to the image width
            dist = np.linspace(0, W, num_of_parts, dtype=int)
            # background subtraction
            fgmask = fgbg.apply(warped)

            # detect in which part of the background there is movement
            # parts will be a bool list, True if there is False if not
            for i in range(num_of_parts - 1):
                parts.append(not (np.average(fgmask[:, dist[i]:dist[i + 1]])))

            # for every part of the image, we add the warped to update the image in the new background parts
            # and we add final_image to keep the previous background
            for i in range(num_of_parts - 1):
                self.final_image[:, dist[i]:dist[i + 1]] = np.multiply(
                    warped[:, dist[i]:dist[i + 1]], parts[i]) + np.multiply(
                    self.final_image[:, dist[i]:dist[i + 1]], not parts[i])

            if timer.get_time() > 60:
                timer.reset()
                self.clean_images.append(clean(self.final_image))

        self.clean_images.append(clean(self.final_image))

