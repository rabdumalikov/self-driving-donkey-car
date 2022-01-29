# self-driving-donkey-car


## TASK 1(full self-driving with collision avoidance):
https://user-images.githubusercontent.com/29214569/151657866-a79e313b-0faa-4d0e-8150-36f45760b465.mp4

## TASK 2(self-driving with steering desire):
https://user-images.githubusercontent.com/29214569/151658079-6bdf933c-10d4-4b5c-98f0-cadd49be2656.mp4




In our solution, we used two different versions of donkeycar 4.2.0 and 4.3.0.
For training, we used 4.3.0 because augmentations and transformations are working correctly in that version.
However, it is not the case for version 4.2.0.

On the car, we used 4.2.0. We could also switch to 4.3.0. Then in such a case, it would be easier to maintain a single code base. 
Right now, we have to maintain the same set of classes for *Behavioral* and *Linear* models, which is far from convenient. But switching to 4.3.0 would require dealing with some errors.

This folder **car_src** contains code that should be used on the car, and the folder **train_src** should be used for training.
# Data
Data for the training both models can be found [here](https://tartuulikool-my.sharepoint.com/:u:/g/personal/abdumali_ut_ee/Efh7AFRC8W1EiCAOUMqieiABL5MP3ss03D6UHnHFZ-c0BQ?e=e3puE2).

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
* **Data processing:**
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


  




