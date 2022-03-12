import cv2 as cv
import numpy as np
import pyautogui as gui
from vision import Vision
from detection import Detection
from capture import Capture
from bot import DofusBot, BotState
import glob

import math
from time import time

# Initialize the window capture
cap = Capture()
# Load the object detectors
wheat_detector = Detection("../assets/resource/wheat_img.png", 0.25)
success_detector = Detection("../assets/button/action_img.png", 0.1)
# Load the vision
vision = Vision()
# Load the bot
bot = DofusBot()


# Starting Everyone
cap.start()
wheat_detector.start()
success_detector.start()
bot.start()

time_it = time()
while True:

    if cap.screenshot is None:
        continue

    """
    # update the bot with the data it needs right now
    if bot.state == BotState.INITIALIZING:
        # while bot is waiting to start, go ahead and start giving it some targets to work
        # on right away when it does start
        targets = vision.get_click_points(wheat_detector.rectangles)
        bot.update_targets(targets)

    elif bot.state == BotState.SEARCHING:
        # when searching for something to click on next, the bot needs to know what the click
        # points are for the current detection results. it also needs an updated screenshot
        # to verify the hover tooltip once it has moved the mouse to that position
        targets = vision.get_click_points(wheat_detector.rectangles)
        target_success = vision.get_click_points(success_detector.rectangles)
        bot.update_targets(targets)
        bot.update_targets_success(target_success)
        bot.update_screenshot(cap.screenshot)


    elif bot.state == BotState.MINING:
        # nothing is needed while we wait for the mining to finish
        pass
    """
    wheat_detector.update(cap.screenshot)
    success_detector.update(cap.screenshot)
    detection_image = vision.draw_rectangles(cap.screenshot, wheat_detector.rectangles)
    detection_image = vision.draw_rectangles(cap.screenshot, success_detector.rectangles)


    if success_detector.score is not None:
        resized_image = cv.resize(success_detector.score, (1280, 720))
    else :
        resized_image = cv.resize(detection_image, (1280, 720))

    print(f"FRP: {1 /(time() - time_it)}")
    time_it = time()
    cv.imshow("Matches", resized_image)

    cv.waitKey(1)

