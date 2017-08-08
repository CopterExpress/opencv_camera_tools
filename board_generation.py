import cv2.aruco

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)
board = cv2.aruco.CharucoBoard_create(32, 28, 0.032, 0.024, dictionary)
img = board.draw((3200, 2800))
cv2.imwrite('charuco_5x5-1000_32x28_0.032-0.024.png', img)
img = board.draw((6400, 5600))
cv2.imwrite('charuco_5x5-1000_32x28_0.032-0.024_large.png', img)

# 75x75 px marker -- 2.4 cm
# 100x100 px square -- 3.2 cm
