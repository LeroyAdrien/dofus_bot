import cv2 as cv
import pyautogui as gui
import numpy as np
from time import time, sleep
import geometry
import detection
import graph
from math import sqrt
from pynput.mouse import Button
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
import sys
import json
from action_sequence import execute_mouseclicks


def sleep_random(mini, maxi):
    rand = np.random.random() * (maxi - mini) + maxi
    gui.sleep(rand)


gui.sleep_random = sleep_random

class GatheringMap:

    """ Stores path dependeing on gathering position"""

    ASTRUB = 1


class BotState:
    """ Stores the bots possible stats"""

    INITIALIZING = 0
    SEARCHING = 1
    GATHERING = 2
    FIGHTING = 3
    TRIP = 4


class DroppingState:

    GOINGTO = 0
    TALKING = 1
    DRAGGING = 2
    GOINGBACK = 3


class CombatState:

    """ Stores the combat stats """

    PLACEMENT = 0
    DESTROYING = 1
    ENDED = 2


class Bot:
    """ Full bot. Operates in this manner :

    1 - You take a screenshot of the map
    2 - You detect all potential targets
    3 - You make a decision depend on your state
    """

    # Attributes of the class

    # Assets
    assets = {}

    # States of the BOT
    bot_state = None
    bot_combat_state = CombatState.PLACEMENT
    bot_dropping_state = None

    # Positions
    click_history = []
    click_tmp = None
    user_mouse = None

    # Annotations
    rectangles = {}
    targets = {}

    # Time
    start_time = None
    current_time = None

    # Specificity of the bot
    mining_time = 0
    initialization_time = 3
    step_time = 0
    time_since_last_action = None
    # Allows to count the number of wheat clicked before success (to not get stuck on the first resource)
    failure_counter = 0

    # Capture
    screenshot = None

    # Combat
    # Graph of the map layout
    map_graph = None
    me_position = None
    enemy_position = None
    range = 13
    wait_a_bit = True

    # Moving
    trip_to = {}
    talk_banker = {}
    drag_items = {}
    trip_back = {}
    between_trip_time = 2000
    triptodone = False

    def __init__(self, botting_time, map_number):

        # Attributes

        # Load Assets
        # For each item we will have a dictionary of rectangles, targets and assets

        # assets contains first name of items then parameters used by the bot (such as sensitivity for object detection)

        self.data_info_search_gather = {"wheat": {"path": "../assets/resource/wheat_img.png",
                                                  "sensitivity": 0.6,
                                                  "color": (0, 255, 0),
                                                  "mask": False},
                                        "barley": {"path": "../assets/resource/barley_img.png",
                                                   "sensitivity": 0.4,
                                                   "color": (0, 255, 0),
                                                  "mask": False},
                                        "oat": {"path": "../assets/resource/oat_img.png",
                                                "sensitivity": 0.4,
                                                "color": (0, 255, 0),
                                                  "mask" : False},
                                        "rye": {"path": "../assets/resource/rye_img.png",
                                                "sensitivity": 0.4,
                                                "color": (0, 255, 0),
                                                "mask": False},
                                        "faucher": {"path": '../assets/button/action_img.png',
                                                    "sensitivity": 0.90,
                                                    "color": (255, 0, 0),
                                                  "mask": False},
                                        "ok": {"path": '../assets/button/ok_img.png',
                                               "sensitivity": 0.75,
                                               "color": (0, 0, 255),
                                                  "mask": False},
                                        "enemy": {"path": '../assets/combat/ready_img.png',
                                                  "sensitivity": 0.92,
                                                  "color": (0, 0, 255),
                                                  "mask": False}
                                        }

        useless_resources = {"flax": {"path": "../assets/resource/flax_img.png",
                                                 "sensitivity": 0.6,
                                                 "color": (0, 255, 0),
                                                  "mask": False},
                               "hop": {"path": "../assets/resource/hop_img.png",
                                       "sensitivity": 1,
                                       "color": (0, 255, 0),
                                       "mask": False},
                               }

        self.data_info_fight = {"strategic": {"path": "../assets/combat/strategic_img.png",
                                              "sensitivity": 0.95,
                                              "color": (0, 0, 255),
                                              "mask": False},
                                "end_combat": {"path": "../assets/combat/end_combat.png",
                                               "sensitivity": 0.95,
                                               "color": (0, 0, 255),
                                               "mask": False},
                                "socle_activate": {"path": "../assets/combat/activate_socles.png",
                                                   "sensitivity": 0.80,
                                                   "color": (0, 0, 255),
                                                   "mask": False},
                                "socle_me": {"path": "../assets/combat/me_socle.png",
                                             "sensitivity": 0.95,
                                             "color": (0, 0, 255),
                                             "mask": True},
                                "socle_enemy": {"path": "../assets/combat/enemy_socle.png",
                                                "sensitivity": 0.95,
                                                "color": (0, 0, 255),
                                                "mask": True},
                                "me": {"path": "../assets/combat/me/me_lr.png",
                                               "sensitivity": 0.7,
                                               "color": (0, 0, 255),
                                               "mask": False},
                                "turn": {"path": "../assets/combat/my_turn.png",
                                                 "sensitivity": 0.96,
                                                 "color": (0, 0, 255),
                                                 "mask": True}}

        self.data_info_trip = {"confirmation": {"path": "../assets/trips/confirmation.png",
                                              "sensitivity": 0.96,
                                              "color": (0, 0, 255),
                                              "mask": False},
                               "banker_ll": {"path": "../assets/trips/banker_ll.png",
                                             "sensitivity": 0.8,
                                             "color": (0, 0, 255),
                                             "mask": False},
                               "banker_lr": {"path": "../assets/trips/banker_lr.png",
                                            "sensitivity": 0.8,
                                            "color": (0, 0, 255),
                                            "mask": False},
                               "parler": {"path": "../assets/trips/speak.png",
                                             "sensitivity": 0.8,
                                             "color": (0, 0, 255),
                                             "mask": False},
                               }

        if int(map_number) == GatheringMap.ASTRUB:

            f = open("../assets/trips/field2bank_astrub.json")
            self.trip_to = json.load(f)
            f.close

            f = open("../assets/trips/banker_validate.json")
            self.talk_banker = json.load(f)
            f.close

            f = open("../assets/trips/dragging_astrub.json")
            self.drag_items = json.load(f)
            f.close

            f = open("../assets/trips/bank2field_astrub.json")
            self.trip_back = json.load(f)
            f.close

        for key in list(self.data_info_search_gather.keys()):
            if self.data_info_search_gather[key]["mask"] is False:
                self.assets[key] = cv.imread(self.data_info_search_gather[key]["path"], cv.IMREAD_COLOR)
            else:
                self.assets[key] = cv.imread(self.data_info_search_gather[key]["path"], cv.IMREAD_UNCHANGED)

            self.rectangles[key] = None
            self.targets[key] = None

        for key in list(self.data_info_fight.keys()):
            if self.data_info_fight[key]["mask"] is False :
                self.assets[key] = cv.imread(self.data_info_fight[key]["path"], cv.IMREAD_COLOR)
            else:
                self.assets[key] = cv.imread(self.data_info_fight[key]["path"], cv.IMREAD_UNCHANGED)
            self.rectangles[key] = None
            self.targets[key] = None

        for key in list(self.data_info_trip.keys()):
            if self.data_info_trip[key]["mask"] is False:
                self.assets[key] = cv.imread(self.data_info_trip[key]["path"], cv.IMREAD_COLOR)
            else:
                self.assets[key] = cv.imread(self.data_info_trip[key]["path"], cv.IMREAD_UNCHANGED)
            self.rectangles[key] = None
            self.targets[key] = None

        # Information regarding time
        self.start_time = time()
        self.step_time = self.start_time
        self.time_since_last_action = 0

        # Specificity of the bot

        self.bot_state = BotState.INITIALIZING

        DEBUG = True

        while time() - self.start_time < botting_time:
            self.user_mouse = gui.position()
            self.current_time = time()
            # Constant Loop

            # 1-Taking a screenshot
            self.screenshot = gui.screenshot()
            self.screenshot = np.array(self.screenshot)
            self.screenshot = cv.cvtColor(self.screenshot, cv.COLOR_RGB2BGR)

            # 2-Analyze the screenshot (depending on your state)
            if self.bot_state is BotState.SEARCHING or self.bot_state is BotState.GATHERING:
                for key in self.data_info_search_gather.keys():

                    # Determine rectangles and targets of each asset
                    self.rectangles[key] = detection.find_rectangles_template_match(self.screenshot,
                                                                                    self.assets[key],
                                                                                    threshold=self.data_info_search_gather[key]["sensitivity"],
                                                                                    mask=self.data_info_search_gather[key]["mask"])

                    self.targets[key] = geometry.find_targets(self.rectangles[key])

            elif self.bot_state is BotState.FIGHTING:
                for key in self.data_info_fight.keys():
                    self.rectangles[key] = detection.find_rectangles_template_match(self.screenshot,
                                                                                    self.assets[key],
                                                                                    threshold=self.data_info_fight[key]["sensitivity"],
                                                                                    mask=self.data_info_fight[key]["mask"])
                    # Determine targets of rectangles
                    self.targets[key] = geometry.find_targets(self.rectangles[key], random=False)

            elif self.bot_state is BotState.TRIP:
                for key in self.data_info_trip.keys():
                    self.rectangles[key] = detection.find_rectangles_template_match(self.screenshot,
                                                                                    self.assets[key],
                                                                                    threshold=self.data_info_trip[key][
                                                                                        "sensitivity"],
                                                                                    mask=self.data_info_trip[key][
                                                                                        "mask"])
                    # Determine targets of rectangles
                    self.targets[key] = geometry.find_targets(self.rectangles[key], random=False)

                # Optional: Display the annotated screenshot
            if DEBUG:
                # Add annotations on the screenshot
                if self.bot_state is BotState.SEARCHING or self.bot_state is BotState.GATHERING:
                    for key in self.data_info_search_gather.keys():
                        # Show rectangles
                        self.screenshot = detection.add_rectangles(self.screenshot,
                                                                   self.rectangles[key],
                                                                   self.data_info_search_gather[key]["color"])

                elif self.bot_state is BotState.FIGHTING:
                    for key in self.data_info_fight.keys():
                        # Show rectangles
                        self.screenshot = detection.add_rectangles(self.screenshot,
                                                                   self.rectangles[key],
                                                                   self.data_info_fight[key]["color"])

                elif self.bot_state is BotState.TRIP:
                    for key in self.data_info_trip.keys():
                        # Show rectangles
                        self.screenshot = detection.add_rectangles(self.screenshot,
                                                                   self.rectangles[key],
                                                                   self.data_info_trip[key]["color"])

                # Resize for better visibility
                self.screenshot = detection.add_targets(self.screenshot, self.click_history)
                scaled_image = cv.resize(self.screenshot, (1280, 720))

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

            # 3-Select Actions depending of the bot state
            self.decide_what_to_do()

            # Put back the user mouse to where it was
            # gui.moveTo(self.user_mouse)

    # Logic of the bot
    def decide_what_to_do(self):

        if self.bot_state == BotState.INITIALIZING:

            # If elapsed time greater than the initialization time
            if self.current_time - self.start_time >= self.initialization_time:
                self.bot_state = BotState.SEARCHING
        elif self.bot_state == BotState.TRIP:
            self.drop_stuff()

        elif self.bot_state == BotState.SEARCHING:
            self.search_and_gather_resources()

        elif self.bot_state == BotState.GATHERING:
            self.wait_for_time_elapsed()

        elif self.bot_state == BotState.FIGHTING:
            self.destroy_opponent()



        pass

    def drop_stuff(self):

        mouse = MouseController()

        if self.bot_dropping_state == DroppingState.GOINGTO:

            if self.triptodone is False:
                execute_mouseclicks(self.trip_to)
                self.triptodone = True

            if self.triptodone is True:
                bankers = []
                if len(self.targets["banker_ll"]) > 0:
                    bankers += self.targets["banker_ll"]
                if len(self.targets["banker_lr"]) > 0:
                    bankers += self.targets["banker_lr"]

                if self.failure_counter >= len(bankers):
                    self.failure_counter = 0

                # If you can speak to the banker
                if len(self.targets["parler"]) > 0:
                    target_pos = self.targets["parler"][0]
                    print(f'Clicking "parler" at x:{target_pos[0]} y:{target_pos[1]}')
                    # move the mouse
                    gui.moveTo(x=target_pos[0] / 2, y=target_pos[1] / 2)
                    mouse.click(Button.left)
                    self.failure_counter = 0
                    return None

                # If there are resources
                if len(bankers) > 0:
                    target_pos = bankers[self.failure_counter]
                    print(f'Clicking Resource at x:{target_pos[0]} y:{target_pos[1]} attempt number:{self.failure_counter}')
                    # move the mouse
                    gui.moveTo(x=target_pos[0] / 2, y=target_pos[1] / 2)
                    # short pause to let the mouse movement complete
                    mouse.click(Button.left)
                    self.click_tmp = (target_pos[0], target_pos[1])
                    self.failure_counter += 1

                # if you talked to it correctly
                if len(self.targets["confirmation"]):
                    execute_mouseclicks(self.talk_banker)
                    self.bot_dropping_state = DroppingState.DRAGGING

        if self.bot_dropping_state == DroppingState.DRAGGING:
            gui.sleep(1)
            execute_mouseclicks(self.drag_items)
            print("items dragged")
            self.bot_dropping_state = DroppingState.GOINGBACK

        if self.bot_dropping_state == DroppingState.GOINGBACK:
            execute_mouseclicks(self.trip_back)
            self.bot_state = BotState.SEARCHING
            self.step_time = self.current_time


    def search_and_gather_resources(self):

        # Select where the next click will occur

        # Prioritize :
        # "OK" Button / Crosses
        # "Faucher" Button
        # resource image

        mouse = MouseController()
        resource_targets = []

        # Adding the resources to the list
        if len(self.targets["wheat"]) > 0:
            resource_targets += self.targets["wheat"]
#        if len(self.targets["flax"]) > 0:
#            resource_targets += self.targets["flax"]
#        if len(self.targets["hop"]) > 0:
#             resource_targets += self.targets["hop"]
        if len(self.targets["barley"]) > 0:
            resource_targets += self.targets["barley"]
        if len(self.targets["oat"]) > 0:
            resource_targets += self.targets["oat"]
        if len(self.targets["rye"]) > 0:
            resource_targets += self.targets["rye"]

        if len(self.click_history) > 0:
            order = geometry.targets_ordered_by_distance(self.click_history[-1], resource_targets)
        else:
            order = geometry.targets_ordered_by_distance((gui.position()[0] * 2, gui.position()[1] * 2), resource_targets)

        resource_targets = [resource_targets[i] for i in order]

        if self.failure_counter >= len(resource_targets):
            self.failure_counter = 0

        # If time to drop stuff is elapsed
        print("Time since last drop: ", self.current_time - self.step_time)
        if self.current_time - self.step_time > self.between_trip_time:
            print(self.current_time - self.step_time)
            print("Time to drop stuff")
            self.bot_state = BotState.TRIP
            self.bot_dropping_state = DroppingState.GOINGTO
            self.failure_counter = 0

            return None

        # If there is a button than prevents collecting resources
        if len(self.targets["ok"]) > 0:
            target_pos = self.targets["ok"][0]
            print(f'Clicking "ok" at x:{target_pos[0]} y:{target_pos[1]}')
            # move the mouse
            gui.moveTo(x=target_pos[0] / 2, y=target_pos[1] / 2)
            mouse.click(Button.left)

        # if there are indications that you entered combat
        if len(self.targets["enemy"]) > 0:

            self.bot_state = BotState.FIGHTING
            self.click_history = []

            return None

        # If you can gather the resources clicked at the previous iteration
        if len(self.targets["faucher"]) > 0:
            target_pos = self.targets["faucher"][0]
            print(f'Clicking "Faucher" at x:{target_pos[0]} y:{target_pos[1]}')
            # move the mouse
            gui.moveTo(x=target_pos[0] / 2, y=target_pos[1] / 2)
            mouse.click(Button.left)
            self.failure_counter = 0
            self.bot_state = BotState.GATHERING
            self.time_since_last_action = time()

            if self.click_tmp is not None:
                self.click_history.append((int(self.click_tmp[0]), int(self.click_tmp[1])))
            else:
                self.click_history.append((int(target_pos[0]), int(target_pos[1])))

            return None

        # If there are resources
        if len(resource_targets) > 0:
            target_pos = resource_targets[self.failure_counter]
            print(f'Clicking Resource at x:{target_pos[0]} y:{target_pos[1]} attempt number:{self.failure_counter}')
            # move the mouse
            gui.moveTo(x=target_pos[0] / 2, y=target_pos[1] / 2)
            # short pause to let the mouse movement complete
            mouse.click(Button.left)
            self.click_tmp = (target_pos[0], target_pos[1])
            self.failure_counter += 1

            return None

    def destroy_opponent(self):

        mouse = MouseController()
        keyboard = KeyboardController()

        # if combat is over return to searching state
        if len(self.targets["end_combat"]) > 0:

            print("c'est fini !!!!")
            print(len(self.targets["end_combat"]))
            target_pos = self.targets["end_combat"][0]
            print(f'Clicking "ok" at x:{target_pos[0]} y:{target_pos[1]}')
            # move the mouse
            gui.moveTo(x=target_pos[0] / 2, y=target_pos[1] / 2)
            mouse.click(Button.left)
            self.bot_combat_state = CombatState.ENDED

        # Click on the buttons to make sure combat is how it should be
        if len(self.targets["strategic"]) > 0:
            target_pos = self.targets["strategic"][0]
            print(f'Clicking "strategic" at x:{target_pos[0]} y:{target_pos[1]}')
            # move the mouse
            gui.moveTo(x=target_pos[0] / 2, y=target_pos[1] / 2)
            mouse.click(Button.left)
            gui.moveTo(x=0, y=10)

        if len(self.targets["socle_activate"]) > 0:
            print("je clique sur les socles")
            target_pos = self.targets["socle_activate"][0]
            print(f'Clicking "socle" at x:{target_pos[0]} y:{target_pos[1]}')
            # move the mouse
            gui.moveTo(x=target_pos[0] / 2, y=target_pos[1] / 2)
            mouse.click(Button.left)
            gui.moveTo(x=0, y=10)

        # Behave according to the combat state
        if self.bot_combat_state == CombatState.PLACEMENT:
            """ Click on the closest target to the bot and validate READY"""
            sleep(0.5)
            print("Combat started")
            keyboard.press("v")
            keyboard.release("v")
            self.bot_combat_state = CombatState.DESTROYING

        elif self.bot_combat_state == CombatState.DESTROYING:

            # If it is my turn, that we can see the socles and we spotted some

            if len(self.targets["turn"]) > 0:

                # First analyse the sreenshot once more
                if self.wait_a_bit is True:
                    self.wait_a_bit = False
                    return None

                print("It is my turn")


                print(f"Enemy found: {len(self.targets['socle_enemy']) > 0}"
                      , f"Correct Display: {len(self.targets['socle_activate']) == 0}"
                      , f"Me found:{len(self.targets['socle_me']) > 0}")

                if len(self.targets["socle_activate"]) == 0 and len(self.targets["socle_me"]) > 0 and len(self.targets["socle_enemy"]) > 0:

                    # We retrieve positions of mobs and me
                    self.me_position = self.targets["socle_me"][0]
                    self.enemy_position = self.targets["socle_enemy"][0]

                    # We create the map layout if it is not done yet
                    if self.map_graph is None:
                        self.map_graph = graph.create_map_layout(self.screenshot, self.targets["socle_me"] + self.targets["socle_enemy"])
                        print("Graph :", self.map_graph)

                    # We pick the node which is the closest to the measured position of ennemy and me
                    closest_me = geometry.targets_ordered_by_distance(self.me_position, list(self.map_graph.nodes))[0]
                    me = list(self.map_graph.nodes)[closest_me]
                    closest_enemy = geometry.targets_ordered_by_distance(self.enemy_position, list(self.map_graph.nodes))[0]
                    enemy = list(self.map_graph.nodes)[closest_enemy]

                    path = graph.create_path(self.map_graph,
                                             me,
                                             enemy)

                    # If you found a path between you and the opponent
                    if path is not None:

                        # You get closer to the opponent by 3 pm or closer depending on your proximity

                        print(len(path))

                        if len(path) > 5:
                            new_pos = path[3]
                            # You click on the coordinate
                            gui.moveTo(x=new_pos[0] / 2, y=new_pos[1] / 2)
                            gui.sleep_random(0.05, 0.95)
                            mouse.click(Button.left)
                            gui.moveTo(x=0, y=10)

                        else:
                            gui.sleep_random(0.05, 0.95)
                            print("directement adjacent")
                            pass

                        # You check if you are close enough to hit the opponent
                        if len(path) <= self.range:
                            print("In range")
                            keyboard.press("a")
                            keyboard.release("a")
                            gui.moveTo(x=enemy[0] / 2, y=enemy[1] / 2)
                            gui.moveTo(x=path[-1][0] / 2, y=path[-1][1] / 2)
                            gui.sleep_random(0.05, 0.5)
                            mouse.click(Button.left)
                            gui.sleep_random(0.05, 0.5)

                            keyboard.press("a")
                            keyboard.release("a")
                            gui.moveTo(x=enemy[0] / 2, y=enemy[1] / 2)
                            gui.moveTo(x=path[-1][0] / 2, y=path[-1][1] / 2)
                            gui.sleep_random(0.05, 0.5)
                            mouse.click(Button.left)

                            gui.moveTo(x=0, y=10)

                elif len(self.targets["socle_me"]) > 0 and len(self.targets["socle_activate"]) == 0 and self.map_graph is not None:
                    # Find a position that is adjacent to your own position
                    self.me_position = self.targets["socle_me"][0]

                    distances = np.array([geometry.calculate_distance(self.me_position, other) for other in list(self.map_graph.nodes)])
                    adjacent = np.where((distances < 100) & (distances > 95))[0]
                    if len(adjacent)>0:
                        adjacent = list(self.map_graph.nodes)[adjacent[0]]
                    else:
                        adjacent = (0, 0)
                    # Create an invocation at that location
                    sleep(0.5)
                    keyboard.press("é")
                    keyboard.release("é")
                    gui.moveTo(x=adjacent[0] / 2, y=adjacent[1] / 2)
                    gui.sleep_random(0.05, 0.5)
                    mouse.click(Button.left)
                    gui.moveTo(x=0, y=10)

                keyboard.press("v")
                keyboard.release("v")
                self.wait_a_bit = True
                sleep(1)

        elif self.bot_combat_state == CombatState.ENDED:
            print("Combat ended")
            self.bot_state = BotState.SEARCHING
            self.bot_combat_state = CombatState.PLACEMENT

    def wait_for_time_elapsed(self):
        if time() - self.time_since_last_action > 0.9 * self.mining_time:
            self.bot_state = BotState.SEARCHING


if __name__ == "__main__":
    a = Bot(int(sys.argv[1]), sys.argv[2])
