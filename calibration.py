import cv2.aruco
import pickle
import io
import time

# dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_100)
# board = cv2.aruco.CharucoBoard_create(10, 14, 0.018, 0.012, dictionary)
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)
board = cv2.aruco.CharucoBoard_create(32, 28, 0.032, 0.024, dictionary)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2592)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1944)

allCorners = []
allIds = []
decimator = 0

for i in range(3000):
    ret,frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    res = cv2.aruco.detectMarkers(gray, dictionary)
    if len(res[0])>0:
        res2 = cv2.aruco.interpolateCornersCharuco(res[0],res[1],gray,board)
        if res2[0]:
            print "\t".join([str(decimator), str(len(res2[1]))])
        if res2[1] is not None and res2[2] is not None and len(res2[1])>100 and cv2.waitKey(1) & 0xFF == ord('c'):
            allCorners.append(res2[1])
            allIds.append(res2[2])
            filename = 'photos_for_calib/' + str(decimator) + '.jpg'
            cv2.imwrite(filename, gray)
            decimator += 1
        cv2.aruco.drawDetectedMarkers(gray,res[0],res[1])
    smallFrame = cv2.resize(gray, (gray.shape[1]/16, gray.shape[0]/16))
    cv2.imshow('frame', smallFrame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cornersFile = io.open("allCorners.pickle", "wb")
idsFile = io.open("allIds.pickle", "wb")
pickle.dump(allCorners, cornersFile)
pickle.dump(allIds, idsFile)
cornersFile.close()
idsFile.close()

'''
allCorners = pickle.load(io.open("allCorners.pickle", "rb"))
allIds = pickle.load(io.open("allIds.pickle", "rb"))
'''

imsize = gray.shape

try:
    print "Calibration started"
    # cal = cv2.aruco.calibrateCameraCharuco(allCorners,allIds,board,imsize,None,None)
    cal = cv2.aruco.calibrateCameraCharucoExtended(allCorners,allIds,board,imsize,None,None, flags=cv2.CALIB_RATIONAL_MODEL)
    print cal[0]
    outFile = io.open("out2.pickle", "wb")
    pickle.dump(cal, outFile)
    outFile.close()
except:
    pass

cv2.destroyAllWindows()
