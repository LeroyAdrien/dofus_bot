import numpy as np
from threading import Thread, Lock
import pyautogui as gui
import cv2 as cv


class Capture:

    # threading properties
    stopped = True
    lock = None
    screenshot = None

    # constructor
    def __init__(self):
        # create a thread lock object
        self.lock = Lock()
        self.screenshot = None

    def get_screenshot(self):

        # Taking a screenshot
        screenshot = gui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv.cvtColor(screenshot, cv.COLOR_RGB2BGR)

        return screenshot

    # threading methods
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        # TODO: you can write your own time/iterations calculation to determine how fast this is
        while not self.stopped:
            # get an updated image of the game
            screenshot = self.get_screenshot()
            # lock the thread while updating the results
            self.lock.acquire()
            self.screenshot = screenshot
            self.lock.release()
