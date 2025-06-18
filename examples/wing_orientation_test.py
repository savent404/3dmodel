#!/usr/bin/env python3
"""
Test script to verify the correct orientation of NACA airfoil sections for wing construction.
This script creates a simple wing with visualizations to verify the coordinate system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend_trimesh import BackendTrimesh
from models import ModelNACA4, ModelCube
from operations import ModelRigidTransform
import numpy as np


def test_wing_orientation():
    """Test wing section orientations to ensure correct layout."""
    print("=== Wing Orientation Test ===\n")
    
    backend = BackendTrimesh("wing_orientation_test")
    naca_tool = ModelNACA4()
    cube_tool = ModelCube()
    
    models = []
    
    # Create reference coordinate system markers
    print("Creating coordinate system markers...")
    
    # X-axis marker (red, forward direction)
    x_marker = cube_tool.call(
        name="X_Axis_Marker",
        width=2.0, height=0.1, depth=0.1,
        coord_x=1.0, coord_y=0.0, coord_z=0.0
    )
    models.append(x_marker)
    
    # Y-axis marker (green, span direction)  
    y_marker = cube_tool.call(
        name="Y_Axis_Marker",
        width=0.1, height=2.0, depth=0.1,
        coord_x=0.0, coord_y=1.0, coord_z=0.0
    )
    models.append(y_marker)
    
    # Z-axis marker (blue, vertical direction)
    z_marker = cube_tool.call(
        name="Z_Axis_Marker", 
        width=0.1, height=0.1, depth=2.0,
        coord_x=0.0, coord_y=0.0, coord_z=1.0
    )
    models.append(z_marker)
    
    print("Creating wing sections with proper orientation...")
    
    # Test different orientations to find the correct one
    orientations = [
        {"name": "Default", "pitch": 0, "yaw": 0, "roll": 0, "y_pos": -2},
        {"name": "Yaw_90", "pitch": 0, "yaw": 90, "roll": 0, "y_pos": -1},
        {"name": "Pitch_90", "pitch": 90, "yaw": 0, "roll": 0, "y_pos": 0},
        {"name": "Roll_90", "pitch": 0, "yaw": 0, "roll": 90, "y_pos": 1},
        {"name": "Pitch_-90", "pitch": -90, "yaw": 0, "roll": 0, "y_pos": 2},
    ]
    
    for orient in orientations:
        section = naca_tool.call(
            name=f"Test_{orient['name']}",
            naca_digits="2412",
            chord_length=0.8,
            thickness=0.02,
            coord_x=0, coord_y=orient['y_pos'], coord_z=0
        )
        section.orientation_pitch = orient['pitch']
        section.orientation_yaw = orient['yaw'] 
        section.orientation_roll = orient['roll']
        models.append(section)
        
        print(f"  - {section.name}: pitch={orient['pitch']}°, yaw={orient['yaw']}°, roll={orient['roll']}° at y={orient['y_pos']}")
    
    print(f"\nCreated {len(models)} test objects")
    print("\nExpected correct orientation:")
    print("  - Airfoil chord should align with X-axis (forward)")
    print("  - Airfoil thickness should be along Z-axis (vertical)")
    print("  - Wing sections should be spaced along Y-axis (span)")
    
    # Render everything
    print("\nRendering test scene...")
    try:
        result = backend.render(models)
        print(f"✓ {result}")
    except Exception as e:
        print(f"⚠ Rendering issue: {e}")
    
    # Export for external viewing
    print("\nExporting test scene...")
    try:
        backend.export_scene("wing_orientation_test.stl", "stl")
        print("✓ Exported to wing_orientation_test.stl")
        print("  You can open this file in a 3D viewer to verify orientations")
    except Exception as e:
        print(f"⚠ Export issue: {e}")
    
    return models


def analyze_naca_coordinates():
    """Analyze NACA coordinate generation to understand the default orientation."""
    print("\n=== NACA Coordinate Analysis ===\n")
    
    from models import ModelNACA4
    
    # Generate coordinates for a simple symmetric airfoil
    x, x_upper, y_upper, x_lower, y_lower = ModelNACA4.generate_naca4_coordinates(
        "0012", chord_length=1.0, resolution=10
    )
    
    print("Generated NACA 0012 coordinates (10 points):")
    print("  x_upper  y_upper  |  x_lower  y_lower")
    print("  ------   ------   |  ------   ------")
    for i in range(len(x_upper)):
        print(f"  {x_upper[i]:6.3f}   {y_upper[i]:6.3f}  |  {x_lower[i]:6.3f}   {y_lower[i]:6.3f}")
    
    print(f"\nCoordinate ranges:")
    print(f"  X: {min(min(x_upper), min(x_lower)):.3f} to {max(max(x_upper), max(x_lower)):.3f}")
    print(f"  Y: {min(min(y_upper), min(y_lower)):.3f} to {max(max(y_upper), max(y_lower)):.3f}")
    
    print(f"\nDefault orientation:")
    print(f"  - X-axis: chord direction (0 to {max(x):.3f})")
    print(f"  - Y-axis: thickness direction ({min(min(y_upper), min(y_lower)):.3f} to {max(max(y_upper), max(y_lower)):.3f})")
    print(f"  - Z-axis: extrusion direction (will be thin sheet)")
    
    print(f"\nFor wing construction, we need:")
    print(f"  - X-axis: forward direction (chord)")
    print(f"  - Y-axis: span direction (wing tip to tip)")  
    print(f"  - Z-axis: thickness direction (up/down)")
    print(f"  → Rotation needed: Pitch -90° to move Y→Z, Z→Y")


if __name__ == "__main__":
    analyze_naca_coordinates()
    test_wing_orientation()
