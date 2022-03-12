import cv2 as cv
import pyautogui
from time import sleep, time
from threading import Thread, Lock
from math import sqrt
import numpy as np
from pynput.mouse import Button, Controller


class BotState:
    INITIALIZING = 0
    SEARCHING = 1
    MINING = 3


class DofusBot:
    # constants
    INITIALIZING_SECONDS = 6
    MINING_SECONDS = 20
    TOOLTIP_MATCH_THRESHOLD = 0.72

    # threading properties
    stopped = True
    lock = None

    # properties
    state = None
    targets = []
    target_success = []
    screenshot = None
    timestamp = None
    movement_screenshot = None
    limestone_tooltip = None
    click_history = []

    def __init__(self):
        # create a thread lock object
        self.lock = Lock()
        # start bot in the initializing mode to allow us time to get setup.
        # mark the time at which this started so we know when to complete it
        self.state = BotState.INITIALIZING
        self.timestamp = time()
        self.click_history = []

    def click_next_target(self):
        # 1. order targets by distance from center
        # loop:
        #   2. hover over the nearest target
        #   3. confirm that it's limestone via the tooltip
        #   4. if it's not, check the next target
        # endloop
        # 5. if no target was found return false
        # 6. click on the found target and return true
        targets = self.targets_ordered_by_distance(self.targets)
        target_success = self.target_success

        mouse = Controller()

        # load up the next target in the list and convert those coordinates
        # that are relative to the game screenshot to a position on our
        # screen
        if len(target_success) > 0:

            print(target_success)
            x = int(target_success[0][0]/2)
            y = int(target_success[0][1]/2)
            pyautogui.moveTo(x=y, y=y)
            sleep(np.random.uniform(1.250, 142.268))
            mouse.click(Button.left)

            target_success = None

            return True

        elif targets:
            x = int(targets[0][0]/2)
            y = int(targets[0][1]/2)

            print('Moving mouse to x:{} y:{}'.format(x, y))

            # move the mouse
            pyautogui.moveTo(x=x, y=y)
            # short pause to let the mouse movement complete and allow
            # time for the tooltip to appear
            sleep(np.random.uniform(1.250, 130.167))


            mouse.click(Button.left)
            pyautogui.click()

            #Check to button to get the resource
            # save this position to the click history
            self.click_history.append((x, y))

            return False

    def targets_ordered_by_distance(self, targets):
        # our character is always in the center of the screen
        my_pos = (500, 200)

        def pythagorean_distance(pos):
            return sqrt((pos[0] - my_pos[0]) ** 2 + (pos[1] - my_pos[1]) ** 2)

        targets.sort(key=pythagorean_distance)

        return targets

    # threading methods

    def update_targets(self, targets):
        self.lock.acquire()
        self.targets = targets
        self.lock.release()

    def update_targets_success(self, target_success):
        self.lock.acquire()
        self.target_success = target_success
        self.lock.release()

    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    # main logic controller
    def run(self):
        while not self.stopped:
            if self.state == BotState.INITIALIZING:
                # do no bot actions until the startup waiting period is complete
                if time() > self.timestamp + self.INITIALIZING_SECONDS:
                    # start searching when the waiting period is over
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()

            elif self.state == BotState.SEARCHING:
                # check the given click point targets, confirm a limestone deposit,
                # then click it.
                success = self.click_next_target()
                # if not successful, try one more time
                if not success:
                    success = self.click_next_target()

                # if successful, switch state to moving
                # if not, backtrack or hold the current position
                if success:
                    self.lock.acquire()
                    self.state = BotState.MINING
                    self.lock.release()

            elif self.state == BotState.MINING:
                # see if we're done mining. just wait some amount of time
                if time() > self.timestamp + self.MINING_SECONDS:
                    # return to the searching state
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()
