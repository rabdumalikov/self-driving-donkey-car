# MM1_STEERING_MID = 1585
MM1_MAX_FORWARD = 1620 #1650  # 1620 Middle Value, Max is 2000
MM1_MAX_REVERSE = 1300
MM1_STOPPED_PWM = 1500
MM1_SHOW_STEERING_VALUE = False
MM1_SERIAL_PORT = '/dev/ttyS0'


TRAIN_BEHAVIORS = True
BEHAVIOR_LIST = ["Left",'Straight', "Right"]#, 'Mixed']


#LOGGING
HAVE_CONSOLE_LOGGING = True
LOGGING_LEVEL = 'INFO'          # (Python logging level) 'NOTSET' / 'DEBUG' / 'INFO' / 'WARNING' / 'ERROR' / 'FATAL' / 'CRITICAL'
LOGGING_FORMAT = '%(message)s'  # (Python logging format - https://docs.python.org/3/library/logging.html#formatter-objects


#STEERING
STEERING_CHANNEL = 1            #channel on the 9685 pwm board 0-15
STEERING_RIGHT_PWM=10
STEERING_LEFT_PWM=10

#THROTTLE
THROTTLE_CHANNEL = 0            #channel on the 9685 pwm board 0-15
THROTTLE_FORWARD_PWM = 430      #pwm value for max forward throttle
THROTTLE_STOPPED_PWM = 370      #pwm value for no movement
THROTTLE_REVERSE_PWM = 320      #pwm value for max reverse throttle

DRIVE_TRAIN_TYPE = "MM1"

JOYSTICK_MAX_THROTTLE = 1.0
JOYSTICK_THROTTLE_DIR = -1.0

# ROI_CROP_TOP = 60                    #the number of rows of pixels to ignore on the top of the image
# ROI_CROP_BOTTOM = 10                 #the number of rows of pixels to ignore on the bottom of the image
# ROI_CROP_LEFT=0
# ROI_CROP_RIGHT=0

#AUGMENTATIONS = ['MULTIPLY', 'BLUR']
#TRANSFORMATIONS = ['CROP']

CONTROLLER_TYPE='F710'           #(ps3|ps4)
DRIVE_LOOP_HZ = 10

if (CONTROLLER_TYPE=='F710'):
    JOYSTICK_DEADZONE = 0.1
AUTO_CREATE_NEW_TUB = True
# #CAMERA
CAMERA_TYPE = "PICAM"   # (PICAM|WEBCAM|CVCAM|CSIC|V4L|MOCK)
IMAGE_W = 320 #160
IMAGE_H = 240 #120
IMAGE_DEPTH = 3
