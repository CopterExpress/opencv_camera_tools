from __future__ import division

import math
from itertools import izip
import cv2.aruco
import numpy as np

from px2meters import CameraModel


FRAME_WIDTH = 2592
FRAME_HEIGHT = 1944
FOV = math.radians(140)

ALTITUDE = 0.5

# Coeffs for RPi Camera (G)
ORIG_CAMERA_MATRIX = np.array([[ 851.97704662,    0.        ,  831.2243264 ],
                               [   0.        ,  855.15220764,  563.7543571 ],
                               [   0.        ,    0.        ,    1.        ]])
ORIG_CAMERA_WIDTH = 1640
ORIG_CAMERA_HEIGHT = 1232
DIST_COEFFS = np.array([[  2.15356885e-01,  -1.17472846e-01,  -3.06197672e-04,
                          -1.09444025e-04,  -4.53657258e-03,   5.73090623e-01,
                          -1.27574577e-01,  -2.86125589e-02,   0.00000000e+00,
                           0.00000000e+00,   0.00000000e+00,   0.00000000e+00,
                           0.00000000e+00,   0.00000000e+00]])

camera_matrix = ORIG_CAMERA_MATRIX * FRAME_WIDTH / ORIG_CAMERA_WIDTH
camera_matrix[0, 2] = ORIG_CAMERA_MATRIX[0, 2] * FRAME_HEIGHT / ORIG_CAMERA_HEIGHT
camera_matrix[1, 2] = ORIG_CAMERA_MATRIX[1, 2] * FRAME_HEIGHT / ORIG_CAMERA_HEIGHT
camera_matrix[2, 2] = 1.0

new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix,
                                                       DIST_COEFFS,
                                                       (FRAME_WIDTH, FRAME_HEIGHT),
                                                       1,
                                                       (FRAME_WIDTH, FRAME_HEIGHT))

camera_model = CameraModel(FRAME_WIDTH, FRAME_HEIGHT, FOV, camera_matrix, DIST_COEFFS, new_camera_matrix)

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
# dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)
board = cv2.aruco.CharucoBoard_create(10, 14, 0.018, 0.012, dictionary)
# board = cv2.aruco.CharucoBoard_create(32, 28, 0.032, 0.024, dictionary)

charuco_board_d = {i: corner for i, corner in enumerate(board.chessboardCorners)}

capture = cv2.VideoCapture(0)
capture.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
capture.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

while(True):
    _, frame = capture.read()
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    undist_frame = cv2.undistort(gray_frame, camera_matrix, DIST_COEFFS, newCameraMatrix=new_camera_matrix)
    aruco_corners, aruco_ids, _ = cv2.aruco.detectMarkers(gray_frame, dictionary)
    
    if len(aruco_corners) > 0:
        # cv2.aruco.drawDetectedMarkers(gray_frame, aruco_corners, aruco_ids)
        charuco_detected, charuco_corners, charuco_ids_in_numpy = cv2.aruco.interpolateCornersCharuco(aruco_corners,
                                                                                                      aruco_ids,
                                                                                                      gray_frame,
                                                                                                      board,
                                                                                                      None,
                                                                                                      None,
                                                                                                      camera_matrix,
                                                                                                      DIST_COEFFS)
        
        if charuco_detected:
            charuco_ids = [id_in_numpy[0] for id_in_numpy in charuco_ids_in_numpy]
            
            undist_charuco_corners = cv2.undistortPoints(charuco_corners, camera_matrix, DIST_COEFFS, P=new_camera_matrix)
            
            assert len(charuco_ids) == len(undist_charuco_corners)
            charuco_corners_d = {id_: coordinates for id_, coordinates in izip(charuco_ids, undist_charuco_corners)}
            
            for id_, coordinates in charuco_corners_d.items():
                coordinates_meters = camera_model.px2meters(coordinates[0][0], coordinates[0][1], ALTITUDE)
                print "%s\t%s\t%s" % (str(id_), str(charuco_board_d[id_]), str(coordinates_meters))
            print "--------------------------"
            
            cv2.aruco.drawDetectedCornersCharuco(undist_frame, undist_charuco_corners, charuco_ids_in_numpy)
            pose_detected, pose_rvec, pose_tvec = cv2.aruco.estimatePoseCharucoBoard(charuco_corners,
                                                                                     charuco_ids_in_numpy,
                                                                                     board,
                                                                                     camera_matrix,
                                                                                     DIST_COEFFS)
            
            if pose_detected:
                print pose_rvec
                print pose_tvec
                print "==========================="
                cv2.aruco.drawAxis(undist_frame, camera_matrix, DIST_COEFFS, pose_rvec, pose_tvec, 0.1)

    small_frame = cv2.resize(undist_frame, (undist_frame.shape[1]/4, undist_frame.shape[0]/4))
    # crop = gray[(gray_frame.shape[0]/2 - 150):(gray_frame.shape[0]/2 + 150),
    #             (gray_frame.shape[1]/2 - 150):(gray_frame.shape[1]/2 + 150)]
    cv2.imshow('frame', small_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
