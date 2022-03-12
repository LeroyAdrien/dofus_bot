import cv2 as cv
import detection
import geometry
import numpy as np
import networkx as nx
from networkx import NetworkXNoPath


def create_map_layout(img, suppl_positions=[]):

    # Converting the map to edges
    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    thresh = cv.adaptiveThreshold(img_gray, 200,
                                  cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv.THRESH_BINARY, 3, 1)

    # finding center of each square
    squares = detection.find_polygons(thresh)
    positions = geometry.find_barycentre(squares)

    # Adding the positions which cannot be spotted by polygon detection
    print(suppl_positions)
    for sup in suppl_positions:
        positions.append(sup)
        # adding adjacent positions
        for x in [-1, 1]:
            for y in [-1, 1]:
                positions.append([sup[0] + x * 85, sup[1] + y * 45])

    positions = np.array(positions).astype(int)

    #detection.add_targets(img, np.array(suppl_positions).astype(int))
    #cv.imshow("lolilol", cv.resize(img, (1280, 720)))
    #cv.waitKey()

    # Removing useless squares and false positives
    # Removing duplicated positions
    squares_analysis_1 = np.unique(np.floor(positions / 10), axis=0, return_counts=True, return_index=True)
    squares_analysis_2 = np.unique(np.round(positions / 10, 0), axis=0, return_counts=True, return_index=True)

    squares_analysis = np.intersect1d(squares_analysis_1[1], squares_analysis_2[1])
    positions = positions[squares_analysis].astype(int)

    # Removing false positives
    min_brightness = np.array([np.min(img_gray[j - 20:j + 20, i - 20: i + 20].flatten()) for i, j in positions])
    good = np.where((min_brightness >= np.quantile(min_brightness, 0.01)) | (min_brightness > 95))
    positions = positions[good]





    # Create a graph of the map

    # Now we devise a graph of the map
    path_dict = {}
    for position in positions:
        distances = np.array([geometry.calculate_distance(position, other) for other in positions])
        adjacent = np.where((distances < 100) & (distances > 95))[0]
        path_dict[tuple(position)] = [tuple(i) for i in positions[adjacent].tolist()]

    print(path_dict)
    graph = nx.Graph(path_dict)

    return graph


def create_path(graph, origin_node: tuple, target_node: tuple):
    try :
        path = nx.astar_path(graph, origin_node, target_node, heuristic=geometry.calculate_distance, weight="cost")
    except NetworkXNoPath:
        path = None
    return path

