from time import time, sleep
from pynput.keyboard import Controller as KeyboardController

keyboard = KeyboardController()
while True:
    sleep(0.1)
    keyboard.press("v")
    sleep(0.1)
    keyboard.release("v")
