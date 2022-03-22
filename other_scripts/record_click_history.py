from pynput import mouse
from time import time, sleep
import json
from functools import partial
import sys


class Recorder:

    dico = {"mouse_clicks": [],
            "timings": []}

    time_marker = None

    filename = None

    def __init__(self, filename):

        self.time_marker = time()
        self.filename = filename
        self.flag = False
        print("Script Launched:")

        while True:
            listener = mouse.Listener(on_click=self.on_click)
            listener.start()
            listener.join()

    def on_click(self, x, y, button, pressed):

        if button == mouse.Button.left:
            self.dico["mouse_clicks"].append([x, y])

        if self.flag is True:
            self.dico["timings"].append(time() - self.time_marker)
        else:
            self.flag = True

        self.time_marker = time()

        print(self.dico)

        jsonString = json.dumps(self.dico)
        jsonFile = open(self.filename, "w")
        jsonFile.write(jsonString)
        jsonFile.close()


Recorder(sys.argv[1])








