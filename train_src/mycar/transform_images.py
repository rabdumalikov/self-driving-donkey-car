import sys
import cv2
import glob
#import matplotlib.pyplot as plt
import pickle

directory = sys.argv[1] + '/'

calib_result_pickle = pickle.load(open("car_camera_320x240_calib_pickle.p", "rb" ))
mtx = calib_result_pickle["mtx"]
newcameramtx = calib_result_pickle["optimal_camera_matrix"]
dist = calib_result_pickle["dist"]
roi = calib_result_pickle["roi"]

print( "started..." )
        
for folder in glob.glob(directory+'*'):
    for fname in glob.glob(folder + '/images/*.jpg'):
        try:
            img = cv2.imread( fname )
        
            img = cv2.undistort(img, mtx, dist, None, newcameramtx)
            img = img[117:200,10:310]

            cv2.imwrite(fname,img)
        except Exception as e:
            print("EXCEPTION", e)


