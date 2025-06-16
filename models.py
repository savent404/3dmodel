from if_tool import ToolIface
from if_model import Model


class ModelCube(ToolIface):
    """
    A tool for creating a cube model with specified dimensions and coordinates.
    """
    def __init__(self, name: str):
        description = "Create a cube model"
        parameters = {
            "width": {
                "type": "float",
                "description": "Width of the cube",
                "default": 1.0,
                "required": True
            },
            "height": {
                "type": "float",
                "description": "Height of the cube",
                "default": 1.0,
                "required": True
            },
            "depth": {
                "type": "float",
                "description": "Depth of the cube",
                "default": 1.0,
                "required": True
            },
        }
        super().__init__(name, description, parameters)

    def call(self, width: float, height: float, depth: float) -> Model:
        box = [width, height, depth]
        extra = {
            "width": width,
            "height": height,
            "depth": depth,
        }
        model = Model(
            name=self.name,
            description=self.description,
            type="cube",
            coord_x=0.0,
            coord_y=0.0,
            coord_z=0.0,
            box_size=box,
            orientation_pitch=0.0,
            orientation_yaw=0.0,
            orientation_roll=0.0,
            model_data=extra
        )
        return model

import unittest

class TestModelCube(unittest.TestCase):
    def test_call(self):
        cube = ModelCube(name="TestCube")
        model = cube.call(width=2.0, height=3.0, depth=4.0)
        self.assertEqual(model.name, "TestCube")
        self.assertEqual(model.type, "cube")
        self.assertEqual(model.box_size, [2.0, 3.0, 4.0])
        self.assertEqual(model.coord_x, 0.0)
        self.assertEqual(model.coord_y, 0.0)
        self.assertEqual(model.coord_z, 0.0)
        self.assertEqual(model.orientation_pitch, 0.0)
        self.assertEqual(model.orientation_yaw, 0.0)
        self.assertEqual(model.orientation_roll, 0.0)
    def test_to_dict(self):
        cube = ModelCube(name="TestCube")
        model = cube.call(width=2.0, height=3.0, depth=4.0)
        model_dict = model.to_dict()
        expected_dict = {
            "name": "TestCube",
            "description": "Create a cube model at (0,0,0)",
            "type": "cube",
            "coord_x": 0.0,
            "coord_y": 0.0,
            "coord_z": 0.0,
            "box_size": [2.0, 3.0, 4.0],
            "orientation_pitch": 0.0,
            "orientation_yaw": 0.0,
            "orientation_roll": 0.0,
            "model_data": None
        }
        self.assertEqual(model_dict, expected_dict)
    def test_to_json(self):
        cube = ModelCube(name="TestCube")
        model = cube.call(width=2.0, height=3.0, depth=4.0)
        json_output = model.to_json()
        expected_json = """{
  "name": "TestCube",
  "description": "Create a cube model at (0,0,0)",
  "type": "cube",
  "coord_x": 0.0,
  "coord_y": 0.0,
  "coord_z": 0.0,
  "box_size": [
    2.0,
    3.0,
    4.0
  ],
  "orientation_pitch": 0.0,
  "orientation_yaw": 0.0,
  "orientation_roll": 0.0,
  "model_data": null
}""".strip()
        self.assertEqual(json_output.strip(), expected_json)

if __name__ == "__main__":
    unittest.main()