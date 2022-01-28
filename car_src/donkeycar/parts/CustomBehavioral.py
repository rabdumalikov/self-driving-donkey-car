import numpy as np
from typing import Dict, Any, Tuple, Optional, Union
from donkeycar.pipeline.types import TubRecord
from donkeycar.utils import normalize_image, linear_bin
import donkeycar as dk
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.layers import Activation, Dropout, Flatten
from tensorflow.keras.backend import concatenate
from tensorflow.keras.models import Model, Sequential

from donkeycar.parts.keras import KerasPilot, core_cnn_layers

# type of x
XY = Union[float, np.ndarray, Tuple[float, ...], Tuple[np.ndarray, ...]]


import donkeycar.parts.custom_utilities as cs

def custom_bhv(num_bvh_inputs, input_shape):
    drop = 0.2
    img_in = Input(shape=input_shape, name='img_in')
    # tensorflow is ordering the model inputs alphabetically in tensorrt,
    # so behavior must come after image, hence we put an x here in front.
    bvh_in = Input(shape=(num_bvh_inputs,), name="xbehavior_in")

    x = core_cnn_layers(img_in, drop)
    x = Dense(100, activation='relu')(x)
    x = Dropout(.1)(x)

    y = bvh_in
    y = Dense(num_bvh_inputs * 2, activation='relu')(y)
    y = Dense(num_bvh_inputs * 2, activation='relu')(y)
    y = Dense(num_bvh_inputs * 2, activation='relu')(y)

    z = concatenate([x, y])
    z = Dense(100, activation='relu')(z)
    z = Dropout(.1)(z)
    z = Dense(50, activation='relu')(z)
    z = Dropout(.1)(z)

    # Categorical output of the angle into 15 bins
    angle_out = Dense(15, activation='softmax', name='angle_out')(z)

    model = Model(inputs=[img_in, bvh_in], outputs=[angle_out], name='behavioral')

    return model

class CustomBehavioral(KerasPilot):
    """
    A Keras part that take an image and Behavior vector as input,
    outputs steering and throttle
    """
    def __init__(self, num_behavior_inputs=2, input_shape=(83, 300, 3), ctr=None):
        super(CustomBehavioral, self).__init__()
        self.model = custom_bhv(num_bvh_inputs=num_behavior_inputs, input_shape=(83, 300, 3))
        self.ctr=ctr
        self.currentThrottleFactor=None

    def run(self, img_arr: np.ndarray, other_arr: np.ndarray = None) \
             -> Tuple[Union[float, np.ndarray], ...]:

        # Cropping
        img = cs.image_to_83_by_300( img_arr )     

        norm_arr = normalize_image( img )
        np_other_array = np.array(other_arr) if other_arr else None
        return self.inference(norm_arr, np_other_array)

    def inference(self, img_arr, state_array):
        img_arr = np.array(img_arr).reshape((1,) + img_arr.shape)
        bhv_arr = state_array.reshape(1, len(state_array))
        
        angle_binned = self.model.predict([img_arr, bhv_arr])
        angle_unbinned = dk.utils.linear_unbin(angle_binned)

        print( f"STEERING_ANGLE={angle_unbinned}" )
        
        # Short speed increase
        cs.apply_short_momentum( self, angle_unbinned, self.ctr )

        return angle_unbinned, 0 #throttle

    def compile(self):
        self.model.compile(optimizer=self.optimizer, loss='mse')

    def interpreter_to_output(self, interpreter_out):
        angle_binned = interpreter_out

        return dk.utils.linear_unbin(angle_binned)

    def y_transform(self, record: TubRecord):
        angle: float = record.underlying['user/angle']
        angle = linear_bin(angle, N=15, offset=1, R=2.0)
        return {'angle_out': angle}

    def output_shapes(self):
        # need to cut off None from [None, 120, 160, 3] tensor shape
        img_shape = self.get_input_shapes()[0][1:]
        # the keys need to match the models input/output layers
        shapes = ({'img_in': tf.TensorShape(img_shape),
                   'xbehavior_in': tf.TensorShape([self.num_behavior_inputs])},
                  {'angle_out': tf.TensorShape([15])})
        return shapes
