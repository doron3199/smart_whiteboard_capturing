import cv2 as cv
import numpy as np


def to_blank(image):
    gray = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
    height, width = gray.shape
    cells = []
    size = image.size
    num = 150
    if size > 10000000:
        num = 300
    # split the wb to cells
    for i in range(num):
        cells.append([])
        for j in range(num):
            cells[i].append(gray[i * height // num:(i + 1) * height // num, j * width // num:(j + 1) * width // num])
    # for each cell compute the average of the 25% most brightness pixels
    for i in range(num):
        for j in range(num):
            va = np.sort(np.reshape(cells[i][j], -1))
            cn = va[-(len(va) // 4):]
            cells[i][j][:, :] = np.average(cn)
    # built the image
    new = []
    for i in range(num):
        new.append(np.concatenate((cells[i][:]), axis=1))
    blank = np.concatenate((new[:]), axis=0)
    # median blur for cells that filled with color
    median = cv.medianBlur(blank, 21)
    return median


def clean(image):
    #  get an image of the blank wb
    blank = to_blank(image.copy())
    blank = cv.cvtColor(blank, cv.COLOR_GRAY2RGB)
    # you should read the microsoft research for this lines
    ones = np.ones(image.shape, dtype=np.uint8)
    divided = image / blank
    # for some reason its make it look better
    # divided += np.array([0.1, 0, 0])
    image = np.minimum(divided, ones)
    image = 0.5 - 0.5 * np.cos(pow(image, 2.5) * np.pi)
    # transform the image back to 0 to 255
    image *= 255
    image = image.astype(np.uint8)
    return image
