import numpy as np
import cv2 as cv

map_img = cv.imread('./map_img.png', cv.IMREAD_REDUCED_COLOR_4)
wheat_img = cv.imread('./wheat_img.png', cv.IMREAD_REDUCED_COLOR_4)

wheat_w = wheat_img.shape[1]
wheat_h = wheat_img.shape[0]

score = cv.matchTemplate(map_img, wheat_img, cv.TM_CCOEFF_NORMED)

# cv.imshow("score",score)
# cv.waitKey()

min_val, max_val, loc_min, loc_max = cv.minMaxLoc(score)

threshold = 0.8

if max_val >= threshold:
    print("Found Wheat")

    top_left = loc_max
    bottom_right = (top_left[0] + wheat_w , top_left[1] + wheat_h)

    cv.rectangle(map_img, top_left, bottom_right,
                 color=(0, 255, 0), thickness=2, lineType=cv.LINE_4)

    cv.imshow("Score", map_img)
    cv.waitKey()
else:
    print("Didn't found wheat")

