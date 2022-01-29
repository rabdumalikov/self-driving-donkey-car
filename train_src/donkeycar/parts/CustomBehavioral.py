
import numpy as np
from typing import Dict, Any, Tuple, Optional, Union, List
from donkeycar.pipeline.types import TubRecord
from donkeycar.utils import normalize_image, linear_bin
import donkeycar as dk
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.layers import Activation, Dropout, Flatten
from tensorflow.keras.backend import concatenate
from tensorflow.keras.models import Model, Sequential
from donkeycar.parts.interpreter import Interpreter, KerasInterpreter
from donkeycar.parts.keras import KerasBehavioral, core_cnn_layers
import tensorflow as tf

# type of x
XY = Union[float, np.ndarray, Tuple[float, ...], Tuple[np.ndarray, ...]]

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

class CustomBehavioral(KerasBehavioral):
    """
    A Keras part that take an image and Behavior vector as input,
    outputs steering and throttle
    """
    def __init__(self,
                 interpreter: Interpreter = KerasInterpreter(),
                 input_shape: Tuple[int, ...] = (83, 300, 3),
                 throttle_range: float = 0.5,
                 num_behavior_inputs: int = 3):
        self.num_behavior_inputs = num_behavior_inputs

        super().__init__(interpreter, input_shape, throttle_range, num_behavior_inputs=self.num_behavior_inputs)

    def create_model(self):
        return custom_bhv(num_bvh_inputs=self.num_behavior_inputs,
                           input_shape=(83, 300, 3))

    def compile(self):
        self.interpreter.compile(
            optimizer=self.optimizer,
            metrics=['accuracy'],
            loss={'angle_out': 'categorical_crossentropy'},
            loss_weights={'angle_out': 0.5})

    def interpreter_to_output(self, interpreter_out):
        angle_binned = interpreter_out
        return dk.utils.linear_unbin(angle_binned)

    def y_transform(self, record: Union[TubRecord, List[TubRecord]]) -> XY:
        assert isinstance(record, TubRecord), "TubRecord expected"
        angle: float = record.underlying['user/angle']
        angle = linear_bin(angle, N=15, offset=1, R=2.0)
        return (angle)

    def y_translate(self, y: XY) -> Dict[str, Union[float, List[float]]]:      
        return {'angle_out': y}

    def output_shapes(self):
        # need to cut off None from [None, 120, 160, 3] tensor shape
        img_shape = self.get_input_shapes()[0][1:]
        # the keys need to match the models input/output layers
        shapes = ({'img_in': tf.TensorShape(img_shape),
                   'xbehavior_in': tf.TensorShape([self.num_behavior_inputs])},
                  {'angle_out': tf.TensorShape([15])})
        return shapes
