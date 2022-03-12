import cv2 as cv
import numpy as np


def find_rectangles_template_match(screenshot, asset, threshold=0.3, return_scores=False, mask=False):

    asset_w = asset.shape[1]
    asset_h = asset.shape[0]
    best_loc = []

    # Assess the score of each subimages in the map
    if mask is True and asset.shape[2] == 4:
        asset_tmp = asset[:, :, :3].copy()
        alpha = np.dstack([asset[:, :, 3], asset[:, :, 3], asset[:, :, 3]])
        score = cv.matchTemplate(screenshot, asset_tmp, cv.TM_CCORR_NORMED, mask=alpha)
    else:
        score = cv.matchTemplate(screenshot, asset, cv.TM_CCOEFF_NORMED)

    locations = np.where(score >= threshold)

    # Format them nicely
    locations = list(zip(*locations[::-1]))

    # Add rectangles
    rectangles = []
    for loc in locations:
        rect = [int(loc[0]), int(loc[1]), asset_w, asset_h]
        rectangles.append(rect)
        rectangles.append(rect)


    rectangles, weights = cv.groupRectangles(rectangles, 1, 0.2)

    if return_scores:
        return rectangles, best_loc
    return rectangles


def find_polygons(img, number_of_edges=4, areas=(6000, 7500)):

    contours = cv.findContours(img, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)[1]

    # Find rectangles in the image
    polygons = []
    for cnt in contours:
        area = cv.contourArea(cnt)

        # Shortlisting the regions based on their area.
        if areas[0] < area < areas[1]:
            approx = cv.approxPolyDP(cnt, 0.009 * cv.arcLength(cnt, True), True)
            # Checking if the no. of sides of the selected region is 7.
            if len(approx) == number_of_edges:
                polygons.append(approx)

    return polygons


def add_rectangles(screenshot, rectangles, line_color=(0, 255, 0)):

    line_type = cv.LINE_4

    for (x, y, w, h) in rectangles:
        # Box positions
        top_left = x, y
        bottom_right = (x + w, y + h)

        # Annotate the map
        cv.rectangle(screenshot, top_left, bottom_right, line_color, cv.LINE_4)

    return screenshot


def add_targets(screenshot, targets, marker_color=(0, 0, 0)):

    marker_type = cv.MARKER_CROSS

    for target in targets:
        cv.drawMarker(screenshot, (target[0], target[1]), marker_color, marker_type)

    return screenshot

if __name__ == "__main__":
    print("Holà")
