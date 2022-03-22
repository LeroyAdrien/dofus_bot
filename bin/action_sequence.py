from pynput.mouse import Button
from pynput.mouse import Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
import pyautogui as gui


def execute_mouseclicks(trip, random=True):

    mouse = MouseController()
    mouse_clicks = trip["mouse_clicks"]
    timings = trip["timings"]

    gui.sleep(2)
    gui.moveTo(x=mouse_clicks[0][0], y=mouse_clicks[0][1])
    mouse.press(Button.left)
    gui.sleep(0.1)
    mouse.release(Button.left)

    for i in range(len(timings)):

        gui.sleep(timings[i])

        gui.moveTo(x=mouse_clicks[i + 1][0], y=mouse_clicks[i + 1][1])

        if i % 2 == 1:
            mouse.press(Button.left)
        else:
            mouse.release(Button.left)





