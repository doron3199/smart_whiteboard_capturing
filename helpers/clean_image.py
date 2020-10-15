import cv2 as cv
import numpy as np


def to_blank(image):
    """
    to blank get an image of a whiteboard and returns blank image of the whiteboard
    without the marker stokes used to improve the whiteboard image
    """
    # blank images for the background image
    board = np.zeros(image.shape)
    height, width = image.shape[:2]
    # divide the images to cells
    cell_size = 7
    bv = list(range(0, height, cell_size))
    bv.append(height)
    bh = list(range(0, width, cell_size))
    bh.append(width)
    for i in range(len(bv) - 1):
        for j in range(len(bh) - 1):
            current = image[bv[i]:bv[i + 1], bh[j]:bh[j + 1]]
            # luminance matrix
            lum = np.multiply(0.2126, current[:, :, 0]) + \
                  np.multiply(0.7152, current[:, :, 1]) + \
                  np.multiply(0.0722, current[:, :, 2])

            # reshape lum for the argsoft, just flatten it to a matrix
            lum = np.reshape(lum.flatten(), (len(lum.flatten()), 1))
            # sort the pixels in current by their luminance value in descending order
            lum1inds = lum.argsort()
            sorted_by_lum = current[lum1inds[::-1]]
            # get the top 25%
            top_lum = sorted_by_lum[:(len(sorted_by_lum) // 4)]
            # average them
            average = top_lum.mean(axis=0).mean(axis=0)
            # put it in the matrix
            board[bv[i]:bv[i + 1],
            bh[j]:bh[j + 1]] = np.ones(shape=current.shape, dtype=np.uint8) * np.uint8(average)

    # median blur for cells that filled with color
    board = cv.medianBlur(board.astype(np.uint8), 21)
    return board


def clean(image):
    """clean get an image of a whiteboard and returns an improved colored image"""
    #  get an image of the blank wb
    blank = to_blank(image.copy())
    # you should read the microsoft research for this lines
    image = np.minimum(image / blank, 1)
    image = np.subtract(0.5, np.multiply(0.5, np.cos(np.power(image, 2.5) * np.pi)))
    # transform the image back to 0 to 255
    image *= 255
    image = image.astype(np.uint8)

    return image
