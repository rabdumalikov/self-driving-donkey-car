
import numpy as np
from donkeycar.parts.keras import KerasLinear
from donkeycar.parts.interpreter import Interpreter, KerasInterpreter
from typing import Dict, Any, Tuple, Optional, Union

class CustomLinear(KerasLinear):
    """
    Basically it is KerasLinear
    """
    def __init__(self,
                 interpreter: Interpreter = KerasInterpreter(),
                 input_shape: Tuple[int, ...] = (83,300,3),
                 num_outputs: int = 2):
        self.num_outputs = num_outputs
        self.input_shape = (83,300,3)
        super().__init__(interpreter, self.input_shape)
