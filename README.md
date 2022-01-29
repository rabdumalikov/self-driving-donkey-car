# self-driving-donkey-car


## TASK 1(full self-driving with collision avoidance):
https://user-images.githubusercontent.com/29214569/151657866-a79e313b-0faa-4d0e-8150-36f45760b465.mp4

## TASK 2(self-driving with steering desire):
https://user-images.githubusercontent.com/29214569/151658079-6bdf933c-10d4-4b5c-98f0-cadd49be2656.mp4




In our solution, we used two different versions of donkeycar 4.2.0 and 4.3.0.
For training models, we used version 4.3.0 due to the availability of augmentations and transformations.

***Note that:** In version 4.2.0, augmentations and transformations are not implemented.*

On the car, we used 4.2.0. However, it makes more sense to switch to 4.3.0 because maintaining a single code base would be easier.
Right now, we have to maintain the same set of classes for *Behavioral* and *Linear* models, which is far from convenient. 
The only thing that stopped us from switching to 4.3.0 was the tedious integration process.

# Data
You can find the training data of both models [here](https://tartuulikool-my.sharepoint.com/:u:/g/personal/abdumali_ut_ee/Efh7AFRC8W1EiCAOUMqieiABL5MP3ss03D6UHnHFZ-c0BQ?e=e3puE2).

# Installation for training

For installing, donkeycar software, you have to follow steps from the official [documentation](https://docs.donkeycar.com/guide/install_software/#step-1-install-software-on-host-pc).

**Note that:** you have to use version 4.3.0, i.e., the master branch.

* **Installing prerequisites:**
  ```
  cd self-driving-donkey-car/train_src/donkeycar/
  cp -r * <path_to_folder_inside_installed_donkey> # for me it is /home/Rustam/donkeycar/donkeycar

  cd cd self-driving-donkey-car/train_src/mycar/
  cp * <path_mycar_folder>
  ```
* **Data preprocessing:**
  ```
  # THIS STEP ONLY REQUIRED FOR THE BEHAVIOR MODEL
  # Since collecting data with consistent behavior information is hard, we 
  # automated this process and discovered a good position for behavioral 
  # states that worked out quite well.
  python set_correct_behavior_offset.py <path_to_data>
  
  # Remove distortion from images and crop them.
  # For big dataset it might take up to two hours.
  python transform_images.py <path_to_data>
  
  # This script was written by Leo. All credits to him.
  # It flips the images and adjust corresponding meta information in catalogs. 
  python flipper.py -c <path_to_mycar> -t <path_to_data>
  ```
* **Training:**

  For some reason, during the training in version 4.3.0 the argument of *--type* option doesn't apply. The workaround for
  that is to set the type manually in the file donkeycar/donkeycar/utils.py in line 461.
  ```
  # Behavior model
  donkey train --tub <path_to_behavior_data>/* --model models/<model_name> --type custombehavior

  # Linear model  
  donkey train --tub <path_to_linear_data>/* --model models/<model_name> --type customlinear  
  ```
  
With those steps, you would be able to train **Behavioral** and **Linear** models.


# Installation inside the car

  * **Installing prerequisites:**
    ```
    cd self-driving-donkey-car/car_src/donkeycar/
    cp -r * /home/pi/donkeycar/donkeycar/

    cd cd self-driving-donkey-car/car_src/mycar/
    cp * /home/pi/mycar/
    ```
  * **Start autopilot:**
    ```
    # for Linear model
    python manage.py drive --model models/linear.h5 --type customlinear --js

    # for Behavior model
    python manage.py drive --model models/behavior.h5 --type custombehavior --js
    ```

# How it works:

## Linear model
Basically it is default linear model which goes with donkeycar. We created our own class 
**CustomLinear** which 99% is default linear model. The only thing we changed. Before the 
inference we applyid removing distoring and then cropped undistorted image. That's it.

### Why do we removed distortion from the image?
First of all our solution is based on [NVIDIA end-to-end driving](https://images.nvidia.com/content/tegra/automotive/images/2016/solutions/pdf/end-to-end-dl-using-px.pdf), where it is one of the 
preprossing that they used so are we. On top of that, we imperically saw that performance of the
model with distorted images is far from great. But it could be because of lightning conditions too.

### How do we cropped our images?
When you try to find good cropping, the main thing you need to know is that you have to remove useless information from the images. You can get it right only empirically. But sometimes useless information might be useful. For example, during the competition for task 1 second-round, our car was always hitting a small toy at the end of the track. We discovered the reason later. We cropped from the bottom by the amount that our car couldn't see that toy because we thought: "why do we need that much information about the floor?".

When you remove distortion from the image, you have less freedom for cropping.

**For Example:**
![undist_image](https://user-images.githubusercontent.com/29214569/151660471-8590a863-2ac3-4e92-ad08-ec041f77f2d2.jpeg)
Our cropping was **img=img[117:120,10:310]**.

## How many images we used?
We trained on less than 50k images, but the performance was terrible. With such a small number of
images, the car could not generalize track at all. But it was possible when we used around 100k images. 
In such a case, our car could drive in the configuration that it didn't see before. But increasing
the number of images doesn't help. I tried a model that was trained on 300k images. There was no difference between models trained on 100k images and 300k images. For competition linear model we used 150k images.


### How to fight lighting conditions?
Somehow the lighting conditions affect the performance of our models drastically even though we collected data during different times of the day.
We don't have an answer for that. In our competition models, we applied image brightness augmentation(available in 4.3.0). Maybe it helped.

### Takeout:
* The quantity isn't essential if the quality of your data is bad. *For better performance, steering should be smooth.*  The main reason for that is that we saw that our car was mainly doing sharp turns, leading to collisions in certain situations. But it is impossible to get smooth steering in the track with sharp turns.
* Use a smaller frame rate(10 frames per second) during data collection since with higher frame rate you would get useless images with pretty much the same information.
* Use higher resolution(320x240 or above). At least the resolution should be 320x240 because you won't be able to remove distortion for the lower resolution. Another point for higher resolution is that later you can downscale your image without losing quality, but it won't be true for upscaled images.

## Behavior model
It is almost default behavior model which goes with donkeycar. We created our own class 
**CustomBehavioral** which 93% similar to default model. 

### Things that we changes:
* Removed throttle prediction, because the data for that are inconsistent. 
* Applied image augmentation before inference such as removing distortion and cropping.
* Mapped left and right states to two different buttons for easy control. On top of that, left and right states are on a 0.30ms timer, after which the car automatically switched to a straight state. The main reason for that is that we want to be in a correct state longer during long turns. That's why by pressing a particular state button several times, the timer adds up.
* Our car was stucking during right turnes, so for short period of time we increased throttle.

### How we collected data?
At first, we tried to collect data properly by pressing the correct state before turning. This approach didn't work because of human error, and as a result, the data was inconsistent. Afterward, we wrote a script that consistently put behavior states on steering angle value.

### Cropping:
Was the same as for **CustomLinear**.

### How many images we used?
We used around 350k images.

### Takeout:
* Overall, it is hard to train a behavior model to self-drive without any nudges.
* Behavior states should be consistent with your data.
  




