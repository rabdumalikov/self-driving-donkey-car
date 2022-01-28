import glob
import os
import shutil

######## Choose the right directory! #########
directory = '/home/pi/mycar/data/'

for folder in glob.glob(directory+'*'):
    splits = folder.split('_')
    num = int( splits[1] )
    if num <= 62:
        #print(folder)
        shutil.rmtree(folder)
    elif len(glob.glob( folder+ '/images/*' )) <= 1500:
        print( folder  )
        shutil.rmtree(folder)
