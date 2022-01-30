# self-driving-donkey-car


## TASK 1(full self-driving with collision avoidance):
https://user-images.githubusercontent.com/29214569/151681847-144bfa37-1817-4665-8097-7149bb9f8f89.mp4


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

**Note that:** you have to use version 4.3.0, i.e., the **dev** branch.

* **Installing prerequisites:**
  * Integrate modifications inside **donkeycar** folder:
    ```sh
    cd self-driving-donkey-car/train_src/donkeycar/
    cp -r * <path_to_folder_inside_installed_donkey> # for me it is /home/Rustam/donkeycar/donkeycar
    ```
  * Integrate modifications inside **mycar** folder:
    ```sh    
    cd self-driving-donkey-car/train_src/mycar/
    cp * <path_to_mycar_folder>
    ```
* **Data preprocessing:**
  
  * **FOR THE BEHAVIOR MODEL ONLY:**
    ```sh
    # Collecting data with consistent behavior information is challenging. We automated this 
    # process and discovered a good position for behavioral states that worked out 
    # quite well during competition because the car was acting instantaneously.
    python set_correct_behavior_offset.py <path_to_data>
    ```
  * **Remove distortion from images and crop them:**
    ```sh
    # For big dataset it might take up to two hours.
    python transform_images.py <path_to_data>
    ```
  * **Flips images and adjust the corresponding meta-information in catalogs:**
    ```sh
    # Leo wrote this script. All credits go to him.
    python flipper.py -c <path_to_mycar> -t <path_to_data>
    ```
* **Training:**

  For some reason, during the training in version 4.3.0 the argument of *--type* option doesn't apply. The workaround for
  that is to set the type manually in the file donkeycar/donkeycar/utils.py in line 461.
  ```sh
  # Behavior model
  donkey train --tub <path_to_behavior_data>/* --model models/<model_name> --type custombehavior

  # Linear model  
  donkey train --tub <path_to_linear_data>/* --model models/<model_name> --type customlinear  
  ```
  
With those steps, you would be able to train **Behavioral** and **Linear** models.


# Installation inside the car

  * **Installing prerequisites:**
    * Integrate modifications inside **donkeycar** folder:
      ```sh
      cd self-driving-donkey-car/car_src/donkeycar/
      cp -r * /home/pi/donkeycar/donkeycar/
      ```
    * Integrate modifications inside **mycar** folder:
      ```sh    
      cd self-driving-donkey-car/car_src/mycar/
      cp * /home/pi/mycar/
      ```
  * **Start autopilot:**
    ```sh
    # for Linear model
    python manage.py drive --model models/linear.h5 --type customlinear --js

    # for Behavior model
    python manage.py drive --model models/behavior.h5 --type custombehavior --js
    ```

# How it works:

## Linear/Task1 model
We created our own class **CustomLinear** which 99% is default linear model. 
The only thing we changed was that we added before the inference image preprocessing steps such as removing distortion and cropping an image.

### Why do we removed distortion from the image?
First of all, our solution is based on [NVIDIA end-to-end driving](https://images.nvidia.com/content/tegra/automotive/images/2016/solutions/pdf/end-to-end-dl-using-px.pdf), where it is one of the 
preprocessing step that they used. On top of that, in our tests, we saw that performance of the
a model with distorted images is far from great. But it could be because of lighting conditions too.

### How do we cropped our images?
When you try to find good cropping, the main thing you need to know is that you have to remove useless information from the images. You can get it right only empirically. But sometimes useless information might be useful. For example, during the competition for task 1 second-round, our car was always hitting a small toy at the end of the track. We discovered the reason for that later. We cropped from the bottom by the amount that our car couldn't see that toy. Before we thought: "why do we need that much information about the floor?".

Nevertheless, here is crop that we used **img=img[117:120,10:310]**.

When you remove distortion from the image, you have less freedom for cropping.
Consider the image below. You can see that distortion is only removed around the center.
Thus it is the only part that makes sense to crop.

**For Example:**

<img src= "https://user-images.githubusercontent.com/29214569/151660471-8590a863-2ac3-4e92-ad08-ec041f77f2d2.jpeg" title="Undistorted image" width="600" height="400">

## How many images did we use?
When we trained on less than 50k images, the performance was terrible. With such a small number of
images, the car could not generalize track at all. But it was possible when we used around 100k images. 
In such a case, our car could drive in the configuration that it didn't see before. But increasing
the number of images doesn't help. I tried a model that was trained on 300k images. There was no difference between models trained on 100k images and 300k images. For the competition for the task1 model, we used approximately 150k images.

### How to fight lighting conditions?
Somehow the lighting conditions affect the performance of our models drastically even though we collected data during different times of the day.
We don't have an answer for that. In our competition models, we applied image brightness augmentation(available in 4.3.0). Maybe it helped.

### Main takeaways:
* The quantity isn't essential if the quality of your data is bad. *For better performance, steering should be smooth.*  The main reason for that is that we saw that our car was mainly doing sharp turns, leading to collisions in certain situations. But it is impossible to get smooth steering in the track with sharp turns.
* Use a smaller frame rate(10 frames per second) during data collection since with higher frame rate you would get useless images with pretty much the same information. 

  However, for inference, you can play around with frame rate, i.e., **increase it => more decisions** or **decrease it => fewer decisions** your car could make. For example, in the competition during the second round of task1, we increased the frame rate from 10 to 15 because we assumed that the car sees the obstacle but doesn't have enough frames to avoid it. 
* Use higher resolution(320x240 or above). The resolution should be at least 320x240 because you won't be able to remove distortion for the lower resolutions. Another point for higher resolution is that later you can downscale your image without losing quality, but it won't be true if you need to upscale images.

## Behavior/Task2 model
For **Behavior model**, we also created the custom class **CustomBehavioral** based on the default behavior model. 
But we did a lot more work to make it work.

### Things that we added/changed:
* Removed throttle prediction, because the data for that are inconsistent. 
* Applied image augmentation before inference such as removing distortion and cropping.
* Mapped *left* and *right* states to two different buttons for easier control. On top of that, *left* and *right* states are on a 0.30ms timer, after which the car automatically switches to a straight state. The main reason for using a timer is that we want to control the duration of being in a specific state, for example, during long turns. That's why by pressing a particular state button several times, the timer adds up.

  https://user-images.githubusercontent.com/29214569/151705186-0a6cb852-ce32-41c2-b32c-a0cdb7f270fb.mp4

* Our car tends to be stuck during right turns, so during the right turns we increase the throttle for a short time.

### How did we collect data?
At first, we tried to collect data properly by pressing the correct state before turning. This approach didn't work because of human error, and as a result, the data was inconsistent. Afterward, we wrote a script that consistently put behavior states based on steering angle value.

### Cropping:
Was the same as for **CustomLinear**.

### How many images did we use?
We used around 350k images.

### Main takeaways:
* Overall, it is hard to train a behavior model to drive on its own without any nudges.
* Behavior states should be consistent with your data.
* Use 10 frames per second for inference and data collection. With a higher frame rate, the performance of the behavioral model was terrible. 
  
# Main Contributors
Rustam Abdumalikov and Aral Acikalin

# Licence
Boost Software License( Version 1.0 )


