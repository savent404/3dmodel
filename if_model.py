from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

@dataclass
class Model:
    name: str
    description: str
    type: str
    coord_x : float = field(default=0.0)
    coord_y : float = field(default=0.0)
    coord_z : float = field(default=0.0)
    box_size: List[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    orientation_pitch : float = field(default=0.0)
    orientation_yaw : float = field(default=0.0)
    orientation_roll : float = field(default=0.0)
    model_data: Optional[Dict[str, Any]] = field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "coord_x": self.coord_x,
            "coord_y": self.coord_y,
            "coord_z": self.coord_z,
            "box_size": self.box_size,
            "orientation_pitch": self.orientation_pitch,
            "orientation_yaw": self.orientation_yaw,
            "orientation_roll": self.orientation_roll,
            "model_data": self.model_data
        }
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            type=data.get("type", ""),
            coord_x=data.get("coord_x", 0.0),
            coord_y=data.get("coord_y", 0.0),
            coord_z=data.get("coord_z", 0.0),
            box_size=data.get("box_size", [0.0, 0.0, 0.0]),
            orientation_pitch=data.get("orientation_pitch"),
            orientation_yaw=data.get("orientation_yaw"),
            orientation_roll=data.get("orientation_roll"),
            model_data=data.get("model_data")
        )
    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), indent=2)
    def from_json(cls, json_str: str) -> 'Model':
        import json
        data = json.loads(json_str)
        return cls.from_dict(data)
    def __str__(self) -> str:
        return f"Model(name={self.name}, type={self.type}, coord=({self.coord_x}, {self.coord_y}, {self.coord_z}), orientation=({self.orientation_pitch}, {self.orientation_yaw}, {self.orientation_roll}))"

@dataclass
class ModelOperation:
    type: str
    description: str
    models: List[Model] = field(default_factory=list)
    parameters: Optional[Dict[str, Any]] = field(default=None)

import unittest

class TestModel(unittest.TestCase):
    def test_model_creation(self):
        model = Model(
            name="TestModel",
            description="A test model",
            type="3D",
            coord_x=1.0,
            coord_y=2.0,
            coord_z=3.0,
            orientation_pitch=0.1,
            orientation_yaw=0.2,
            orientation_roll=0.3,
            model_data={"key": "value"}
        )
        
        self.assertEqual(model.name, "TestModel")
        self.assertEqual(model.description, "A test model")
        self.assertEqual(model.type, "3D")
        self.assertEqual(model.coord_x, 1.0)
        self.assertEqual(model.coord_y, 2.0)
        self.assertEqual(model.coord_z, 3.0)
        self.assertAlmostEqual(model.orientation_pitch, 0.1)
        self.assertAlmostEqual(model.orientation_yaw, 0.2)
        self.assertAlmostEqual(model.orientation_roll, 0.3)
        self.assertEqual(model.model_data, {"key": "value"})
    def test_model_default_values(self):
        model = Model(
            name="DefaultModel",
            description="A model with default values",
            type="2D"
        )
        self.assertEqual(model.coord_x, 0.0)
        self.assertEqual(model.coord_y, 0.0)
        self.assertEqual(model.coord_z, 0.0)
        self.assertEqual(model.orientation_pitch, 0.0)
        self.assertEqual(model.orientation_yaw, 0.0)
        self.assertEqual(model.orientation_roll, 0.0)
        self.assertEqual(model.box_size, [0.0, 0.0, 0.0])
        self.assertIsNone(model.model_data)
        self.assertEqual(model.name, "DefaultModel")
        self.assertEqual(model.description, "A model with default values")
        self.assertEqual(model.type, "2D")
    
    def test_model_to_dict(self):
        model = Model(
            name="DictModel",
            description="A model for dict conversion",
            type="3D",
            coord_x=1.0,
            coord_y=2.0,
            coord_z=3.0
        )
        expected_dict = {
            "name": "DictModel",
            "description": "A model for dict conversion",
            "type": "3D",
            "coord_x": 1.0,
            "coord_y": 2.0,
            "coord_z": 3.0,
            "box_size": [0.0, 0.0, 0.0],
            "orientation_pitch": 0.0,
            "orientation_yaw": 0.0,
            "orientation_roll": 0.0,
            "model_data": None
        }
        self.assertEqual(model.to_dict(), expected_dict)

    def test_model_from_dict(self):
        model_data = {
            "name": "FromDictModel",
            "description": "A model created from dict",
            "type": "2D",
            "coord_x": 4.0,
            "coord_y": 5.0,
            "coord_z": 6.0
        }
        model = Model.from_dict(model_data)
        self.assertEqual(model.name, "FromDictModel")
        self.assertEqual(model.description, "A model created from dict")
        self.assertEqual(model.type, "2D")
        self.assertEqual(model.coord_x, 4.0)
        self.assertEqual(model.coord_y, 5.0)
        self.assertEqual(model.coord_z, 6.0)

class TestModeOperation(unittest.TestCase):
    def test_mode_operation_creation(self):
        model1 = Model(name="Model1", description="First model", type="3D")
        model2 = Model(name="Model2", description="Second model", type="2D")
        
        operation = ModelOperation(
            type="TestOperation",
            description="A test operation",
            models=[model1, model2],
            parameters={"param1": "value1"}
        )
        
        self.assertEqual(operation.type, "TestOperation")
        self.assertEqual(operation.description, "A test operation")
        self.assertEqual(len(operation.models), 2)
        self.assertEqual(operation.parameters, {"param1": "value1"})

if __name__ == "__main__":
    unittest.main()

