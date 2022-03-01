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

rectangles = []
for loc in locations:
    rect = [int(loc[0]), int(loc[1]), wheat_w, wheat_h]
    rectangles.append(rect)
    rectangles.append(rect)

rectangles, weights = cv.groupRectangles(rectangles, 1, 0.2)
print(rectangles)

if len(rectangles):

    line_color = (0, 255, 0)
    line_type = cv.LINE_4

    marker_color = (255, 0, 0)
    marker_type = cv.MARKER_CROSS



    for (x, y, w, h) in rectangles:
        """
        # Box positions
        top_left = x, y
        bottom_right = (x + w, y + h)

        # Annotate the map
        cv.rectangle(map_img, top_left, bottom_right, line_color, line_type)
        """

        center_x = np.random.randint(x, int(x + w))
        center_y = np.random.randint(y, int(y + h))
        cv.drawMarker(map_img, (center_x, center_y), marker_color, marker_type)

    cv.imshow("Matches", map_img)
    cv.waitKey()
else:
    print("No wheat found ")




