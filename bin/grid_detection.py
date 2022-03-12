import numpy as np
import cv2 as cv
import detection
import geometry
import networkx as nx
import sys
import matplotlib.pyplot as plt

cible_enemy = cv.imread("./enemy_socle.png", cv.IMREAD_UNCHANGED)
cible_me = cv.imread("./me_socle.png", cv.IMREAD_UNCHANGED)

for i in range(10):
    img = cv.imread("grid_" + str(i) + ".png", cv.IMREAD_COLOR)

    img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    thresh = cv.adaptiveThreshold(img_gray, 200,
                                  cv.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv.THRESH_BINARY, 3, 1)


    # Find targets socles
    rectangle_cible_me = detection.find_rectangles_template_match(img, cible_me, 0.95, mask=True)
    rectangle_cible_enemy = detection.find_rectangles_template_match(img, cible_enemy, 0.95, mask=True)
    rectangles = detection.find_polygons(thresh)

    me_position = np.array(geometry.find_targets(rectangle_cible_me, random=False)) * 2
    enemy_positions = np.array(geometry.find_targets(rectangle_cible_enemy, random=False)) * 2
    enemy_positions = enemy_positions.astype(int)
    me_position = me_position.astype(int)
    squares_positions = geometry.find_barycentre(rectangles)

    # Add positions near the enemy and the target to the squares positions
    for x in [-1, 1]:
        for y in [-1, 1]:
            squares_positions.append(list(me_position[0] + [x * 85, y * 45]))
            for enemy in enemy_positions:
                squares_positions.append(list(enemy + [x * 85, y * 45]))

    squares_positions.append(me_position[0])
    for enemy in enemy_positions:
        squares_positions.append(enemy)

    squares_positions = np.array(squares_positions)


    # Removing useless squares and false positives

    # Removing duplicated positions
    squares_analysis_1 = np.unique(np.floor(squares_positions / 10), axis=0, return_counts=True, return_index=True)
    squares_analysis_2 = np.unique(np.round(squares_positions / 10, 0), axis=0, return_counts=True, return_index=True)

    squares_analysis = np.intersect1d(squares_analysis_1[1], squares_analysis_2[1])
    np.set_printoptions(threshold=sys.maxsize)
    squares_positions = squares_positions[squares_analysis].astype(int)

    detection.add_targets(img, squares_positions.astype(int), marker_color=(0, 0, 0))
    
    # Removing false positives
    min_brightness = np.array([np.min(img_gray[j-20:j+20, i-20: i+20].flatten()) for i, j in squares_positions])
    good = np.where((min_brightness >= np.quantile(min_brightness, 0.01)) | (min_brightness > 95))
    squares_positions = squares_positions[good]

    img = detection.add_rectangles(img, rectangle_cible_me)
    img = detection.add_rectangles(img, rectangle_cible_enemy)



    # Now we devise a graph of the map
    path_dict = {}
    for squares_position in squares_positions:
        distances = np.array([geometry.calculate_distance(squares_position, tutu) for tutu in squares_positions])
        ou = np.where((distances < 100) & (distances > 95))[0]
        path_dict[tuple(squares_position.astype(int))] = [tuple(i) for i in squares_positions[ou].astype(int).tolist()]

    graphs = nx.Graph(path_dict)

    # We select only the biggest connected subgraph
    img_temp = img.copy()
   # detection.add_targets(img_temp, list(path_dict.keys()), marker_color=(0, 0, 255))
    cv.imshow('image2', cv.resize(img_temp, (1240, 720)))
    cv.waitKey()
    # Showing the image along with outlined arrow.

    # Exiting the window if 'q' is pressed on the keyboard.
    #cv.waitKey()

    #combat_graph = nx.Graph(best_dict)
    #print(combat_graph.edges(enemy_positions[0]))
    #plt.show()
    path = nx.astar_path(graphs, tuple(me_position[0].astype(int)),
                        tuple(enemy_positions[0].astype(int)), heuristic=geometry.calculate_distance, weight="cost")

    detection.add_targets(img, path, marker_color=(0, 0, 255))
    cv.imshow('image2', cv.resize(img, (1240, 720)))
    cv.waitKey()








    # Now we search for a path between the target and us








