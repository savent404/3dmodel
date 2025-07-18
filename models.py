from if_tool import ToolIface
from if_model import Model

# Global coordinate system definitions
COORDINATE_SYSTEM = {
    "x_axis": {
        "name": "Primary/Length/Chord",
        "description": "Main dimension of the object (e.g., chord direction for airfoils, length for boxes)",
        "typical_use": "Airfoil chord direction, box length, cylinder axis"
    },
    "y_axis": {
        "name": "Secondary/Width/Span", 
        "description": "Secondary dimension (e.g., span direction for wings, width for boxes)",
        "typical_use": "Wing span direction, box width, stackable dimension"
    },
    "z_axis": {
        "name": "Height/Thickness/Vertical",
        "description": "Height or thickness dimension (e.g., airfoil thickness, box height)",
        "typical_use": "Airfoil thickness direction, box height, vertical dimension"
    }
}

def get_coordinate_system_description() -> str:
    """Get the standard coordinate system description."""
    return """Standard coordinate system used throughout the system:
- X-axis: Primary/Length/Chord direction
- Y-axis: Secondary/Width/Span direction  
- Z-axis: Height/Thickness/Vertical direction"""


class ModelCube(ToolIface):
    """
    A tool for creating a cube model with specified dimensions and coordinates.
    """
    
    # Orientation configuration for cube models
    ORIENTATION_CONFIG = {
        "length_direction": "x_axis",
        "width_direction": "y_axis",
        "height_direction": "z_axis", 
        "description": "Cube with length along X-axis, width along Y-axis, height along Z-axis",
        "default_orientation": {
            "pitch": 0.0,
            "yaw": 0.0,
            "roll": 0.0
        }
    }
    
    def __init__(self):
        description = """Cube model with standardized orientation:
- Length dimension: X-axis 
- Width dimension: Y-axis
- Height dimension: Z-axis
Centered at specified coordinates with edges aligned to coordinate axes."""
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
    
    # Orientation configuration for cylinder models
    ORIENTATION_CONFIG = {
        "axis_direction": "z_axis",
        "radius_x_direction": "x_axis",
        "radius_y_direction": "y_axis",
        "description": "Cylinder with main axis along Z-axis, circular cross-section in X-Y plane",
        "default_orientation": {
            "pitch": 0.0,
            "yaw": 0.0, 
            "roll": 0.0
        }
    }
    
    def __init__(self):
        description = """Cylinder model with standardized orientation:
- Cylinder axis: Z-axis (height direction)
- Circular cross-section: X-Y plane
- Radius along X and Y axes can be different for elliptical cylinders
- X-axis: Primary radius direction
- Y-axis: Secondary radius direction  
- Z-axis: Height/length direction
Centered at specified coordinates."""
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
    A tool for creating a half cylinder model with specified dimensions and coordinates.
    """
    
    # Orientation configuration for half-cylinder models
    ORIENTATION_CONFIG = {
        "axis_direction": "z_axis",
        "radius_x_direction": "x_axis", 
        "radius_y_direction": "y_axis",
        "description": "Half-cylinder with main axis along Z-axis, half-circular cross-section in X-Y plane",
        "default_orientation": {
            "pitch": 0.0,
            "yaw": 0.0,
            "roll": 0.0
        }
    }
    
    def __init__(self):
        description = """Half-cylinder model with standardized orientation:
- Cylinder axis: Z-axis (height direction)
- Half-circular cross-section: X-Y plane (cut along Y-axis)
- X-axis: Primary radius direction
- Y-axis: Secondary radius direction (cut plane)
- Z-axis: Height/length direction
Centered at specified coordinates with flat face along the Y-axis."""
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

class ModelNACA4(ToolIface):
    """
    A tool for creating a NACA 4-digit airfoil model for wing design.
    Creates a thin airfoil section that can be used to build wing structures.
    """
    
    # Orientation configuration for NACA4 airfoil models
    ORIENTATION_CONFIG = {
        "chord_direction": "x_axis",
        "span_direction": "y_axis", 
        "thickness_direction": "z_axis",
        "section_normal": "y_axis",
        "description": "NACA airfoil with chord along X-axis, stackable along Y-axis (span), thickness along Z-axis",
        "default_orientation": {
            "pitch": 0.0,  # rotation around X-axis
            "yaw": 0.0,    # rotation around Y-axis  
            "roll": 0.0    # rotation around Z-axis
        }
    }
    
    def __init__(self):
        description = """NACA 4-digit airfoil model with standardized orientation:
- Chord direction: X-axis (leading edge to trailing edge)
- Span direction: Y-axis (wing spread, stackable along this axis)
- Thickness direction: Z-axis (airfoil thickness, bottom to top)
- Section normal: Y-axis direction (perpendicular to airfoil surface)
At default orientation (0,0,0), the airfoil points along positive X-axis."""
        
        parameters = {
            "name": {
                "type": "string",
                "description": "Name of the NACA airfoil model",
                "default": "NACA_0012",
                "required": True
            },
            "naca_digits": {
                "type": "string",
                "description": "4-digit NACA designation (e.g., '0012', '2412', '4412')",
                "default": "0012",
                "required": True
            },
            "chord_length": {
                "type": "float",
                "description": "Chord length of the airfoil",
                "default": 1.0,
                "required": True
            },
            "thickness": {
                "type": "float",
                "description": "Thickness of the airfoil sheet",
                "default": 0.01,
                "required": True
            },
            "resolution": {
                "type": "integer",
                "description": "Number of points to define the airfoil curve (higher = smoother)",
                "default": 50,
                "required": False
            },
            "coord_x": {
                "type": "float",
                "description": "X coordinate of the airfoil center",
                "default": 0.0,
                "required": False
            },
            "coord_y": {
                "type": "float",
                "description": "Y coordinate of the airfoil center",
                "default": 0.0,
                "required": False
            },
            "coord_z": {
                "type": "float",
                "description": "Z coordinate of the airfoil center",
                "default": 0.0,
                "required": False
            }
        }
        super().__init__("NACA4", description, parameters, "model")

    def call(self, name: str, naca_digits: str, chord_length: float, thickness: float, 
             resolution: int = 50, coord_x: float = 0.0, coord_y: float = 0.0, coord_z: float = 0.0) -> Model:
        """
        Create a NACA 4-digit airfoil model.
        
        Args:
            name: Name of the model
            naca_digits: 4-digit NACA designation (e.g., '0012')
            chord_length: Chord length of the airfoil
            thickness: Thickness of the airfoil sheet
            resolution: Number of points for airfoil curve
            coord_x, coord_y, coord_z: Position coordinates
        """
        
        # Validate NACA digits
        if len(naca_digits) != 4 or not naca_digits.isdigit():
            raise ValueError("NACA digits must be a 4-digit string (e.g., '0012')")
        
        # Parse NACA parameters
        m = int(naca_digits[0]) / 100.0  # Maximum camber as fraction of chord
        p = int(naca_digits[1]) / 10.0   # Position of maximum camber as fraction of chord
        t = int(naca_digits[2:4]) / 100.0  # Maximum thickness as fraction of chord
        
        # Calculate bounding box
        box = [chord_length, thickness, chord_length * t * 2]  # Approximate dimensions
        
        extra = {
            "naca_digits": naca_digits,
            "chord_length": chord_length,
            "sheet_thickness": thickness,
            "resolution": resolution,
            "max_camber": m,
            "max_camber_position": p,
            "thickness_ratio": t,
            "airfoil_type": "naca4"
        }
        
        model = Model(
            name=name,
            description=self.description,
            type="naca4",
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

    @staticmethod
    def generate_naca4_coordinates(naca_digits: str, chord_length: float = 1.0, resolution: int = 50):
        """
        Generate NACA 4-digit airfoil coordinates.
        
        Args:
            naca_digits: 4-digit NACA designation
            chord_length: Chord length
            resolution: Number of points
            
        Returns:
            tuple: (x_coords, y_upper, y_lower) arrays
        """
        import numpy as np
        
        # Parse NACA parameters
        m = int(naca_digits[0]) / 100.0  # Maximum camber
        p = int(naca_digits[1]) / 10.0   # Position of maximum camber
        t = int(naca_digits[2:4]) / 100.0  # Maximum thickness
        
        # Generate x coordinates (cosine spacing for better leading/trailing edge resolution)
        beta = np.linspace(0, np.pi, resolution)
        x = chord_length * (1 - np.cos(beta)) / 2
        
        # Thickness distribution (symmetric airfoil)
        yt = 5 * t * chord_length * (
            0.2969 * np.sqrt(x / chord_length) - 
            0.1260 * (x / chord_length) - 
            0.3516 * (x / chord_length)**2 + 
            0.2843 * (x / chord_length)**3 - 
            0.1015 * (x / chord_length)**4
        )
        
        # Camber line
        if m == 0 or p == 0:
            # Symmetric airfoil
            yc = np.zeros_like(x)
            dyc_dx = np.zeros_like(x)
        else:
            # Cambered airfoil
            yc = np.zeros_like(x)
            dyc_dx = np.zeros_like(x)
            
            # Forward of maximum camber
            mask1 = x <= p * chord_length
            yc[mask1] = m * chord_length * (2 * p * x[mask1] / chord_length - (x[mask1] / chord_length)**2) / p**2
            dyc_dx[mask1] = 2 * m * (p - x[mask1] / chord_length) / p**2
            
            # Aft of maximum camber
            mask2 = x > p * chord_length
            yc[mask2] = m * chord_length * ((1 - 2*p) + 2*p*x[mask2]/chord_length - (x[mask2]/chord_length)**2) / (1-p)**2
            dyc_dx[mask2] = 2 * m * (p - x[mask2] / chord_length) / (1-p)**2
        
        # Calculate angle
        theta = np.arctan(dyc_dx)
        
        # Upper and lower surface coordinates
        x_upper = x - yt * np.sin(theta)
        y_upper = yc + yt * np.cos(theta)
        x_lower = x + yt * np.sin(theta)
        y_lower = yc - yt * np.cos(theta)
        
        return x, x_upper, y_upper, x_lower, y_lower

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