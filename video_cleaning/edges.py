import cv2 as cv


def choose_edges(image):
    points = []

    def click_and_crop(event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONUP:
            if len(points) < 4:
                points.append((x, y))
                cv.circle(image, (x, y), 5, (0, 0, 255), 15)
                cv.imshow('select edges', image)

    # clone it, and setup the mouse callback function
    clone = image.copy()
    cv.namedWindow('select edges', cv.WINDOW_NORMAL)
    cv.setMouseCallback('select edges', click_and_crop)
    # keep looping until the 'q' key is pressed

        # display the image and wait for a keypress
    cv.imshow('select edges', image)
    key = cv.waitKey(1) & 0xFF
    # if the 'r' key is pressed, reset the cropping region
    if key == ord("r"):
        points = []
        image = clone.copy()
    # if the 'c' key is pressed, break from the loop
    elif key == ord("c"):
        cv.destroyWindow('select edges')
        return points
