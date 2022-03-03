import numpy as np


def project_target(projection_matrix, target):

    target = np.array(target)
    new_target = np.matmul(projection_matrix, target)

    return new_target


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
                      [0, 1.5]])
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
        ret = project_targets(B, ret)

        return ret

    return new_function


def find_targets(rectangles):

    coords = []
    # If there are resources
    for (x, y, w, h) in rectangles:

        # Create the clicking positions
        center_x = np.random.randint(int(x + w * 0.1), int(x + w * 0.9))/2
        center_y = np.random.randint(int(y + w * 0.1), int(y + h * 0.9))/2
        coords.append((center_x, center_y))

    return coords


@in_true_space
def targets_ordered_by_distance(position, targets):
    # our character is always in the center of the screen

    distances = np.array([np.abs(position[0] - i[0]) + np.abs(position[1] - i[1]) for i in targets])
    closest = np.argsort(distances)
    new_targets = [targets[i] for i in closest]

    return new_targets

