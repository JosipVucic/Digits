import math

import numpy as np
from PIL import Image, ImageOps
import cv2
from scipy import ndimage
from torchvision.transforms import transforms


# noinspection PyTypeChecker
def preprocess_image(file):
    """Preprocesses an image file, so it can be used with the GACNN model.
    :param file: image file to be opened with Pillow
    :return: input for the GACNN model, containing the processed image"""
    with Image.open(file) as original:

        img = np.array(original)

        # convert to grayscale, invert colors, resize to 28x28
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img = cv2.resize(255-img, (28, 28))
        (thresh, img) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # remove rows and columns that do not contain the digit
        while np.sum(img[0]) == 0:
            img = img[1:]
        while np.sum(img[:, 0]) == 0:
            img = np.delete(img, 0, 1)
        while np.sum(img[-1]) == 0:
            img = img[:-1]
        while np.sum(img[:, -1]) == 0:
            img = np.delete(img, -1, 1)

        # resize to 20x20
        rows, cols = img.shape
        if rows > cols:
            factor = 20.0 / rows
            rows = 20
            cols = int(round(cols * factor))
            img = cv2.resize(img, (cols, rows))
        else:
            factor = 20.0 / cols
            cols = 20
            rows = int(round(rows * factor))
            img = cv2.resize(img, (cols, rows))

        # add padding until 28x28
        cols_padding = (int(math.ceil((28 - cols) / 2.0)), int(math.floor((28 - cols) / 2.0)))
        rows_padding = (int(math.ceil((28 - rows) / 2.0)), int(math.floor((28 - rows) / 2.0)))
        img = np.lib.pad(img, (rows_padding, cols_padding), 'constant')

        # shift image according to center of mass
        shiftx, shifty = get_best_shift(img)
        shifted = shift(img, shiftx, shifty)
        img = shifted

        img = img / 255.0

        transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.1307,), (0.3081,))])

        img = transform(img)
        img = img.float().unsqueeze(axis=0)
        return img


def get_best_shift(img):
    """Gets the image shift required according to center of mass.
    :return: shiftx, shifty - representing the necessary shifts on x and y axes"""
    cy, cx = ndimage.measurements.center_of_mass(img)

    rows, cols = img.shape
    shiftx = np.round(cols / 2.0 - cx).astype(int)
    shifty = np.round(rows / 2.0 - cy).astype(int)

    return shiftx, shifty


def shift(img, sx, sy):
    """
    Shifts the image according to the specified x and y shift amounts.
    :param img: The image as numpy array.
    :param sx: The shift amount for x-axis.
    :param sy: The shift amount for y-axis.
    :return: The shifted image.
    """
    rows, cols = img.shape
    M = np.float32([[1, 0, sx], [0, 1, sy]])
    shifted = cv2.warpAffine(img, M, (cols, rows))
    return shifted
