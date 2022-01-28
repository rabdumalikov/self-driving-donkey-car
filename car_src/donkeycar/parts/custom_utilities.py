import pickle
import cv2

calib_result_pickle = pickle.load(open("/home/pi/mycar/car_camera_320x240_calib_pickle.p", "rb" ))
mtx = calib_result_pickle["mtx"]
newcameramtx = calib_result_pickle["optimal_camera_matrix"]
dist = calib_result_pickle["dist"]
roi = calib_result_pickle["roi"]

# Removes image distortion and crops it
def image_to_83_by_300( img ):
    global calib_result_pickle
    global mtx
    global newcameramtx
    global dist
    global roi

    img = cv2.undistort(img, mtx, dist, None, newcameramtx)

    return img[117:200,10:310]

## Those donkey cars have problem that they are stop moving during turning right with low throttle.
## This part increases throttle_scale for a short period of time
def apply_short_momentum( model, angle, ctr ):
    if ctr == None:
        return

    if angle > 0.5:
        if model.currentThrottleFactor == None:
            model.currentThrottleFactor=ctr.throttle_scale
        ctr.throttle_scale=0.8
        ctr.increase_max_throttle()
    elif not model.currentThrottleFactor == None:
        ctr.throttle_scale=model.currentThrottleFactor
        model.currentThrottleFactor=None
        ctr.decrease_max_throttle()
        ctr.increase_max_throttle()

## Calculate quantitative value of difference between two images 
def image_diff( prev_image, new_image ):

    gray_image_1 = cv2.cvtColor(prev_image, cv2.COLOR_BGR2GRAY)
    gray_image_2 = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
    difference = cv2.subtract(gray_image_1, gray_image_2)

    return np.sum(difference[:])
