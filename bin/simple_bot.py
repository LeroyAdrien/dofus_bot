import cv2 as cv
import pyautogui as gui
import numpy as np
from time import time, sleep
import geometry
import detection
from math import sqrt
from pynput.mouse import Button, Controller

import random


class BotState:

    """ Stores the bots possible stats"""

    INITIALIZING = 0
    SEARCHING = 1
    GATHERING = 2
    FIGHTING = 3


class Bot():

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

        # assets contains first name of items then parameters used by the bot (such as sensitivity for object detection)

        self.data_info = {"wheat": {"path": "../assets/resource/wheat_img.png",
                                    "sensitivity": 0.6,
                                    "color": (0, 255, 0)},
                          "barley": {"path": "../assets/resource/barley_img.png",
                                     "sensitivity": 0.4,
                                     "color": (0, 255, 0)},
                          "oat": {"path": "../assets/resource/oat_img.png",
                                     "sensitivity": 0.4,
                                     "color": (0, 255, 0)},
                          "hop": {"path": "../assets/resource/hop_img.png",
                                  "sensitivity": 0.4,
                                  "color": (0, 255, 0)},
                          "faucher": {"path": '../assets/button/action_img.png',
                                      "sensitivity": 0.96,
                                      "color": (255, 0, 0)},
                          "ok": {"path": '../assets/button/ok_img.png',
                                 "sensitivity": 0.75,
                                 "color": (0, 0, 255)},
                          "placement": {"path": '../assets/combat/placement_img.png',
                                        "sensitivity": 0.95,
                                        "color": (0, 0, 255)}
                          }


        for key in self.data_info.keys():
            self.assets[key] = cv.imread(self.data_info[key]["path"], cv.IMREAD_COLOR)
            self.rectangles[key] = None
            self.targets[key] = None

        # Information regarding time
        self.start_time = time()
        self.time_since_last_action = 0

        # Specificity of the bot
        self.initialization_time = 5
        self.mining_time = 8.4

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
                self.rectangles[key] = detection.find_rectangles(self.screenshot,
                                                                 self.assets[key],
                                                                 threshold=self.data_info[key]["sensitivity"])
                # Determine targets of rectangles
                self.targets[key] = geometry.find_targets(self.rectangles[key])

            # 3-Select Actions depending of the bot state
            self.decideWhatToDo()

            # Optional: Display the annotated screenshot
            if DEBUG:
                # Add annotations on the screenshot
                for key in self.data_info.keys():
                    # Show rectangles
                    self.add_rectangles(self.rectangles[key], self.data_info[key]["color"])

                # Resize for better visibility
                scaled_image = cv.resize(self.screenshot, (720, 480))

                # Add bot state
                if self.bot_state == BotState.INITIALIZING:
                    cv.putText(img=scaled_image, text="Initializing",
                               org=(0, 35), fontFace=cv.FONT_HERSHEY_TRIPLEX,
                               fontScale=1, color=(100, 100, 100))

                elif self.bot_state == BotState.SEARCHING:
                    cv.putText(img=scaled_image, text="Searching",
                               org=(0, 35), fontFace=cv.FONT_HERSHEY_TRIPLEX,
                               fontScale=1, color=(0, 127, 255))

                elif self.bot_state == BotState.GATHERING:
                    cv.putText(img=scaled_image, text="Gathering",
                               org=(0, 35), fontFace=cv.FONT_HERSHEY_TRIPLEX,
                               fontScale=1, color=(0, 255, 0))

                elif self.bot_state == BotState.FIGHTING:
                    cv.putText(img=scaled_image, text="Fighting",
                               org=(0, 35), fontFace=cv.FONT_HERSHEY_TRIPLEX,
                               fontScale=1, color=(0, 0, 255))

                else:
                    cv.putText(img=scaled_image, text="UNKNOWN",
                               org=(0, 35), fontFace=cv.FONT_HERSHEY_TRIPLEX,
                               fontScale=1, color=(255, 255, 255))

                # Add fps_count
                fps = 1 / (time() - self.current_time)
                cv.putText(img=scaled_image, text=str(round(fps, 1)),
                           org=(0, 60), fontFace=cv.FONT_HERSHEY_TRIPLEX,
                           fontScale=1, color=(255, 255, 255))

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
            self.search_and_gather_resources()

        elif self.bot_state == BotState.GATHERING:
            self.wait_for_time_elapsed()

        elif self.bot_state == BotState.FIGHTING:
            self.wait_for_time_elapsed()
            quit()

        pass

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

    def search_and_gather_resources(self):

        # Select where the next click will occur

        # Prioritize :
        # "OK" Button / Crosses
        # "Faucher" Button
        # resource image

        mouse = Controller()
        resource_targets = []

        # Adding the resources to the list
        if len(self.targets["wheat"]) > 0:
            resource_targets += self.targets["wheat"]
        if len(self.targets["hop"]) > 0:
                resource_targets += self.targets["hop"]
        if len(self.targets["oat"]) > 0:
                resource_targets += self.targets["oat"]
        if len(self.targets["barley"]) > 0:
            resource_targets += self.targets["barley"]

        if len(self.click_history) > 0:
            resource_targets = geometry.targets_ordered_by_distance(self.click_history[-1], resource_targets)
        else:
            resource_targets = geometry.targets_ordered_by_distance((0,0), resource_targets)

        if self.failure_counter >= len(resource_targets):
            self.failure_counter = 0

        # If there is a button than prevents collecting resources
        if len(self.targets["ok"]) > 0:
            target_pos = self.targets["ok"][0]
            print(f'Clicking "ok" at x:{target_pos[0]} y:{target_pos[1]}')
            # move the mouse
            gui.moveTo(x=target_pos[0], y=target_pos[1])
            mouse.click(Button.left)

        # if there are indications that you entered combat
        if len(self.targets["placement"]) > 0:
            self.bot_state = BotState.FIGHTING
            return None

        # If you can gather the resources clicked at the previous iteration
        if len(self.targets["faucher"]) > 0:
            target_pos = self.targets["faucher"][0]
            print(f'Clicking "Faucher" at x:{target_pos[0]} y:{target_pos[1]}')
            # move the mouse
            gui.moveTo(x=target_pos[0], y=target_pos[1])
            mouse.click(Button.left)
            self.failure_counter = 0
            self.bot_state = BotState.GATHERING
            self.time_since_last_action = time()
            self.click_history.append((target_pos[0], target_pos[1]))

            return None

        # If there are resources
        if len(resource_targets) > 0:
            target_pos = resource_targets[self.failure_counter]
            print(f'Clicking Resource at x:{target_pos[0]} y:{target_pos[1]} attempt number:{self.failure_counter}')
            # move the mouse
            gui.moveTo(x=target_pos[0], y=target_pos[1])
            # short pause to let the mouse movement complete
            mouse.click(Button.left)
            self.failure_counter += 1

            return None

    def wait_for_time_elapsed(self):
        if time() - self.time_since_last_action > 0.9 * self.mining_time:
            self.bot_state = BotState.SEARCHING




a = Bot()
