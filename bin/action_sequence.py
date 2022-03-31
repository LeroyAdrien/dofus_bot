from pynput.mouse import Button
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
import pyautogui as gui
import numpy as np


def execute_mouseclicks(trip, random=True):

    mouse = MouseController()
    keyboard = KeyboardController()
    mouse_clicks = trip["mouse_clicks"]
    timings = trip["timings"]

    # Deactivate sprites
    with keyboard.pressed("e"):

        for i in range(len(timings)):

            gui.sleep(timings[i] + 0.1 * timings[i] * np.random.rand())

            if random is True:
                a = np.random.rand() * 2
                b = np.random.rand() * 2

            gui.moveTo(x=mouse_clicks[i][0] + a, y=mouse_clicks[i][1] + b)

            if i % 2 == 0:
                mouse.press(Button.left)
            else:
                mouse.release(Button.left)






