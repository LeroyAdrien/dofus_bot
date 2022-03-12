import cv2 as cv
import numpy as np
import geometry
import detection
import main

data_info_fight = {"enemy_ul": {"path": '../assets/combat/enemy/enemy_ul.png',
                                "sensitivity": 0.85,
                                "color": (0, 0, 255)},
                   "enemy_ur": {"path": '../assets/combat/enemy/enemy_ur.png',
                                        "sensitivity": 0.85,
                                        "color": (0, 0, 255)},
                   "enemy_ll": {"path": '../assets/combat/enemy/enemy_ll.png',
                                        "sensitivity": 0.85,
                                        "color": (0, 0, 255)},
                   "enemy_lr": {"path": '../assets/combat/enemy/enemy_lr.png',
                                        "sensitivity": 0.85,
                                        "color": (0, 0, 255)},
                    }

assets = {}
rectangles = {}
targets = {}

for key in list(data_info_fight.keys()):
    assets[key] = cv.imread(data_info_fight[key]["path"], cv.IMREAD_COLOR)
    rectangles[key] = None
    targets[key] = None

images = [cv.imread("../assets/combat/combat_screens/combat" + str(i) + ".png", cv.IMREAD_COLOR) for i in range(34)]

for image in images:
    for key in data_info_fight.keys():

        rectangles[key] = detection.find_rectangles_template_match(image,
                                                                   assets[key],
                                                                   threshold=data_info_fight[key]["sensitivity"])
        # Determine targets of rectangles
        targets[key] = geometry.find_targets(rectangles[key])

        image = detection.add_rectangles(image,
                                         rectangles[key],
                                         data_info_fight[key]["color"])

    cv.imshow("Test1", cv.resize(image, (1240, 720)))
    cv.waitKey()

