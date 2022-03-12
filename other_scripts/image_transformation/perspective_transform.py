# import necessary libraries

import cv2
import numpy as np

frame = cv2.imread("sample_capture.png", cv2.IMREAD_COLOR)

# We scale
matrix = np.float32([[1, 0,   0],
                     [0, 1.5, 0],
                     [0, 0,   1]])

print(matrix)
result = cv2.warpPerspective(frame, matrix, (2880, 1800))
result = cv2.resize(result, (720, 480))

# Wrap the transformed image
cv2.imshow('frame', frame)  # Initial Capture
cv2.imshow('frame1', result)  # Transformed Capture

cv2.waitKey()
