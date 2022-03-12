import numpy as np
from math import sqrt


def project_target(projection_matrix, target):

    target = np.array(target)
    new_target = np.matmul(projection_matrix, target)

    return tuple(new_target)


def project_targets(projection_matrix, targets):

    new_targets = []

    for target in targets:

        new_target = project_target(projection_matrix, target)

        new_targets.append(new_target)

    return new_targets


def in_true_space(function):

    """ Wrapper around functions that sort by proximity but in true space"""
    def new_function(*args):

        # Projection Matrix
        A = np.array([[1, 0],
                      [0, 2]])
        # Inverse of the projection matrix
        B = np.linalg.inv(A)

        # We first transform each position
        new_args = []
        for arg in args:
            if isinstance(arg, list):
                arg = project_targets(A, arg)
            else:
                arg = project_target(A, arg)

            new_args.append(arg)

        # We apply the function
        ret = function(*new_args)

        # We put back in original space to get accurate click positions
        # ret = project_targets(B, ret)

        return ret

    return new_function


def find_targets(rectangles, random=True):

    coords = []
    # If there are resources
    for (x, y, w, h) in rectangles:

        # Create the clicking positions
        if random:
            center_x = np.random.randint(int(x + w * 0.1), int(x + w * 0.9))
            center_y = np.random.randint(int(y + w * 0.1), int(y + h * 0.9))
        else:
            center_x = int(x + w/2)
            center_y = int(y + h/2)

        coords.append((center_x, center_y))

    return coords



def targets_ordered_by_distance(position, targets):
    # our character is always in the center of the screen


    distances = np.array([sqrt((position[0] - i[0])**2 + (position[1] - i[1])**2) for i in targets])
    closest = np.argsort(distances)
    return closest


def calculate_distance(origin, target):
    return sqrt((origin[0] - target[0])**2 + (origin[1] - target[1])**2)

@in_true_space
def find_direction(origin, target):
    distance = calculate_distance(origin, target)
    return (target[0] - origin[0]) / distance, (target[1] - origin[1]) / distance


def find_barycentre(shapes: list):
    return [((p0[0] + p1[0] + p2[0] + p3[0])/4).astype(int) for (p0, p1, p2, p3) in shapes]


def calculate_area_rectangle(rectangle):
    d1 = calculate_distance(rectangle[0, 0], rectangle[1, 0])
    d2 = calculate_distance(rectangle[2, 0], rectangle[3, 0])
    return d1 * d2



