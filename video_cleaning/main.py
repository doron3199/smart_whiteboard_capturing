import numpy as np
import cv2
from PIL import ImageGrab
from video_cleaning.transform import four_point_transform
from imutils.video import FPS
from video_cleaning.clean import clean


def click_and_crop(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        if len(points) < 4:
            points.append((x, y))


OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}
# grab the appropriate object tracker using our dictionary of
# OpenCV object tracker objects
track_name = "csrt"

tracker = OPENCV_OBJECT_TRACKERS[track_name]()
initBB = None
directions = {"l": (0, 0, 960, 1080), "r": (960, 0, 1920, 1080), "u": (0, 0, 1920, 540), "d": (0, 540, 1920, 1080)}
side = input("pick side ")[0].lower()
cv2.namedWindow("Board", cv2.WINDOW_NORMAL)
is_edges = False
points = []
prev = 0
fps = None
fgbg = cv2.createBackgroundSubtractorKNN()
while True:
    image = ImageGrab.grab(directions[side])
    image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB)
    if not is_edges:

        cv2.setMouseCallback('Board', click_and_crop)
        for p in points:
            cv2.circle(image, p, 5, (0, 0, 255), 15)

        cv2.imshow('Board', image)
        key = cv2.waitKey(1) & 0xFF
        # if the 'r' key is pressed, reset the cropping region
        if key == ord("r"):
            points = []
        # if the 'c' key is pressed, break from the loop
        elif key == ord("c"):
            is_edges = True
    else:
        warped = four_point_transform(image, np.array(points, dtype="float32"))

        (H, W) = warped.shape[:2]

        # check to see if we are currently tracking an object
        if initBB is not None:
            # grab the new bounding box coordinates of the object
            (success, box) = tracker.update(warped)
            # check to see if the tracking was a success
            if success:
                (x, y, w, h) = [int(v) for v in box]
                p = (x + w) // 2
                e = x + w
                # cv2.rectangle(warped, (x, y), (x + w, y + h),
                #               (0, 255, 0), 2)
                print("p:", p)
            # update the FPS counter
            fps.update()
            fps.stop()
            # initialize the set of information we'll be displaying on
            # the frame
            info = [
                ("Tracker", track_name),
                ("Success", "Yes" if success else "No"),
                ("FPS", "{:.2f}".format(fps.fps())),
            ]
            # loop over the info tuples and draw them on our frame
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(warped, text, (10, H - ((i * 20) + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            num_of_parts = round((W/H))*2
            if num_of_parts < 2:
                num_of_parts = 2
            parts = []
            dist = np.linspace(0, W, num_of_parts, endpoint=False)
            for i in range(num_of_parts):
                if i == num_of_parts - 1:
                    parts.append(warped[:, int(dist[i]):])
                else:
                    parts.append(warped[:, int(dist[i]):int(dist[i+1])-1])
            # if prev is 0:
            #     prev = warped.copy()
            # if initBB is not None and success:
            #     for i in range(len(dist)):
            #         if dist[i] < p and dist[i+1] > p:

            prev = np.concatenate(tuple(parts), axis=1)
            fgmask = fgbg.apply(prev)

        if prev is 0:
            cv2.imshow("Board", warped)
        else:
            cv2.imshow("ssoard", fgmask)
            cv2.imshow("Board", prev)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            # select the bounding box of the object we want to track (make
            # sure you press ENTER or SPACE after selecting the ROI)
            initBB = cv2.selectROI("Board", warped, fromCenter=False,
                                   showCrosshair=True)
            # start OpenCV object tracker using the supplied bounding box
            # coordinates, then start the FPS throughput estimator as well
            tracker.init(warped, initBB)
            fps = FPS().start()
        # if the 'c' key is pressed, break from the loop
        if key == ord("c"):
            break

cv2.destroyAllWindows()
