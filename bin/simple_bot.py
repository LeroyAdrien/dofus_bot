import cv2 as cv
import pyautogui as gui
import numpy as np
from time import time, sleep
from math import sqrt
from pynput.mouse import Button, Controller

import random


class BotState:

    """ Stores the bots possible stats"""

    INITIALIZING = 0
    SEARCHING = 1
    GATHERING = 2

class Bot:

    """ Full bot. Operates in this manner :

    1 - You take a screenshot of the map
    2 - You detect all potential targets
    3 - You make a decision depend on your state
    """

    # Attributes of the class

    # Assets
    assets = {}

    # Positions
    click_history = []
    user_mouse = None

    # Annotations
    rectangles = {}
    targets = {}

    # Time
    start_time = None
    current_time = None

    # Specificity of the bot
    mining_time = None
    initialization_time = None
    time_since_last_action = None
    # Allows to count the number of wheat clicked before success (to not get stuck on the first resource)
    failure_counter = 0

    # Capture
    screenshot = None

    def __init__(self):

        # Attributes

        # Load Assets
        # For each item we will have a dictionary of rectangles, targets and assets

        #assets contains first name of items then parameters used by the bot (such as sensitivity for object detection)
        self.data_info = {"wheat": {"path": "../assets/resource/wheat_img.png",
                                    "sensitivity": 0.3,
                                    "color": (0, 255, 0)},
                          "faucher": {"path": '../assets/button/action_img.png',
                                      "sensitivity": 0.7,
                                      "color": (255, 0, 0)},
                          "ok": {"path": '../assets/button/ok_img.png',
                                 "sensitivity": 0.7,
                                 "color": (0, 0, 255)}}


        for key in self.data_info.keys():
            self.assets[key] = cv.imread(self.data_info[key]["path"], cv.IMREAD_COLOR)
            self.rectangles[key] = None
            self.targets[key] = None

        # Information regarding time
        self.start_time = time()
        self.time_since_last_action = 0

        # Specificity of the bot
        self.initialization_time = 5
        self.mining_time = 11

        self.bot_state = BotState.INITIALIZING

        DEBUG = True
        while True:
            self.user_mouse = gui.position()
            self.current_time = time()
            # Constant Loop

            # 1-Taking a screenshot
            self.screenshot = gui.screenshot()
            self.screenshot = np.array(self.screenshot)
            self.screenshot = cv.cvtColor(self.screenshot, cv.COLOR_RGB2BGR)

            # 2-Analyze the screenshot
            for key in self.data_info.keys():
                # Determine rectangles and targets of each asset
                cv.imshow(str(key), self.assets[key])
                self.rectangles[key] = self.find_rectangles(self.assets[key],
                                                            threshold=self.data_info[key]["sensitivity"])
                # Determine targets of rectangles
                self.targets[key] = self.targets_ordered_by_distance(self.find_targets(self.rectangles[key]))

            # 3-Select Actions depending of the bot state
            self.decideWhatToDo()

            # Optional: Display the annotated screenshot
            if DEBUG:
                # Add annotations on the screenshot
                for key in self.data_info.keys():
                    self.add_rectangles(self.rectangles[key], self.data_info[key]["color"])

                # Resize for better lisibility
                scaled_image = cv.resize(self.screenshot, (1280, 720))

                # Add fps_count
                fps = 1 / (time() - self.current_time)
                cv.putText(img=scaled_image, text=str(round(fps, 1)),
                           org=(150, 250), fontFace=cv.FONT_HERSHEY_PLAIN,
                           fontScale=3, color=(255, 255, 255), thickness=3)

                cv.imshow("Bot capture", scaled_image)

                # Give Opportunity to leave the bot
                if cv.waitKey(10) == ord('q'):
                    cv.destroyAllWindows()
                    break

            # Put back the user mouse to where it was
            #gui.moveTo(self.user_mouse)

    # Logic of the bot
    def decideWhatToDo(self):

        if self.bot_state == BotState.INITIALIZING:

            # If elapsed time greater than the initialization time
            if self.current_time - self.start_time >= self.initialization_time:
                self.bot_state = BotState.SEARCHING

        elif self.bot_state == BotState.SEARCHING:
            self.click_next_target()

        elif self.bot_state == BotState.GATHERING:
            self.wait_for_time_elapsed()

        pass


    def find_rectangles(self, asset, threshold=0.3, return_scores=False):

        asset_w = asset.shape[1]
        asset_h = asset.shape[0]
        best_loc = []

        # Assess the score of each subimages in the map
        score = cv.matchTemplate(self.screenshot, asset, cv.TM_CCOEFF_NORMED)

        # Search for the resource in the image
        locations = np.where(score >= threshold)
        #tmp = cv.resize(score, (1240, 720))
        #cv.imshow("score",tmp)
        #cv.waitKey()

        # Format them nicely
        locations = list(zip(*locations[::-1]))

        # Add rectangles
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), asset_w, asset_h]
            rectangles.append(rect)
            rectangles.append(rect)

        rectangles, weights = cv.groupRectangles(rectangles, 1, 0.2)

        if return_scores:
            return rectangles, best_loc

        return rectangles

    def add_rectangles(self, rectangles, line_color = (0, 255, 0)):

        line_type = cv.LINE_4

        for (x, y, w, h) in rectangles:

            # Box positions
            top_left = x, y
            bottom_right = (x + w, y + h)

            # Annotate the map
            cv.rectangle(self.screenshot, top_left, bottom_right, line_color, cv.LINE_4)

    def add_targets(self, targets):

        marker_color = (255, 0, 0)
        marker_type = cv.MARKER_CROSS

        for target in targets:
            cv.drawMarker(self.screenshot, (target[0], target[1]), marker_color, marker_type)



    def find_targets(self, rectangles):

        coords = []
        # If there are resources
        for (x, y, w, h) in rectangles:

            # Create the clicking positions
            center_x = np.random.randint(int(x + w * 0.1), int(x + w * 0.9))
            center_y = np.random.randint(int(y + w * 0.1), int(y + h * 0.9))
            coords.append((center_x, center_y))

        return coords


    def targets_ordered_by_distance(self, targets):
        # our character is always in the center of the screen
        if len(self.click_history) > 0 :
            pos = self.click_history[-1]
        else:
            pos = (0, 0)

        def pythagorean_distance(pos):
            return sqrt((pos[0] - pos[0]) ** 2 + (pos[1] - pos[1]) ** 2)

        targets.sort(key=pythagorean_distance)

        return targets


    def click_next_target(self):

        # Select where the next click will occur

        # Prioritize :
        # "OK" Button / Crosses
        # "Faucher" Button
        # resource image


        mouse = Controller()

        targets = self.targets
        target_i = 0

        if len(targets["ok"]) > 0:
            target_pos = targets["ok"][0]
            print(f'Clicking "Faucher" at x:{target_pos[0]} y:{target_pos[1]}')
            # move the mouse
            gui.moveTo(x=target_pos[0]/2, y=target_pos[1]/2)
            # short pause to let the mouse movement complete
            sleep(np.random.uniform(0.127, 0.222))
            mouse.click(Button.left)

        if len(targets["faucher"]) > 0:
            target_pos = targets["faucher"][0]
            print(f'Clicking "Faucher" at x:{target_pos[0]} y:{target_pos[1]}')
            # move the mouse
            gui.moveTo(x=target_pos[0]/2, y=target_pos[1]/2)
            # short pause to let the mouse movement complete
            sleep(np.random.uniform(0.127, 0.222))
            mouse.click(Button.left)
            self.failure_counter = 0
            self.bot_state = BotState.GATHERING
            self.time_since_last_action = time()
            self.click_history.append((target_pos[0]/2, target_pos[1]/2))

            return None

        if len(targets["wheat"]) > 0:
            target_pos = targets["wheat"][self.failure_counter]
            print(f'Clicking Wheat at x:{target_pos[0]} y:{target_pos[1]} attempt number:{self.failure_counter}')
            # move the mouse
            gui.moveTo(x=target_pos[0]/2, y=target_pos[1]/2)
            # short pause to let the mouse movement complete
            sleep(np.random.uniform(0.127, 0.222))
            mouse.click(Button.left)
            self.failure_counter += 1
            if self.failure_counter >= len(targets["wheat"]):
                self.failure_counter = 0

            return None



    def wait_for_time_elapsed(self):
        if time() - self.time_since_last_action > 0.9 * self.mining_time:
            self.bot_state = BotState.SEARCHING




a = Bot()
