from if_tool import ToolIface
from if_model import Model


class ModelCube(ToolIface):
    """
    A tool for creating a cube model with specified dimensions and coordinates.
    """
    def __init__(self):
        description = "Create a cube model, the cube is centered at (0,0,0) with specified width, height, and depth."
        parameters = {
            "name": {
                "type": "string",
                "description": "Name of the cube model, incremented if already exists",
                "default": "Cube_1",
                "required": True
            },
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
            }
        }
        super().__init__("Cube", description, parameters, "model")

    def call(self, name: str, width: float, height: float, depth: float) -> Model:
        box = [width, height, depth]
        extra = {
            "width": width,
            "height": height,
            "depth": depth,
        }
        model = Model(
            name=name,
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

class ModelCylinder(ToolIface):
    """
    A tool for creating a cylinder model with specified dimensions and coordinates.
    """
    def __init__(self):
        description = "Create a cylinder model, the cylinder is centered at (0,0,0) with specified radius and height."
        parameters = {
            "name": {
                "type": "string",
                "description": "Name of the cylinder model, incremented if already exists",
                "default": "Cylinder_1",
                "required": True
            },
            "radius_x": {
                "type": "float",
                "description": "Radius of the cylinder",
                "default": 1.0,
                "required": True
            },
            "radius_y": {
                "type": "float",
                "description": "Radius of the cylinder (usually same as radius_x)",
                "default": 1.0,
                "required": True
            },
            "height": {
                "type": "float",
                "description": "Height of the cylinder",
                "default": 1.0,
                "required": True
            },
            "coord_x": {
                "type": "float",
                "description": "X coordinate of the cylinder center",
                "default": 0.0,
                "required": False
            },
            "coord_y": {
                "type": "float",
                "description": "Y coordinate of the cylinder center",
                "default": 0.0,
                "required": False
            },
            "coord_z": {
                "type": "float",
                "description": "Z coordinate of the cylinder center",
                "default": 0.0,
                "required": False
            },
        }
        super().__init__("Cylinder", description, parameters, "model")

    def call(self, name: str, radius_x: float, radius_y: float, height: float, coord_x: float = 0, coord_y: float = 0, coord_z: float = 0) -> Model:

        box = [radius_x * 2, radius_y * 2, height]
        extra = {
            "radius_x": radius_x,
            "radius_y": radius_y,
            "height": height,
        }
        model = Model(
            name=name,
            description=self.description,
            type="cylinder",
            coord_x=coord_x,
            coord_y=coord_y,
            coord_z=coord_z,
            box_size=box,
            orientation_pitch=0.0,
            orientation_yaw=0.0,
            orientation_roll=0.0,
            model_data=extra
        )
        return model

class ModelHalfCylinder(ToolIface):
    """
    A tool for creating a half cylinder model with specified dimensions and coordinates, 在y轴上对称, 正视图为矩形
    """
    def __init__(self):
        description = "Create a half cylinder model, the half cylinder is centered at (0,0,0) with specified radius and height (y轴对称). 正视图为矩形."
        parameters = {
            "name": {
                "type": "string",
                "description": "Name of the half cylinder model, incremented if already exists",
                "default": "HalfCylinder_1",
                "required": True
            },
            "radius_x": {
                "type": "float",
                "description": "Radius of the half cylinder",
                "default": 1.0,
                "required": True
            },
            "radius_y": {
                "type": "float",
                "description": "Radius of the half cylinder (usually same as radius_x)",
                "default": 1.0,
                "required": True
            },
            "height": {
                "type": "float",
                "description": "Height of the half cylinder",
                "default": 1.0,
                "required": True
            }
        }
        super().__init__("HalfCylinder", description, parameters, "model")

    def call(self, name: str, radius_x: float, radius_y: float, height: float) -> Model:

        box = [radius_x * 2, radius_y * 2, height]
        extra = {
            "radius_x": radius_x,
            "radius_y": radius_y,
            "height": height,
        }
        model = Model(
            name=name,
            description=self.description,
            type="half cylinder",
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