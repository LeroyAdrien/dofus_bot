import numpy as np
import cv2 as cv

map_img = cv.imread('./map_img.png', cv.IMREAD_REDUCED_COLOR_2)
wheat_img = cv.imread('./wheat_img.png', cv.IMREAD_REDUCED_COLOR_2)

wheat_w = wheat_img.shape[1]
wheat_h = wheat_img.shape[0]

# Assess the score of each subimages in the map
score = cv.matchTemplate(map_img, wheat_img, cv.TM_CCOEFF_NORMED)

# Select the subimages which match the wheat template
threshold = 0.3
locations = np.where(score >= threshold)

# Format them nicely
locations = list(zip(*locations[::-1]))

if locations:
    wheat_w = wheat_img.shape[1]
    wheat_h = wheat_img.shape[0]
    line_color = (0, 255, 0)
    line_type = cv.LINE_4

    for loc in locations:

        # Box positions
        top_left = loc
        bottom_right = (top_left[0] + wheat_w, top_left[1] + wheat_h)

        # Annotate the map
        cv.rectangle(map_img, top_left, bottom_right, line_color, line_type)

    cv.imshow("Matches", map_img)
    cv.waitKey()
else:
    print("No wheat found ")




