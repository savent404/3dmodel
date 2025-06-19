"""
Model Orientation Configuration Module

This module defines the standardized coordinate system and orientation constraints
for all 3D models in the system. All models, tools, backends, and agents must
follow these constraints to ensure consistency.

GLOBAL COORDINATE SYSTEM:
- X-axis: Primary dimension (length/chord direction)
- Y-axis: Secondary dimension (width/span direction) 
- Z-axis: Height/thickness dimension (vertical direction)

This configuration must be used by:
1. Model creation tools (models.py)
2. Backend implementations (backend_trimesh.py, etc.)
3. Agent system prompts (agent.py)
4. Tool descriptions and parameters
"""

# Standard coordinate system definitions
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

# Model-specific orientation constraints
MODEL_ORIENTATIONS = {
    "naca4": {
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
    },
    "cube": {
        "length_direction": "x_axis",
        "width_direction": "y_axis",
        "height_direction": "z_axis", 
        "description": "Cube with length along X-axis, width along Y-axis, height along Z-axis",
        "default_orientation": {
            "pitch": 0.0,
            "yaw": 0.0,
            "roll": 0.0
        }
    },
    "cylinder": {
        "axis_direction": "z_axis",
        "radius_x_direction": "x_axis",
        "radius_y_direction": "y_axis",
        "description": "Cylinder with main axis along Z-axis, circular cross-section in X-Y plane",
        "default_orientation": {
            "pitch": 0.0,
            "yaw": 0.0, 
            "roll": 0.0
        }
    },
    "half_cylinder": {
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
}

# Common phrases for descriptions
ORIENTATION_DESCRIPTIONS = {
    "naca4_full": """NACA 4-digit airfoil model with standardized orientation:
- Chord direction: X-axis (leading edge to trailing edge)
- Span direction: Y-axis (wing spread, stackable along this axis)
- Thickness direction: Z-axis (airfoil thickness, bottom to top)
- Section normal: Y-axis direction (perpendicular to airfoil surface)
At default orientation (0,0,0), the airfoil points along positive X-axis.""",
    
    "cube_full": """Cube model with standardized orientation:
- Length dimension: X-axis 
- Width dimension: Y-axis
- Height dimension: Z-axis
Centered at specified coordinates with edges aligned to coordinate axes.""",
      "cylinder_full": """Cylinder model with standardized orientation:
- Cylinder axis: Z-axis (height direction)
- Circular cross-section: X-Y plane
- Radius along X and Y axes can be different for elliptical cylinders
- X-axis: Primary radius direction
- Y-axis: Secondary radius direction  
- Z-axis: Height/length direction
Centered at specified coordinates.""",
    
    "half_cylinder_full": """Half-cylinder model with standardized orientation:
- Cylinder axis: Z-axis (height direction)
- Half-circular cross-section: X-Y plane (cut along Y-axis)
- X-axis: Primary radius direction
- Y-axis: Secondary radius direction (cut plane)
- Z-axis: Height/length direction
Centered at specified coordinates with flat face along the Y-axis.""",
    
    "coordinate_system": """Standard coordinate system used throughout the system:
- X-axis: Primary/Length/Chord direction
- Y-axis: Secondary/Width/Span direction  
- Z-axis: Height/Thickness/Vertical direction"""
}

def get_model_orientation(model_type: str) -> dict:
    """
    Get the orientation configuration for a specific model type.
    
    Args:
        model_type: Type of model ("naca4", "cube", "cylinder", etc.)
        
    Returns:
        Dictionary containing orientation configuration for the model
        
    Raises:
        ValueError: If model type is not supported
    """
    if model_type not in MODEL_ORIENTATIONS:
        raise ValueError(f"Unsupported model type: {model_type}. Supported types: {list(MODEL_ORIENTATIONS.keys())}")
    
    return MODEL_ORIENTATIONS[model_type]

def get_orientation_description(model_type: str) -> str:
    """
    Get the full orientation description for a model type.
    
    Args:
        model_type: Type of model
        
    Returns:
        Full description string for the model orientation
    """
    key = f"{model_type}_full"
    if key in ORIENTATION_DESCRIPTIONS:
        return ORIENTATION_DESCRIPTIONS[key]
    else:
        config = get_model_orientation(model_type)
        return config["description"]

def validate_model_orientation(model_type: str, orientation: dict) -> bool:
    """
    Validate that a model's orientation follows the standard constraints.
    
    Args:
        model_type: Type of model
        orientation: Dictionary with pitch, yaw, roll values
        
    Returns:
        True if orientation is valid, False otherwise
    """
    try:
        config = get_model_orientation(model_type)
        default_orientation = config["default_orientation"]
        
        # Check if all required orientation keys are present
        required_keys = ["pitch", "yaw", "roll"]
        for key in required_keys:
            if key not in orientation:
                return False
                
        return True
    except ValueError:
        return False

def get_coordinate_system_description() -> str:
    """Get the standard coordinate system description."""
    return ORIENTATION_DESCRIPTIONS["coordinate_system"]
