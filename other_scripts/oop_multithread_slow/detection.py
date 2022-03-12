import cv2 as cv
from threading import Thread, Lock
import numpy as np


class Detection:

    # threading properties
    stopped = True
    lock = None
    rectangles = []

    # properties
    screenshot = None
    threshold = None
    asset = None

    #For debugging
    score = None

    def __init__(self, img_file, threshold):
        self.threshold = threshold

        if isinstance(img_file, str):
            self.asset = cv.imread(img_file)
        if isinstance(img_file, list):
            self.asset = [cv.imread(i) for i in img_file]

        # create a thread lock object
        self.lock = Lock()

    def update(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):

        while not self.stopped:
            if not self.screenshot is None:

                # do object detection
                score = cv.matchTemplate(self.screenshot, self.asset, cv.TM_CCOEFF_NORMED)
                locations = np.where(score >= self.threshold)
                # Format them nicely
                locations = list(zip(*locations[::-1]))

                # Add rectangles
                rectangles = []
                for loc in locations:
                    if isinstance(self.asset, list):
                        rect = [int(loc[0]), int(loc[1]), self.asset[0].shape[1], self.asset[0].shape[0]]
                    else:
                        rect = [int(loc[0]), int(loc[1]), self.asset.shape[1], self.asset.shape[0]]
                    rectangles.append(rect)
                    rectangles.append(rect)

                rectangles, weights = cv.groupRectangles(rectangles, 1, 0.2)
                # lock the thread while updating the results
                self.lock.acquire()
                self.rectangles = rectangles
                self.lock.release()
