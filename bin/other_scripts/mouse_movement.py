import pyautogui
from pynput.mouse import Button, Controller
from time import time


a = pyautogui.size()
print(a)

while True:
    a = pyautogui.position()
    print(a)
    mouse = Controller()
    if int(time() % 5) == 0:
        mouse.click(Button.left)


