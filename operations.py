from if_tool import ToolIface
from if_model import Model, ModelOperation
from typing import List, Dict, Any, Optional

class ModelRigidTransform(ToolIface):
    """
    A tool for performing rigid transformations on 3D models.
    This tool can translate, rotate, and scale models.
    """
    
    def __init__(self):
        super().__init__(
            name="transform_rigid",
            description="A tool to perform rigid transformations on 3D models.",
            parameters={
                "model": {"type": "string", "description": "The model to be transformed", "required": True},
                "translation": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0.0, 0.0, 0.0]},
                "rotation": {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3, "default": [0.0, 0.0, 0.0]},
                "scale": {"type": "number", "default": 1.0}
            },
            tool_type="operation"
        )
    
    def call(self, models: List[Model], model: str, translation: List[float] = [0.0, 0.0, 0.0], 
             rotation: List[float] = [0.0, 0.0, 0.0], scale: float = 1.0) -> ModelOperation:
        """
        Perform a rigid transformation on the specified model.
        
        :param models: List of models to apply the transformation to.
        :param model: The model to be transformed.
        :param translation: Translation vector [tx, ty, tz].
        :param rotation: Rotation vector [rx, ry, rz] in radians.
        :param scale: Scaling factor.
        :return: A ModelOperation object representing the transformation.
        """
        if not isinstance(models, list):
            raise ValueError("models must be a list of Model objects.")
        
        if not isinstance(model, str):
            raise ValueError("model must be a string representing the model name.")
        
        # Create a ModelOperation instance with the provided parameters
        operation = ModelOperation(
            type="transform_rigid",
            description="Rigid transformation operation",
            models=[model],
            parameters={
                "translation": translation,
                "rotation": rotation,
                "scale": scale
            },
        )
        
        return operation

import unittest

class TestModelRigidTransform(unittest.TestCase):
    def call_missing_part_of_parameters(self):
        parameters = {
            "translation": [1.0, 2.0, 3.0],
            "rotation": [0.1, 0.2, 0.3],
            # "scale" is missing
        }

        tool = ModelRigidTransform()
        model