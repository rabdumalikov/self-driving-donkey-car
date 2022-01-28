import numpy as np
from typing import Dict, Any, Tuple, Optional, Union
from donkeycar.pipeline.types import TubRecord
from donkeycar.utils import normalize_image

# type of x
XY = Union[float, np.ndarray, Tuple[float, ...], Tuple[np.ndarray, ...]]

import donkeycar.parts.custom_utilities as cs
from donkeycar.parts.keras import KerasPilot, default_n_linear

class CustomLinear(KerasPilot):
    """
    The KerasLinear pilot uses one neuron to output a continous value via the
    Keras Dense layer with linear activation. One each for steering and
    throttle. The output is not bounded.
    """
    def __init__(self, num_outputs=2, input_shape=(83,300,3)):
        super().__init__()
        self.model = default_n_linear(num_outputs, (83,300,3))

    def compile(self):
        self.model.compile(optimizer=self.optimizer, loss='mse')

    def run(self, img_arr: np.ndarray, other_arr: np.ndarray = None) \
             -> Tuple[Union[float, np.ndarray], ...]:

        # Cropping
        img = cs.image_to_83_by_300( img_arr ) 

        norm_arr = normalize_image( img )
        np_other_array = np.array(other_arr) if other_arr else None
        return self.inference(norm_arr, np_other_array)

    def inference(self, img_arr, other_arr):
        outputs = self.model.predict(np.array([img_arr]))

        steering = outputs[0][0]

        return steering, 0

    def y_transform(self, record: TubRecord):
        angle: float = record.underlying['user/angle']
        throttle: float = record.underlying['user/throttle']
        return angle, throttle

    def y_translate(self, y: XY) -> Dict[str, Union[float, np.ndarray]]:
        if isinstance(y, tuple):
            angle, throttle = y
            return {'n_outputs0': angle, 'n_outputs1': throttle}
        else:
            raise TypeError('Expected tuple')

    def output_shapes(self):
        # need to cut off None from [None, 120, 160, 3] tensor shape
        img_shape = self.get_input_shape()[1:]
        shapes = ({'img_in': tf.TensorShape(img_shape)},
                  {'n_outputs0': tf.TensorShape([]),
                   'n_outputs1': tf.TensorShape([])})
        return shapes
