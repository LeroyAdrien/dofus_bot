import cv2 as cv
import numpy as np


def find_rectangles(screenshot, asset, threshold=0.3, return_scores=False):

    asset_w = asset.shape[1]
    asset_h = asset.shape[0]
    best_loc = []

    # Assess the score of each subimages in the map
    score = cv.matchTemplate(screenshot, asset, cv.TM_CCOEFF_NORMED)

    # Search for the resource in the image
    locations = np.where(score >= threshold)
    # tmp = cv.resize(score, (1240, 720))
    # cv.imshow("score",tmp)
    # cv.waitKey()

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


if __name__ == "__main__":
    print("Holà")
